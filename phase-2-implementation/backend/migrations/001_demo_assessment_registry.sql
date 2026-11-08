-- API-owned metadata only; never modify Phase 1C business evidence.
CREATE SCHEMA IF NOT EXISTS dealdesk_demo;
CREATE TABLE IF NOT EXISTS dealdesk_demo.assessments (
  assessment_id text PRIMARY KEY,
  owner_id text NOT NULL,
  idempotency_key text NOT NULL,
  scenario text NOT NULL,
  request_digest text NOT NULL,
  run_id uuid NOT NULL,
  source_deal_id text NOT NULL,
  phase1c_pin text NOT NULL,
  bundle_sha256 text,
  source_input_digest text,
  status text NOT NULL CHECK (status IN ('accepted','running','completed','stopped','uncertain')),
  last_sequence bigint NOT NULL DEFAULT 0 CHECK (last_sequence >= 0),
  created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  UNIQUE (owner_id, idempotency_key)
);
CREATE TABLE IF NOT EXISTS dealdesk_demo.assessment_events (
  assessment_id text NOT NULL REFERENCES dealdesk_demo.assessments(assessment_id),
  sequence bigint NOT NULL CHECK (sequence > 0),
  occurred_at timestamptz NOT NULL DEFAULT clock_timestamp(),
  kind text NOT NULL,
  stage text,
  PRIMARY KEY (assessment_id, sequence)
);
CREATE OR REPLACE FUNCTION dealdesk_demo.reject_event_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'assessment events are append-only'; END $$;
DROP TRIGGER IF EXISTS assessment_events_immutable ON dealdesk_demo.assessment_events;
CREATE TRIGGER assessment_events_immutable BEFORE UPDATE OR DELETE
ON dealdesk_demo.assessment_events FOR EACH ROW EXECUTE FUNCTION dealdesk_demo.reject_event_mutation();
