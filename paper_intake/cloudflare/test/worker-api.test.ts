import { env } from "cloudflare:workers";
import { SELF } from "cloudflare:test";
import { describe, expect, it } from "vitest";

import { IntakeRepository } from "../src/repository";
import type { AppEnv } from "../src/security";

const testEnv = env as AppEnv;
const machineHeaders = {
  authorization: "Bearer test-worker-token",
  "content-type": "application/json",
};

async function seedJob(inputType: "url" | "pdf" = "url") {
  const repository = new IntakeRepository(testEnv.DB);
  const paper = await repository.createOrReusePaper({
    canonicalUrl: `https://papers.example/${crypto.randomUUID()}`,
  });
  const inputRef = inputType === "pdf"
    ? `originals/${paper.paperId}/paper.pdf`
    : paper.canonicalUrl;
  if (inputType === "pdf") {
    await testEnv.ARTIFACTS.put(inputRef, new TextEncoder().encode("%PDF-1.7\n%%EOF"));
  }
  return repository.createJob({
    paperId: paper.paperId,
    ownerIdentity: "owner@example.com",
    inputType,
    inputRef,
  });
}

async function claim(workerId = "worker-a", authorization = machineHeaders.authorization) {
  return SELF.fetch("https://worker.test/v1/worker/claim", {
    method: "POST",
    headers: { ...machineHeaders, authorization },
    body: JSON.stringify({ worker_id: workerId, lease_seconds: 600 }),
  });
}

describe("remote worker API", () => {
  it("returns 204 when no work is queued", async () => {
    const response = await SELF.fetch("https://worker.test/v1/worker/jobs/claim", {
      method: "POST",
      headers: machineHeaders,
      body: JSON.stringify({ worker_id: "worker-a" }),
    });
    expect(response.status).toBe(204);
  });

  it("requires the machine token and renews only the current lease", async () => {
    const job = await seedJob();
    expect((await claim("worker-a", "Bearer wrong")).status).toBe(401);
    const claimedResponse = await claim();
    expect(claimedResponse.status).toBe(200);
    const claimed = await claimedResponse.json<{ job_id: string; lease_owner: string }>();
    expect(claimed.job_id).toBe(job.jobId);

    const heartbeat = (workerId: string) => SELF.fetch(
      `https://worker.test/v1/worker/jobs/${job.jobId}/heartbeat`,
      {
        method: "POST",
        headers: machineHeaders,
        body: JSON.stringify({ worker_id: workerId, lease_seconds: 600 }),
      },
    );
    expect((await heartbeat("other-worker")).status).toBe(409);
    expect((await heartbeat(claimed.lease_owner)).status).toBe(200);
  });

  it("serves the claimed PDF without exposing its R2 key", async () => {
    const job = await seedJob("pdf");
    await claim();
    const response = await SELF.fetch(
      `https://worker.test/v1/worker/jobs/${job.jobId}/input?worker_id=worker-a`,
      { headers: { authorization: machineHeaders.authorization } },
    );
    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toBe("application/pdf");
    expect(new TextDecoder().decode(await response.arrayBuffer())).toContain("%PDF-");
    expect(response.headers.get("x-r2-key")).toBeNull();
  });

  it("verifies artifact hashes before writing R2 and records checkpoints", async () => {
    const job = await seedJob();
    await claim();
    const bytes = new TextEncoder().encode("# parsed paper");
    const upload = (sha256: string) => SELF.fetch(
      `https://worker.test/v1/worker/jobs/${job.jobId}/artifacts/parsed_markdown?worker_id=worker-a`,
      {
        method: "PUT",
        headers: {
          authorization: machineHeaders.authorization,
          "content-type": "text/markdown; charset=utf-8",
          "x-content-sha256": sha256,
          "x-artifact-name": "paper.md",
        },
        body: bytes,
      },
    );
    expect((await upload("wrong")).status).toBe(422);
    expect((await testEnv.ARTIFACTS.list({ prefix: "derived/" })).objects).toHaveLength(0);

    const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", bytes));
    const sha256 = [...digest].map((value) => value.toString(16).padStart(2, "0")).join("");
    const accepted = await upload(sha256);
    expect(accepted.status).toBe(201);
    expect((await testEnv.ARTIFACTS.list({ prefix: "derived/" })).objects).toHaveLength(1);

    const checkpoint = await SELF.fetch(
      `https://worker.test/v1/worker/jobs/${job.jobId}/checkpoint`,
      {
        method: "POST",
        headers: machineHeaders,
        body: JSON.stringify({
          worker_id: "worker-a",
          stage: "parsed",
          output: { artifact_id: (await accepted.json<{ artifact_id: string }>()).artifact_id },
        }),
      },
    );
    expect(checkpoint.status).toBe(200);
  });

  it("records processing failures without losing completed checkpoints", async () => {
    const job = await seedJob();
    await claim();
    const checkpoint = await SELF.fetch(
      `https://worker.test/v1/worker/jobs/${job.jobId}/checkpoint`,
      {
        method: "POST",
        headers: machineHeaders,
        body: JSON.stringify({ worker_id: "worker-a", stage: "parsed", output: { ok: true } }),
      },
    );
    expect(checkpoint.status).toBe(200);
    const failed = await SELF.fetch(`https://worker.test/v1/worker/jobs/${job.jobId}/fail`, {
      method: "POST",
      headers: machineHeaders,
      body: JSON.stringify({
        worker_id: "worker-a",
        error_code: "deepseek_failed",
        error_message: "generation failed",
      }),
    });
    expect(failed.status).toBe(200);
    const stored = await new IntakeRepository(testEnv.DB).getJob(job.jobId);
    expect(stored?.status).toBe("failed");
    expect(stored?.checkpoints.parsed).toEqual({ ok: true });
  });
});
