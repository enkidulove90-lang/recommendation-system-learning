ALTER TABLE papers ADD COLUMN metadata_json TEXT;
ALTER TABLE papers ADD COLUMN metadata_source TEXT;

CREATE TABLE metadata_refresh_operations (
  idempotency_key TEXT PRIMARY KEY,
  job_id TEXT NOT NULL REFERENCES jobs(job_id),
  state TEXT NOT NULL CHECK(state IN ('queued', 'processing', 'completed', 'failed')),
  lease_owner TEXT,
  lease_until TEXT,
  result_json TEXT NOT NULL DEFAULT '{}',
  error_code TEXT,
  error_message TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX metadata_refresh_claim_idx
ON metadata_refresh_operations(state, lease_until, created_at);
