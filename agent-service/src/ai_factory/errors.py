"""Safe application errors matching the public API contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class FactoryError(Exception):
    status_code: int
    code: str
    message: str
    details: list[dict[str, object]] = field(default_factory=list)
    run_id: UUID | None = None
    retryable: bool = False

    def public_body(self) -> dict[str, object]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "run_id": str(self.run_id) if self.run_id else None,
            "retryable": self.retryable,
        }
