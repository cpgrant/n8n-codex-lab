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
    risks: list[str]
    assumptions: list[str]


class SuccessMeasure(StrictModel):
    id: str = Field(pattern=r"^MET-[1-9][0-9]*$")
    measure: str = Field(min_length=1)
    target: str = Field(min_length=1)
    review_frequency: str = Field(min_length=1)


class NextStep(StrictModel):
    order: int = Field(ge=1)
    action: str = Field(min_length=1)
    owner_role: str = Field(min_length=1)


class StrategyResponse(StrictModel):
    schema_version: Literal["0.1"]
    run_id: UUID
    status: Literal[RunStatus.AWAITING_REVIEW]
    executive_summary: str = Field(min_length=1)
    current_situation: CurrentSituation
    objectives: list[Objective] = Field(min_length=1)
    strategic_choices: list[StrategicChoice] = Field(min_length=1)
    recommended_initiatives: list[RecommendedInitiative] = Field(min_length=1)
    risks_and_assumptions: RisksAndAssumptions
    success_measures: list[SuccessMeasure] = Field(min_length=1)
    next_steps: list[NextStep] = Field(min_length=1)
    generated_at: datetime
    provider: Literal["fake", "openai"]


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
