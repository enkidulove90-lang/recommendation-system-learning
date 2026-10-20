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
}

export interface PublicationInput {
  notionPageId: string;
  slug: string;
  siteUrl: string;
}
