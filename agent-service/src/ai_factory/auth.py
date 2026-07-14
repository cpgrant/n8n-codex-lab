"""Fail-closed bearer-token authentication for the local factory API."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from secrets import compare_digest

from .config import Settings
from .errors import FactoryError

SERVICE_SCOPE = "service"
REVIEW_SCOPE = "review"
ACTOR_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


@dataclass(frozen=True)
class AuthContext:
    scope: str
    actor_id: str | None = None


def _bearer_token(authorization: str | None) -> str:
    if authorization is None:
        raise FactoryError(
            401,
            "AUTHENTICATION_REQUIRED",
            "A bearer token is required for this operation.",
        )
    scheme, separator, token = authorization.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token.strip():
        raise FactoryError(
            401,
            "AUTHENTICATION_INVALID",
            "The supplied authentication credential is invalid.",
        )
    return token.strip()


def _configured_token(
    settings: Settings, scope: str
) -> tuple[str | None, datetime | None]:
    if scope == REVIEW_SCOPE:
        return settings.review_token, settings.review_token_expires_at
    return settings.service_token, settings.service_token_expires_at


def authenticate(
    settings: Settings,
    authorization: str | None,
    required_scope: str,
    actor_id: str | None = None,
    now: datetime | None = None,
) -> AuthContext:
    expected, expires_at = _configured_token(settings, required_scope)
    if expected is None:
        raise FactoryError(
            503,
            "AUTHENTICATION_NOT_CONFIGURED",
            "Authentication is not configured for this operation.",
            retryable=True,
        )

    supplied = _bearer_token(authorization)
    service_match = settings.service_token is not None and compare_digest(
        supplied, settings.service_token
    )
    review_match = settings.review_token is not None and compare_digest(
        supplied, settings.review_token
    )
    if not service_match and not review_match:
        raise FactoryError(
            401,
            "AUTHENTICATION_INVALID",
            "The supplied authentication credential is invalid.",
        )

    actual_scope = REVIEW_SCOPE if review_match else SERVICE_SCOPE
    if actual_scope != required_scope:
        raise FactoryError(
            403,
            "AUTHORIZATION_DENIED",
            "The authenticated identity is not authorized for this operation.",
        )

    current = now or datetime.now(timezone.utc)
    if expires_at is not None and current >= expires_at:
        raise FactoryError(
            401,
            "AUTHENTICATION_EXPIRED",
            "The supplied authentication credential has expired.",
        )

    if required_scope == REVIEW_SCOPE:
        normalized_actor = actor_id.strip() if actor_id is not None else ""
        if not ACTOR_PATTERN.fullmatch(normalized_actor):
            raise FactoryError(
                403,
                "AUTHORIZATION_DENIED",
                "An authenticated human actor is required for this operation.",
            )
        return AuthContext(scope=actual_scope, actor_id=normalized_actor)

    return AuthContext(scope=actual_scope)
