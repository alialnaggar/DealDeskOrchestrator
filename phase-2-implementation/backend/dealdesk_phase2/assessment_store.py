"""Transactional, owner-scoped API registry in the dedicated checkpoint database."""

from hashlib import sha256
import json
import re
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

from .phase1c_adapter import EvidenceMismatch, PHASE1C_COMMIT

_ID = re.compile(r"[0-9a-f]{32}\Z")
_KEY = re.compile(r"[A-Za-z0-9_-]{8,128}\Z")
_OWNER = re.compile(r"[A-Za-z0-9_-]{1,80}\Z")


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


class AssessmentStore:
    def __init__(self, dsn):
        self.dsn = dsn

    def connect(self):
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def create(self, owner, key, scenario, run_id, deal_id):
        if not _OWNER.fullmatch(owner) or not _KEY.fullmatch(key):
            raise ValueError("Invalid owner or idempotency key")
        digest = sha256(json.dumps({"scenario": scenario, "run_id": str(run_id),
            "deal_id": deal_id}, sort_keys=True).encode()).hexdigest()
        assessment_id = uuid4().hex
        with self.connect() as db:
            row = db.execute("""INSERT INTO dealdesk_demo.assessments
                (assessment_id, owner_id, idempotency_key, scenario, request_digest,
                 run_id, source_deal_id, phase1c_pin, status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'accepted')
                ON CONFLICT (owner_id, idempotency_key) DO UPDATE SET
                idempotency_key=EXCLUDED.idempotency_key
                RETURNING *""", (assessment_id, owner, key, scenario, digest, run_id,
                    deal_id, PHASE1C_COMMIT)).fetchone()
            if row["request_digest"] != digest or row["phase1c_pin"] != PHASE1C_COMMIT:
                raise Conflict("Idempotency key reused for different source")
            if row["assessment_id"] == assessment_id:
                self._append(db, assessment_id, "accepted", None)
            return row["assessment_id"], row["assessment_id"] == assessment_id

    def _append(self, db, assessment_id, kind, stage):
        row = db.execute("""UPDATE dealdesk_demo.assessments SET last_sequence=last_sequence+1
            WHERE assessment_id=%s RETURNING last_sequence""", (assessment_id,)).fetchone()
        if row is None:
            raise NotFound()
        db.execute("""INSERT INTO dealdesk_demo.assessment_events
            (assessment_id,sequence,kind,stage) VALUES (%s,%s,%s,%s)""",
            (assessment_id, row["last_sequence"], kind, stage))

    def get(self, owner, assessment_id):
        if not _ID.fullmatch(assessment_id) or not _OWNER.fullmatch(owner):
            raise NotFound()
        with self.connect() as db:
            row = db.execute("""SELECT a.*, e.n AS event_count, e.last AS event_last
                FROM dealdesk_demo.assessments a CROSS JOIN LATERAL
                (SELECT count(*) AS n, coalesce(max(sequence),0) AS last
                 FROM dealdesk_demo.assessment_events WHERE assessment_id=a.assessment_id) e
                WHERE a.owner_id=%s AND a.assessment_id=%s""",
                (owner, assessment_id)).fetchone()
        if row is None or row["phase1c_pin"] != PHASE1C_COMMIT:
            raise NotFound()
        if row["event_count"] != row["last_sequence"] or row["event_last"] != row["last_sequence"]:
            raise EvidenceMismatch("Assessment event cursor differs")
        return row

    def events(self, owner, assessment_id, after):
        self.get(owner, assessment_id)
        with self.connect() as db:
            return db.execute("""SELECT assessment_id,sequence,occurred_at,kind,stage
                FROM dealdesk_demo.assessment_events WHERE assessment_id=%s AND sequence>%s
                ORDER BY sequence LIMIT 100""", (assessment_id, after)).fetchall()

    def claim(self, assessment_id):
        with self.connect() as db:
            row = db.execute("""UPDATE dealdesk_demo.assessments SET status='running'
                WHERE assessment_id=%s AND status='accepted' RETURNING assessment_id""",
                (assessment_id,)).fetchone()
            if row is None:
                return False
            self._append(db, assessment_id, "running", None)
            return True

    def get_ownerless_for_worker(self, assessment_id):
        if not _ID.fullmatch(assessment_id):
            raise NotFound()
        with self.connect() as db:
            row = db.execute("SELECT * FROM dealdesk_demo.assessments WHERE assessment_id=%s AND status='running'",
                (assessment_id,)).fetchone()
        if row is None or row["phase1c_pin"] != PHASE1C_COMMIT:
            raise NotFound()
        return row

    def record(self, assessment_id, kind, stage=None, *, status=None, source=None):
        if kind not in ("preflight_ok", "checkpoint", "fixed_completed", "ai_completed",
                        "review_ready", "stopped", "uncertain") or stage not in (
                        None, "original", "configuration", "pricing", "fulfillment",
                        "credit", "policy", "approval_routing", "candidate", "review"):
            raise ValueError("Unknown progress boundary")
        with self.connect() as db:
            row = db.execute("SELECT status,bundle_sha256,source_input_digest FROM dealdesk_demo.assessments WHERE assessment_id=%s FOR UPDATE",
                (assessment_id,)).fetchone()
            if row is None or row["status"] != "running":
                raise EvidenceMismatch("Assessment is not exclusively running")
            if source is not None:
                bundle, digest = source
                if (row["bundle_sha256"] is not None and row["bundle_sha256"] != bundle or
                        row["source_input_digest"] is not None and row["source_input_digest"] != digest):
                    raise EvidenceMismatch("Assessment pinned source changed")
                db.execute("""UPDATE dealdesk_demo.assessments SET bundle_sha256=%s,
                    source_input_digest=%s WHERE assessment_id=%s""", (bundle, digest, assessment_id))
            if status is not None:
                if (status not in ("completed", "stopped", "uncertain") or
                        (kind, status) not in (("review_ready", "completed"),
                                               ("stopped", "stopped"),
                                               ("uncertain", "uncertain"))):
                    raise ValueError("Invalid terminal status")
                db.execute("UPDATE dealdesk_demo.assessments SET status=%s WHERE assessment_id=%s",
                           (status, assessment_id))
            self._append(db, assessment_id, kind, stage)

    def mark_interrupted(self):
        """On server startup, never resume a run whose worker ownership was lost."""
        with self.connect() as db:
            ids = db.execute("SELECT assessment_id FROM dealdesk_demo.assessments WHERE status IN ('running','accepted') FOR UPDATE").fetchall()
            for row in ids:
                db.execute("UPDATE dealdesk_demo.assessments SET status='uncertain' WHERE assessment_id=%s",
                           (row["assessment_id"],))
                self._append(db, row["assessment_id"], "uncertain", None)

    def mark_unscheduled(self, assessment_id):
        with self.connect() as db:
            row = db.execute("""UPDATE dealdesk_demo.assessments SET status='uncertain'
                WHERE assessment_id=%s AND status='accepted' RETURNING assessment_id""",
                (assessment_id,)).fetchone()
            if row is not None:
                self._append(db, assessment_id, "uncertain", None)
