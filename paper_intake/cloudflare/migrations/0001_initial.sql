PRAGMA foreign_keys = ON;

CREATE TABLE papers (
  paper_id TEXT PRIMARY KEY,
  doi TEXT UNIQUE,
  arxiv_id TEXT UNIQUE,
  canonical_url TEXT NOT NULL DEFAULT '',
  normalized_title TEXT NOT NULL DEFAULT '',
  title_fingerprint TEXT NOT NULL DEFAULT '',
  pdf_sha256 TEXT UNIQUE,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX papers_title_fingerprint_idx ON papers(title_fingerprint);

CREATE TABLE jobs (
  job_id TEXT PRIMARY KEY,
  paper_id TEXT NOT NULL REFERENCES papers(paper_id),
  owner_identity TEXT NOT NULL,
  input_type TEXT NOT NULL CHECK(input_type IN ('url', 'pdf')),
  input_ref TEXT NOT NULL,
  stage TEXT NOT NULL DEFAULT 'received',
  status TEXT NOT NULL DEFAULT 'queued',
  attempt INTEGER NOT NULL DEFAULT 0,
  lease_owner TEXT,
  lease_until TEXT,
  checkpoint_json TEXT NOT NULL DEFAULT '{}',
  error_code TEXT,
  error_message TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX jobs_claim_idx ON jobs(status, lease_until, created_at);
CREATE INDEX jobs_owner_idx ON jobs(owner_identity, created_at);

CREATE TABLE artifacts (
  artifact_id TEXT PRIMARY KEY,
  paper_id TEXT NOT NULL REFERENCES papers(paper_id),
  job_id TEXT NOT NULL REFERENCES jobs(job_id),
  kind TEXT NOT NULL,
  r2_key TEXT NOT NULL UNIQUE,
  sha256 TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  content_type TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE publications (
  paper_id TEXT PRIMARY KEY REFERENCES papers(paper_id),
  job_id TEXT NOT NULL REFERENCES jobs(job_id),
  notion_page_id TEXT NOT NULL,
  slug TEXT NOT NULL,
  site_url TEXT NOT NULL,
  git_commit TEXT NOT NULL DEFAULT '',
  publish_status TEXT NOT NULL,
  published_at TEXT
);

CREATE TABLE login_codes (
  code_hash TEXT PRIMARY KEY,
  owner_identity TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  consumed_at TEXT
);

CREATE TABLE job_events (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT NOT NULL REFERENCES jobs(job_id),
  event_type TEXT NOT NULL,
  details_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX job_events_once_idx ON job_events(job_id, event_type)
WHERE event_type IN ('publication.dispatched', 'publication.completed');
