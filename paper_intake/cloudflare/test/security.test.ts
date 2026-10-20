import { env } from "cloudflare:workers";
import { SELF } from "cloudflare:test";
import { describe, expect, it } from "vitest";

import {
  assertOrigin,
  consumeLoginCode,
  createLoginCode,
  signSession,
  verifySession,
  type AppEnv,
} from "../src/security";
import worker from "../src/index";

const testEnv = env as AppEnv;

describe("owner security", () => {
  it("keeps owner login closed until Cloudflare Access is configured", async () => {
    const response = await worker.fetch(
      new Request("https://worker.test/v1/session/start?return_origin=http%3A%2F%2F127.0.0.1%3A4322", {
        headers: { "cf-access-authenticated-user-email": "owner@example.com" },
      }),
      { ...testEnv, BROWSER_AUTH_ENABLED: "false" },
    );
    expect(response.status).toBe(503);
    expect((await response.json<{ code: string }>()).code).toBe("owner_login_unavailable");
  });

  it("accepts only configured GitHub Pages and local origins", () => {
    expect(assertOrigin("https://enkidulove90-lang.github.io", testEnv)).toBe(
      "https://enkidulove90-lang.github.io",
    );
    expect(assertOrigin("http://127.0.0.1:4322", testEnv)).toBe(
      "http://127.0.0.1:4322",
    );
    expect(() => assertOrigin("https://attacker.example", testEnv)).toThrowError(
      expect.objectContaining({ code: "origin_denied" }),
    );
  });

  it("signs short-lived sessions and rejects tampering or expiry", async () => {
    const now = 1_800_000_000;
    const token = await signSession("owner@example.com", testEnv.SESSION_SIGNING_KEY, now);
    expect((await verifySession(token, testEnv.SESSION_SIGNING_KEY, now))?.sub).toBe(
      "owner@example.com",
    );
    expect(await verifySession(`${token}x`, testEnv.SESSION_SIGNING_KEY, now)).toBeNull();
    expect(await verifySession(token, testEnv.SESSION_SIGNING_KEY, now + 1801)).toBeNull();
  });

  it("consumes a login code exactly once", async () => {
    const code = await createLoginCode(testEnv, "owner@example.com", 1_800_000_000);
    expect(await consumeLoginCode(testEnv, code, 1_800_000_001)).toBe("owner@example.com");
    expect(await consumeLoginCode(testEnv, code, 1_800_000_002)).toBeNull();
  });

  it("exchanges an Access-authenticated popup code for one browser session", async () => {
    const origin = "http://127.0.0.1:4322";
    const started = await SELF.fetch(
      `https://worker.test/v1/session/start?return_origin=${encodeURIComponent(origin)}`,
      { headers: { "cf-access-authenticated-user-email": "owner@example.com" } },
    );
    expect(started.status).toBe(200);
    const html = await started.text();
    const match = html.match(/code:"([A-Za-z0-9_-]+)"/u);
    expect(match?.[1]).toBeTruthy();
    expect(html).not.toContain(testEnv.SESSION_SIGNING_KEY);

    const exchange = await SELF.fetch("https://worker.test/v1/session/exchange", {
      method: "POST",
      headers: { "content-type": "application/json", origin },
      body: JSON.stringify({ code: match?.[1] }),
    });
    expect(exchange.status).toBe(200);
    const payload = await exchange.json<{ code: string; token: string }>();
    expect(payload.code).toBe("session_created");
    expect((await verifySession(payload.token, testEnv.SESSION_SIGNING_KEY, Math.floor(Date.now() / 1000)))?.sub)
      .toBe("owner@example.com");

    const replay = await SELF.fetch("https://worker.test/v1/session/exchange", {
      method: "POST",
      headers: { "content-type": "application/json", origin },
      body: JSON.stringify({ code: match?.[1] }),
    });
    expect(replay.status).toBe(401);
    expect((await replay.json<{ code: string }>()).code).toBe("invalid_login_code");
  });
});
