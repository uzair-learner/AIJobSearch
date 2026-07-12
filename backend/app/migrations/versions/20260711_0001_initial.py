"""Initial VisaSponsor Jobs schema."""

from alembic import op
import sqlalchemy as sa

revision = "20260711_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=120)),
        sa.Column("state", sa.String(length=50)),
        sa.Column("postal_code", sa.String(length=20)),
        sa.Column("country", sa.String(length=100)),
        sa.Column("website", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_employers_normalized_name", "employers", ["normalized_name"])
    op.create_table(
        "occupations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("soc_code", sa.String(length=20), nullable=False),
        sa.Column("soc_title", sa.String(length=255), nullable=False),
        sa.Column("profession_category", sa.String(length=100)),
        sa.Column("normalized_title", sa.String(length=255), nullable=False),
        sa.Column("is_it_profession", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("source_year", sa.Integer()),
    )
    op.create_index("ix_occupations_soc_code", "occupations", ["soc_code"])
    op.create_index("ix_occupations_normalized_title", "occupations", ["normalized_title"])
    op.create_table(
        "employer_aliases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employer_id", sa.Integer(), sa.ForeignKey("employers.id"), nullable=False),
        sa.Column("alias_name", sa.String(length=255), nullable=False),
        sa.Column("normalized_alias", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default=sa.text("1.0")),
        sa.Column("manually_verified", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )
    op.create_index("ix_employer_aliases_employer_id", "employer_aliases", ["employer_id"])
    op.create_index("ix_employer_aliases_normalized_alias", "employer_aliases", ["normalized_alias"])
    op.create_table(
        "perm_cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_number", sa.String(length=80), nullable=False),
        sa.Column("employer_id", sa.Integer(), sa.ForeignKey("employers.id"), nullable=False),
        sa.Column("fiscal_year", sa.Integer(), nullable=False),
        sa.Column("case_status", sa.String(length=80), nullable=False),
        sa.Column("filing_date", sa.Date()),
        sa.Column("decision_date", sa.Date()),
        sa.Column("job_title", sa.String(length=255)),
        sa.Column("occupation_id", sa.Integer(), sa.ForeignKey("occupations.id")),
        sa.Column("original_soc_code", sa.String(length=20)),
        sa.Column("original_soc_title", sa.String(length=255)),
        sa.Column("worksite_city", sa.String(length=120)),
        sa.Column("worksite_state", sa.String(length=50)),
        sa.Column("worksite_postal_code", sa.String(length=20)),
        sa.Column("offered_wage_from", sa.Float()),
        sa.Column("offered_wage_to", sa.Float()),
        sa.Column("wage_unit", sa.String(length=50)),
        sa.Column("minimum_education", sa.String(length=120)),
        sa.Column("major_field", sa.String(length=120)),
        sa.Column("experience_required", sa.String(length=120)),
        sa.Column("foreign_worker_education", sa.String(length=120)),
        sa.Column("source_file", sa.String(length=255)),
        sa.Column("source_url", sa.String(length=500)),
        sa.Column("imported_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("source_updated_at", sa.DateTime()),
        sa.UniqueConstraint("case_number"),
    )
    op.create_index("ix_perm_cases_employer_id", "perm_cases", ["employer_id"])
    op.create_index("ix_perm_cases_fiscal_year", "perm_cases", ["fiscal_year"])
    op.create_index("ix_perm_cases_case_status", "perm_cases", ["case_status"])
    op.create_index("ix_perm_cases_worksite_state", "perm_cases", ["worksite_state"])
    op.create_table(
        "h1b_employer_statistics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employer_id", sa.Integer(), sa.ForeignKey("employers.id"), nullable=False),
        sa.Column("fiscal_year", sa.Integer(), nullable=False),
        sa.Column("initial_approvals", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("initial_denials", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("continuing_approvals", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("continuing_denials", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("source_updated_at", sa.DateTime()),
    )
    op.create_index("ix_h1b_employer_statistics_employer_id", "h1b_employer_statistics", ["employer_id"])
    op.create_index("ix_h1b_employer_statistics_fiscal_year", "h1b_employer_statistics", ["fiscal_year"])
    op.create_table(
        "current_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_job_id", sa.String(length=120), nullable=False),
        sa.Column("employer_id", sa.Integer(), sa.ForeignKey("employers.id"), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("city", sa.String(length=120)),
        sa.Column("state", sa.String(length=50)),
        sa.Column("remote_type", sa.String(length=50)),
        sa.Column("employment_type", sa.String(length=50)),
        sa.Column("posted_date", sa.Date()),
        sa.Column("retrieved_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime()),
        sa.Column("occupation_id", sa.Integer(), sa.ForeignKey("occupations.id")),
        sa.Column("sponsorship_classification", sa.String(length=80), nullable=False),
        sa.Column("sponsorship_score", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("sponsorship_reasons", sa.Text(), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.UniqueConstraint("external_job_id"),
    )
    op.create_index("ix_current_jobs_employer_id", "current_jobs", ["employer_id"])
    op.create_index("ix_current_jobs_state", "current_jobs", ["state"])
    op.create_index("ix_current_jobs_sponsorship_classification", "current_jobs", ["sponsorship_classification"])
    op.create_table(
        "data_imports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_name", sa.String(length=120), nullable=False),
        sa.Column("source_url", sa.String(length=500)),
        sa.Column("fiscal_year", sa.Integer()),
        sa.Column("reporting_period", sa.String(length=80)),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_hash", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("records_processed", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("records_inserted", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("records_updated", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("records_rejected", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime()),
        sa.Column("error_message", sa.Text()),
    )
    op.create_index("ix_data_imports_fiscal_year", "data_imports", ["fiscal_year"])
    op.create_index("ix_data_imports_file_hash", "data_imports", ["file_hash"])
    op.create_index("ix_data_imports_status", "data_imports", ["status"])
    op.create_table(
        "saved_searches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("search_filters", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("last_run_at", sa.DateTime()),
    )


def downgrade() -> None:
    op.drop_table("saved_searches")
    op.drop_index("ix_data_imports_status", table_name="data_imports")
    op.drop_index("ix_data_imports_file_hash", table_name="data_imports")
    op.drop_index("ix_data_imports_fiscal_year", table_name="data_imports")
    op.drop_table("data_imports")
    op.drop_index("ix_current_jobs_sponsorship_classification", table_name="current_jobs")
    op.drop_index("ix_current_jobs_state", table_name="current_jobs")
    op.drop_index("ix_current_jobs_employer_id", table_name="current_jobs")
    op.drop_table("current_jobs")
    op.drop_index("ix_h1b_employer_statistics_fiscal_year", table_name="h1b_employer_statistics")
    op.drop_index("ix_h1b_employer_statistics_employer_id", table_name="h1b_employer_statistics")
    op.drop_table("h1b_employer_statistics")
    op.drop_index("ix_perm_cases_worksite_state", table_name="perm_cases")
    op.drop_index("ix_perm_cases_case_status", table_name="perm_cases")
    op.drop_index("ix_perm_cases_fiscal_year", table_name="perm_cases")
    op.drop_index("ix_perm_cases_employer_id", table_name="perm_cases")
    op.drop_table("perm_cases")
    op.drop_index("ix_employer_aliases_normalized_alias", table_name="employer_aliases")
    op.drop_index("ix_employer_aliases_employer_id", table_name="employer_aliases")
    op.drop_table("employer_aliases")
    op.drop_index("ix_occupations_normalized_title", table_name="occupations")
    op.drop_index("ix_occupations_soc_code", table_name="occupations")
    op.drop_table("occupations")
    op.drop_index("ix_employers_normalized_name", table_name="employers")
    op.drop_table("employers")
