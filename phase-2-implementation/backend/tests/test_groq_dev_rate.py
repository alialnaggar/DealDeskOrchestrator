"""No-network, isolated filesystem tests of Groq-only development pacing."""

from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from unittest import TestCase
from unittest.mock import patch
from urllib.error import HTTPError
from io import BytesIO
import json
import os
from multiprocessing import get_context

from dealdesk_phase2.groq_dev_rate import rate_headers, send_with_limit
from dealdesk_phase2.live_models import ProviderError, _post


BODY = {"model": "openai/gpt-oss-120b", "max_completion_tokens": 1024,
        "messages": [{"role": "user", "content": "synthetic"}]}
KEY = "gsk_offline_test_placeholder_123456789"


class GroqDevRate(TestCase):
    def test_transport_captures_429_headers_without_reading_error_body(self):
        class Unreadable(BytesIO):
            def read(self, *args, **kwargs):
                raise AssertionError("never read provider error text")
        class Opener:
            calls = 0
            def open(self, request, timeout):
                self.calls += 1
                raise HTTPError(request.full_url, 429, "redacted", {
                    "retry-after": "12", "x-ratelimit-limit-requests": "1000",
                    "x-ratelimit-remaining-requests": "0",
                    "x-ratelimit-reset-requests": "2h",
                    "x-ratelimit-limit-tokens": "8000",
                    "x-ratelimit-remaining-tokens": "7777",
                    "x-ratelimit-reset-tokens": "1s"}, Unreadable(b"private"))
        opener = Opener()
        with patch.dict(os.environ, {"DEALDESK_GROQ_DEV_ENABLE": "1"}), patch(
                "dealdesk_phase2.live_models.build_opener", return_value=opener):
            with self.assertRaises(ProviderError) as caught:
                _post("https://api.groq.com/openai/v1/chat/completions",
                    "Bearer " + KEY, "Authorization", BODY, classify_transport=True,
                    reject_redirects=True)
            self.assertEqual(caught.exception.code, "http_429")
            with self.assertRaises(ProviderError) as blocked:
                _post("https://api.groq.com/openai/v1/chat/completions",
                    "Bearer " + KEY, "Authorization", BODY, classify_transport=True,
                    reject_redirects=True)
        self.assertEqual(blocked.exception.code, "groq_daily_limit")
        self.assertEqual(opener.calls, 1)

    def setUp(self):
        self.temp = TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "rate"
        patcher = patch("dealdesk_phase2.groq_dev_rate._DIR", self.directory)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_header_allowlist_and_rpd_tpm_reset_semantics(self):
        result = rate_headers({"retry-after": "2.5",
            "x-ratelimit-limit-requests": "1000",
            "x-ratelimit-remaining-requests": "0",
            "x-ratelimit-reset-requests": "1h2m3.5s",
            "x-ratelimit-limit-tokens": "8000",
            "x-ratelimit-remaining-tokens": "300",
            "x-ratelimit-reset-tokens": "5.5s", "Authorization": "secret",
            "x-ratelimit-reset-other": "private"})
        self.assertEqual(result["x-ratelimit-reset-requests"], 3723.5)
        self.assertEqual(result["x-ratelimit-reset-tokens"], 5.5)
        self.assertEqual(result["retry-after"], 2.5)
        self.assertNotIn("Authorization", str(result))

    def test_tpm_spacing_and_daily_stop_without_second_send(self):
        clock = [1000000.0]
        waits = []
        calls = []
        def sender(hook):
            calls.append(clock[0])
            hook(200, {})
            return {"usage": {"prompt_tokens": 100, "completion_tokens": 900}}
        def pause(seconds):
            waits.append(seconds)
            clock[0] += seconds
        with patch.dict(os.environ, {"DEALDESK_GROQ_RPM": "30",
                "DEALDESK_GROQ_RPD": "2", "DEALDESK_GROQ_TPM": "1500",
                "DEALDESK_GROQ_TPD": "10000"}), patch(
                "dealdesk_phase2.groq_dev_rate.time", side_effect=lambda: clock[0]), patch(
                "dealdesk_phase2.groq_dev_rate.sleep", side_effect=pause):
            send_with_limit(BODY, KEY, sender)
            send_with_limit(BODY, KEY, sender)
            self.assertGreaterEqual(calls[1] - calls[0], 60)
            self.assertTrue(waits)
            with self.assertRaises(ProviderError) as caught:
                send_with_limit(BODY, KEY, sender)
        self.assertEqual(caught.exception.code, "groq_daily_limit")
        self.assertEqual(len(calls), 2)

    def test_same_org_different_keys_share_daily_quota(self):
        sent = []
        def sender(hook):
            sent.append(1)
            hook(200, {})
            return {"usage": {"prompt_tokens": 10, "completion_tokens": 10}}
        with patch.dict(os.environ, {"DEALDESK_GROQ_ACCOUNT_ID": "org_synthetic123",
                "DEALDESK_GROQ_RPD": "1"}):
            send_with_limit(BODY, KEY, sender)
            with self.assertRaises(ProviderError) as caught:
                send_with_limit(BODY, KEY + "other", sender)
        self.assertEqual(caught.exception.code, "groq_daily_limit")
        self.assertEqual(len(sent), 1)

    def test_429_headers_stop_daily_and_record_only_bounded_metadata(self):
        def rejected(hook):
            hook(429, {"retry-after": "15", "x-ratelimit-limit-requests": "1000",
                "x-ratelimit-remaining-requests": "0",
                "x-ratelimit-reset-requests": "1h", "x-ratelimit-limit-tokens": "8000",
                "x-ratelimit-remaining-tokens": "7000",
                "x-ratelimit-reset-tokens": "1s", "private": "never persist"})
            raise ProviderError("http_429")
        with self.assertRaises(ProviderError):
            send_with_limit(BODY, KEY, rejected)
        with self.assertRaises(ProviderError) as caught:
            send_with_limit(BODY, KEY, lambda hook: self.fail("should not send"))
        self.assertEqual(caught.exception.code, "groq_daily_limit")
        text = next(self.directory.glob("*.json")).read_text()
        self.assertNotIn("never persist", text)
        self.assertNotIn(KEY, text)

    def test_unclassified_429_blocks_new_case_without_an_immediate_retry(self):
        def rejected(hook):
            hook(429, {"private": "not persisted"})
            raise ProviderError("http_429")
        with patch("dealdesk_phase2.groq_dev_rate.time", return_value=1000000.0):
            with self.assertRaises(ProviderError):
                send_with_limit(BODY, KEY, rejected)
            with self.assertRaisesRegex(ProviderError, "groq_daily_limit|groq_"):
                # No send callback is invoked; this fresh case must wait for
                # a separately checked normal provider quota window.
                send_with_limit(BODY, KEY, lambda hook: self.fail("unexpected send"))

    def test_cross_process_lock_charges_only_one_send_at_rpd_one(self):
        context = get_context("fork")
        start = context.Event()
        results = context.Queue()
        def worker():
            start.wait(5)
            def sender(hook):
                results.put("sent")
                hook(200, {})
                return {"usage": {"prompt_tokens": 10, "completion_tokens": 10}}
            try:
                send_with_limit(BODY, KEY, sender)
                results.put("ok")
            except ProviderError as exc:
                results.put(exc.code)
        with patch.dict(os.environ, {"DEALDESK_GROQ_RPD": "1"}):
            workers = [context.Process(target=worker) for _ in range(2)]
            for process in workers:
                process.start()
            start.set()
            for process in workers:
                process.join(10)
                self.assertEqual(process.exitcode, 0)
        self.assertEqual(sorted(results.get(timeout=2) for _ in range(3)),
                         ["groq_daily_limit", "ok", "sent"])

    def test_interrupted_send_retains_its_daily_charge(self):
        sent = []
        def interrupted(hook):
            sent.append(1)
            raise KeyboardInterrupt("synthetic interrupted POST")
        with patch.dict(os.environ, {"DEALDESK_GROQ_RPD": "1"}):
            with self.assertRaises(KeyboardInterrupt):
                send_with_limit(BODY, KEY, interrupted)
            with self.assertRaisesRegex(ProviderError, "groq_daily_limit"):
                send_with_limit(BODY, KEY, lambda hook: self.fail("unexpected send"))
        self.assertEqual(sent, [1])

    def test_groq_only_opt_in_and_cross_thread_lock(self):
        from threading import Event
        first = Event()
        release = Event()
        order = []
        errors = []
        def sender(hook):
            order.append("start")
            if len(order) == 1:
                first.set()
                self.assertTrue(release.wait(timeout=2))
            hook(200, {})
            order.append("end")
            return {"usage": {"prompt_tokens": 10, "completion_tokens": 10}}
        def run():
            try:
                send_with_limit(BODY, KEY, sender)
            except Exception as exc:
                errors.append(type(exc).__name__)
        with patch.dict(os.environ, {"DEALDESK_GROQ_RPM": "30"}):
            one = Thread(target=run); one.start()
            self.assertTrue(first.wait(timeout=2))
            two = Thread(target=run); two.start()
            release.set(); one.join(timeout=3); two.join(timeout=3)
        self.assertEqual(errors, [])
        self.assertEqual(order, ["start", "end", "start", "end"])
        with patch.dict(os.environ, {"DEALDESK_GROQ_DEV_ENABLE": "1"}), patch(
                "dealdesk_phase2.live_models._post_once", return_value={}) as direct:
            _post("https://api.openai.com/v1/chat/completions", "Bearer any",
                "Authorization", {"model": "other", "messages": []})
        direct.assert_called_once()
