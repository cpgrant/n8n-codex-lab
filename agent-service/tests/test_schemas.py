import json

import pytest
from pydantic import ValidationError

from ai_factory.schemas import (
    QualityAssessment,
    StrategyBrief,
    StrategyContent,
    StrategyResponse,
)


def test_checked_in_examples_match_contract(brief, response_fixture):
    assert brief.schema_version == "0.1"
    response = StrategyResponse.model_validate(response_fixture)
    assert response.provider == "fake"


def test_unknown_brief_fields_are_rejected(brief):
    payload = brief.model_dump(mode="json")
    payload["unexpected"] = True

    with pytest.raises(ValidationError):
        StrategyBrief.model_validate(payload)


def test_brief_requires_an_outcome(brief):
    payload = brief.model_dump(mode="json")
    payload["desired_outcomes"] = []

    with pytest.raises(ValidationError):
        StrategyBrief.model_validate(payload)


def strategy_content(response_fixture):
    return {
        key: value
        for key, value in response_fixture.items()
        if key
        not in {"schema_version", "run_id", "status", "generated_at", "provider"}
    }


def test_strategy_rejects_shallow_sections(response_fixture):
    payload = strategy_content(response_fixture)
    payload["objectives"] = payload["objectives"][:1]

    with pytest.raises(ValidationError, match="at least 2 items"):
        StrategyContent.model_validate(payload)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda payload: payload["objectives"][1].update(id="OBJ-1"),
            "IDs must be unique and sequential",
        ),
        (
            lambda payload: payload["recommended_initiatives"][0][
                "supports_objectives"
            ].append("OBJ-99"),
            "must identify existing objectives",
        ),
        (
            lambda payload: payload["next_steps"][1].update(order=3),
            "order values must be unique and sequential",
        ),
    ],
)
def test_strategy_rejects_inconsistent_references(
    response_fixture, mutate, message
):
    payload = strategy_content(response_fixture)
    mutate(payload)

    with pytest.raises(ValidationError, match=message):
        StrategyContent.model_validate(payload)


def test_quality_assessment_rejects_out_of_range_score():
    with pytest.raises(ValidationError, match="less than or equal to 10"):
        QualityAssessment.model_validate(
            {
                "checks": {
                    "brief_alignment": 11,
                    "evidence_grounding": 10,
                    "constraint_adherence": 10,
                    "objective_quality": 10,
                    "measurement_quality": 10,
                    "initiative_feasibility": 10,
                    "internal_consistency": 10,
                },
                "strengths": [],
                "issues": [],
                "unsupported_claims": [],
                "missing_considerations": [],
                "review_questions": [],
            }
        )
