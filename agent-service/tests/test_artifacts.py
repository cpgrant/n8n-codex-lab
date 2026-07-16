from datetime import UTC, datetime
from uuid import UUID

from ai_factory.artifacts import MarkdownArtifactStore, draft_checksum, sha256_text
from ai_factory.schemas import ReviewRecord, StrategyBrief, StrategyResponse


RUN_ID = UUID("4a3fd768-726a-4d7c-a722-5215d87511e4")


def test_approved_markdown_is_service_named_atomic_and_checksummed(
    tmp_path, brief, response_fixture
):
    strategy = StrategyResponse.model_validate(response_fixture)
    review = ReviewRecord(
        decision="approved",
        reviewer="synthetic-reviewer",
        comment="Approved for synthetic testing.",
        decided_at=datetime(2026, 7, 12, 10, 5, tzinfo=UTC),
        draft_checksum=draft_checksum(strategy),
    )
    store = MarkdownArtifactStore(tmp_path)

    metadata = store.create(RUN_ID, brief, strategy, review)
    path = store.path_for(RUN_ID, metadata)
    content = path.read_text(encoding="utf-8")

    assert metadata.filename == f"strategy-{RUN_ID}.md"
    assert metadata.checksum == sha256_text(content)
    assert "## Decision summary" in content
    assert "### Objectives" in content
    assert "### Strategic choices" in content
    assert "| Strategy provider | fake |" in content
    assert "## Executive summary" in content
    assert "## Current situation" in content
    assert "## Objectives" in content
    assert "## Strategic choices" in content
    assert "## Recommended initiatives" in content
    assert "## Risks and assumptions" in content
    assert "## Success measures" in content
    assert "## Next steps" in content
    assert list(tmp_path.glob("*.tmp")) == []


def test_untrusted_markdown_is_escaped(tmp_path, brief, response_fixture):
    payload = brief.model_dump(mode="json")
    payload["title"] = "# Synthetic [link](https://invalid.example)"
    unsafe_brief = StrategyBrief.model_validate(payload)
    strategy = StrategyResponse.model_validate(response_fixture)
    review = ReviewRecord(
        decision="approved",
        reviewer="synthetic-reviewer",
        comment=None,
        decided_at=datetime(2026, 7, 12, 10, 5, tzinfo=UTC),
        draft_checksum=draft_checksum(strategy),
    )

    content = MarkdownArtifactStore(tmp_path).render(unsafe_brief, strategy, review)

    assert content.startswith("# \\# Synthetic \\[link\\]\\(https://invalid\\.example\\)")
    assert "No review comment provided\\." in content
