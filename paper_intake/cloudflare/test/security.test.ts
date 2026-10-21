import { env } from "cloudflare:workers";
import { SELF } from "cloudflare:test";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  assertOrigin,
  consumeOAuthState,
  consumeLoginCode,
  createOAuthState,
  createLoginCode,
  requireMachine,
  requirePublishCallback,
  signSession,
  verifySession,
  type AppEnv,
} from "../src/security";
import worker from "../src/index";

const testEnv = env as AppEnv;

afterEach(() => vi.restoreAllMocks());

describe("owner security", () => {
  it("exposes an unauthenticated health endpoint", async () => {
    const response = await SELF.fetch("https://worker.test/health");
    expect(response.status).toBe(200);
    await expect(response.json()).resolves.toMatchObject({ status: "ok" });
  });

  it("refreshes a valid owner session without GitHub OAuth", async () => {
    const now = Math.floor(Date.now() / 1000);
    const token = await signSession("owner@example.com", testEnv.SESSION_SIGNING_KEY, now);
    const response = await SELF.fetch("https://worker.test/v1/session/refresh", {
      method: "POST",
      headers: { authorization: `Bearer ${token}`, origin: "http://127.0.0.1:4322" },
    });
    expect(response.status).toBe(200);
    const payload = await response.json<{ token: string }>();
    expect((await verifySession(payload.token, testEnv.SESSION_SIGNING_KEY, now))?.sub).toBe("owner@example.com");
  });

  it("fails closed when machine or callback secrets are not configured", async () => {
    const missingSecrets = {
      ...testEnv,
      WORKER_TOKEN: undefined,
      PUBLISH_CALLBACK_TOKEN: undefined,
    } as unknown as AppEnv;
    await expect(requireMachine(
      new Request("https://worker.test/v1/worker/jobs/claim", {
        headers: { authorization: "Bearer undefined" },
      }),
      missingSecrets,
    )).rejects.toMatchObject({ status: 503, code: "worker_not_configured" });
    await expect(requirePublishCallback(
      new Request("https://worker.test/v1/publications/callback", {
        headers: { authorization: "Bearer undefined" },
      }),
      missingSecrets,
    )).rejects.toMatchObject({ status: 503, code: "callback_not_configured" });
  });

  it("keeps owner login closed until browser OAuth is enabled", async () => {
    const response = await worker.fetch(
      new Request("https://worker.test/v1/session/start?return_origin=http%3A%2F%2F127.0.0.1%3A4322"),
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

  it("keeps owner sessions for a working day and rejects tampering or expiry", async () => {
    const now = 1_800_000_000;
    const token = await signSession("owner@example.com", testEnv.SESSION_SIGNING_KEY, now);
    expect((await verifySession(token, testEnv.SESSION_SIGNING_KEY, now))?.sub).toBe(
      "owner@example.com",
    );
    expect(await verifySession(`${token}x`, testEnv.SESSION_SIGNING_KEY, now)).toBeNull();
    expect((await verifySession(token, testEnv.SESSION_SIGNING_KEY, now + 8 * 60 * 60))?.sub).toBe(
      "owner@example.com",
    );
    expect(await verifySession(token, testEnv.SESSION_SIGNING_KEY, now + 12 * 60 * 60 + 1)).toBeNull();
  });

  it("consumes a login code exactly once", async () => {
    const code = await createLoginCode(testEnv, "owner@example.com", 1_800_000_000);
    expect(await consumeLoginCode(testEnv, code, 1_800_000_001)).toBe("owner@example.com");
    expect(await consumeLoginCode(testEnv, code, 1_800_000_002)).toBeNull();
  });

  it("consumes an OAuth state exactly once and restores its return origin", async () => {
    const origin = "http://127.0.0.1:4322";
    const state = await createOAuthState(testEnv, origin, 1_800_000_000);
    expect(await consumeOAuthState(testEnv, state, 1_800_000_001)).toBe(origin);
    expect(await consumeOAuthState(testEnv, state, 1_800_000_002)).toBeNull();
  });

  it("redirects to GitHub and accepts only the configured stable GitHub user id", async () => {
    const origin = "http://127.0.0.1:4322";
    const started = await SELF.fetch(
      `https://worker.test/v1/session/start?return_origin=${encodeURIComponent(origin)}`,
      { redirect: "manual" },
    );
    expect(started.status).toBe(302);
    const authorization = new URL(started.headers.get("location") || "");
    expect(authorization.origin + authorization.pathname).toBe("https://github.com/login/oauth/authorize");
    expect(authorization.searchParams.get("client_id")).toBe("test-github-client-id");
    expect(authorization.searchParams.get("scope")).toBeNull();
    expect(authorization.searchParams.get("redirect_uri")).toBe(
      "https://paper-intake.example/v1/session/callback",
    );

    const github = vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        text: async () => JSON.stringify({ access_token: "temporary-oauth-token" }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        text: async () => JSON.stringify({ id: 123456, login: "owner-login" }),
      } as Response);
    const callback = await SELF.fetch(
      `https://worker.test/v1/session/callback?code=temporary-code&state=${encodeURIComponent(authorization.searchParams.get("state") || "")}`,
    );
    const html = await callback.text();
    expect(github).toHaveBeenCalledTimes(2);
    expect(callback.status, html).toBe(200);
    const match = html.match(/code:"([A-Za-z0-9_-]+)"/u);
    expect(match?.[1]).toBeTruthy();

    const exchange = await SELF.fetch("https://worker.test/v1/session/exchange", {
      method: "POST",
      headers: { "content-type": "application/json", origin },
      body: JSON.stringify({ code: match?.[1] }),
    });
    const payload = await exchange.json<{ token: string }>();
    expect((await verifySession(
      payload.token,
      testEnv.SESSION_SIGNING_KEY,
      Math.floor(Date.now() / 1000),
    ))?.sub).toBe("github:123456");
  });

  it("rejects a valid GitHub login from any other user id", async () => {
    const origin = "http://127.0.0.1:4322";
    const started = await SELF.fetch(
      `https://worker.test/v1/session/start?return_origin=${encodeURIComponent(origin)}`,
      { redirect: "manual" },
    );
    const authorization = new URL(started.headers.get("location") || "");
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        text: async () => JSON.stringify({ access_token: "other-user-token" }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        text: async () => JSON.stringify({ id: 999999, login: "not-the-owner" }),
      } as Response);
    const callback = await SELF.fetch(
      `https://worker.test/v1/session/callback?code=temporary-code&state=${encodeURIComponent(authorization.searchParams.get("state") || "")}`,
    );
    expect(callback.status).toBe(403);
    expect((await callback.json<{ code: string }>()).code).toBe("owner_denied");
  });

  it("exchanges a popup code for one browser session", async () => {
    const origin = "http://127.0.0.1:4322";
    const code = await createLoginCode(
      testEnv,
      "owner@example.com",
      Math.floor(Date.now() / 1000),
    );

    const exchange = await SELF.fetch("https://worker.test/v1/session/exchange", {
      method: "POST",
      headers: { "content-type": "application/json", origin },
      body: JSON.stringify({ code }),
    });
    expect(exchange.status).toBe(200);
    const payload = await exchange.json<{ code: string; token: string }>();
    expect(payload.code).toBe("session_created");
    expect((await verifySession(payload.token, testEnv.SESSION_SIGNING_KEY, Math.floor(Date.now() / 1000)))?.sub)
      .toBe("owner@example.com");

    const replay = await SELF.fetch("https://worker.test/v1/session/exchange", {
      method: "POST",
      headers: { "content-type": "application/json", origin },
      body: JSON.stringify({ code }),
    });
    expect(replay.status).toBe(401);
    expect((await replay.json<{ code: string }>()).code).toBe("invalid_login_code");
  });
});
