CREATE TABLE retry_operations (
  idempotency_key TEXT PRIMARY KEY,
  job_id TEXT NOT NULL REFERENCES jobs(job_id),
  operation TEXT NOT NULL CHECK(operation = 'retry'),
  state TEXT NOT NULL CHECK(state IN ('pending', 'completed')),
  response_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX retry_operations_job_idx ON retry_operations(job_id, created_at);
