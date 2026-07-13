"""Pydantic models matching the Stage 0 contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .statuses import RunStatus


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Organization(StrictModel):
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    context: str = Field(min_length=1)


class StrategyBrief(StrictModel):
    schema_version: Literal["0.1"]
    title: str = Field(min_length=1, max_length=200)
    organization: Organization
    decision_horizon: str = Field(min_length=1)
    challenge: str = Field(min_length=1)
    desired_outcomes: list[str] = Field(min_length=1)
    constraints: list[str]
    available_evidence: list[str]
    stakeholders: list[str]
    requested_by: str = Field(min_length=1)
    supersedes_run_id: UUID | None = None


class CurrentSituation(StrictModel):
    summary: str = Field(min_length=1)
    evidence: list[str]


class Objective(StrictModel):
    id: str = Field(pattern=r"^OBJ-[1-9][0-9]*$")
    statement: str = Field(min_length=1)
    time_horizon: str = Field(min_length=1)


class StrategicChoice(StrictModel):
    id: str = Field(pattern=r"^CHO-[1-9][0-9]*$")
    choice: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    trade_offs: str = Field(min_length=1)


class RecommendedInitiative(StrictModel):
    id: str = Field(pattern=r"^INIT-[1-9][0-9]*$")
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    owner_role: str = Field(min_length=1)
    timeframe: str = Field(min_length=1)
    supports_objectives: list[str] = Field(min_length=1)


class RisksAndAssumptions(StrictModel):
    risks: list[str] = Field(min_length=1, max_length=6)
    assumptions: list[str] = Field(min_length=1, max_length=6)


class SuccessMeasure(StrictModel):
    id: str = Field(pattern=r"^MET-[1-9][0-9]*$")
    measure: str = Field(min_length=1)
    target: str = Field(min_length=1)
    review_frequency: str = Field(min_length=1)


class NextStep(StrictModel):
    order: int = Field(ge=1)
    action: str = Field(min_length=1)
    owner_role: str = Field(min_length=1)


class StrategyContent(StrictModel):
    executive_summary: str = Field(min_length=1)
    current_situation: CurrentSituation
    objectives: list[Objective] = Field(min_length=2, max_length=4)
    strategic_choices: list[StrategicChoice] = Field(min_length=2, max_length=4)
    recommended_initiatives: list[RecommendedInitiative] = Field(
        min_length=3, max_length=5
    )
    risks_and_assumptions: RisksAndAssumptions
    success_measures: list[SuccessMeasure] = Field(min_length=2, max_length=4)
    next_steps: list[NextStep] = Field(min_length=3, max_length=6)

    @model_validator(mode="after")
    def validate_strategy_references(self) -> "StrategyContent":
        expected_ids = {
            "objectives": [f"OBJ-{index}" for index in range(1, len(self.objectives) + 1)],
            "strategic_choices": [
                f"CHO-{index}" for index in range(1, len(self.strategic_choices) + 1)
            ],
            "recommended_initiatives": [
                f"INIT-{index}"
                for index in range(1, len(self.recommended_initiatives) + 1)
            ],
            "success_measures": [
                f"MET-{index}" for index in range(1, len(self.success_measures) + 1)
            ],
        }
        actual_ids = {
            "objectives": [item.id for item in self.objectives],
            "strategic_choices": [item.id for item in self.strategic_choices],
            "recommended_initiatives": [
                item.id for item in self.recommended_initiatives
            ],
            "success_measures": [item.id for item in self.success_measures],
        }
        for section, expected in expected_ids.items():
            if actual_ids[section] != expected:
                raise ValueError(f"{section} IDs must be unique and sequential")

        objective_ids = set(actual_ids["objectives"])
        for initiative in self.recommended_initiatives:
            references = initiative.supports_objectives
            if len(references) != len(set(references)):
                raise ValueError(
                    "initiative objective references must not contain duplicates"
                )
            if not set(references).issubset(objective_ids):
                raise ValueError(
                    "initiative objective references must identify existing objectives"
                )

        orders = [step.order for step in self.next_steps]
        if orders != list(range(1, len(self.next_steps) + 1)):
            raise ValueError("next step order values must be unique and sequential")
        return self


class StrategyResponse(StrategyContent):
    schema_version: Literal["0.1"]
    run_id: UUID
    status: Literal[RunStatus.AWAITING_REVIEW]
    generated_at: datetime
    provider: Literal["fake", "ollama", "openai"]


class QualityScorecard(StrictModel):
    brief_alignment: int = Field(ge=0, le=10)
    evidence_grounding: int = Field(ge=0, le=10)
    constraint_adherence: int = Field(ge=0, le=10)
    objective_quality: int = Field(ge=0, le=10)
    measurement_quality: int = Field(ge=0, le=10)
    initiative_feasibility: int = Field(ge=0, le=10)
    internal_consistency: int = Field(ge=0, le=10)


class QualityIssue(StrictModel):
    severity: Literal["low", "medium", "high"]
    section: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=1000)
    suggestion: str = Field(min_length=1, max_length=1000)


class QualityAssessment(StrictModel):
    checks: QualityScorecard
    strengths: list[str] = Field(max_length=10)
    issues: list[QualityIssue] = Field(max_length=20)
    unsupported_claims: list[str] = Field(max_length=20)
    missing_considerations: list[str] = Field(max_length=20)
    review_questions: list[str] = Field(max_length=20)


class QualityReport(QualityAssessment):
    schema_version: Literal["0.1"] = "0.1"
    run_id: UUID
    mode: Literal["basic", "pro"]
    overall_score: int = Field(ge=0, le=100)
    recommendation: Literal["ready_for_review", "review_with_caution"]
    draft_checksum: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    generated_at: datetime
    critic_provider: Literal["deterministic", "ollama", "openai"]
    critic_model: str | None = Field(default=None, min_length=1, max_length=200)


class ReviewRequest(StrictModel):
    decision: Literal["approved", "rejected"]
    reviewer: str = Field(min_length=1, max_length=200)
    comment: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def rejection_requires_comment(self) -> "ReviewRequest":
        if self.decision == "rejected" and not self.comment:
            raise ValueError("comment is required when decision is rejected")
        return self


class ReviewRecord(StrictModel):
    decision: Literal["approved", "rejected"]
    reviewer: str
    comment: str | None
    decided_at: datetime
    draft_checksum: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class ArtifactMetadata(StrictModel):
    filename: str = Field(pattern=r"^strategy-[0-9a-f-]{36}\.md$")
    media_type: Literal["text/markdown"] = "text/markdown"
    checksum: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    created_at: datetime


class HealthResponse(StrictModel):
    status: Literal["ok"] = "ok"
    service: Literal["ai-strategy-factory"] = "ai-strategy-factory"
    version: Literal["0.1"] = "0.1"


class CreateRunData(StrictModel):
    run_id: UUID
    status: RunStatus
    strategy: StrategyResponse
    created_at: datetime
    updated_at: datetime


class ReadRunData(StrictModel):
    run_id: UUID
    status: RunStatus
    brief: StrategyBrief
    strategy: StrategyResponse | None
    quality_report: QualityReport | None = None
    review: ReviewRecord | None = None
    artifact: ArtifactMetadata | None = None
    error_code: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class ResponseMeta(StrictModel):
    request_id: str
    idempotent_replay: bool | None = None


class CreateRunResponse(StrictModel):
    data: CreateRunData
    meta: ResponseMeta


class ReadRunResponse(StrictModel):
    data: ReadRunData
    meta: ResponseMeta


class ReviewRunData(StrictModel):
    run_id: UUID
    status: RunStatus
    review: ReviewRecord
    artifact: ArtifactMetadata | None


class ReviewRunResponse(StrictModel):
    data: ReviewRunData
    meta: ResponseMeta


class QualityReportData(StrictModel):
    run_id: UUID
    status: RunStatus
    quality_report: QualityReport
