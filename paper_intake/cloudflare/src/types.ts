export type JobStatus =
  | "queued"
  | "processing"
  | "publishing"
  | "published"
  | "failed"
  | "cancelled";

export interface PaperIdentity {
  doi?: string;
  arxivId?: string;
  canonicalUrl?: string;
  normalizedTitle?: string;
  titleFingerprint?: string;
  pdfSha256?: string;
}

export interface PaperRecord {
  paperId: string;
  doi: string | null;
  arxivId: string | null;
  canonicalUrl: string;
  normalizedTitle: string;
  titleFingerprint: string;
  pdfSha256: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface PaperResolution extends PaperRecord {
  reused: boolean;
}

export interface CreateJobInput {
  paperId: string;
  ownerIdentity: string;
  inputType: "url" | "pdf";
  inputRef: string;
  traceId?: string;
}

export type FailureCategory = "validation" | "network" | "auth" | "provider" | "internal" | "config" | "publication";

export interface FailureDescriptor {
  stage: string;
  code: string;
  category: FailureCategory;
  retryable: boolean;
  httpStatus?: number | null;
  providerErrorCode?: string | null;
  providerRequestId?: string | null;
  attempt: number;
  durationMs?: number | null;
  safeMessage: string;
  diagnosticHint: string;
  errorFingerprint: string;
  localLogRef?: string | null;
  exceptionType?: string | null;
  module?: string | null;
  functionName?: string | null;
}

export interface JobRecord {
  jobId: string;
  paperId: string;
  ownerIdentity: string;
  inputType: "url" | "pdf";
  inputRef: string;
  stage: string;
  status: JobStatus;
  attempt: number;
  leaseOwner: string | null;
  leaseUntil: string | null;
  checkpoints: Record<string, unknown>;
  errorCode: string | null;
  errorMessage: string | null;
  createdAt: string;
  updatedAt: string;
  traceId: string;
}

export interface PublicationInput {
  notionPageId: string;
  slug: string;
  siteUrl: string;
}

export interface ArtifactInput {
  kind: string;
  r2Key: string;
  sha256: string;
  sizeBytes: number;
  contentType: string;
}

export interface ArtifactRecord extends ArtifactInput {
  artifactId: string;
  paperId: string;
  jobId: string;
  createdAt: string;
}
