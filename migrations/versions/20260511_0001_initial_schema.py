"""Initial schema.

Revision ID: 20260511_0001
Revises:
Create Date: 2026-05-11
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260511_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "job_postings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("source_job_id", sa.String(length=255), nullable=False),
        sa.Column("board_token", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.Column("department", sa.String(length=255), nullable=True),
        sa.Column("location_text", sa.String(length=255), nullable=True),
        sa.Column("employment_type", sa.String(length=100), nullable=True),
        sa.Column("remote_type", sa.String(length=100), nullable=True),
        sa.Column("seniority", sa.String(length=100), nullable=True),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column("salary_currency", sa.String(length=10), nullable=True),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("description_html", sa.Text(), nullable=True),
        sa.Column("apply_url", sa.String(length=1000), nullable=True),
        sa.Column("posting_url", sa.String(length=1000), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("raw_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source", "source_job_id", name="uq_source_job"),
    )
    op.create_index("ix_job_postings_board_token", "job_postings", ["board_token"])
    op.create_index("ix_job_postings_company_name", "job_postings", ["company_name"])
    op.create_index("ix_job_postings_source", "job_postings", ["source"])
    op.create_index("ix_job_postings_title", "job_postings", ["title"])

    op.create_table(
        "job_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("source_job_id", sa.String(length=255), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("normalized_json", sa.JSON(), nullable=False),
        sa.Column("raw_json", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_snapshots_observed_at", "job_snapshots", ["observed_at"])
    op.create_index("ix_job_snapshots_source", "job_snapshots", ["source"])
    op.create_index("ix_job_snapshots_source_job_id", "job_snapshots", ["source_job_id"])


def downgrade() -> None:
    op.drop_index("ix_job_snapshots_source_job_id", table_name="job_snapshots")
    op.drop_index("ix_job_snapshots_source", table_name="job_snapshots")
    op.drop_index("ix_job_snapshots_observed_at", table_name="job_snapshots")
    op.drop_table("job_snapshots")
    op.drop_index("ix_job_postings_title", table_name="job_postings")
    op.drop_index("ix_job_postings_source", table_name="job_postings")
    op.drop_index("ix_job_postings_company_name", table_name="job_postings")
    op.drop_index("ix_job_postings_board_token", table_name="job_postings")
    op.drop_table("job_postings")
