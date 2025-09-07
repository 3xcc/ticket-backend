"""Make ticket fields nullable

Revision ID: a269f8450e55
Revises: add_ticket_number
Create Date: 2025-09-07 09:05:02.749996
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a269f8450e55'
down_revision = 'add_ticket_number'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('ticket', 'name',
        existing_type=sa.VARCHAR(),
        nullable=True)
    op.alter_column('ticket', 'id_card_number',
        existing_type=sa.VARCHAR(),
        nullable=True)
    op.alter_column('ticket', 'date_of_birth',
        existing_type=sa.VARCHAR(),
        nullable=True)
    op.alter_column('ticket', 'phone_number',
        existing_type=sa.VARCHAR(),
        nullable=True)

def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('ticket', 'phone_number',
        existing_type=sa.VARCHAR(),
        nullable=False)
    op.alter_column('ticket', 'date_of_birth',
        existing_type=sa.VARCHAR(),
        nullable=False)
    op.alter_column('ticket', 'id_card_number',
        existing_type=sa.VARCHAR(),
        nullable=False)
    op.alter_column('ticket', 'name',
        existing_type=sa.VARCHAR(),
        nullable=False)
