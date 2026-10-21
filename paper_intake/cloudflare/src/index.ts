import { IntakeRepository } from "./repository";
import type { JobRecord } from "./types";
import {
  ApiError,
  assertOrigin,
  consumeOAuthState,
  consumeLoginCode,
  createOAuthState,
  createLoginCode,
  requireMachine,
  requireOwner,
  requirePublishCallback,
  signSession,
  type AppEnv,
  type Owner,
} from "./security";

interface EnvelopeInput {
  paperId?: string;
  jobId?: string;
  status?: string;
  code: string;
  message: string;
  retryable?: boolean;
}

interface NormalizedUrl {
  canonicalUrl: string;
  doi?: string;
  arxivId?: string;
}

const MAX_PDF_BYTES = 50 * 1024 * 1024;

function artifactStorage(env: AppEnv): R2Bucket {
  if (env.ARTIFACT_STORAGE_ENABLED !== "true" || !env.ARTIFACTS) {
    throw new ApiError(
      503,
      "pdf_upload_unavailable",
      "PDF 上传暂未启用，请改用公开论文链接提交。",
      false,
    );
  }
  return env.ARTIFACTS;
}

function corsHeaders(origin: string, env: AppEnv): Headers {
  const allowed = assertOrigin(origin, env);
  return new Headers({
    "access-control-allow-origin": allowed,
    "access-control-allow-methods": "GET,POST,OPTIONS",
    "access-control-allow-headers": "authorization,content-type,idempotency-key",
    "access-control-max-age": "600",
    vary: "Origin",
  });
}

function envelope(
  httpStatus: number,
  requestId: string,
  input: EnvelopeInput,
  origin?: string,
  env?: AppEnv,
): Response {
  const headers = origin && env ? corsHeaders(origin, env) : new Headers();
  headers.set("content-type", "application/json; charset=utf-8");
  headers.set("cache-control", "no-store");
  return new Response(
    JSON.stringify({
      ok: httpStatus >= 200 && httpStatus < 300,
      request_id: requestId,
      paper_id: input.paperId ?? null,
      job_id: input.jobId ?? null,
      status: input.status ?? null,
      code: input.code,
      message: input.message,
      retryable: input.retryable ?? false,
    }),
    { status: httpStatus, headers },
  );
}

function publicJob(job: JobRecord): Record<string, unknown> {
  const checkpointTitle = job.checkpoints.title;
  return {
    job_id: job.jobId,
    paper_id: job.paperId,
    title: typeof checkpointTitle === "string" ? checkpointTitle : null,
    input_type: job.inputType,
    stage: job.stage,
    status: job.status,
    attempt: job.attempt,
    error_code: job.errorCode,
    error_message: job.errorMessage,
    retryable: job.status === "failed",
    created_at: job.createdAt,
    updated_at: job.updatedAt,
  };
}

function ownerJson(
  status: number,
  requestId: string,
  origin: string,
  env: AppEnv,
  payload: Record<string, unknown>,
): Response {
  const headers = corsHeaders(origin, env);
  headers.set("content-type", "application/json; charset=utf-8");
  headers.set("cache-control", "no-store");
  return new Response(JSON.stringify({ ok: status >= 200 && status < 300, request_id: requestId, ...payload }), {
    status,
    headers,
  });
}

function isPrivateHostname(hostname: string): boolean {
  const host = hostname.replace(/^\[|\]$/gu, "").toLowerCase();
  if (host === "localhost" || host.endsWith(".localhost") || host.endsWith(".local")) return true;
  if (host === "::1" || host.startsWith("fc") || host.startsWith("fd") || host.startsWith("fe80:")) {
    return true;
  }
  const octets = host.split(".").map(Number);
  if (octets.length !== 4 || octets.some((value) => !Number.isInteger(value) || value < 0 || value > 255)) {
    return false;
  }
  return (
    octets[0] === 0 ||
    octets[0] === 10 ||
    octets[0] === 127 ||
    (octets[0] === 169 && octets[1] === 254) ||
    (octets[0] === 172 && octets[1] >= 16 && octets[1] <= 31) ||
    (octets[0] === 192 && octets[1] === 168)
  );
}

