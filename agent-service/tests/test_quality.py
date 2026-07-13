import pytest

from ai_factory.artifacts import draft_checksum
from ai_factory.database import initialize_database
from ai_factory.errors import FactoryError
from ai_factory.providers import FakeStrategyProvider
from ai_factory.quality import DeterministicQualityReviewer
from ai_factory.quality_service import QualityReportService
from ai_factory.repository import RunRepository
from ai_factory.schemas import QualityAssessment, QualityIssue, StrategyResponse
from ai_factory.service import StrategyService


def generated_run(tmp_path, brief, response_fixture):
    database_path = tmp_path / "runs.db"
    initialize_database(database_path)
    repository = RunRepository(database_path)
    run = StrategyService(
        repository, FakeStrategyProvider(response_fixture)
    ).create_run(brief)
    return repository, run


def test_basic_quality_report_is_durable_immutable_and_checksum_bound(
    tmp_path, brief, response_fixture
):
    repository, run = generated_run(tmp_path, brief, response_fixture)
    service = QualityReportService(repository, mode="basic")

    created = service.create_report(run.run_id)
    repeated = service.create_report(run.run_id)
    reopened = RunRepository(repository.database_path).get(run.run_id)

    report = created.quality_report
    assert report is not None
    assert report == repeated.quality_report == reopened.quality_report
    assert report["mode"] == "basic"
    assert report["critic_provider"] == "deterministic"
    assert report["critic_model"] is None
    assert report["overall_score"] >= 0
    assert report["recommendation"] in {
        "ready_for_review",
        "review_with_caution",
    }
    strategy = StrategyResponse.model_validate(run.strategy)
    assert report["draft_checksum"] == draft_checksum(strategy)


class ConservativeCritic:
    name = "ollama"
    model = "synthetic-critic"

    def review_strategy(self, brief, strategy, deterministic):
        del brief, strategy
        payload = deterministic.model_dump(mode="json")
        payload["checks"]["brief_alignment"] = 2
        payload["issues"].append(
            QualityIssue(
                severity="high",
                section="brief_alignment",
                message="The synthetic critic found weak alignment.",
                suggestion="Ask the reviewer to compare every objective to the brief.",
            ).model_dump(mode="json")
        )
        payload["review_questions"].append(
            "Does every objective trace to a requested outcome?"
        )
        return QualityAssessment.model_validate(payload).model_dump(mode="json")


def test_pro_quality_report_merges_critic_conservatively(
    tmp_path, brief, response_fixture
):
    repository, run = generated_run(tmp_path, brief, response_fixture)

    created = QualityReportService(
        repository, mode="pro", critic=ConservativeCritic()
    ).create_report(run.run_id)
    report = created.quality_report

    assert report["mode"] == "pro"
    assert report["critic_provider"] == "ollama"
    assert report["critic_model"] == "synthetic-critic"
    assert report["checks"]["brief_alignment"] == 2
    assert report["recommendation"] == "review_with_caution"
    assert any(issue["severity"] == "high" for issue in report["issues"])


class InvalidCritic:
    name = "ollama"
    model = "synthetic-invalid"

    def review_strategy(self, brief, strategy, deterministic):
        del brief, strategy, deterministic
        return {"checks": {}}


def test_invalid_critic_output_does_not_persist_a_report(
    tmp_path, brief, response_fixture
):
    repository, run = generated_run(tmp_path, brief, response_fixture)

    with pytest.raises(FactoryError) as caught:
        QualityReportService(
            repository, mode="pro", critic=InvalidCritic()
        ).create_report(run.run_id)

    assert caught.value.code == "QUALITY_REVIEW_OUTPUT_INVALID"
    assert repository.get(run.run_id).quality_report is None


def test_deterministic_review_flags_vague_objective_target(
    brief, response_fixture
):
    response_fixture["objectives"][0]["statement"] = (
        "Increase conversion from 35% to a higher specific target."
    )
    strategy = StrategyResponse.model_validate(response_fixture)

    assessment = DeterministicQualityReviewer().assess(brief, strategy)

    assert assessment.checks.objective_quality == 6
    assert any(
        issue.section == "objective_quality" for issue in assessment.issues
    )
    assert any(
        "Objective target is vague" in item
        for item in assessment.missing_considerations
    )
