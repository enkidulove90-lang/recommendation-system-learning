ALTER TABLE jobs ADD COLUMN trace_id TEXT;
UPDATE jobs SET trace_id = 'tr_' || job_id WHERE trace_id IS NULL OR trace_id = '';
CREATE UNIQUE INDEX jobs_trace_id_once_idx ON jobs(trace_id);
