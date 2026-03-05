"""add style tokens to carousel_design

Revision ID: 0002_style_tokens
Revises: 0001_init
Create Date: 2026-03-04 13:40:00
"""

from alembic import op


revision = "0002_style_tokens"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE carousel_design
        ADD COLUMN IF NOT EXISTS style_tokens JSONB NOT NULL DEFAULT '{}'::jsonb
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE carousel_design
        DROP COLUMN IF EXISTS style_tokens
        """
    )
