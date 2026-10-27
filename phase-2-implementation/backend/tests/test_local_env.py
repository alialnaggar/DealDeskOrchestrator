"""Offline-only local launcher contract: no credential appears in test output."""

from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

from dealdesk_phase2.local_env import main, with_local_groq_key


class LocalEnvTests(unittest.TestCase):
    def test_loads_owner_only_ignored_style_without_mutating_parent(self):
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            path = Path(directory) / ".env"
            path.write_text("GROQ_API_KEY=" + "gsk_" + "x" * 47 + "\n")
            path.chmod(0o600)
            incoming = {"KEEP": "value"}
            outgoing = with_local_groq_key(incoming, path)
            self.assertEqual(incoming, {"KEEP": "value"})
            self.assertEqual(outgoing["KEEP"], "value")
            self.assertEqual(len(outgoing["GROQ_API_KEY"]), 51)
            path.chmod(0o644)
            with self.assertRaises(ValueError):
                with_local_groq_key({}, path)
            path.chmod(0o600)
            path.write_text("GROQ_API_KEY=" + "gsk_" + "x" * 47 + "\nOTHER=unsafe\n")
            with self.assertRaises(ValueError):
                with_local_groq_key({}, path)

    def test_launcher_does_not_autorun_and_passes_only_child_environment(self):
        before = os.environ.get("GROQ_API_KEY")
        with patch("dealdesk_phase2.local_env.with_local_groq_key",
                   return_value={"GROQ_API_KEY": "offline-fixture"}), patch(
                "dealdesk_phase2.local_env.os.execvpe") as execute, patch(
                "sys.argv", ["local_env", "--", "python", "-m", "package.runner"]):
            self.assertEqual(main(), 0)
        execute.assert_called_once()
        self.assertEqual(execute.call_args.args[:2], ("python", ["python", "-m", "package.runner"]))
        self.assertEqual(os.environ.get("GROQ_API_KEY"), before)
