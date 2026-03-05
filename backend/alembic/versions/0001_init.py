"""init schema

Revision ID: 0001_init
Revises:
Create Date: 2026-03-04 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("kind", sa.String(length=64), nullable=False),
        sa.Column("bucket", sa.String(length=128), nullable=False),
        sa.Column("object_key", sa.String(length=512), nullable=False),
        sa.Column("mime", sa.String(length=128), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assets_object_key"), "assets", ["object_key"], unique=True)

    op.create_table(
        "carousels",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_payload", sa.JSON(), nullable=False),
        sa.Column("language", sa.String(length=8), nullable=False),
        sa.Column("slides_count", sa.Integer(), nullable=False),
        sa.Column("style_hint", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "carousel_design",
        sa.Column("carousel_id", sa.String(length=36), nullable=False),
        sa.Column("template", sa.String(length=32), nullable=False),
        sa.Column("bg_type", sa.String(length=16), nullable=False),
        sa.Column("bg_value", sa.String(length=512), nullable=False),
        sa.Column("bg_overlay", sa.Float(), nullable=False),
        sa.Column("layout_padding", sa.Integer(), nullable=False),
        sa.Column("align_x", sa.String(length=16), nullable=False),
        sa.Column("align_y", sa.String(length=16), nullable=False),
        sa.Column("show_header", sa.Boolean(), nullable=False),
        sa.Column("show_footer", sa.Boolean(), nullable=False),
        sa.Column("header_text", sa.String(length=255), nullable=False),
        sa.Column("footer_text", sa.String(length=255), nullable=False),
        sa.Column("apply_all_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["carousel_id"], ["carousels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("carousel_id"),
    )

    op.create_table(
        "slides",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("carousel_id", sa.String(length=36), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("footer_cta", sa.String(length=300), nullable=True),
        sa.Column("design_overrides", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["carousel_id"], ["carousels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_slides_carousel_id"), "slides", ["carousel_id"], unique=False)

    op.create_table(
        "generation_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("carousel_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("estimated_tokens", sa.Integer(), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("cost_usd_estimate", sa.Float(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["carousel_id"], ["carousels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_generation_jobs_carousel_id"),
        "generation_jobs",
        ["carousel_id"],
        unique=False,
    )

    op.create_table(
        "export_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("carousel_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("format", sa.String(length=8), nullable=False),
        sa.Column("slides_count", sa.Integer(), nullable=False),
        sa.Column("zip_asset_id", sa.String(length=36), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["carousel_id"], ["carousels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["zip_asset_id"], ["assets.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_export_jobs_carousel_id"), "export_jobs", ["carousel_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_export_jobs_carousel_id"), table_name="export_jobs")
    op.drop_table("export_jobs")
    op.drop_index(op.f("ix_generation_jobs_carousel_id"), table_name="generation_jobs")
    op.drop_table("generation_jobs")
    op.drop_index(op.f("ix_slides_carousel_id"), table_name="slides")
    op.drop_table("slides")
    op.drop_table("carousel_design")
    op.drop_table("carousels")
    op.drop_index(op.f("ix_assets_object_key"), table_name="assets")
    op.drop_table("assets")

