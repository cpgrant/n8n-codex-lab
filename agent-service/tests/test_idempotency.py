import pytest

from ai_factory.database import initialize_database
from ai_factory.errors import FactoryError
from ai_factory.idempotency import (
    IdempotencyRepository,
    canonical_json_hash,
    validate_idempotency_key,
)


def test_canonical_hash_ignores_object_key_order():
    assert canonical_json_hash({"a": 1, "b": 2}) == canonical_json_hash(
        {"b": 2, "a": 1}
    )


def test_idempotency_reservation_completion_and_replay(tmp_path):
    database_path = tmp_path / "runs.db"
    initialize_database(database_path)
    repository = IdempotencyRepository(database_path)

    assert repository.reserve("create", "synthetic-key", "hash") is None
    repository.complete(
        "create", "synthetic-key", "hash", 201, {"data": {"ok": True}}, None
    )
    replay = repository.reserve("create", "synthetic-key", "hash")

    assert replay.status_code == 201
    assert replay.payload == {"data": {"ok": True}}


def test_idempotency_conflict_and_pending_are_explicit(tmp_path):
    database_path = tmp_path / "runs.db"
    initialize_database(database_path)
    repository = IdempotencyRepository(database_path)
    repository.reserve("create", "synthetic-key", "hash-one")

    with pytest.raises(FactoryError) as pending:
        repository.reserve("create", "synthetic-key", "hash-one")
    assert pending.value.code == "IDEMPOTENCY_IN_PROGRESS"

    with pytest.raises(FactoryError) as conflict:
        repository.reserve("create", "synthetic-key", "hash-two")
    assert conflict.value.code == "IDEMPOTENCY_CONFLICT"


def test_idempotency_key_validation():
    with pytest.raises(FactoryError) as missing:
        validate_idempotency_key(None)
    assert missing.value.code == "IDEMPOTENCY_KEY_REQUIRED"
