"""Create the current AI Factory schema.

Revision ID: 0001_current_factory_schema
Revises:
Create Date: 2026-07-18
"""

from datetime import UTC, datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_current_factory_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "schema_version",
        sa.Column("version", sa.Integer(), primary_key=True),
        sa.Column("applied_at", sa.Text(), nullable=False),
    )
    op.create_table(
        "strategy_runs",
        sa.Column("run_id", sa.Text(), primary_key=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("brief_json", sa.Text(), nullable=False),
        sa.Column("strategy_json", sa.Text()),
        sa.Column("error_code", sa.Text()),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "status IN ('received', 'generating', 'awaiting_review', "
            "'approved', 'artifact_created', 'rejected', 'failed')",
            name="ck_strategy_runs_status",
        ),
    )
    op.create_table(
        "idempotency_requests",
        sa.Column("operation", sa.Text(), nullable=False),
        sa.Column("idempotency_key", sa.Text(), nullable=False),
        sa.Column("request_hash", sa.Text(), nullable=False),
        sa.Column("state", sa.Text(), nullable=False),
        sa.Column("response_status", sa.Integer()),
        sa.Column("response_json", sa.Text()),
        sa.Column("run_id", sa.Text()),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "state IN ('pending', 'completed')",
            name="ck_idempotency_requests_state",
        ),
        sa.ForeignKeyConstraint(["run_id"], ["strategy_runs.run_id"]),
        sa.PrimaryKeyConstraint("operation", "idempotency_key"),
    )
    op.create_table(
        "run_reviews",
        sa.Column("run_id", sa.Text(), primary_key=True),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("reviewer", sa.Text(), nullable=False),
        sa.Column("comment", sa.Text()),
        sa.Column("decided_at", sa.Text(), nullable=False),
        sa.Column("draft_checksum", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "decision IN ('approved', 'rejected')",
            name="ck_run_reviews_decision",
        ),
        sa.ForeignKeyConstraint(["run_id"], ["strategy_runs.run_id"]),
    )
    op.create_table(
        "run_artifacts",
        sa.Column("run_id", sa.Text(), primary_key=True),
        sa.Column("filename", sa.Text(), nullable=False, unique=True),
        sa.Column("media_type", sa.Text(), nullable=False),
        sa.Column("checksum", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["strategy_runs.run_id"]),
    )
    op.create_table(
        "run_quality_reports",
        sa.Column("run_id", sa.Text(), primary_key=True),
        sa.Column("report_json", sa.Text(), nullable=False),
        sa.Column("draft_checksum", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["strategy_runs.run_id"]),
    )
    op.create_table(
        "run_quality_artifacts",
        sa.Column("run_id", sa.Text(), primary_key=True),
        sa.Column("filename", sa.Text(), nullable=False, unique=True),
        sa.Column("media_type", sa.Text(), nullable=False),
        sa.Column("checksum", sa.Text(), nullable=False),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["run_quality_reports.run_id"]),
    )

    applied_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    schema_version = sa.table(
        "schema_version",
        sa.column("version", sa.Integer()),
        sa.column("applied_at", sa.Text()),
    )
    op.bulk_insert(
        schema_version,
        [
            {"version": version, "applied_at": applied_at}
            for version in range(1, 6)
        ],
    )


def downgrade() -> None:
    op.drop_table("run_quality_artifacts")
    op.drop_table("run_quality_reports")
    op.drop_table("run_artifacts")
    op.drop_table("run_reviews")
    op.drop_table("idempotency_requests")
    op.drop_table("strategy_runs")
    op.drop_table("schema_version")