function normalizePaperUrl(value: unknown): NormalizedUrl {
  if (typeof value !== "string" || value.length > 4096) {
    throw new ApiError(400, "invalid_url", "请提供有效的论文 HTTPS 链接。", false);
  }
  let parsed: URL;
  try {
    parsed = new URL(value.trim());
  } catch {
    throw new ApiError(400, "invalid_url", "请提供有效的论文 HTTPS 链接。", false);
  }
  if (parsed.protocol !== "https:" || parsed.username || parsed.password || isPrivateHostname(parsed.hostname)) {
    throw new ApiError(400, "url_not_allowed", "仅允许公开网络上的 HTTPS 论文链接。", false);
  }

  const hostname = parsed.hostname.toLowerCase();
  if (hostname === "doi.org" || hostname === "dx.doi.org") {
    const doi = decodeURIComponent(parsed.pathname).replace(/^\/+/, "").trim().toLowerCase();
    if (!/^10\.\d{4,9}\/.+/u.test(doi)) {
      throw new ApiError(400, "invalid_doi", "DOI 链接格式无效。", false);
    }
    return { canonicalUrl: `https://doi.org/${doi}`, doi };
  }

  if (hostname === "arxiv.org" || hostname === "www.arxiv.org") {
    const match = parsed.pathname.match(/^\/(?:abs|pdf)\/(\d{4}\.\d{4,5})(?:v\d+)?(?:\.pdf)?\/?$/u);
    if (!match) throw new ApiError(400, "invalid_arxiv", "arXiv 链接格式无效。", false);
    return { canonicalUrl: `https://arxiv.org/abs/${match[1]}`, arxivId: match[1] };
  }

  parsed.hash = "";
  for (const key of [...parsed.searchParams.keys()]) {
    if (key.toLowerCase().startsWith("utm_")) parsed.searchParams.delete(key);
  }
  parsed.searchParams.sort();
  return { canonicalUrl: parsed.toString() };
}

async function digestHex(bytes: Uint8Array): Promise<string> {
  const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", bytes));
  return [...digest].map((value) => value.toString(16).padStart(2, "0")).join("");
}

async function readJsonObject(request: Request): Promise<Record<string, unknown>> {
  try {
    const value: unknown = await request.json();
    if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("invalid");
    return value as Record<string, unknown>;
  } catch {
    throw new ApiError(400, "invalid_json", "请求内容必须是 JSON 对象。", false);
  }
}

async function existingOrNewJob(
  repository: IntakeRepository,
  paperId: string,
  owner: Owner,
  inputType: "url" | "pdf",
  inputRef: string,
  reused: boolean,
): Promise<{ jobId: string; duplicate: boolean }> {
  if (reused) {
    const existing = await repository.getLatestJobForPaper(paperId);
    if (existing) return { jobId: existing.jobId, duplicate: true };
  }
  const created = await repository.createJob({
    paperId,
    ownerIdentity: owner.identity,
    inputType,
    inputRef,
  });
  return { jobId: created.jobId, duplicate: false };
}

async function ingestUrl(request: Request, env: AppEnv, owner: Owner, requestId: string): Promise<Response> {
  const body = await readJsonObject(request);
  const normalized = normalizePaperUrl(body.url);
  const repository = new IntakeRepository(env.DB);
  const paper = await repository.createOrReusePaper({
    canonicalUrl: normalized.canonicalUrl,
    doi: normalized.doi,
    arxivId: normalized.arxivId,
  });
  const job = await existingOrNewJob(
    repository,
    paper.paperId,
    owner,
    "url",
    normalized.canonicalUrl,
    paper.reused,
  );
  return envelope(job.duplicate ? 200 : 202, requestId, {
    paperId: paper.paperId,
    jobId: job.jobId,
    status: job.duplicate ? "existing" : "queued",
    code: job.duplicate ? "duplicate_paper" : "intake_accepted",
    message: job.duplicate ? "该论文已在处理记录中。" : "论文链接已进入处理队列。",
  });
}

async function ingestPdf(request: Request, env: AppEnv, owner: Owner, requestId: string): Promise<Response> {
  const artifacts = artifactStorage(env);
  const declaredLength = Number(request.headers.get("content-length") || 0);
  if (declaredLength > MAX_PDF_BYTES) {
    throw new ApiError(413, "pdf_too_large", "PDF 必须小于 50 MB。", false);
  }
  const bytes = new Uint8Array(await request.arrayBuffer());
  if (bytes.byteLength === 0 || bytes.byteLength > MAX_PDF_BYTES) {
    throw new ApiError(413, "pdf_too_large", "PDF 必须小于 50 MB。", false);
  }
  if (new TextDecoder().decode(bytes.slice(0, 5)) !== "%PDF-") {
    throw new ApiError(415, "invalid_pdf", "上传内容不是有效 PDF。", false);
  }
  const sha256 = await digestHex(bytes);
  const repository = new IntakeRepository(env.DB);
  const paper = await repository.createOrReusePaper({ pdfSha256: sha256 });
  const existing = paper.reused ? await repository.getLatestJobForPaper(paper.paperId) : null;
  if (existing) {
    return envelope(200, requestId, {
      paperId: paper.paperId,
      jobId: existing.jobId,
      status: "existing",
      code: "duplicate_paper",
      message: "该 PDF 已在处理记录中。",
    });
  }

  const inputRef = `originals/${paper.paperId}/${sha256}.pdf`;
  await artifacts.put(inputRef, bytes, {
    httpMetadata: { contentType: "application/pdf" },
    customMetadata: { sha256 },
  });
  try {
    const job = await existingOrNewJob(repository, paper.paperId, owner, "pdf", inputRef, false);
    return envelope(202, requestId, {
      paperId: paper.paperId,
      jobId: job.jobId,
      status: "queued",
      code: "intake_accepted",
      message: "PDF 已安全保存并进入处理队列。",
    });
  } catch (error) {
    await artifacts.delete(inputRef);
    throw error;
  }
}

