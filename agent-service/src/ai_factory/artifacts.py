"""Safe, deterministic Markdown artifact rendering and atomic storage."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from .schemas import (
    ArtifactMetadata,
    QualityArtifactMetadata,
    QualityReport,
    ReviewRecord,
    StrategyBrief,
    StrategyResponse,
)


def sha256_text(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def draft_checksum(strategy: StrategyResponse) -> str:
    canonical = json.dumps(
        strategy.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    )
    return sha256_text(canonical)


def escape_markdown(value: object) -> str:
    text = str(value).replace("\\", "\\\\")
    for character in "`*_{}[]()#+-.!|>":
        text = text.replace(character, f"\\{character}")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def table_text(value: object) -> str:
    return escape_markdown(value).replace("\n", "<br>")


class MarkdownArtifactStore:
    def __init__(self, artifact_dir: Path) -> None:
        self.artifact_dir = artifact_dir

    def render(
        self,
        brief: StrategyBrief,
        strategy: StrategyResponse,
        review: ReviewRecord,
        quality_report: QualityReport | None = None,
        quality_artifact: QualityArtifactMetadata | None = None,
    ) -> str:
        lines = [
            f"# {escape_markdown(brief.title)}",
            "",
            "> Approved AI Strategy Factory v0.1 artifact",
            "",
            "| Metadata | Value |",
            "| --- | --- |",
            f"| Organization | {table_text(brief.organization.name)} |",
            f"| Decision horizon | {table_text(brief.decision_horizon)} |",
            f"| Run ID | `{strategy.run_id}` |",
            f"| Strategy provider | {table_text(strategy.provider)} |",
            f"| Generated at | {strategy.generated_at.isoformat()} |",
            f"| Approved by | {table_text(review.reviewer)} |",
            f"| Approved at | {review.decided_at.isoformat()} |",
            f"| Draft checksum | `{review.draft_checksum}` |",
        ]
        if quality_report is not None:
            critic = quality_report.critic_provider
            if quality_report.critic_model is not None:
                critic = f"{critic} / {quality_report.critic_model}"
            lines.extend(
                [
                    f"| Advisory quality score | {quality_report.overall_score}/100 |",
                    "| Advisory recommendation | "
                    f"{table_text(quality_report.recommendation)} |",
                    f"| Quality mode | {table_text(quality_report.mode)} |",
                    f"| Quality critic | {table_text(critic)} |",
                ]
            )
        if quality_artifact is not None:
            lines.append(
                "| Quality report artifact | "
                f"`quality-reports/{quality_artifact.filename}` |"
            )
        lines.extend(
            [
                "",
                "## Decision summary",
                "",
                "### Objectives",
                "",
                "| ID | Outcome | Time horizon |",
                "| --- | --- | --- |",
            ]
        )
        for item in strategy.objectives:
            lines.append(
                f"| {item.id} | {table_text(item.statement)} | "
                f"{table_text(item.time_horizon)} |"
            )
        lines.extend(
            [
                "",
                "### Strategic choices",
                "",
                "| ID | Choice | Trade-off |",
                "| --- | --- | --- |",
            ]
        )
        for item in strategy.strategic_choices:
            lines.append(
                f"| {item.id} | {table_text(item.choice)} | "
                f"{table_text(item.trade_offs)} |"
            )
        lines.extend(
            [
                "",
                "## Executive summary",
                "",
                escape_markdown(strategy.executive_summary),
                "",
                "## Current situation",
                "",
                escape_markdown(strategy.current_situation.summary),
                "",
                "### Evidence",
                "",
            ]
        )
        lines.extend(f"- {escape_markdown(item)}" for item in strategy.current_situation.evidence)
        lines.extend(["", "## Objectives", ""])
        for item in strategy.objectives:
            lines.extend(
                [
                    f"### {item.id} — {escape_markdown(item.statement)}",
                    "",
                    f"- Time horizon: {escape_markdown(item.time_horizon)}",
                    "",
                ]
            )
        lines.extend(["## Strategic choices", ""])
        for item in strategy.strategic_choices:
            lines.extend(
                [
                    f"### {item.id} — {escape_markdown(item.choice)}",
                    "",
                    escape_markdown(item.rationale),
                    "",
                    f"- Trade-off: {escape_markdown(item.trade_offs)}",
                    "",
                ]
            )
        lines.extend(["## Recommended initiatives", ""])
        for item in strategy.recommended_initiatives:
            objectives = ", ".join(item.supports_objectives)
            lines.extend(
                [
                    f"### {item.id} — {escape_markdown(item.name)}",
                    "",
                    escape_markdown(item.description),
                    "",
                    f"- Owner role: {escape_markdown(item.owner_role)}",
                    f"- Timeframe: {escape_markdown(item.timeframe)}",
                    f"- Supports objectives: {escape_markdown(objectives)}",
                    "",
                ]
            )
        lines.extend(["## Risks and assumptions", "", "### Risks", ""])
        lines.extend(f"- {escape_markdown(item)}" for item in strategy.risks_and_assumptions.risks)
        lines.extend(["", "### Assumptions", ""])
        lines.extend(f"- {escape_markdown(item)}" for item in strategy.risks_and_assumptions.assumptions)
        lines.extend(
            [
                "",
                "## Success measures",
                "",
                "| ID | Measure | Target | Review frequency |",
                "| --- | --- | --- | --- |",
            ]
        )
        for item in strategy.success_measures:
            lines.append(
                f"| {item.id} | {table_text(item.measure)} | {table_text(item.target)} | "
                f"{table_text(item.review_frequency)} |"
            )
        lines.extend(["", "## Next steps", ""])
        for item in strategy.next_steps:
            lines.append(
                f"{item.order}. {escape_markdown(item.action)} — "
                f"**{escape_markdown(item.owner_role)}**"
            )
        lines.extend(
            [
                "",
                "## Review note",
                "",
                escape_markdown(review.comment or "No review comment provided."),
                "",
                "---",
                "",
                "This artifact was generated from synthetic test data and explicitly approved by",
                "the reviewer recorded above.",
                "",
            ]
        )
        return "\n".join(lines)

    def create(
        self,
        run_id: UUID,
        brief: StrategyBrief,
        strategy: StrategyResponse,
        review: ReviewRecord,
        quality_report: QualityReport | None = None,
        quality_artifact: QualityArtifactMetadata | None = None,
    ) -> ArtifactMetadata:
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        filename = f"strategy-{run_id}.md"
        target = self.artifact_dir / filename
        content = self.render(
            brief,
            strategy,
            review,
            quality_report=quality_report,
            quality_artifact=quality_artifact,
        )
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.artifact_dir,
                prefix=f".{filename}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, target)
        except Exception:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise
        return ArtifactMetadata(
            filename=filename,
            checksum=sha256_text(content),
            created_at=datetime.now(UTC),
        )

    def path_for(self, run_id: UUID, metadata: ArtifactMetadata) -> Path:
        expected = f"strategy-{run_id}.md"
        if metadata.filename != expected:
            raise ValueError("artifact filename does not match its run ID")
        return self.artifact_dir / expected
