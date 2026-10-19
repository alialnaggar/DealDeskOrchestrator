"""M1.1 PostgreSQL checkpoint lifecycle. Use a dedicated thesis test database."""

from contextlib import contextmanager
import os

from langgraph.checkpoint.postgres import PostgresSaver


@contextmanager
def thesis_checkpointer(dsn: str):
    if not dsn:
        raise ValueError("Dedicated checkpoint database URL required")
    # Our graph state contains only primitive Python/JSON values. Disallow
    # importing arbitrary Python objects while deserializing checkpoint data.
    previous = os.environ.get("LANGGRAPH_STRICT_MSGPACK")
    os.environ["LANGGRAPH_STRICT_MSGPACK"] = "true"
    try:
        with PostgresSaver.from_conn_string(dsn) as saver:
            saver.setup()
            yield saver
    finally:
        if previous is None:
            os.environ.pop("LANGGRAPH_STRICT_MSGPACK", None)
        else:
            os.environ["LANGGRAPH_STRICT_MSGPACK"] = previous