function htmlLoginResponse(code: string, targetOrigin: string): Response {
  const safeCode = JSON.stringify(code).replaceAll("<", "\\u003c");
  const safeOrigin = JSON.stringify(targetOrigin).replaceAll("<", "\\u003c");
  const html = `<!doctype html><meta charset="utf-8"><title>登录完成</title><script>
window.opener?.postMessage({type:"paper-intake-login",code:${safeCode}},${safeOrigin});window.close();
</script><p>身份验证完成，可以关闭此窗口。</p>`;
  return new Response(html, {
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
      "content-security-policy": "default-src 'none'; script-src 'unsafe-inline'",
      "referrer-policy": "no-referrer",
    },
  });
}

function githubCallbackUrl(env: AppEnv): string {
  let base: URL;
  try {
    base = new URL(env.PUBLIC_BASE_URL);
  } catch {
    throw new ApiError(503, "owner_login_unavailable", "GitHub 登录尚未完成配置。", false);
  }
  if (base.protocol !== "https:" || base.username || base.password || base.pathname !== "/") {
    throw new ApiError(503, "owner_login_unavailable", "GitHub 登录尚未完成配置。", false);
  }
  return new URL("/v1/session/callback", base).toString();
}

function requireGitHubOAuth(env: AppEnv): void {
  if (!env.GITHUB_OAUTH_CLIENT_ID || !env.GITHUB_OAUTH_CLIENT_SECRET || !env.GITHUB_OWNER_IDS) {
    throw new ApiError(503, "owner_login_unavailable", "GitHub 登录尚未完成配置。", false);
  }
}

async function githubIdentity(env: AppEnv, code: string): Promise<string> {
  const tokenResponse = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: {
      accept: "application/json",
      "content-type": "application/x-www-form-urlencoded",
      "user-agent": "enkidu-paper-intake-worker",
    },
    body: new URLSearchParams({
      client_id: env.GITHUB_OAUTH_CLIENT_ID,
      client_secret: env.GITHUB_OAUTH_CLIENT_SECRET,
      code,
      redirect_uri: githubCallbackUrl(env),
    }),
  });
  let tokenPayload: Record<string, unknown> = {};
  try {
    tokenPayload = JSON.parse(await tokenResponse.text()) as Record<string, unknown>;
  } catch {
    tokenPayload = {};
  }
  const accessToken = typeof tokenPayload.access_token === "string" ? tokenPayload.access_token : "";
  if (!tokenResponse.ok || !accessToken) {
    throw new ApiError(401, "github_oauth_failed", "GitHub 身份验证失败，请重新登录。", false);
  }

  const userResponse = await fetch("https://api.github.com/user", {
    headers: {
      accept: "application/vnd.github+json",
      authorization: `Bearer ${accessToken}`,
      "user-agent": "enkidu-paper-intake-worker",
      "x-github-api-version": "2022-11-28",
    },
  });
  let user: Record<string, unknown> = {};
  try {
    user = JSON.parse(await userResponse.text()) as Record<string, unknown>;
  } catch {
    user = {};
  }
  const id = typeof user.id === "number" && Number.isSafeInteger(user.id) ? String(user.id) : "";
  const allowedIds = env.GITHUB_OWNER_IDS.split(",").map((value) => value.trim());
  if (!userResponse.ok || !id || !allowedIds.includes(id)) {
    throw new ApiError(403, "owner_denied", "当前 GitHub 账号没有投稿权限。", false);
  }
  return `github:${id}`;
}

