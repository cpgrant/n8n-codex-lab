"""SQLite-backed idempotency reservations and completed response replay."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from .database import connect
from .errors import FactoryError
from .repository import utc_now


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
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def reserve(
        self, operation: str, key: str, request_hash: str
    ) -> IdempotencyReplay | None:
        timestamp = utc_now()
        with connect(self.database_path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """
                SELECT * FROM idempotency_requests
                WHERE operation = ? AND idempotency_key = ?
                """,
                (operation, key),
            ).fetchone()
            if row is None:
                connection.execute(
                    """
                    INSERT INTO idempotency_requests (
                        operation, idempotency_key, request_hash, state,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, 'pending', ?, ?)
                    """,
                    (operation, key, request_hash, timestamp, timestamp),
                )
                return None
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

    def complete(
        self,
        operation: str,
        key: str,
        request_hash: str,
        status_code: int,
        payload: dict[str, object],
        run_id: UUID | None,
    ) -> None:
        timestamp = utc_now()
        response_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with connect(self.database_path) as connection:
            result = connection.execute(
                """
                UPDATE idempotency_requests
                SET state = 'completed', response_status = ?, response_json = ?,
                    run_id = ?, updated_at = ?
                WHERE operation = ? AND idempotency_key = ?
                    AND request_hash = ? AND state = 'pending'
                """,
                (
                    status_code,
                    response_json,
                    str(run_id) if run_id else None,
                    timestamp,
                    operation,
                    key,
                    request_hash,
                ),
            )
            if result.rowcount != 1:
                raise RuntimeError("idempotency reservation could not be completed")
