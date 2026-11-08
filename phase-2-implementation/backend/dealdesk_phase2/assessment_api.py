"""Loopback-only, offline synthetic assessment HTTP API. No hosted model routes."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime
import hmac
import os
from pathlib import Path
import re

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
import psycopg
from psycopg.conninfo import conninfo_to_dict
from starlette.responses import JSONResponse

from .assessment_service import AssessmentService, SCENARIOS
from .assessment_store import Conflict, NotFound
from .phase1c_adapter import EvidenceMismatch, PHASE1C_COMMIT


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class CreateRequest(_Strict):
    scenario: str = Field(min_length=1, max_length=40)


class StatusResponse(_Strict):
    version: Literal["demo-api-v1"]
    assessment_id: str
    scenario: str
    mode: str
    status: str
    last_sequence: int
    phase1c_pin: str


class CreateResponse(StatusResponse):
    created: bool


class EventResponse(_Strict):
    assessment_id: str
    sequence: int
    occurred_at: datetime
    kind: str
    stage: str | None


class EventsResponse(_Strict):
    version: Literal["demo-api-v1"]
    assessment_id: str
    events: list[EventResponse]


def create_app(service: AssessmentService, tokens: dict[str, str]) -> FastAPI:
    if (not tokens or any(not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", owner)
            or len(token) < 32 or len(token) > 256 for token, owner in tokens.items())
            or len(set(tokens.values())) != len(tokens)):
        raise ValueError("Configured operator tokens and distinct owners required")
    executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="offline-assessment")

    @asynccontextmanager
    async def lifespan(_app):
        with psycopg.connect(service.checkpoint_dsn, autocommit=True) as lock:
            # One API owner per registry, across processes, not merely per worker.
            if not lock.execute("SELECT pg_try_advisory_lock(847276142)").fetchone()[0]:
                raise RuntimeError("Another offline API already owns the registry")
            service.store.mark_interrupted()  # Never resume a lost worker/send.
            try:
                yield
            finally:
                executor.shutdown(wait=True, cancel_futures=True)

    app = FastAPI(title="Deal Desk offline demo", version="demo-api-v1",
                  docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_request, _error):
        # FastAPI's default error includes rejected input (possibly a credential).
        return JSONResponse({"detail": "Invalid request"}, status_code=422)

    @app.exception_handler(psycopg.Error)
    async def unavailable_database(_request, _error):
        # Connection/SQL exceptions may contain a DSN or source details. A lost
        # worker is never resumed here; startup marks interrupted runs uncertain.
        return JSONResponse({"detail": "Local assessment storage unavailable"}, status_code=503)

    @app.middleware("http")
    async def bounded_request(request: Request, call_next):
        if request.headers.get("host") != "127.0.0.1:8765":
            return JSONResponse({"detail": "Invalid local host"}, status_code=400,
                                headers={"Cache-Control": "no-store"})
        size = request.headers.get("content-length")
        if (size is None and request.method == "POST") or (size is not None and
                (not size.isdecimal() or int(size) > 512)):
            return JSONResponse({"detail": "Request too large"}, status_code=413,
                                headers={"Cache-Control": "no-store"})
        if request.method == "POST":
            chunks = bytearray()
            async for chunk in request.stream():
                chunks.extend(chunk)
                if len(chunks) > 512:
                    return JSONResponse({"detail": "Request too large"}, status_code=413,
                                        headers={"Cache-Control": "no-store"})
            request._body = bytes(chunks)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    def owner(authorization: str = Header(default="")):
        supplied = authorization.removeprefix("Bearer ") if authorization.startswith(
            "Bearer ") else ""
        result = None
        for token, identity in tokens.items():
            if hmac.compare_digest(supplied, token) and supplied:
                result = identity
        if result is None:
            raise HTTPException(status_code=401, detail="Unauthorized",
                                headers={"WWW-Authenticate": "Bearer"})
        return result

    def row(owner_id, assessment_id, *, check_completed=True):
        try:
            record = service.store.get(owner_id, assessment_id)
        except NotFound:
            raise HTTPException(status_code=404, detail="Assessment not found") from None
        except EvidenceMismatch:
            raise HTTPException(status_code=409, detail="Assessment registry invalid") from None
        expected = SCENARIOS.get(record["scenario"])
        if (expected is None or record["run_id"] != expected[0] or
                record["source_deal_id"] != expected[1] or
                record["status"] == "completed" and (
                    not record["bundle_sha256"] or not record["source_input_digest"])):
            raise HTTPException(status_code=409, detail="Assessment registry invalid")
        if check_completed and record["status"] == "completed":
            try:
                service.review(owner_id, assessment_id)
            except (Conflict, EvidenceMismatch, KeyError, TypeError, ValueError):
                raise HTTPException(status_code=409, detail="Completed evidence unavailable") from None
        return record

    def status(record):
        return {"version": "demo-api-v1", "assessment_id": record["assessment_id"],
                "scenario": record["scenario"],
                "mode": "offline_scripted", "status": record["status"],
                "last_sequence": record["last_sequence"], "phase1c_pin": PHASE1C_COMMIT}

    def run(assessment_id):
        try:
            service.run(assessment_id)
        except Exception:
            # Failure metadata is stored as an allowlisted status/event, never logged here.
            pass

    @app.post("/demo/assessments", response_model=CreateResponse, status_code=202)
    def create(body: CreateRequest, idempotency_key: str = Header(alias="Idempotency-Key"),
               owner_id: str = Depends(owner)):
        if body.scenario not in SCENARIOS:
            raise HTTPException(status_code=422, detail="Unsupported synthetic scenario")
        try:
            assessment_id, fresh = service.create(owner_id, idempotency_key,
                body.scenario, lambda ident: executor.submit(run, ident))
        except Conflict:
            raise HTTPException(status_code=409, detail="Idempotency conflict") from None
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid request") from None
        return {**status(row(owner_id, assessment_id)), "status": "accepted" if fresh
                else row(owner_id, assessment_id)["status"], "created": fresh}

    @app.get("/demo/assessments/{assessment_id}", response_model=StatusResponse)
    def get(assessment_id: str, owner_id: str = Depends(owner)):
        return status(row(owner_id, assessment_id))

    @app.get("/demo/assessments/{assessment_id}/events", response_model=EventsResponse)
    def events(assessment_id: str, after: int = Query(default=0, ge=0, le=9223372036854775807),
               owner_id: str = Depends(owner)):
        row(owner_id, assessment_id)
        return {"version": "demo-api-v1", "assessment_id": assessment_id,
                "events": service.store.events(owner_id, assessment_id, after)}

    @app.get("/demo/assessments/{assessment_id}/review")
    def review(assessment_id: str, owner_id: str = Depends(owner)):
        row(owner_id, assessment_id, check_completed=False)
        try:
            return service.review(owner_id, assessment_id)
        except Conflict:
            raise HTTPException(status_code=409, detail="Review not ready") from None
        except (EvidenceMismatch, KeyError, TypeError, ValueError):
            raise HTTPException(status_code=409, detail="Review evidence unavailable") from None

    return app


def _disposable(dsn):
    parts = conninfo_to_dict(dsn)
    if parts.get("host") != "/tmp/opencode" or parts.get("dbname") in (None, "postgres"):
        raise ValueError("Dedicated local disposable database required")
    with psycopg.connect(dsn) as db:
        directory, address = db.execute("SELECT current_setting('data_directory'), inet_server_addr()").fetchone()
    if address is not None or not Path(directory).resolve().is_relative_to("/tmp/opencode"):
        raise ValueError("Non-disposable PostgreSQL cluster refused")


def create_app_from_env():
    token = os.environ["DEALDESK_DEMO_TOKEN"]
    identity = os.environ["DEALDESK_DEMO_OWNER"]
    business = os.environ["DEALDESK_DEMO_BUSINESS_DSN"]
    checkpoint = os.environ["DEALDESK_DEMO_CHECKPOINT_DSN"]
    checkout = Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]).resolve()
    if business == checkpoint or len(token) < 32 or not identity.isascii() or not identity:
        raise ValueError("Separate disposable databases and long operator token required")
    business_name = conninfo_to_dict(business).get("dbname", "")
    checkpoint_name = conninfo_to_dict(checkpoint).get("dbname", "")
    if (not re.fullmatch(r"demo_api_[0-9a-f]{12}_business", business_name) or
            checkpoint_name != business_name.removesuffix("_business") + "_checkpoint"):
        raise ValueError("Dedicated matching demo fixture databases required")
    _disposable(business)
    _disposable(checkpoint)
    service = AssessmentService(business, checkpoint, checkout)
    return create_app(service, {token: identity})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(create_app_from_env(), host="127.0.0.1", port=8765,
                workers=1, access_log=False)
