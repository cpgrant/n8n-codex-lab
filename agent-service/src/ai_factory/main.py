"""FastAPI application for AI Strategy Factory v0.1."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator
from uuid import UUID, uuid4

from fastapi import FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse

from .artifacts import MarkdownArtifactStore, sha256_text
from .config import REPOSITORY_ROOT, Settings
from .database import initialize_database
from .errors import FactoryError
from .idempotency import (
    IdempotencyRepository,
    canonical_json_hash,
    validate_idempotency_key,
)
from .providers import (
    FakeStrategyProvider,
    OllamaQualityCritic,
    OllamaStrategyProvider,
    OpenAIStrategyProvider,
    StrategyProvider,
)
from .quality_service import QualityCritic, QualityReportService
from .repository import RunNotFound, RunRecord, RunRepository
from .review_service import ReviewService
from .schemas import (
    ArtifactMetadata,
    CreateRunData,
    HealthResponse,
    QualityReport,
    QualityReportData,
    ReadRunData,
    ReviewRecord,
    ReviewRequest,
    ReviewRunData,
    StrategyBrief,
    StrategyResponse,
)
from .service import StrategyService

CREATE_OPERATION = "create_strategy_run"


def error_response(error: FactoryError, request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": error.public_body(),
            "meta": {"request_id": request_id},
        },
    )


def create_run_data(record: RunRecord) -> dict[str, object]:
    if record.strategy is None:
        raise RuntimeError("completed generation has no strategy")
    return CreateRunData(
        run_id=record.run_id,
        status=record.status,
        strategy=StrategyResponse.model_validate(record.strategy),
        created_at=record.created_at,
        updated_at=record.updated_at,
    ).model_dump(mode="json")


def read_run_data(record: RunRecord) -> dict[str, object]:
    return ReadRunData(
        run_id=record.run_id,
        status=record.status,
        brief=StrategyBrief.model_validate(record.brief),
        strategy=(
            StrategyResponse.model_validate(record.strategy)
            if record.strategy is not None
            else None
        ),
        quality_report=(
            QualityReport.model_validate(record.quality_report)
            if record.quality_report is not None
            else None
        ),
        review=(
            ReviewRecord.model_validate(record.review)
            if record.review is not None
            else None
        ),
        artifact=(
            ArtifactMetadata.model_validate(record.artifact)
            if record.artifact is not None
            else None
        ),
        error_code=record.error_code,
        error_message=record.error_message,
        created_at=record.created_at,
        updated_at=record.updated_at,
    ).model_dump(mode="json")


def review_run_data(record: RunRecord) -> dict[str, object]:
    if record.review is None:
        raise RuntimeError("reviewed run has no review record")
    return ReviewRunData(
        run_id=record.run_id,
        status=record.status,
        review=ReviewRecord.model_validate(record.review),
        artifact=(
            ArtifactMetadata.model_validate(record.artifact)
            if record.artifact is not None
            else None
        ),
    ).model_dump(mode="json")


def quality_report_data(record: RunRecord) -> dict[str, object]:
    if record.quality_report is None:
        raise RuntimeError("quality report operation has no stored report")
    return QualityReportData(
        run_id=record.run_id,
        status=record.status,
        quality_report=QualityReport.model_validate(record.quality_report),
    ).model_dump(mode="json")


def default_provider(settings: Settings) -> StrategyProvider:
    if settings.provider == "openai":
        return OpenAIStrategyProvider()
    if settings.provider == "ollama":
        return OllamaStrategyProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
        )
    fixture = REPOSITORY_ROOT / "examples/strategy-response.synthetic.json"
    return FakeStrategyProvider.from_fixture(fixture)


def default_quality_critic(settings: Settings) -> QualityCritic | None:
    if settings.quality_mode == "basic":
        return None
    return OllamaQualityCritic(
        base_url=settings.ollama_base_url,
        model=settings.ollama_quality_model,
        timeout_seconds=settings.ollama_timeout_seconds,
    )


def create_app(
    settings: Settings | None = None,
    provider: StrategyProvider | None = None,
    quality_critic: QualityCritic | None = None,
) -> FastAPI:
    resolved = settings or Settings.from_env()
    resolved_provider = provider or default_provider(resolved)
    resolved_quality_critic = quality_critic or default_quality_critic(resolved)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        resolved.data_dir.mkdir(parents=True, exist_ok=True)
        resolved.artifact_dir.mkdir(parents=True, exist_ok=True)
        initialize_database(resolved.database_path)
        app.state.settings = resolved
        app.state.repository = RunRepository(resolved.database_path)
        app.state.idempotency = IdempotencyRepository(resolved.database_path)
        app.state.service = StrategyService(app.state.repository, resolved_provider)
        app.state.quality_service = QualityReportService(
            app.state.repository,
            mode=resolved.quality_mode,
            critic=resolved_quality_critic,
        )
        app.state.artifact_store = MarkdownArtifactStore(resolved.artifact_dir)
        app.state.review_service = ReviewService(
            app.state.repository, app.state.artifact_store
        )
        yield

    app = FastAPI(
        title="AI Strategy Factory",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or f"req_{uuid4().hex}"
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(FactoryError)
    async def factory_error_handler(
        request: Request, error: FactoryError
    ) -> JSONResponse:
        return error_response(error, request.state.request_id)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        details = [
            {
                "field": ".".join(str(part) for part in item["loc"] if part != "body"),
                "reason": item["msg"],
            }
            for item in error.errors()
        ]
        return error_response(
            FactoryError(
                400,
                "VALIDATION_ERROR",
                "The request did not satisfy the strategy brief contract.",
                details=details,
            ),
            request.state.request_id,
        )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse()

    @app.post("/v1/strategy-runs", status_code=201)
    def create_strategy_run(
        brief: StrategyBrief,
        request: Request,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> JSONResponse:
        key = validate_idempotency_key(idempotency_key)
        request_hash = canonical_json_hash(brief.model_dump(mode="json"))
        idempotency: IdempotencyRepository = request.app.state.idempotency
        replay = idempotency.reserve(CREATE_OPERATION, key, request_hash)
        if replay is not None:
            content = dict(replay.payload)
            content["meta"] = {
                "request_id": request.state.request_id,
                "idempotent_replay": True,
            }
            return JSONResponse(status_code=replay.status_code, content=content)

        try:
            record = request.app.state.service.create_run(brief)
            stored_payload: dict[str, object] = {"data": create_run_data(record)}
            idempotency.complete(
                CREATE_OPERATION,
                key,
                request_hash,
                201,
                stored_payload,
                record.run_id,
            )
            return JSONResponse(
                status_code=201,
                content={
                    **stored_payload,
                    "meta": {
                        "request_id": request.state.request_id,
                        "idempotent_replay": False,
                    },
                },
            )
        except FactoryError as error:
            stored_payload = {"error": error.public_body()}
            idempotency.complete(
                CREATE_OPERATION,
                key,
                request_hash,
                error.status_code,
                stored_payload,
                error.run_id,
            )
            return JSONResponse(
                status_code=error.status_code,
                content={
                    **stored_payload,
                    "meta": {
                        "request_id": request.state.request_id,
                        "idempotent_replay": False,
                    },
                },
            )
        except Exception as exc:
            error = FactoryError(
                500,
                "INTERNAL_ERROR",
                "An unexpected internal error occurred.",
                retryable=True,
            )
            stored_payload = {"error": error.public_body()}
            idempotency.complete(
                CREATE_OPERATION,
                key,
                request_hash,
                error.status_code,
                stored_payload,
                None,
            )
            return JSONResponse(
                status_code=error.status_code,
                content={
                    **stored_payload,
                    "meta": {
                        "request_id": request.state.request_id,
                        "idempotent_replay": False,
                    },
                },
            )

    @app.get("/v1/strategy-runs/{run_id}")
    def get_strategy_run(run_id: UUID, request: Request) -> dict[str, object]:
        try:
            record = request.app.state.repository.get(run_id)
        except RunNotFound as exc:
            raise FactoryError(
                404,
                "RUN_NOT_FOUND",
                "The requested strategy run does not exist.",
            ) from exc
        return {
            "data": read_run_data(record),
            "meta": {"request_id": request.state.request_id},
        }

    @app.post("/v1/strategy-runs/{run_id}/quality-report")
    def create_quality_report(
        run_id: UUID,
        request: Request,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> JSONResponse:
        key = validate_idempotency_key(idempotency_key)
        settings: Settings = request.app.state.settings
        request_hash = canonical_json_hash(
            {
                "run_id": str(run_id),
                "mode": settings.quality_mode,
                "critic_model": (
                    settings.ollama_quality_model
                    if settings.quality_mode == "pro"
                    else None
                ),
            }
        )
        operation = f"create_quality_report:{run_id}"
        idempotency: IdempotencyRepository = request.app.state.idempotency
        replay = idempotency.reserve(operation, key, request_hash)
        if replay is not None:
            content = dict(replay.payload)
            content["meta"] = {
                "request_id": request.state.request_id,
                "idempotent_replay": True,
            }
            return JSONResponse(status_code=replay.status_code, content=content)

        try:
            record = request.app.state.quality_service.create_report(run_id)
            stored_payload: dict[str, object] = {
                "data": quality_report_data(record)
            }
            idempotency.complete(
                operation, key, request_hash, 200, stored_payload, run_id
            )
            return JSONResponse(
                status_code=200,
                content={
                    **stored_payload,
                    "meta": {
                        "request_id": request.state.request_id,
                        "idempotent_replay": False,
                    },
                },
            )
        except FactoryError as error:
            if error.retryable:
                idempotency.release(operation, key, request_hash)
            else:
                idempotency.complete(
                    operation,
                    key,
                    request_hash,
                    error.status_code,
                    {"error": error.public_body()},
                    error.run_id,
                )
            return JSONResponse(
                status_code=error.status_code,
                content={
                    "error": error.public_body(),
                    "meta": {
                        "request_id": request.state.request_id,
                        "idempotent_replay": False,
                    },
                },
            )
        except Exception:
            idempotency.release(operation, key, request_hash)
            error = FactoryError(
                500,
                "INTERNAL_ERROR",
                "An unexpected internal error occurred.",
                run_id=run_id,
                retryable=True,
            )
            return JSONResponse(
                status_code=error.status_code,
                content={
                    "error": error.public_body(),
                    "meta": {
                        "request_id": request.state.request_id,
                        "idempotent_replay": False,
                    },
                },
            )

    @app.get("/v1/strategy-runs/{run_id}/quality-report")
    def get_quality_report(run_id: UUID, request: Request) -> dict[str, object]:
        try:
            record = request.app.state.repository.get(run_id)
        except RunNotFound as exc:
            raise FactoryError(
                404,
                "RUN_NOT_FOUND",
                "The requested strategy run does not exist.",
            ) from exc
        if record.quality_report is None:
            raise FactoryError(
                409,
                "QUALITY_REPORT_NOT_READY",
                "The strategy run does not have a quality report.",
                run_id=run_id,
            )
        return {
            "data": quality_report_data(record),
            "meta": {"request_id": request.state.request_id},
        }

    @app.post("/v1/strategy-runs/{run_id}/review")
    def review_strategy_run(
        run_id: UUID,
        review: ReviewRequest,
        request: Request,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> JSONResponse:
        key = validate_idempotency_key(idempotency_key)
        request_hash = canonical_json_hash(review.model_dump(mode="json"))
        operation = f"review_strategy_run:{run_id}"
        idempotency: IdempotencyRepository = request.app.state.idempotency
        replay = idempotency.reserve(operation, key, request_hash)
        if replay is not None:
            content = dict(replay.payload)
            content["meta"] = {
                "request_id": request.state.request_id,
                "idempotent_replay": True,
            }
            return JSONResponse(status_code=replay.status_code, content=content)

        try:
            record = request.app.state.review_service.review_run(run_id, review)
            stored_payload: dict[str, object] = {"data": review_run_data(record)}
            idempotency.complete(
                operation, key, request_hash, 200, stored_payload, run_id
            )
            return JSONResponse(
                status_code=200,
                content={
                    **stored_payload,
                    "meta": {
                        "request_id": request.state.request_id,
                        "idempotent_replay": False,
                    },
                },
            )
        except FactoryError as error:
            if error.code == "ARTIFACT_RENDER_FAILED":
                idempotency.release(operation, key, request_hash)
            else:
                idempotency.complete(
                    operation,
                    key,
                    request_hash,
                    error.status_code,
                    {"error": error.public_body()},
                    error.run_id,
                )
            return JSONResponse(
                status_code=error.status_code,
                content={
                    "error": error.public_body(),
                    "meta": {
                        "request_id": request.state.request_id,
                        "idempotent_replay": False,
                    },
                },
            )
        except Exception:
            error = FactoryError(
                500,
                "INTERNAL_ERROR",
                "An unexpected internal error occurred.",
                run_id=run_id,
                retryable=True,
            )
            idempotency.complete(
                operation,
                key,
                request_hash,
                error.status_code,
                {"error": error.public_body()},
                run_id,
            )
            return JSONResponse(
                status_code=error.status_code,
                content={
                    "error": error.public_body(),
                    "meta": {
                        "request_id": request.state.request_id,
                        "idempotent_replay": False,
                    },
                },
            )

    @app.get("/v1/strategy-runs/{run_id}/artifact")
    def get_strategy_artifact(run_id: UUID, request: Request) -> PlainTextResponse:
        try:
            record = request.app.state.repository.get(run_id)
        except RunNotFound as exc:
            raise FactoryError(
                404,
                "RUN_NOT_FOUND",
                "The requested strategy run does not exist.",
            ) from exc
        if record.artifact is None:
            raise FactoryError(
                409,
                "ARTIFACT_NOT_READY",
                "The strategy run does not have an approved artifact.",
                run_id=run_id,
            )
        metadata = ArtifactMetadata.model_validate(record.artifact)
        try:
            path = request.app.state.artifact_store.path_for(run_id, metadata)
            content = path.read_text(encoding="utf-8")
        except (OSError, ValueError) as exc:
            raise FactoryError(
                500,
                "INTERNAL_ERROR",
                "The approved strategy artifact is unavailable.",
                run_id=run_id,
                retryable=True,
            ) from exc
        if sha256_text(content) != metadata.checksum:
            raise FactoryError(
                500,
                "INTERNAL_ERROR",
                "The approved strategy artifact failed its integrity check.",
                run_id=run_id,
                retryable=False,
            )
        return PlainTextResponse(
            content,
            media_type=metadata.media_type,
            headers={
                "Content-Disposition": f'inline; filename="{metadata.filename}"'
            },
        )

    return app


app = create_app()
