"""Explicit disposable synthetic API fixture setup; never invoked by the API."""

import argparse
import os
from pathlib import Path
import subprocess
import sys
from tempfile import NamedTemporaryFile
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from dealdesk_phase2.phase1c_adapter import PHASE1C_COMMIT
from m18_case_setup import install_disposable_cases
from m21_integrated_credit_setup import install_integrated_credit
from run_week4_disposable import require_disposable_cluster


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cluster-dsn", required=True)
    parser.add_argument("--phase1c", type=Path, required=True)
    parser.add_argument("--pg-bin", type=Path, required=True)
    parser.add_argument("--pg-lib", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    args = parser.parse_args()
    require_disposable_cluster(args.cluster_dsn)
    checkout = args.phase1c.resolve()
    if subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"],
                               text=True).strip() != PHASE1C_COMMIT:
        raise ValueError("Pinned Phase 1C checkout required")
    if (not args.pg_bin.resolve().is_relative_to("/tmp/opencode") or
            not args.pg_lib.resolve().is_relative_to("/tmp/opencode") or
            not (args.pg_bin / "psql").is_file()):
        raise ValueError("Disposable PostgreSQL tools required")
    env_file = args.env_file.resolve()
    if not env_file.is_relative_to("/tmp/opencode"):
        raise ValueError("Owner-only environment file must be in /tmp/opencode")
    # Claim output before creating databases, so a failed file claim changes nothing.
    fd = os.open(env_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    os.close(fd)
    tag = "demo_api_" + uuid4().hex[:12]
    business, checkpoint = tag + "_business", tag + "_checkpoint"
    parts = conninfo_to_dict(args.cluster_dsn)
    base = {k: v for k, v in parts.items() if k != "dbname"}
    business_dsn = make_conninfo(**base, dbname=business)
    checkpoint_dsn = make_conninfo(**base, dbname=checkpoint)
    with psycopg.connect(args.cluster_dsn, autocommit=True) as db:
        for name in (business, checkpoint):
            db.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    impl = checkout / "phase-1c-data" / "implementation"
    with psycopg.connect(business_dsn) as db:
        db.execute((impl / "schema.sql").read_text())
    env = {**os.environ, "PATH": str(args.pg_bin.resolve()) + os.pathsep +
        os.environ.get("PATH", ""), "LD_LIBRARY_PATH": str(args.pg_lib.resolve()),
        "DATABASE_URL": business_dsn, "PGHOST": "/tmp/opencode",
        "PGPORT": parts.get("port", "5432"), "PGDATABASE": business,
        "PGUSER": parts.get("user", "ubuntu"), "TMPDIR": "/tmp/opencode"}
    subprocess.run([sys.executable, "-c", "from test_phase1c_reader import "
                    "load_fixture_rows;load_fixture_rows()"], cwd=impl, env=env,
                   check=True, stdout=subprocess.DEVNULL)
    with NamedTemporaryFile(dir="/tmp/opencode", suffix=".sql") as rules:
        subprocess.run([sys.executable, "compile_phase1c_policy.py", "--output", rules.name],
            cwd=impl, env=env, check=True, stdout=subprocess.DEVNULL)
        with psycopg.connect(business_dsn) as db:
            db.execute(Path(rules.name).read_text())
    with psycopg.connect(business_dsn) as db:
        install_disposable_cases(db)
    for case, variant in (("B01", "RC01"), ("N01", "UC02")):
        with psycopg.connect(business_dsn) as db:
            install_integrated_credit(db, case_id=case, variant=variant)
    with psycopg.connect(checkpoint_dsn) as db:
        db.execute((Path(__file__).parents[1] / "migrations" /
                    "001_demo_assessment_registry.sql").read_text())
    with open(env_file, "w") as output:
        for key, value in (("DEALDESK_DEMO_BUSINESS_DSN", business_dsn),
                           ("DEALDESK_DEMO_CHECKPOINT_DSN", checkpoint_dsn),
                           ("DEALDESK_PHASE1C_CHECKOUT", str(checkout))):
            output.write(f"export {key}='{value}'\n")
    print("Disposable API fixture ready; owner-only environment:", env_file)


if __name__ == "__main__":
    main()