function machineResponse(
  status: number,
  requestId: string,
  payload: Record<string, unknown>,
): Response {
  return new Response(JSON.stringify({ ok: status >= 200 && status < 300, request_id: requestId, ...payload }), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

function requiredString(value: unknown, code: string, message: string): string {
  if (typeof value !== "string" || !value.trim()) throw new ApiError(400, code, message, false);
  return value.trim();
}

function leaseConflict(error: unknown): never {
  if (error instanceof Error && error.message === "lease_lost") {
    throw new ApiError(409, "lease_lost", "任务租约已经失效，请停止当前处理。", true);
  }
  throw error;
}

const artifactRules: Record<string, { maxBytes: number; contentTypes: string[] }> = {
  parsed_markdown: { maxBytes: 20 * 1024 * 1024, contentTypes: ["text/markdown", "text/plain"] },
  generated_article: { maxBytes: 10 * 1024 * 1024, contentTypes: ["text/markdown", "text/plain"] },
  article_json: { maxBytes: 10 * 1024 * 1024, contentTypes: ["application/json"] },
  metadata: { maxBytes: 2 * 1024 * 1024, contentTypes: ["application/json"] },
  figure: { maxBytes: 20 * 1024 * 1024, contentTypes: ["image/jpeg", "image/png", "image/webp"] },
};

async function dispatchPublication(
  env: AppEnv,
  jobId: string,
  paperId: string,
  notionPageId: string,
  slug: string,
): Promise<void> {
  const repository = new IntakeRepository(env.DB);
  if (await repository.hasJobEvent(jobId, "publication.dispatched")) return;
  const response = await fetch(`https://api.github.com/repos/${env.GITHUB_REPOSITORY}/dispatches`, {
    method: "POST",
    headers: {
      authorization: `Bearer ${env.GITHUB_TOKEN}`,
      accept: "application/vnd.github+json",
      "content-type": "application/json",
      "user-agent": "enkidu-paper-intake-worker",
      "x-github-api-version": "2022-11-28",
    },
    body: JSON.stringify({
      event_type: "notion-updated",
      client_payload: {
        job_id: jobId,
        paper_id: paperId,
        notion_page_id: notionPageId,
        slug,
      },
    }),
  });
  if (!response.ok) {
    await repository.failPublicationDispatch(jobId, response.status);
    throw new ApiError(502, "github_dispatch_failed", "GitHub Pages 构建触发失败。", true);
  }
  await repository.recordJobEvent(jobId, "publication.dispatched", { status: response.status });
}

async function routeWorker(request: Request, env: AppEnv, requestId: string, url: URL): Promise<Response> {
  await requireMachine(request, env);
  const repository = new IntakeRepository(env.DB);

  if (url.pathname === "/v1/worker/intake/url" && request.method === "POST") {
    const githubOwnerId = env.GITHUB_OWNER_IDS.split(",").map((value) => value.trim()).find(Boolean);
    const ownerIdentity = githubOwnerId ? `github:${githubOwnerId}` : "machine:operator";
    return ingestUrl(request, env, { identity: ownerIdentity }, requestId);
  }

  const operationMatch = url.pathname.match(/^\/v1\/worker\/operations\/([^/]+)$/u);
  if (operationMatch && request.method === "GET") {
    const operation = await repository.getRetryOperation(operationMatch[1]);
    if (!operation) throw new ApiError(404, "operation_not_found", "幂等操作不存在。", false);
    const job = await repository.getJob(operation.jobId);
    const payload = Object.keys(operation.response).length > 0
      ? operation.response
      : {
          job_id: operation.jobId,
          status: job?.status ?? "unknown",
          code: operation.state === "completed" ? "retry_accepted" : "operation_pending",
        };
    return machineResponse(operation.state === "completed" ? 200 : 202, requestId, payload);
  }

  const operatorRetryMatch = url.pathname.match(/^\/v1\/worker\/jobs\/([^/]+)\/retry$/u);
  if (operatorRetryMatch && request.method === "POST") {
    const idempotencyKey = request.headers.get("idempotency-key")?.trim() ?? "";
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/iu.test(idempotencyKey)) {
      throw new ApiError(400, "invalid_idempotency_key", "必须提供有效的 Idempotency-Key。", false);
    }
    const current = await repository.getJob(operatorRetryMatch[1]);
    if (!current) throw new ApiError(404, "job_not_found", "任务不存在。", false);
    try {
      const { job, replayed } = await repository.retryIdempotent(
        current.jobId,
        current.ownerIdentity,
        idempotencyKey,
      );
      const response = machineResponse(202, requestId, {
        job_id: job.jobId,
        paper_id: job.paperId,
        status: job.status,
        code: "retry_accepted",
      });
      if (replayed) response.headers.set("idempotency-replayed", "true");
      return response;
    } catch (error) {
      if (error instanceof Error && error.message === "idempotency_conflict") {
        throw new ApiError(409, "idempotency_conflict", "该 Idempotency-Key 已用于其他任务。", false);
      }
      if (error instanceof Error && error.message === "job_not_retryable") {
        throw new ApiError(409, "job_not_retryable", "任务当前不可重试。", false);
      }
      throw error;
    }
  }

  if (url.pathname === "/v1/worker/health" && request.method === "GET") {
    return machineResponse(200, requestId, {
      status: "ok",
      code: "worker_authenticated",
      artifact_storage_enabled: env.ARTIFACT_STORAGE_ENABLED === "true" && Boolean(env.ARTIFACTS),
    });
  }

  if (
    (url.pathname === "/v1/worker/claim" || url.pathname === "/v1/worker/jobs/claim") &&
    request.method === "POST"
  ) {
    const body = await readJsonObject(request);
    const workerId = requiredString(body.worker_id, "invalid_worker_id", "必须提供 Worker ID。");
    const requestedLease = typeof body.lease_seconds === "number" ? body.lease_seconds : 600;
    const leaseSeconds = Math.max(60, Math.min(900, Math.floor(requestedLease)));
    const job = await repository.claim(workerId, leaseSeconds);
    if (!job) return new Response(null, { status: 204, headers: { "cache-control": "no-store" } });
    const inputUrl = job.inputType === "pdf"
      ? `${url.origin}/v1/worker/jobs/${job.jobId}/input?worker_id=${encodeURIComponent(workerId)}`
      : null;
    const claimPayload = {
      status: "processing",
      job_id: job.jobId,
      paper_id: job.paperId,
      input_type: job.inputType,
      input_ref: job.inputType === "url" ? job.inputRef : inputUrl,
      source_url: job.inputType === "url" ? job.inputRef : null,
      input_url: inputUrl,
      lease_owner: job.leaseOwner,
      lease_until: job.leaseUntil,
      attempt: job.attempt,
      stage: job.stage,
      checkpoints: job.checkpoints,
      artifact_storage_enabled: env.ARTIFACT_STORAGE_ENABLED === "true" && Boolean(env.ARTIFACTS),
    };
    return machineResponse(200, requestId, { ...claimPayload, job: claimPayload });
  }

  const inputMatch = url.pathname.match(/^\/v1\/worker\/jobs\/([^/]+)\/input$/u);
  if (inputMatch && request.method === "GET") {
    const workerId = requiredString(url.searchParams.get("worker_id"), "invalid_worker_id", "必须提供 Worker ID。");
    const job = await repository.getActiveLease(inputMatch[1], workerId);
    if (!job) throw new ApiError(409, "lease_lost", "任务租约已经失效。", true);
    if (job.inputType !== "pdf") throw new ApiError(409, "input_not_pdf", "该任务没有托管 PDF。", false);
    const object = await artifactStorage(env).get(job.inputRef);
    if (!object) throw new ApiError(404, "input_missing", "原始 PDF 不存在。", true);
    const headers = new Headers({
      "content-type": "application/pdf",
      "cache-control": "no-store",
    });
    object.writeHttpMetadata(headers);
    return new Response(object.body, { headers });
  }

  const heartbeatMatch = url.pathname.match(/^\/v1\/worker\/jobs\/([^/]+)\/heartbeat$/u);
  if (heartbeatMatch && request.method === "POST") {
    const body = await readJsonObject(request);
    const workerId = requiredString(body.worker_id, "invalid_worker_id", "必须提供 Worker ID。");
    const requestedLease = typeof body.lease_seconds === "number" ? body.lease_seconds : 600;
    const stage = typeof body.stage === "string" ? body.stage.slice(0, 100) : "";
    const renewed = await repository.heartbeat(
      heartbeatMatch[1],
      workerId,
      Math.max(60, Math.min(900, Math.floor(requestedLease))),
      stage,
    );
    if (!renewed) throw new ApiError(409, "lease_lost", "任务租约已经失效，请停止当前处理。", true);
    return machineResponse(200, requestId, { job_id: heartbeatMatch[1], status: "processing" });
  }

  const checkpointMatch = url.pathname.match(/^\/v1\/worker\/jobs\/([^/]+)\/checkpoint$/u);
  if (checkpointMatch && request.method === "POST") {
    const body = await readJsonObject(request);
    const workerId = requiredString(body.worker_id, "invalid_worker_id", "必须提供 Worker ID。");
    const stage = requiredString(body.stage, "invalid_stage", "必须提供处理阶段。");
    try {
      const job = await repository.checkpoint(checkpointMatch[1], workerId, stage, body.output ?? {});
      return machineResponse(200, requestId, { job_id: job.jobId, stage: job.stage, status: job.status });
    } catch (error) {
      return leaseConflict(error);
    }
  }

  const artifactMatch = url.pathname.match(/^\/v1\/worker\/jobs\/([^/]+)\/artifacts\/([^/]+)$/u);
  if (artifactMatch && request.method === "GET") {
    const [jobId, artifactId] = [artifactMatch[1], decodeURIComponent(artifactMatch[2])];
    const workerId = requiredString(url.searchParams.get("worker_id"), "invalid_worker_id", "必须提供 Worker ID。");
    if (!(await repository.getActiveLease(jobId, workerId))) {
      throw new ApiError(409, "lease_lost", "任务租约已经失效。", true);
    }
    const artifact = await repository.getArtifactForJob(jobId, artifactId);
    if (!artifact) throw new ApiError(404, "artifact_missing", "处理产物不存在。", true);
    const object = await artifactStorage(env).get(artifact.r2Key);
    if (!object) throw new ApiError(404, "artifact_missing", "处理产物不存在。", true);
    return new Response(object.body, {
      headers: {
        "content-type": artifact.contentType,
        "content-length": String(artifact.sizeBytes),
        "x-content-sha256": artifact.sha256,
        "cache-control": "no-store",
      },
    });
  }
  if (artifactMatch && request.method === "PUT") {
    const [jobId, kind] = [artifactMatch[1], decodeURIComponent(artifactMatch[2])];
    const workerId = requiredString(url.searchParams.get("worker_id"), "invalid_worker_id", "必须提供 Worker ID。");
    const job = await repository.getActiveLease(jobId, workerId);
    if (!job) throw new ApiError(409, "lease_lost", "任务租约已经失效。", true);
    const rule = artifactRules[kind];
    if (!rule) throw new ApiError(400, "artifact_kind_denied", "不支持该产物类型。", false);
    const contentType = (request.headers.get("content-type") || "").split(";", 1)[0].toLowerCase();
    if (!rule.contentTypes.includes(contentType)) {
      throw new ApiError(415, "artifact_type_denied", "产物 MIME 类型不受支持。", false);
    }
    const declaredHash = (request.headers.get("x-content-sha256") || "").toLowerCase();
    if (!/^[a-f0-9]{64}$/u.test(declaredHash)) {
      throw new ApiError(422, "artifact_hash_invalid", "必须提供有效的 SHA-256。", false);
    }
    const bytes = new Uint8Array(await request.arrayBuffer());
    if (bytes.byteLength === 0 || bytes.byteLength > rule.maxBytes) {
      throw new ApiError(413, "artifact_too_large", "产物为空或超过大小限制。", false);
    }
    const actualHash = await digestHex(bytes);
    if (actualHash !== declaredHash) {
      throw new ApiError(422, "artifact_hash_mismatch", "产物 SHA-256 校验失败。", false);
    }
    const requestedName = request.headers.get("x-artifact-name") || `${kind}.bin`;
    const safeName = requestedName.replace(/[^A-Za-z0-9._-]+/gu, "-").slice(0, 120) || `${kind}.bin`;
    const r2Key = `derived/${job.paperId}/${jobId}/${kind}/${crypto.randomUUID()}-${safeName}`;
    const artifacts = artifactStorage(env);
    await artifacts.put(r2Key, bytes, {
      httpMetadata: { contentType },
      customMetadata: { sha256: actualHash, kind },
    });
    try {
      const artifact = await repository.recordArtifact(jobId, workerId, {
        kind,
        r2Key,
        sha256: actualHash,
        sizeBytes: bytes.byteLength,
        contentType,
      });
      return machineResponse(201, requestId, {
        artifact_id: artifact.artifactId,
        job_id: jobId,
        kind,
        sha256: actualHash,
        size_bytes: bytes.byteLength,
      });
    } catch (error) {
      await artifacts.delete(r2Key);
      return leaseConflict(error);
    }
  }

  const completionMatch = url.pathname.match(/^\/v1\/worker\/jobs\/([^/]+)\/complete$/u);
  if (completionMatch && request.method === "POST") {
    const body = await readJsonObject(request);
    const workerId = requiredString(body.worker_id, "invalid_worker_id", "必须提供 Worker ID。");
    const publication = body.publication;
    if (!publication || typeof publication !== "object" || Array.isArray(publication)) {
      throw new ApiError(400, "invalid_publication", "必须提供发布信息。", false);
    }
    const values = publication as Record<string, unknown>;
    try {
      const notionPageId = requiredString(
        values.notion_page_id,
        "invalid_notion_page",
        "缺少 Notion Page ID。",
      );
      const slug = requiredString(values.slug, "invalid_slug", "缺少文章 slug。");
      const job = await repository.complete(completionMatch[1], workerId, {
        notionPageId,
        slug,
        siteUrl: requiredString(values.site_url, "invalid_site_url", "缺少文章地址。"),
      });
      await dispatchPublication(env, job.jobId, job.paperId, notionPageId, slug);
      return machineResponse(200, requestId, {
        job_id: job.jobId,
        paper_id: job.paperId,
        status: "publishing",
      });
    } catch (error) {
      return leaseConflict(error);
    }
  }

  const failureMatch = url.pathname.match(/^\/v1\/worker\/jobs\/([^/]+)\/fail$/u);
  if (failureMatch && request.method === "POST") {
    const body = await readJsonObject(request);
    const workerId = requiredString(body.worker_id, "invalid_worker_id", "必须提供 Worker ID。");
    const errorCode = requiredString(body.error_code, "invalid_error_code", "必须提供错误代码。");
    const errorMessage = typeof body.error_message === "string"
      ? body.error_message.slice(0, 1000)
      : "Processing failed.";
    try {
      const job = await repository.fail(failureMatch[1], workerId, errorCode.slice(0, 100), errorMessage);
      return machineResponse(200, requestId, {
        job_id: job.jobId,
        paper_id: job.paperId,
        status: job.status,
        code: job.errorCode,
      });
    } catch (error) {
      return leaseConflict(error);
    }
  }

  throw new ApiError(404, "not_found", "Worker 接口不存在。", false);
}

async function routePublicationCallback(
  request: Request,
  env: AppEnv,
  requestId: string,
): Promise<Response> {
  await requirePublishCallback(request, env);
  if (request.method !== "POST") throw new ApiError(405, "method_not_allowed", "请求方法不允许。", false);
  const body = await readJsonObject(request);
  const jobId = requiredString(body.job_id, "invalid_job_id", "必须提供 Job ID。");
  const success = body.ok === true;
  const job = await new IntakeRepository(env.DB).finishPublication(
    jobId,
    success,
    typeof body.git_commit === "string" ? body.git_commit : "",
  );
  return machineResponse(200, requestId, {
    job_id: job.jobId,
    paper_id: job.paperId,
    status: job.status,
  });
}

async function route(request: Request, env: AppEnv, requestId: string): Promise<Response> {
  const url = new URL(request.url);
  if (url.pathname === "/health" && request.method === "GET") {
    return new Response(JSON.stringify({ status: "ok", service: "paper-intake-gateway" }), {
      status: 200,
      headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
    });
  }
  if (url.pathname.startsWith("/v1/worker/")) {
    return routeWorker(request, env, requestId, url);
  }
  if (url.pathname === "/v1/publications/callback") {
    return routePublicationCallback(request, env, requestId);
  }
  if (url.pathname === "/v1/session/start" && request.method === "GET") {
    if (env.BROWSER_AUTH_ENABLED !== "true") {
      throw new ApiError(
        503,
        "owner_login_unavailable",
        "站点所有者登录尚未启用。",
        false,
      );
    }
    requireGitHubOAuth(env);
    const targetOrigin = assertOrigin(url.searchParams.get("return_origin"), env);
    const state = await createOAuthState(env, targetOrigin, Math.floor(Date.now() / 1000));
    const authorization = new URL("https://github.com/login/oauth/authorize");
    authorization.searchParams.set("client_id", env.GITHUB_OAUTH_CLIENT_ID);
    authorization.searchParams.set("redirect_uri", githubCallbackUrl(env));
    authorization.searchParams.set("state", state);
    return Response.redirect(authorization.toString(), 302);
  }
  if (url.pathname === "/v1/session/callback" && request.method === "GET") {
    requireGitHubOAuth(env);
    if (url.searchParams.get("error")) {
      throw new ApiError(401, "github_oauth_cancelled", "GitHub 登录已取消。", false);
    }
    const state = url.searchParams.get("state") || "";
    const targetOrigin = await consumeOAuthState(env, state, Math.floor(Date.now() / 1000));
    if (!targetOrigin) {
      throw new ApiError(401, "invalid_oauth_state", "登录请求无效或已过期，请重新登录。", false);
    }
    const code = url.searchParams.get("code") || "";
    if (!code || code.length > 512) {
      throw new ApiError(401, "github_oauth_failed", "GitHub 身份验证失败，请重新登录。", false);
    }
    const identity = await githubIdentity(env, code);
    return htmlLoginResponse(
      await createLoginCode(env, identity, Math.floor(Date.now() / 1000)),
      targetOrigin,
    );
  }

  const origin = assertOrigin(request.headers.get("origin"), env);
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders(origin, env) });
  }

  if (url.pathname === "/v1/session/exchange" && request.method === "POST") {
    const body = await readJsonObject(request);
    const identity = await consumeLoginCode(
      env,
      typeof body.code === "string" ? body.code : "",
      Math.floor(Date.now() / 1000),
    );
    if (!identity) throw new ApiError(401, "invalid_login_code", "登录凭据无效或已过期。", false);
    const token = await signSession(identity, env.SESSION_SIGNING_KEY, Math.floor(Date.now() / 1000));
    const response = envelope(200, requestId, {
      status: "authenticated",
      code: "session_created",
      message: "GitHub 身份验证成功。",
    }, origin, env);
    const payload = (await response.json()) as Record<string, unknown>;
    payload.token = token;
    return new Response(JSON.stringify(payload), { status: 200, headers: response.headers });
  }

  const owner = await requireOwner(request, env);
  if (url.pathname === "/v1/session/refresh" && request.method === "POST") {
    const token = await signSession(owner.identity, env.SESSION_SIGNING_KEY, Math.floor(Date.now() / 1000));
    return ownerJson(200, requestId, origin, env, { token, status: "authenticated" });
  }
  let response: Response;
  if (url.pathname === "/v1/intake/url" && request.method === "POST") {
    response = await ingestUrl(request, env, owner, requestId);
  } else if (url.pathname === "/v1/intake/pdf" && request.method === "POST") {
    response = await ingestPdf(request, env, owner, requestId);
  } else if (url.pathname === "/v1/jobs" && request.method === "GET") {
    const jobs = await new IntakeRepository(env.DB).listOwnerJobs(owner.identity);
    return ownerJson(200, requestId, origin, env, { jobs: jobs.map(publicJob) });
  } else if (request.method === "GET" && /^\/v1\/jobs\/[^/]+\/log$/u.test(url.pathname)) {
    const jobId = url.pathname.split("/")[3];
    const repository = new IntakeRepository(env.DB);
    const job = await repository.getOwnerJob(jobId, owner.identity);
    if (!job) throw new ApiError(404, "job_not_found", "任务不存在。", false);
    const events = await repository.listJobEvents(jobId);
    return ownerJson(200, requestId, origin, env, { job: publicJob(job), events });
  } else if (request.method === "POST" && /^\/v1\/jobs\/[^/]+\/retry$/u.test(url.pathname)) {
    const jobId = url.pathname.split("/")[3];
    const idempotencyKey = request.headers.get("idempotency-key")?.trim() ?? "";
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/iu.test(idempotencyKey)) {
      throw new ApiError(400, "invalid_idempotency_key", "必须提供有效的 Idempotency-Key。", false);
    }
    try {
      const { job, replayed } = await new IntakeRepository(env.DB).retryIdempotent(
        jobId,
        owner.identity,
        idempotencyKey,
      );
      response = envelope(202, requestId, {
        paperId: job.paperId,
        jobId: job.jobId,
        status: job.status,
        code: "retry_accepted",
        message: "任务已重新进入处理队列。",
      });
      if (replayed) response.headers.set("idempotency-replayed", "true");
    } catch (error) {
      if (error instanceof Error && error.message === "idempotency_conflict") {
        throw new ApiError(409, "idempotency_conflict", "该 Idempotency-Key 已用于其他任务。", false);
      }
      if (error instanceof Error && error.message === "job_not_retryable") {
        throw new ApiError(409, "job_not_retryable", "任务不存在、并非失败状态或不属于当前用户。", false);
      }
      throw error;
    }
  } else {
    throw new ApiError(404, "not_found", "接口不存在。", false);
  }
  const headers = new Headers(response.headers);
  for (const [key, value] of corsHeaders(origin, env)) headers.set(key, value);
  return new Response(response.body, { status: response.status, headers });
}

export default {
  async fetch(request: Request, env: AppEnv): Promise<Response> {
    const requestId = crypto.randomUUID();
    try {
      return await route(request, env, requestId);
    } catch (error) {
      const apiError = error instanceof ApiError
        ? error
        : new ApiError(500, "internal_error", "服务暂时不可用，请稍后重试。", true);
      const origin = request.headers.get("origin");
      let allowedOrigin: string | undefined;
      try {
        allowedOrigin = origin ? assertOrigin(origin, env) : undefined;
      } catch {
        allowedOrigin = undefined;
      }
      return envelope(apiError.status, requestId, {
        code: apiError.code,
        message: apiError.message,
        retryable: apiError.retryable,
      }, allowedOrigin, env);
    }
  },
} satisfies ExportedHandler<AppEnv>;
