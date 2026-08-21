"""phase 1 schema

Revision ID: 0001_phase1_schema
Revises:
Create Date: 2026-08-21
"""

from alembic import op

revision = "0001_phase1_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Keep the initial migration compact by delegating full table metadata to SQLAlchemy.
    from tactical_analyst.db.models import Base

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    from tactical_analyst.db.models import Base

    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
