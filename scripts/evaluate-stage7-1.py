#!/usr/bin/env python3
"""Run or finalize the Stage 7.1 synthetic local-model evaluation."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "agent-service" / "src"))

from ai_factory.evaluation import (  # noqa: E402
    apply_preferences,
    evaluate_models,
    write_evaluation_artifacts,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--models",
        nargs="+",
        default=["gemma4:12b", "gemma4:26b", "gemma4:31b"],
    )
    parser.add_argument(
        "--briefs",
        nargs="+",
        type=Path,
        default=[REPOSITORY_ROOT / "examples/strategy-brief.synthetic.json"],
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:11888")
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPOSITORY_ROOT / "artifacts/evaluations/stage-7.1",
    )
    parser.add_argument(
        "--apply-preferences",
        action="store_true",
        help="Validate review-preferences.json and update report.md without rerunning models.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.apply_preferences:
        apply_preferences(
            args.output_dir / "results.json",
            args.output_dir / "review-preferences.json",
            args.output_dir / "report.md",
        )
        print(f"Updated {args.output_dir / 'report.md'}")
        return 0
    payload = evaluate_models(
        models=args.models,
        brief_paths=args.briefs,
        base_url=args.base_url,
        timeout_seconds=args.timeout,
        progress=lambda message: print(message, flush=True),
    )
    paths = write_evaluation_artifacts(payload, args.output_dir)
    for name, path in paths.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
