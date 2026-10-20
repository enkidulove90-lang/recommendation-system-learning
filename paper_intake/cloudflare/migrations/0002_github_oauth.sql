CREATE TABLE oauth_states (
  state_hash TEXT PRIMARY KEY,
  return_origin TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  consumed_at TEXT
);
