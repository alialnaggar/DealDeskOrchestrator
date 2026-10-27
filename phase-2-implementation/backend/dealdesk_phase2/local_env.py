"""Explicit local .env launcher for opt-in development tools; never auto-load in CI.

Run ``python -m dealdesk_phase2.local_env -- <existing command>`` from a
configured backend checkout. Only GROQ_API_KEY is read, never logged or
written to the checkpoint. Hosted authorization remains a separate gate.
"""

import os
from pathlib import Path
import stat
import sys

from .groq_preflight import credential_shape


BACKEND_ENV = Path(__file__).resolve().parents[1] / ".env"


def with_local_groq_key(environment: dict[str, str], path: Path = BACKEND_ENV) -> dict[str, str]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("Local Groq .env unavailable")
    file_stat = path.stat()
    if (file_stat.st_uid != os.geteuid()
            or stat.S_IMODE(file_stat.st_mode) != 0o600):
        raise ValueError("Local Groq .env ownership or mode invalid")
    content = path.read_text(encoding="ascii")
    if not content.endswith("\n") or content.count("\n") != 1:
        raise ValueError("Local Groq .env format invalid")
    name, separator, value = content.strip("\n").partition("=")
    if name != "GROQ_API_KEY" or separator != "=" or credential_shape(value) != "credential_shape_ok":
        raise ValueError("Local Groq credential shape invalid")
    return {**environment, "GROQ_API_KEY": value}


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--":
        args = args[1:]
    if not args:
        raise ValueError("Supply an existing command to run")
    os.execvpe(args[0], args, with_local_groq_key(dict(os.environ)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
