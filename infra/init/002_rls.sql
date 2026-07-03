-- Enable Row Level Security (RLS) on all tables with a pipeline_id-based policy

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY documents_pipeline_isolation_policy ON documents
  USING (pipeline_id = current_setting('neuroflow.current_pipeline_id', true)::uuid);

ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY chunks_pipeline_isolation_policy ON chunks
  USING (
    document_id IN (
      SELECT id FROM documents WHERE pipeline_id = current_setting('neuroflow.current_pipeline_id', true)::uuid
    )
  );

ALTER TABLE pipeline_runs ENABLE ROW LEVEL SECURITY;
CREATE POLICY pipeline_runs_isolation_policy ON pipeline_runs
  USING (pipeline_id = current_setting('neuroflow.current_pipeline_id', true)::uuid);

ALTER TABLE evaluations ENABLE ROW LEVEL SECURITY;
CREATE POLICY evaluations_isolation_policy ON evaluations
  USING (
    run_id IN (
      SELECT id FROM pipeline_runs WHERE pipeline_id = current_setting('neuroflow.current_pipeline_id', true)::uuid
    )
  );

ALTER TABLE training_pairs ENABLE ROW LEVEL SECURITY;
CREATE POLICY training_pairs_isolation_policy ON training_pairs
  USING (
    run_id IN (
      SELECT id FROM pipeline_runs WHERE pipeline_id = current_setting('neuroflow.current_pipeline_id', true)::uuid
    )
  );
