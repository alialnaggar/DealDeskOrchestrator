"""Real PostgreSQL checkpoint recovery against the separately pinned Phase 1C."""

import os
from pathlib import Path
import subprocess
import sys
import unittest
from uuid import UUID

try:
    import psycopg
except ImportError:
    psycopg = None

from dealdesk_phase2.checkpoint import thesis_checkpointer
from dealdesk_phase2.graph_state import pinned_from_state
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import Phase1CAdapter


RUN = UUID("00000000-0000-4000-8000-000000010001")
OFFER = UUID("00000000-0000-4000-8000-000000030001")
READY = all((psycopg, os.getenv("DATABASE_URL"), os.getenv("CHECKPOINT_DATABASE_URL"),
             os.getenv("DEALDESK_PHASE1C_CHECKOUT")))


def _adapter():
    return Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))


def _connect():
    return psycopg.connect(os.environ["DATABASE_URL"])


def pause_in_first_process(assessment_id):
    adapter = _adapter()
    with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
        graph = build_original_graph(adapter, _connect, saver,
                                     interrupt_after=("configuration",))
        config = {"configurable": {"thread_id": assessment_id}}
        graph.invoke(initial_state(assessment_id, RUN), config)
        state = graph.get_state(config)
        assert state.next == ("pricing",), state.next
        assert list(state.values["specialist_results"]) == ["configuration"]
        print("M1.1 first process paused after Configuration", flush=True)


@unittest.skipUnless(READY, "Requires pinned fixtures and separate disposable checkpoint database")
class CheckpointResumeTests(unittest.TestCase):
    def test_original_binding_and_conditional_reference_facts(self):
        adapter = _adapter()
        for name, run, expected in (("binding", RUN, "confirmed_by_date"),
                                    ("offer", OFFER, "conditional")):
            with self.subTest(name=name), thesis_checkpointer(
                    os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(adapter, _connect, saver)
                assessment = "M11-" + name
                state = graph.invoke(initial_state(assessment, run),
                                     {"configurable": {"thread_id": assessment}})
                pinned = pinned_from_state(state)
                self.assertEqual(pinned.context.phase1c_run_id, run)
                self.assertEqual(state["specialist_results"]["fulfillment"]["payload"][0]["status"],
                                 expected)
                self.assertEqual(len(state["specialist_results"]), 6)
                self.assertEqual(state["specialist_results"]["approval_routing"]["payload"][
                    "route_withheld"], state["review_status"] != "approval_required")

    def test_restart_preserves_evidence_and_completed_configuration(self):
        assessment = "M11-restart"
        cmd = [sys.executable, str(Path(__file__).resolve()), "--pause", assessment]
        child = subprocess.run(cmd, env=os.environ.copy(), capture_output=True, text=True,
                               timeout=90, check=True)
        self.assertIn("first process paused", child.stdout)
        with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
            config = {"configurable": {"thread_id": assessment}}
            graph = build_original_graph(_adapter(), _connect, saver)
            paused = graph.get_state(config)
            pinned = pinned_from_state(paused.values)
            self.assertEqual(paused.next, ("pricing",))
            self.assertEqual(paused.values["trace"], ["evidence_pinned", "configuration:completed"])
            resumed = graph.invoke(None, config)
            self.assertEqual(resumed["context"], paused.values["context"])
            self.assertEqual(resumed["sealed_bundle"], paused.values["sealed_bundle"])
            self.assertEqual(resumed["specialist_results"]["configuration"],
                             paused.values["specialist_results"]["configuration"])
            self.assertEqual(resumed["trace"].count("configuration:completed"), 1)
            self.assertEqual(resumed["trace"].count("evidence_pinned"), 1)
            self.assertEqual(len(resumed["specialist_results"]), 6)
            self.assertEqual(pinned_from_state(resumed).context.bundle_sha256,
                             pinned.context.bundle_sha256)
            self.assertEqual(resumed["review_status"], "approval_required")
            with psycopg.connect(os.environ["CHECKPOINT_DATABASE_URL"]) as conn:
                latest = conn.execute(
                    "SELECT pg_column_size(checkpoint), pg_column_size(metadata) "
                    "FROM checkpoints WHERE thread_id=%s ORDER BY checkpoint_id DESC LIMIT 1",
                    (assessment,)).fetchone()
                sizes = conn.execute(
                    "SELECT pg_total_relation_size('checkpoints'), "
                    "pg_total_relation_size('checkpoint_blobs'), "
                    "pg_total_relation_size('checkpoint_writes')").fetchone()
            self.assertTrue(latest and all(size > 0 for size in latest + sizes))
            print(f"M1.1 completed checkpoint JSONB fields: {latest[0]} checkpoint bytes, "
                  f"{latest[1]} metadata bytes; total relation+index sizes "
                  f"checkpoints={sizes[0]}, blobs={sizes[1]}, writes={sizes[2]} bytes; "
                  f"sealed bundle={pinned.size_bytes} UTF-8 bytes")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--pause":
        pause_in_first_process(sys.argv[2])
    else:
        unittest.main()
