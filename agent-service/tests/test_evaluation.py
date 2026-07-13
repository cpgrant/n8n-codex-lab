from copy import deepcopy
import json
from pathlib import Path

import pytest

from ai_factory.evaluation import (
    apply_preferences,
    evaluate_models,
    validate_preferences,
    write_evaluation_artifacts,
)


def synthetic_transport(response_fixture):
    def transport(url, payload, timeout):
        del url, timeout
        system = payload["messages"][0]["content"]
        if "advisory strategy-quality critic" in system:
            content = {
                "checks": {
                    "brief_alignment": 9,
                    "evidence_grounding": 9,
                    "constraint_adherence": 9,
                    "objective_quality": 9,
                    "measurement_quality": 9,
                    "initiative_feasibility": 9,
                    "internal_consistency": 9,
                },
                "strengths": ["The synthetic draft is reviewable."],
                "issues": [],
                "unsupported_claims": [],
                "missing_considerations": [],
                "review_questions": ["Is the synthetic strategy useful?"],
            }
        else:
            content = deepcopy(response_fixture)
        return {
            "message": {"content": json.dumps(content)},
            "total_duration": 2_000_000_000,
            "load_duration": 500_000_000,
            "prompt_eval_count": 100,
            "eval_count": 50,
        }

    return transport


def test_evaluation_measures_generation_critique_and_quality(
    tmp_path, response_fixture
):
    brief_path = tmp_path / "brief.synthetic.json"
    source = Path(__file__).parents[2] / "examples/strategy-brief.synthetic.json"
    brief_path.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    payload = evaluate_models(
        models=["gemma4:test-a", "gemma4:test-b"],
        brief_paths=[brief_path],
        base_url="http://127.0.0.1:11888",
        timeout_seconds=10,
        transport=synthetic_transport(response_fixture),
    )

    assert payload["synthetic_only"] is True
    assert len(payload["results"]) == 2
    assert all(row["schema_success"] for row in payload["results"])
    assert all(row["critique_success"] for row in payload["results"])
    assert all(
        row["generation"]["total_seconds"] == 2.0
        for row in payload["results"]
    )
    assert all(
        row["checks"]["evidence_grounding"] >= 0
        for row in payload["results"]
    )
    assert payload["summary"][0]["schema_success_rate"] == 100.0


def test_evaluation_artifacts_are_blinded_and_preferences_are_validated(
    tmp_path, response_fixture
):
    source = Path(__file__).parents[2] / "examples/strategy-brief.synthetic.json"
    payload = evaluate_models(
        models=["gemma4:test-a", "gemma4:test-b"],
        brief_paths=[source],
        base_url="http://127.0.0.1:11888",
        timeout_seconds=10,
        transport=synthetic_transport(response_fixture),
    )
    paths = write_evaluation_artifacts(payload, tmp_path / "evaluation")

    packet = paths["review_packet"].read_text(encoding="utf-8")
    assert "Candidate A" in packet
    assert "gemma4:test-a" not in packet
    preferences = json.loads(paths["preferences"].read_text(encoding="utf-8"))
    preferences["preferences"][0]["reviewer"] = "synthetic-human-reviewer"
    paths["preferences"].write_text(json.dumps(preferences), encoding="utf-8")

    applied = apply_preferences(
        paths["results"], paths["preferences"], paths["report"]
    )

    assert applied == preferences
    report = paths["report"].read_text(encoding="utf-8")
    assert "Recorded:" in report
    assert "Select `gemma4:test" in report


def test_invalid_preference_ranking_is_rejected():
    payload = {"models": ["a", "b"], "briefs": ["brief.json"]}
    preferences = {
        "preferences": [
            {
                "brief": "brief.json",
                "ranking": ["Candidate A", "Candidate A"],
                "reviewer": "reviewer",
            }
        ]
    }

    with pytest.raises(ValueError, match="every candidate"):
        validate_preferences(payload, preferences)
