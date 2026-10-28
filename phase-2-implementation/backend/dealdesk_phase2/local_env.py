"""Explicit local .env launcher for opt-in development tools; never auto-load in CI.

Run ``python -m dealdesk_phase2.local_env -- <existing command>`` for the
original key or add ``--credential secondary`` before ``--`` for the separate
key. Only the selected credential enters the child's GROQ_API_KEY environment.
Hosted authorization remains a separate gate.
"""

import os
from pathlib import Path
import stat
import sys

from .groq_preflight import credential_shape


BACKEND_ENV = Path(__file__).resolve().parents[1] / ".env"


def with_local_groq_key(environment: dict[str, str], path: Path = BACKEND_ENV,
                        *, credential: str = "primary") -> dict[str, str]:
    if credential not in ("primary", "secondary"):
        raise ValueError("Unknown explicit local Groq credential selection")
    if path.is_symlink() or not path.is_file():
        raise ValueError("Local Groq .env unavailable")
    file_stat = path.stat()
    if (file_stat.st_uid != os.geteuid()
            or stat.S_IMODE(file_stat.st_mode) != 0o600):
        raise ValueError("Local Groq .env ownership or mode invalid")
    content = path.read_text(encoding="ascii")
    if not content.endswith("\n") or content.count("\n") not in (1, 2):
        raise ValueError("Local Groq .env format invalid")
    entries = [line.partition("=") for line in content.splitlines()]
    values = {}
    for name, separator, value in entries:
        if (separator != "=" or name not in ("GROQ_API_KEY", "GROQ_SECONDARY_API_KEY")
                or name in values):
            raise ValueError("Local Groq .env format invalid")
        values[name] = value
    if "GROQ_API_KEY" not in values:
        raise ValueError("Original local Groq key is required")
    selected = values.get("GROQ_API_KEY" if credential == "primary" else
                          "GROQ_SECONDARY_API_KEY")
    if credential_shape(selected) != "credential_shape_ok":
        raise ValueError("Selected local Groq credential unavailable or invalid")
    # Explicit selection only; never implicitly try the other account.
    return {**{name: value for name, value in environment.items()
               if name != "GROQ_SECONDARY_API_KEY"}, "GROQ_API_KEY": selected}


def main() -> int:
    args = sys.argv[1:]
    credential = "primary"
    if args[:1] == ["--credential"]:
        if len(args) < 2 or args[1] not in ("primary", "secondary"):
            raise ValueError("Explicit Groq credential must be primary or secondary")
        credential = args[1]
        args = args[2:]
    if args and args[0] == "--":
        args = args[1:]
    if not args:
        raise ValueError("Supply an existing command to run")
    os.execvpe(args[0], args, with_local_groq_key(dict(os.environ),
                                                 credential=credential))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
