"""Synchronous strategy generation use case."""

from __future__ import annotations

from pydantic import ValidationError

from .errors import FactoryError
from .providers import ProviderOutputError, StrategyProvider
from .repository import RunRecord, RunRepository
from .schemas import StrategyBrief, StrategyResponse
from .statuses import RunStatus


class StrategyService:
    def __init__(self, repository: RunRepository, provider: StrategyProvider) -> None:
        self.repository = repository
        self.provider = provider

    def create_run(self, brief: StrategyBrief) -> RunRecord:
        run = self.repository.create(brief)
        self.repository.transition(run.run_id, RunStatus.GENERATING)
        try:
            raw_strategy = self.provider.generate_strategy(brief, run.run_id)
        except ProviderOutputError as exc:
            self.repository.fail_generation(
                run.run_id,
                "PROVIDER_OUTPUT_INVALID",
                "The provider output did not satisfy the strategy contract.",
            )
            raise FactoryError(
                422,
                "PROVIDER_OUTPUT_INVALID",
                "The provider output did not satisfy the strategy contract.",
                run_id=run.run_id,
                retryable=False,
            ) from exc
        except Exception as exc:
            self.repository.fail_generation(
                run.run_id, "PROVIDER_ERROR", "The strategy provider failed."
            )
            raise FactoryError(
                502,
                "PROVIDER_ERROR",
                "The strategy provider failed.",
                run_id=run.run_id,
                retryable=True,
            ) from exc

        try:
            strategy = StrategyResponse.model_validate(raw_strategy)
        except ValidationError as exc:
            self.repository.fail_generation(
                run.run_id,
                "PROVIDER_OUTPUT_INVALID",
                "The provider output did not satisfy the strategy contract.",
            )
            raise FactoryError(
                422,
                "PROVIDER_OUTPUT_INVALID",
                "The provider output did not satisfy the strategy contract.",
                details=[
                    {
                        "field": ".".join(str(part) for part in error["loc"]),
                        "reason": error["msg"],
                    }
                    for error in exc.errors()
                ],
                run_id=run.run_id,
                retryable=False,
            ) from exc

        return self.repository.complete_generation(run.run_id, strategy)
