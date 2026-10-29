"""Provision two new local disposable PostgreSQL DBs and run Week 4 offline.

Prerequisites: locked backend venv, already-running test PostgreSQL and a
separate exact pinned Phase 1C checkout. No service installation or cleanup.
The explicitly supplied cluster must use /tmp/opencode socket/data directory.
"""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import NamedTemporaryFile

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from dealdesk_phase2.phase1c_adapter import PHASE1C_COMMIT, Phase1CAdapter
from m18_case_setup import install_disposable_cases
from run_week4_development import report, run


def require_disposable_cluster(dsn):
    parts = conninfo_to_dict(dsn)
    if parts.get("host") != "/tmp/opencode" or parts.get("dbname") != "postgres":
        raise ValueError("Expected explicit /tmp/opencode PostgreSQL socket and postgres database")
    with psycopg.connect(dsn) as db:
        directory, addr = db.execute("SELECT current_setting('data_directory'), "
            "inet_server_addr()").fetchone()
    if not Path(directory).resolve().is_relative_to("/tmp/opencode") or addr is not None:
        raise ValueError("Only local /tmp/opencode disposable PostgreSQL cluster allowed")


def provision_and_run(dsn, checkout, output_json, output_md, pg_bin, pg_lib):
    require_disposable_cluster(dsn)
    pg_bin = pg_bin.resolve()
    if not pg_bin.is_relative_to("/tmp/opencode") or not (pg_bin / "psql").is_file():
        raise ValueError("Explicit local /tmp/opencode PostgreSQL psql directory required")
    pg_lib = pg_lib.resolve()
    if not pg_lib.is_relative_to("/tmp/opencode") or not (pg_lib / "libpq.so.5").exists():
        raise ValueError("Explicit local /tmp/opencode PostgreSQL shared libraries required")
    checkout = checkout.resolve()
    commit = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"],
                                     text=True).strip()
    if commit != PHASE1C_COMMIT:
        raise ValueError("Phase 1C checkout is not the exact authorized pin")
    dirty = subprocess.check_output(["git", "-C", str(checkout), "status", "--porcelain"],
                                    text=True).splitlines()
    if any(not line.startswith("?? phase-1c-data/implementation/__pycache__/")
           for line in dirty):
        raise ValueError("Pinned Phase 1C checkout is modified")
    from uuid import uuid4
    suffix = uuid4().hex[:12]
    business, checkpoint = ("recovery_" + suffix + "_m20",
                            "recovery_" + suffix + "_m20_checkpoint")
    admin = conninfo_to_dict(dsn)
    admin.pop("dbname")
    with psycopg.connect(dsn, autocommit=True) as db:
        for name in (business, checkpoint):
            db.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    business_dsn = make_conninfo(**admin, dbname=business)
    checkpoint_dsn = make_conninfo(**admin, dbname=checkpoint)
    impl = checkout / "phase-1c-data" / "implementation"
    with psycopg.connect(business_dsn) as db:
        db.execute((impl / "schema.sql").read_text())
        db.commit()
    env = os.environ.copy()
    env["PATH"] = str(pg_bin) + os.pathsep + env.get("PATH", "")
    env["LD_LIBRARY_PATH"] = str(pg_lib) + os.pathsep + env.get("LD_LIBRARY_PATH", "")
    env["TMPDIR"] = "/tmp/opencode"
    env.update({"DATABASE_URL": business_dsn, "PGHOST": "/tmp/opencode",
                "PGDATABASE": business, "PGPORT": str(admin.get("port", 5432))})
    if admin.get("user"):
        env["PGUSER"] = admin["user"]
    subprocess.run([sys.executable, "-c", "from test_phase1c_reader import "
                    "load_fixture_rows; load_fixture_rows()"],
                   cwd=impl, env=env, check=True, stdout=subprocess.DEVNULL)
    with NamedTemporaryFile(dir="/tmp/opencode", prefix="dealdesk-w4-rules-", suffix=".sql") as tmp:
        subprocess.run([sys.executable, "compile_phase1c_policy.py", "--output", tmp.name],
                       cwd=impl, env=env, check=True, stdout=subprocess.DEVNULL)
        with psycopg.connect(business_dsn) as db:
            db.execute(Path(tmp.name).read_text())
            db.commit()
    with psycopg.connect(business_dsn) as db:
        install_disposable_cases(db)
    adapter = Phase1CAdapter(checkout)
    result = run(lambda: psycopg.connect(business_dsn), checkpoint_dsn, adapter)
    # Never put DB credentials, connection strings or owner secrets in artifacts.
    result["disposable_setup"] = {"business_database": business,
        "checkpoint_database": checkpoint, "phase1c_pin": commit}
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    output_md.write_text(report(result))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cluster-dsn", required=True,
                        help="Local test cluster admin DSN, dbname=postgres, host=/tmp/opencode")
    parser.add_argument("--phase1c", required=True, type=Path)
    parser.add_argument("--pg-bin", required=True, type=Path,
                        help="Local /tmp/opencode PostgreSQL bin directory containing psql")
    parser.add_argument("--pg-lib", required=True, type=Path,
                        help="Local /tmp/opencode PostgreSQL shared library directory")
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()
    provision_and_run(args.cluster_dsn, args.phase1c, args.json, args.markdown,
                      args.pg_bin, args.pg_lib)


if __name__ == "__main__":
    main()
