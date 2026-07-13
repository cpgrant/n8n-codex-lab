"""Safe Markdown rendering for advisory quality-report artifacts."""

from __future__ import annotations

import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from .artifacts import escape_markdown, sha256_text, table_text
from .schemas import QualityArtifactMetadata, QualityReport


class QualityMarkdownArtifactStore:
    def __init__(self, artifact_dir: Path) -> None:
        self.artifact_dir = artifact_dir / "quality-reports"

    def render(self, report: QualityReport) -> str:
        lines = [
            f"# Quality report — {report.run_id}",
            "",
            "> Advisory AI Strategy Factory quality report — not an approval",
            "",
            "This report cannot approve, reject, or rewrite the strategy. The human",
            "reviewer makes the final decision.",
            "",
            "| Metadata | Value |",
            "| --- | --- |",
            f"| Run ID | `{report.run_id}` |",
            f"| Draft checksum | `{report.draft_checksum}` |",
            f"| Generated at | {report.generated_at.isoformat()} |",
            f"| Mode | {table_text(report.mode)} |",
            f"| Critic provider | {table_text(report.critic_provider)} |",
            f"| Critic model | {table_text(report.critic_model or 'None')} |",
            f"| Overall score | {report.overall_score}/100 |",
            f"| Recommendation | {table_text(report.recommendation)} |",
            "",
            "## Scorecard",
            "",
            "| Check | Score |",
            "| --- | --- |",
        ]
        for name, score in report.checks.model_dump().items():
            lines.append(f"| {table_text(name.replace('_', ' '))} | {score}/10 |")

        lines.extend(["", "## Strengths", ""])
        lines.extend(
            [f"- {escape_markdown(item)}" for item in report.strengths]
            or ["- None recorded."]
        )
        lines.extend(["", "## Issues", ""])
        if report.issues:
            for issue in report.issues:
                lines.extend(
                    [
                        f"### {escape_markdown(issue.severity.upper())} — "
                        f"{escape_markdown(issue.section)}",
                        "",
                        escape_markdown(issue.message),
                        "",
                        f"- Suggestion: {escape_markdown(issue.suggestion)}",
                        "",
                    ]
                )
        else:
            lines.extend(["No issues were recorded.", ""])

        for heading, values, empty_text in (
            (
                "Unsupported claims",
                report.unsupported_claims,
                "No unsupported claims were identified.",
            ),
            (
                "Missing considerations",
                report.missing_considerations,
                "No missing considerations were identified.",
            ),
            (
                "Questions for the reviewer",
                report.review_questions,
                "No additional reviewer questions were generated.",
            ),
        ):
            lines.extend([f"## {heading}", ""])
            lines.extend(
                [f"- {escape_markdown(item)}" for item in values]
                or [empty_text]
            )
            lines.append("")
        return "\n".join(lines)

    def create(
        self, run_id: UUID, report: QualityReport
    ) -> QualityArtifactMetadata:
        if report.run_id != run_id:
            raise ValueError("quality report run ID does not match")
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        filename = f"quality-report-{run_id}.md"
        target = self.artifact_dir / filename
        content = self.render(report)
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
        return QualityArtifactMetadata(
            filename=filename,
            checksum=sha256_text(content),
            created_at=datetime.now(UTC),
        )

    def path_for(
        self, run_id: UUID, metadata: QualityArtifactMetadata
    ) -> Path:
        expected = f"quality-report-{run_id}.md"
        if metadata.filename != expected:
            raise ValueError("quality artifact filename does not match its run ID")
        return self.artifact_dir / expected
