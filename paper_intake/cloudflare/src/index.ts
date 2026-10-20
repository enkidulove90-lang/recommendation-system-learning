import { IntakeRepository } from "./repository";
import {
  ApiError,
  assertOrigin,
  consumeLoginCode,
  createLoginCode,
  requireAccessIdentity,
  requireOwner,
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

function corsHeaders(origin: string, env: AppEnv): Headers {
  const allowed = assertOrigin(origin, env);
  return new Headers({
    "access-control-allow-origin": allowed,
    "access-control-allow-methods": "GET,POST,OPTIONS",
    "access-control-allow-headers": "authorization,content-type",
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
  await env.ARTIFACTS.put(inputRef, bytes, {
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
    await env.ARTIFACTS.delete(inputRef);
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

async function route(request: Request, env: AppEnv, requestId: string): Promise<Response> {
  const url = new URL(request.url);
  if (url.pathname === "/v1/session/start" && request.method === "GET") {
    const targetOrigin = assertOrigin(url.searchParams.get("return_origin"), env);
    const identity = requireAccessIdentity(request, env);
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
  let response: Response;
  if (url.pathname === "/v1/intake/url" && request.method === "POST") {
    response = await ingestUrl(request, env, owner, requestId);
  } else if (url.pathname === "/v1/intake/pdf" && request.method === "POST") {
    response = await ingestPdf(request, env, owner, requestId);
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
