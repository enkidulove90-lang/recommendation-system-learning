import { env } from "cloudflare:workers";
import { SELF } from "cloudflare:test";
import { describe, expect, it } from "vitest";

import { signSession, type AppEnv } from "../src/security";
import worker from "../src/index";

const testEnv = env as AppEnv & { ARTIFACTS: R2Bucket };
const origin = "http://127.0.0.1:4322";

async function authorization(): Promise<string> {
  const now = Math.floor(Date.now() / 1000);
  return `Bearer ${await signSession("owner@example.com", testEnv.SESSION_SIGNING_KEY, now)}`;
}

async function submitUrl(url: string): Promise<Record<string, unknown>> {
  const response = await SELF.fetch("https://worker.test/v1/intake/url", {
    method: "POST",
    headers: {
      authorization: await authorization(),
      "content-type": "application/json",
      origin,
    },
    body: JSON.stringify({ url }),
  });
  expect([200, 202]).toContain(response.status);
  return response.json<Record<string, unknown>>();
}

describe("paper intake API", () => {
  it("keeps URL intake available while PDF storage is disabled", async () => {
    const disabledEnv = {
      ...testEnv,
      ARTIFACT_STORAGE_ENABLED: "false",
      ARTIFACTS: undefined,
    } as unknown as AppEnv;
    const pdf = new TextEncoder().encode("%PDF-1.7\n%%EOF");
    const pdfResponse = await worker.fetch(
      new Request("https://worker.test/v1/intake/pdf", {
        method: "POST",
        headers: {
          authorization: await authorization(),
          "content-type": "application/pdf",
          origin,
        },
        body: pdf,
      }),
      disabledEnv,
    );
    expect(pdfResponse.status).toBe(503);
    expect((await pdfResponse.json<{ code: string }>()).code).toBe("pdf_upload_unavailable");

    const urlResponse = await worker.fetch(
      new Request("https://worker.test/v1/intake/url", {
        method: "POST",
        headers: {
          authorization: await authorization(),
          "content-type": "application/json",
          origin,
        },
        body: JSON.stringify({ url: "https://papers.example/url-only-paper" }),
      }),
      disabledEnv,
    );
    expect(urlResponse.status).toBe(202);
  });

  it("lists only the owner's sanitized jobs", async () => {
    const submitted = await submitUrl("https://papers.example/private-source.pdf");
    const response = await SELF.fetch("https://worker.test/v1/jobs", {
      headers: { authorization: await authorization(), origin },
    });
    expect(response.status).toBe(200);
    const payload = await response.json<{ jobs: Array<Record<string, unknown>> }>();
    const job = payload.jobs.find((item) => item.job_id === submitted.job_id);
    expect(job).toMatchObject({ status: "queued", retryable: false });
    expect(job).not.toHaveProperty("input_ref");
    expect(job).not.toHaveProperty("owner_identity");
    expect(job).not.toHaveProperty("lease_owner");
    expect(JSON.stringify(job)).not.toContain("private-source.pdf");
  });

  it("exports an owner-scoped task log with stage events", async () => {
    const submitted = await submitUrl("https://papers.example/loggable-paper");
    const repository = new (await import("../src/repository")).IntakeRepository(testEnv.DB);
    await repository.recordJobEvent(String(submitted.job_id), "job.stage_completed", {
      stage: "mineru_parse",
    });

    const response = await SELF.fetch(`https://worker.test/v1/jobs/${submitted.job_id}/log`, {
      headers: { authorization: await authorization(), origin },
    });
    expect(response.status).toBe(200);
    const payload = await response.json<{ job: Record<string, unknown>; events: Array<Record<string, unknown>> }>();
    expect(payload.job).toMatchObject({ job_id: submitted.job_id, status: "queued" });
    expect(payload.events.some((event) => event.event_type === "job.stage_completed")).toBe(true);
    expect(JSON.stringify(payload)).not.toContain("input_ref");
    expect(JSON.stringify(payload)).not.toContain("lease_owner");
  });

  it("retries only failed jobs owned by the authenticated user", async () => {
    const submitted = await submitUrl("https://papers.example/retry-me");
    await testEnv.DB.prepare(
      "UPDATE jobs SET status = 'failed', error_code = 'parse_failed', error_message = '解析失败' WHERE job_id = ?",
    ).bind(submitted.job_id).run();

    const idempotencyKey = "77777777-7777-4777-8777-777777777777";
    const response = await SELF.fetch(`https://worker.test/v1/jobs/${submitted.job_id}/retry`, {
      method: "POST",
      headers: { authorization: await authorization(), origin, "idempotency-key": idempotencyKey },
    });
    expect(response.status).toBe(202);
    expect(await response.json<Record<string, unknown>>()).toMatchObject({
      job_id: submitted.job_id,
      status: "queued",
      code: "retry_accepted",
    });

    const second = await SELF.fetch(`https://worker.test/v1/jobs/${submitted.job_id}/retry`, {
      method: "POST",
      headers: { authorization: await authorization(), origin, "idempotency-key": idempotencyKey },
    });
    expect(second.status).toBe(202);
    expect(second.headers.get("idempotency-replayed")).toBe("true");
    expect((await second.json<{ code: string }>()).code).toBe("retry_accepted");
  });

  it("rejects non-PDF bodies before writing R2", async () => {
    const bytes = new TextEncoder().encode("not a pdf");
    const response = await SELF.fetch("https://worker.test/v1/intake/pdf", {
      method: "POST",
      headers: {
        authorization: await authorization(),
        "content-length": String(bytes.byteLength),
        "content-type": "application/pdf",
        origin,
      },
      body: bytes,
    });
    expect(response.status).toBe(415);
    expect((await testEnv.ARTIFACTS.list()).objects).toHaveLength(0);
  });

  it("stores one valid PDF and reuses it on a repeated upload", async () => {
    const bytes = new TextEncoder().encode("%PDF-1.7\n%%EOF");
    const upload = async () => {
      const response = await SELF.fetch("https://worker.test/v1/intake/pdf", {
        method: "POST",
        headers: {
          authorization: await authorization(),
          "content-type": "application/pdf",
          origin,
        },
        body: bytes,
      });
      return { response, payload: await response.json<Record<string, unknown>>() };
    };

    const first = await upload();
    const second = await upload();
    expect(first.response.status).toBe(202);
    expect(second.response.status).toBe(200);
    expect(second.payload.paper_id).toBe(first.payload.paper_id);
    expect(second.payload.job_id).toBe(first.payload.job_id);
    expect(second.payload.code).toBe("duplicate_paper");
    expect((await testEnv.ARTIFACTS.list()).objects).toHaveLength(1);
  });

  it("returns an existing identity for a duplicate DOI", async () => {
    const first = await submitUrl("https://doi.org/10.1287/mnsc.2024.04540");
    const second = await submitUrl("https://doi.org/10.1287/mnsc.2024.04540");
    expect(second.paper_id).toBe(first.paper_id);
    expect(second.job_id).toBe(first.job_id);
    expect(second.code).toBe("duplicate_paper");
  });

  it("deduplicates normalized publisher links and concurrent submissions", async () => {
    const [first, second] = await Promise.all([
      submitUrl("https://papers.example/item?id=42&utm_source=test#abstract"),
      submitUrl("https://papers.example/item?utm_source=other&id=42"),
    ]);
    expect(second.paper_id).toBe(first.paper_id);
    expect(second.job_id).toBe(first.job_id);
    const count = await testEnv.DB.prepare("SELECT COUNT(*) AS count FROM jobs WHERE paper_id = ?")
      .bind(first.paper_id)
      .first<{ count: number }>();
    expect(count?.count).toBe(1);
  });

  it("normalizes arXiv PDF links and rejects local network targets", async () => {
    const accepted = await submitUrl("https://arxiv.org/pdf/2608.17316.pdf?download=1");
    expect(accepted.code).toBe("intake_accepted");

    const response = await SELF.fetch("https://worker.test/v1/intake/url", {
      method: "POST",
      headers: {
        authorization: await authorization(),
        "content-type": "application/json",
        origin,
      },
      body: JSON.stringify({ url: "https://127.0.0.1/private.pdf" }),
    });
    expect(response.status).toBe(400);
    expect((await response.json<{ code: string }>()).code).toBe("url_not_allowed");
  });

  it("echoes CORS only for an exact allowed origin", async () => {
    const allowed = await SELF.fetch("https://worker.test/v1/intake/url", {
      method: "OPTIONS",
      headers: { origin },
    });
    expect(allowed.status).toBe(204);
    expect(allowed.headers.get("access-control-allow-origin")).toBe(origin);

    const denied = await SELF.fetch("https://worker.test/v1/intake/url", {
      method: "OPTIONS",
      headers: { origin: "https://attacker.example" },
    });
    expect(denied.status).toBe(403);
    expect(denied.headers.get("access-control-allow-origin")).toBeNull();
  });
});
