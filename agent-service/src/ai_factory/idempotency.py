"""SQLite/PostgreSQL-portable idempotency reservations and response replay."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from uuid import UUID

from sqlalchemy import Engine, text
from sqlalchemy.exc import IntegrityError

from .database import engine_for_target, sqlite_path_for_target
from .errors import FactoryError
from .repository import utc_now

DatabaseTarget = Path | str | Engine


def canonical_json_hash(payload: dict[str, object]) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def validate_idempotency_key(value: str | None) -> str:
    if value is None:
        raise FactoryError(
            400,
            "IDEMPOTENCY_KEY_REQUIRED",
            "Idempotency-Key is required for this operation.",
        )
    if not 8 <= len(value) <= 255 or not value.isprintable():
        raise FactoryError(
            400,
            "IDEMPOTENCY_KEY_REQUIRED",
            "Idempotency-Key must contain 8-255 printable characters.",
        )
    return value


@dataclass(frozen=True)
class IdempotencyReplay:
    status_code: int
    payload: dict[str, object]


class IdempotencyRepository:
    def __init__(self, database: DatabaseTarget) -> None:
        self.engine = engine_for_target(database)
        self.database_path = sqlite_path_for_target(self.engine)

    @staticmethod
    def _existing_result(
        row: Mapping[str, Any], request_hash: str
    ) -> IdempotencyReplay:
        if row["request_hash"] != request_hash:
            raise FactoryError(
                409,
                "IDEMPOTENCY_CONFLICT",
                "The idempotency key was already used with different input.",
            )
        if row["state"] == "pending":
            raise FactoryError(
                409,
                "IDEMPOTENCY_IN_PROGRESS",
                "An operation with this idempotency key is still in progress.",
                retryable=True,
            )
        return IdempotencyReplay(
            status_code=int(row["response_status"]),
            payload=json.loads(row["response_json"]),
        )

    def _get_existing(
        self, operation: str, key: str
    ) -> Mapping[str, Any] | None:
        with self.engine.connect() as connection:
            return connection.execute(
                text(
                    """
                    SELECT * FROM idempotency_requests
                    WHERE operation = :operation AND idempotency_key = :key
                    """
                ),
                {"operation": operation, "key": key},
            ).mappings().first()

    def reserve(
        self, operation: str, key: str, request_hash: str
    ) -> IdempotencyReplay | None:
        parameters = {"operation": operation, "key": key}
        try:
            with self.engine.begin() as connection:
                row = connection.execute(
                    text(
                        """
                        SELECT * FROM idempotency_requests
                        WHERE operation = :operation AND idempotency_key = :key
                        """
                    ),
                    parameters,
                ).mappings().first()
                if row is not None:
                    return self._existing_result(row, request_hash)
                timestamp = utc_now()
                connection.execute(
                    text(
                        """
                        INSERT INTO idempotency_requests (
                            operation, idempotency_key, request_hash, state,
                            created_at, updated_at
                        ) VALUES (
                            :operation, :key, :request_hash, 'pending',
                            :created_at, :updated_at
                        )
                        """
                    ),
                    {
                        **parameters,
                        "request_hash": request_hash,
                        "created_at": timestamp,
                        "updated_at": timestamp,
                    },
                )
                return None
        except IntegrityError:
            row = self._get_existing(operation, key)
            if row is None:
                raise RuntimeError("idempotency reservation conflict was lost")
            return self._existing_result(row, request_hash)

    def complete(
        self,
        operation: str,
        key: str,
        request_hash: str,
        status_code: int,
        payload: dict[str, object],
        run_id: UUID | None,
    ) -> None:
        response_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with self.engine.begin() as connection:
            result = connection.execute(
                text(
                    """
                    UPDATE idempotency_requests
                    SET state = 'completed', response_status = :response_status,
                        response_json = :response_json, run_id = :run_id,
                        updated_at = :updated_at
                    WHERE operation = :operation AND idempotency_key = :key
                        AND request_hash = :request_hash AND state = 'pending'
                    """
                ),
                {
                    "response_status": status_code,
                    "response_json": response_json,
                    "run_id": str(run_id) if run_id else None,
                    "updated_at": utc_now(),
                    "operation": operation,
                    "key": key,
                    "request_hash": request_hash,
                },
            )
            if result.rowcount != 1:
                raise RuntimeError("idempotency reservation could not be completed")

    def release(self, operation: str, key: str, request_hash: str) -> None:
        """Release only an unfinished reservation so an exact retry may resume."""
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    DELETE FROM idempotency_requests
                    WHERE operation = :operation AND idempotency_key = :key
                        AND request_hash = :request_hash AND state = 'pending'
                    """
                ),
                {"operation": operation, "key": key, "request_hash": request_hash},
            )
