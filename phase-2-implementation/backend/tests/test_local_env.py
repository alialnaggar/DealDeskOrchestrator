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

    def test_explicit_secondary_isolated_from_original_and_never_falls_back(self):
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            path = Path(directory) / ".env"
            path.write_text("GROQ_API_KEY=" + "gsk_" + "x" * 47 + "\n")
            path.chmod(0o600)
            with self.assertRaises(ValueError):
                with_local_groq_key({}, path, credential="secondary")
            path.write_text("GROQ_API_KEY=" + "gsk_" + "x" * 47 +
                            "\nGROQ_SECONDARY_API_KEY=" + "gsk_" + "y" * 47 + "\n")
            environment = {"KEEP": "value", "GROQ_SECONDARY_API_KEY": "ambient-value"}
            primary = with_local_groq_key(environment, path)
            secondary = with_local_groq_key(environment, path, credential="secondary")
            self.assertEqual(primary["GROQ_API_KEY"], "gsk_" + "x" * 47)
            self.assertEqual(secondary["GROQ_API_KEY"], "gsk_" + "y" * 47)
            self.assertNotIn("GROQ_SECONDARY_API_KEY", primary)
            self.assertNotIn("GROQ_SECONDARY_API_KEY", secondary)
            self.assertEqual(environment["GROQ_SECONDARY_API_KEY"], "ambient-value")
            path.write_text("GROQ_API_KEY=" + "gsk_" + "x" * 47 +
                            "\nGROQ_SECONDARY_API_KEY=not-a-key\n")
            with self.assertRaises(ValueError):
                with_local_groq_key({}, path, credential="secondary")
            self.assertEqual(with_local_groq_key({}, path)["GROQ_API_KEY"],
                             "gsk_" + "x" * 47)
            path.write_text("GROQ_API_KEY=" + "gsk_" + "x" * 47 +
                            "\nGROQ_SECONDARY_API_KEY=" + "gsk_" + "y" * 47 +
                            "\nGROQ_SECONDARY_API_KEY=" + "gsk_" + "z" * 47 + "\n")
            with self.assertRaises(ValueError):
                with_local_groq_key({}, path, credential="primary")

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

    def test_launcher_requires_explicit_secondary_choice(self):
        with patch("dealdesk_phase2.local_env.with_local_groq_key",
                   return_value={"GROQ_API_KEY": "offline-fixture"}) as loader, patch(
                "dealdesk_phase2.local_env.os.execvpe") as execute, patch(
                "sys.argv", ["local_env", "--credential", "secondary", "--", "python", "-m",
                             "package.runner"]):
            self.assertEqual(main(), 0)
        self.assertEqual(loader.call_args.kwargs["credential"], "secondary")
        self.assertEqual(execute.call_args.args[0], "python")
