"""Read-only offline recheck of a private, pre-provisioned B05 SCRAM trial fixture.

No hosted sender, approval record, database creation or credentials in output.
The provisioner must run separately; this check never makes a Groq request.
"""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import stat

from langgraph.checkpoint.postgres import PostgresSaver
import psycopg

from dealdesk_phase2.graph_state import SPECIALISTS, pinned_from_state
from dealdesk_phase2.groq_typed_final import FINAL_SYSTEM_INSTRUCTION
from dealdesk_phase2.hybrid_pack import _canonical
from dealdesk_phase2.m20_groq import system_instruction
from dealdesk_phase2.orchestrator import build_original_graph
from dealdesk_phase2.phase1c_adapter import PHASE1C_COMMIT, Phase1CAdapter
from dealdesk_phase2.typed_final_hosted import (
    HOSTED_ACTIVATION, _checkpoint_send_lock, _database_identity,
    _history_identity, budgets, inspection_instruction, SCHEMA_SHA256,
    APPROVAL_NAME,
)


def verify(inventory_path):
    inventory_path = inventory_path.resolve(strict=True)
    root = inventory_path.parent
    if (not root.is_relative_to('/tmp/opencode') or root.is_symlink()
            or stat.S_IMODE(root.stat().st_mode) != 0o700
            or inventory_path.name != 'provisioning-evidence.json'
            or HOSTED_ACTIVATION is not False):
        raise ValueError('restricted_preflight_location_or_gate_changed')
    data = json.loads(inventory_path.read_text())
    proposal_path = root / 'b05-proposal-not-authorized.json'
    proposal = json.loads(proposal_path.read_text())
    owner = Path(proposal['execution_context']['owner_directory'])
    if (any(stat.S_IMODE(p.stat().st_mode) != 0o600 for p in (
            inventory_path, proposal_path, Path(data['passfile'])))
            or data['root'] != str(root) or data['socket'] != str(root / 'socket')
            or not Path(data['pgdata'] if 'pgdata' in data else root / 'pgdata').is_dir()
            or owner != root / 'owner' or owner.is_symlink()
            or stat.S_IMODE(owner.stat().st_mode) != 0o700 or list(owner.iterdir())
            or data['phase1c_pin'] != PHASE1C_COMMIT
            or proposal['status'] != 'proposal_not_authorized_not_executable'
            or proposal['account_id'] is not None or proposal['billing_state'] is not None
            or proposal['case'] != data['assessment']
            or proposal['budgets'] != budgets('pricing', 1)
            or (proposal['specialist'], proposal['inspection_plan']) != ('pricing', 1)
            or (root / APPROVAL_NAME).exists()):
        raise ValueError('restricted_preflight_identity_changed')
    for key, text in (('inspection_prompt_sha256', inspection_instruction('pricing')),
                      ('configuration_prompt_sha256', system_instruction('configuration')),
                      ('final_prompt_sha256', FINAL_SYSTEM_INSTRUCTION)):
        if proposal[key] != sha256(text.encode()).hexdigest():
            raise ValueError('restricted_preflight_prompt_changed')
    if proposal['schema_sha256'] != SCHEMA_SHA256:
        raise ValueError('restricted_preflight_schema_changed')
    checkout = Path('/tmp/opencode/dealdesk-phase1c-pinned')
    schema_file = checkout / 'phase-1c-data/implementation/schema.sql'
    fixture_file = Path(__file__).with_name('m18_case_setup.py')
    if (sha256(schema_file.read_bytes()).hexdigest() != data['schema_sha256']
            or sha256(fixture_file.read_bytes()).hexdigest() != data['b05_fixture_sha256']):
        raise ValueError('restricted_preflight_source_changed')
    base = {'host': data['socket'], 'port': data['port'],
            'user': data['runner_role'], 'passfile': data['passfile'],
            'connect_timeout': 5}
    with psycopg.connect(**{**base, 'dbname': data['checkpoint']}) as db:
        if db.execute("SHOW listen_addresses").fetchone() != ('',):
            raise ValueError('restricted_preflight_network_changed')
        role = db.execute('SELECT rolsuper, rolcreatedb, rolcreaterole, '
            'rolreplication, rolcanlogin FROM pg_roles WHERE rolname = current_user').fetchone()
        bootstrap = db.execute('SELECT rolcanlogin FROM pg_roles WHERE rolname = %s',
            (data['bootstrap_role'],)).fetchone()
        grants = dict(db.execute("SELECT datname, "
            "has_database_privilege(current_user, datname, 'CONNECT') "
            "FROM pg_database").fetchall())
        if (role != (False, False, False, False, True) or bootstrap != (False,)
                or {k for k, allowed in grants.items() if allowed} != {
                    data['business'], data['checkpoint']}
                or db.execute("SELECT has_schema_privilege(current_user, 'public', "
                    "'CREATE')").fetchone()[0]):
            raise ValueError('restricted_preflight_role_or_grants_changed')
    hba = (root / 'pgdata' / 'pg_hba.conf').read_text()
    local = [row.split('#')[0].split() for row in hba.splitlines()
             if row.split('#')[0].strip().startswith('local')]
    if not local or any(row[-1] != 'scram-sha-256' for row in local):
        raise ValueError('restricted_preflight_authentication_changed')
    # Explicitly bad password must fail, even over the local socket.
    try:
        with psycopg.connect(**{**base, 'dbname': data['checkpoint'],
                'password': 'definitely-not-the-runner-password'}):
            raise ValueError('restricted_preflight_password_not_required')
    except psycopg.OperationalError as exc:
        if 'password authentication failed' not in str(exc):
            raise
    with psycopg.connect(**{**base, 'dbname': data['business']}) as db:
        if db.execute("SHOW default_transaction_read_only").fetchone() != ('on',):
            raise ValueError('restricted_preflight_business_not_read_only')
        deals = db.execute("SELECT count(*) FROM deal_desk.deals "
            "WHERE deal_id LIKE 'M18-D-%'").fetchone()[0]
        if deals != 1:
            raise ValueError('restricted_preflight_business_reused')
        if db.execute("SELECT has_table_privilege(current_user, 'deal_desk.deals', "
                "'UPDATE')").fetchone()[0]:
            raise ValueError('restricted_preflight_business_write_grant')
        if db.execute("SELECT has_schema_privilege(current_user, 'deal_desk', "
                "'CREATE')").fetchone()[0]:
            raise ValueError('restricted_preflight_business_ddl_grant')
    with psycopg.connect(**{**base, 'dbname': data['checkpoint']}) as db:
        if db.execute("SELECT has_schema_privilege(current_user, 'public', "
                "'CREATE')").fetchone()[0]:
            raise ValueError('restricted_preflight_checkpoint_ddl_grant')
    previous = os.environ.get('LANGGRAPH_STRICT_MSGPACK')
    os.environ['LANGGRAPH_STRICT_MSGPACK'] = 'true'
    try:
        # Admin installed the saver schema before removing bootstrap LOGIN.
        # Do not call saver.setup(): that would require CREATE on public.
        dsn = psycopg.conninfo.make_conninfo(**{**base, 'dbname': data['checkpoint']})
        with PostgresSaver.from_conn_string(dsn) as saver:
            adapter = Phase1CAdapter(checkout)
            graph = build_original_graph(adapter,
                lambda: psycopg.connect(**{**base, 'dbname': data['business']}), saver)
            config = {'configurable': {'thread_id': proposal['case']['assessment_id']}}
            state = graph.get_state(config)
            pinned = pinned_from_state(state.values)
            adapter.validate_pinned_context(pinned)
            if (state.next or state.values.get('stop_reason') or
                    set(state.values['specialist_results']) != set(SPECIALISTS) or
                    state.values['review_status'] != 'needs_revision' or
                    adapter.read_original(graph.phase2_connection_factory,
                        pinned.context.phase1c_run_id,
                        pinned.context.assessment_id).context != pinned.context):
                raise ValueError('restricted_preflight_original_changed')
            _database_identity(graph, proposal, exclusive=True)
            _history_identity(graph, config, proposal,
                sha256(_canonical(proposal).encode()).hexdigest())
            history = list(graph.get_state_history(config))
            if (not history or any(item.values and any(item.values.get(key) for key in (
                    'typed_final_hosted_start', 'typed_final_attempts',
                    'm20_model_attempts', 'm21_model_attempts',
                    'hybrid_investigation_start')) for item in history)):
                raise ValueError('restricted_preflight_prior_attempt')
            with _checkpoint_send_lock(graph):
                pass  # Check DB grant for runtime's exact lock; no provider send.
            counts = {table: saver.conn.execute('SELECT count(*) AS n FROM public.' +
                table).fetchone()['n'] for table in (
                    'checkpoints', 'checkpoint_writes', 'checkpoint_blobs')}
    finally:
        if previous is None:
            os.environ.pop('LANGGRAPH_STRICT_MSGPACK', None)
        else:
            os.environ['LANGGRAPH_STRICT_MSGPACK'] = previous
    if counts != data['checkpoint_counts'] or len(history) != data['history_length']:
        raise ValueError('restricted_preflight_checkpoint_changed')
    return {'assessment_id': proposal['case']['assessment_id'],
        'databases': data['created_databases'], 'checkpoint_counts': counts,
        'history_length': len(history), 'fixed_review': 'needs_revision',
        'runner_role': data['runner_role'], 'bootstrap_login_disabled': True,
        'authentication': 'local_scram_no_tcp', 'private_ci': 'exception_not_pass',
        'manifest_sha256': None, 'proposal_sha256_not_authorization':
        sha256(_canonical(proposal).encode()).hexdigest(),
        'hosted_activation': False, 'provider_requests': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, required=True)
    print(json.dumps(verify(parser.parse_args().inventory), sort_keys=True))
