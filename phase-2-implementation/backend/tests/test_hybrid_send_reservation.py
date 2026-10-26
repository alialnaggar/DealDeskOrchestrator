"""Mocked send; never opens a socket or runs a provider adapter."""

from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

from dealdesk_phase2.hybrid_send_reservation import (attempt_path, claim_and_call,
                                                    exclusive_owner, verify_receipt)
from dealdesk_phase2.hybrid_contracts import HybridContractError


START = "a" * 64
WIRE = "b" * 64


class ExclusiveHybridSendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def invoke(self, send):
        return claim_and_call(self.root, assessment_id="HYBRID-A", start_digest=START,
                              stage="decision", ordinal=0, request_digest=WIRE, send=send)

    def audit(self):
        path = attempt_path(self.root, assessment_id="HYBRID-A", start_digest=START,
                            stage="decision", ordinal=0)
        return path, [json.loads(line) for line in path.read_text().splitlines()]

    def test_one_send_and_terminal_replay_block(self):
        sender = Mock(return_value={"private": "response never persisted"})
        self.assertEqual(self.invoke(sender), sender.return_value)
        path, events = self.audit()
        self.assertEqual([x["event"] for x in events], ["reserved", "returned"])
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertNotIn("private", path.read_text())
        with self.assertRaises(FileExistsError):
            self.invoke(sender)
        sender.assert_called_once_with()

    def test_receipt_does_not_accept_changed_request_digest(self):
        self.invoke(lambda: {"safe": True})
        path, _ = self.audit()
        self.assertTrue(verify_receipt(path, start_digest=START, stage="decision", ordinal=0,
                                       request_digest=WIRE))
        with self.assertRaisesRegex(HybridContractError, "send_receipt_invalid"):
            verify_receipt(path, start_digest=START, stage="decision", ordinal=0,
                           request_digest="c" * 64)

    def test_receipt_rejects_malformed_returned_and_extra_fields(self):
        self.invoke(lambda: {"safe": True})
        path, events = self.audit()
        for modified in ({**events[1], "untrusted": "marker"},
                         {**events[1], "returned_at_utc": None},
                         ["returned", "not an event"]):
            with self.subTest(modified=modified):
                path.write_text("\n".join(json.dumps(x) for x in (events[0], modified)) + "\n")
                with self.assertRaisesRegex(HybridContractError, "send_receipt_invalid"):
                    verify_receipt(path, start_digest=START, stage="decision", ordinal=0,
                                   request_digest=WIRE)
        path.write_text("\n".join(json.dumps(x) for x in (
            {**events[0], "untrusted": "marker"}, events[1])) + "\n")
        with self.assertRaisesRegex(HybridContractError, "send_receipt_invalid"):
            verify_receipt(path, start_digest=START, stage="decision", ordinal=0,
                           request_digest=WIRE)

    def test_reserved_only_receipt_cannot_prove_completed_send(self):
        self.invoke(lambda: {"safe": True})
        path, events = self.audit()
        path.write_text(json.dumps(events[0]) + "\n")
        self.assertFalse(verify_receipt(path, start_digest=START, stage="decision",
                                        ordinal=0, request_digest=WIRE))

    def test_directory_and_receipt_owner_are_verified(self):
        import os

        self.invoke(lambda: {"safe": True})
        path, _ = self.audit()
        with patch("dealdesk_phase2.hybrid_send_reservation.os.geteuid",
                   return_value=os.geteuid() + 1):
            with self.assertRaisesRegex(HybridContractError,
                                        "invalid_send_reservation_scope"):
                attempt_path(self.root, assessment_id="HYBRID-A", start_digest=START,
                             stage="decision", ordinal=0)
            with self.assertRaisesRegex(HybridContractError, "send_receipt_invalid"):
                verify_receipt(path, start_digest=START, stage="decision", ordinal=0,
                               request_digest=WIRE)

    def test_crash_network_error_and_pre_send_sync_failure_are_not_retried(self):
        for failure in (KeyboardInterrupt, TimeoutError, OSError):
            with self.subTest(failure=failure):
                with tempfile.TemporaryDirectory(dir="/tmp/opencode") as root:
                    parent = self.root
                    self.root = Path(root)
                    try:
                        sender = Mock(side_effect=failure("unknown provider state"))
                        with self.assertRaises(failure):
                            self.invoke(sender)
                        self.assertEqual([x["event"] for x in self.audit()[1]], ["reserved"])
                        with self.assertRaises(FileExistsError):
                            self.invoke(sender)
                        sender.assert_called_once_with()
                    finally:
                        self.root = parent
        sender = Mock()
        with patch("dealdesk_phase2.hybrid_send_reservation.os.fsync",
                   side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.invoke(sender)
        sender.assert_not_called()
        with self.assertRaises(FileExistsError):
            self.invoke(sender)

    def test_concurrent_threads_only_one_calls_sender(self):
        entered = threading.Event()
        finish = threading.Event()
        count = 0
        lock = threading.Lock()

        def sender():
            nonlocal count
            with lock:
                count += 1
            entered.set()
            if not finish.wait(5):
                raise TimeoutError("test synchronization")
            return "sent"

        with ThreadPoolExecutor(max_workers=2) as workers:
            first = workers.submit(self.invoke, sender)
            self.assertTrue(entered.wait(5))
            second = workers.submit(self.invoke, sender)
            with self.assertRaises(FileExistsError):
                second.result(timeout=5)
            finish.set()
            self.assertEqual(first.result(timeout=5), "sent")
        self.assertEqual(count, 1)

    def test_process_owner_released_after_crash_but_uncertain_send_never_replayed(self):
        # 'spawn' uses independent file descriptors and an independent Python
        # process; this is not merely a thread scheduling assertion.
        ctx = multiprocessing.get_context("spawn")
        queue = ctx.Queue()
        with exclusive_owner(self.root, "same-assessment"):
            worker = ctx.Process(target=_try_owner, args=(str(self.root), queue))
            worker.start()
            self.assertEqual(queue.get(timeout=10), "hybrid_owner_busy")
            worker.join(10)
            self.assertEqual(worker.exitcode, 0)
        worker = ctx.Process(target=_try_owner, args=(str(self.root), queue))
        worker.start()
        self.assertEqual(queue.get(timeout=10), "acquired")
        worker.join(10)
        self.assertEqual(worker.exitcode, 0)
        with self.assertRaises(KeyboardInterrupt):
            self.invoke(lambda: (_ for _ in ()).throw(KeyboardInterrupt()))
        with self.assertRaises(FileExistsError):
            self.invoke(lambda: "must never send")


def _try_owner(directory, queue):
    try:
        with exclusive_owner(Path(directory), "same-assessment"):
            queue.put("acquired")
    except HybridContractError as exc:
        queue.put(exc.code)


if __name__ == "__main__":
    unittest.main()
