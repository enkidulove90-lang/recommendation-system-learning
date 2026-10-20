export type AppEnv = Omit<Env, "ARTIFACT_STORAGE_ENABLED" | "BROWSER_AUTH_ENABLED"> & {
  ACCESS_IDENTITY_HEADER: string;
  ARTIFACT_STORAGE_ENABLED: string;
  ARTIFACTS?: R2Bucket;
  BROWSER_AUTH_ENABLED: string;
  GITHUB_TOKEN: string;
  OWNER_IDENTITIES: string;
  PUBLISH_CALLBACK_TOKEN: string;
  SESSION_SIGNING_KEY: string;
  WORKER_TOKEN: string;
};

export interface Owner {
  identity: string;
}

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    readonly retryable = false,
  ) {
    super(message);
  }
}

interface SessionClaims {
  sub: string;
  exp: number;
}

const encoder = new TextEncoder();

function bytesToBase64Url(bytes: Uint8Array): string {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/u, "");
}

function base64UrlToBytes(value: string): Uint8Array {
  const normalized = value.replaceAll("-", "+").replaceAll("_", "/");
  const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");
  const binary = atob(padded);
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

async function importHmacKey(secret: string): Promise<CryptoKey> {
  return crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"],
  );
}

async function sha256(value: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", encoder.encode(value));
  return bytesToBase64Url(new Uint8Array(digest));
}

export function assertOrigin(origin: string | null, env: AppEnv): string {
  const allowed = env.ALLOWED_ORIGINS.split(",").map((value) => value.trim());
  if (!origin || !allowed.includes(origin)) {
    throw new ApiError(403, "origin_denied", "当前来源不允许访问上传接口。", false);
  }
  return origin;
}

export async function signSession(identity: string, key: string, now: number): Promise<string> {
  const payload = bytesToBase64Url(
    encoder.encode(JSON.stringify({ sub: identity, exp: now + 1800 } satisfies SessionClaims)),
  );
  const signature = await crypto.subtle.sign("HMAC", await importHmacKey(key), encoder.encode(payload));
  return `${payload}.${bytesToBase64Url(new Uint8Array(signature))}`;
}

export async function verifySession(
  token: string,
  key: string,
  now: number,
): Promise<SessionClaims | null> {
  try {
    const parts = token.split(".");
    if (parts.length !== 2) return null;
    const [payload, signature] = parts;
    const valid = await crypto.subtle.verify(
      "HMAC",
      await importHmacKey(key),
      base64UrlToBytes(signature),
      encoder.encode(payload),
    );
    if (!valid) return null;
    const claims = JSON.parse(new TextDecoder().decode(base64UrlToBytes(payload))) as SessionClaims;
    if (!claims || typeof claims.sub !== "string" || typeof claims.exp !== "number") return null;
    if (claims.exp < now) return null;
    return claims;
  } catch {
    return null;
  }
}

export async function requireOwner(request: Request, env: AppEnv): Promise<Owner> {
  const token = request.headers.get("authorization")?.replace(/^Bearer\s+/iu, "");
  const claims = token
    ? await verifySession(token, env.SESSION_SIGNING_KEY, Math.floor(Date.now() / 1000))
    : null;
  const owners = env.OWNER_IDENTITIES.split(",").map((value) => value.trim().toLowerCase());
  if (!claims || !owners.includes(claims.sub.toLowerCase())) {
    throw new ApiError(401, "auth_required", "请使用已授权的 GitHub 账号登录。", false);
  }
  return { identity: claims.sub };
}

async function secureEqual(left: string, right: string): Promise<boolean> {
  const [leftDigest, rightDigest] = await Promise.all([
    crypto.subtle.digest("SHA-256", encoder.encode(left)),
    crypto.subtle.digest("SHA-256", encoder.encode(right)),
  ]);
  const leftBytes = new Uint8Array(leftDigest);
  const rightBytes = new Uint8Array(rightDigest);
  let difference = 0;
  for (let index = 0; index < leftBytes.length; index += 1) {
    difference |= leftBytes[index] ^ rightBytes[index];
  }
  return difference === 0;
}

export async function requireMachine(request: Request, env: AppEnv): Promise<void> {
  if (!env.WORKER_TOKEN) {
    throw new ApiError(503, "worker_not_configured", "Worker authentication is not configured.", false);
  }
  const provided = request.headers.get("authorization") || "";
  if (!(await secureEqual(provided, `Bearer ${env.WORKER_TOKEN}`))) {
    throw new ApiError(401, "worker_auth_required", "Worker authentication failed.", false);
  }
}

export async function requirePublishCallback(request: Request, env: AppEnv): Promise<void> {
  if (!env.PUBLISH_CALLBACK_TOKEN) {
    throw new ApiError(503, "callback_not_configured", "Publication callback is not configured.", false);
  }
  const provided = request.headers.get("authorization") || "";
  if (!(await secureEqual(provided, `Bearer ${env.PUBLISH_CALLBACK_TOKEN}`))) {
    throw new ApiError(401, "callback_auth_required", "Publication callback authentication failed.", false);
  }
}

export function requireAccessIdentity(request: Request, env: AppEnv): string {
  const header = env.ACCESS_IDENTITY_HEADER || "cf-access-authenticated-user-email";
  const identity = request.headers.get(header)?.trim();
  const owners = env.OWNER_IDENTITIES.split(",").map((value) => value.trim().toLowerCase());
  if (!identity || !owners.includes(identity.toLowerCase())) {
    throw new ApiError(403, "owner_denied", "当前 GitHub 身份没有上传权限。", false);
  }
  return identity;
}

export async function createLoginCode(
  env: AppEnv,
  identity: string,
  now: number,
): Promise<string> {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  const code = bytesToBase64Url(bytes);
  const expiresAt = new Date((now + 120) * 1000).toISOString();
  await env.DB.prepare(
    "INSERT INTO login_codes (code_hash, owner_identity, expires_at) VALUES (?, ?, ?)",
  )
    .bind(await sha256(code), identity, expiresAt)
    .run();
  return code;
}

export async function consumeLoginCode(
  env: AppEnv,
  code: string,
  now: number,
): Promise<string | null> {
  if (!code || code.length > 256) return null;
  const timestamp = new Date(now * 1000).toISOString();
  const row = await env.DB.prepare(
    `UPDATE login_codes SET consumed_at = ?
     WHERE code_hash = ? AND consumed_at IS NULL AND expires_at >= ?
     RETURNING owner_identity`,
  )
    .bind(timestamp, await sha256(code), timestamp)
    .first<{ owner_identity: string }>();
  return row?.owner_identity ?? null;
}
