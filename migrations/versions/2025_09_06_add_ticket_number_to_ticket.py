"""add ticket_number to Ticket

Revision ID: add_ticket_number
Revises: 
Create Date: 2025-09-06 20:58:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'add_ticket_number'
down_revision = None  # or your last migration ID if you have one
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'ticket',
        sa.Column('ticket_number', sa.String(), nullable=True)
    )
    op.create_index(
        op.f('ix_ticket_ticket_number'),
        'ticket',
        ['ticket_number'],
        unique=True
    )


def downgrade():
    op.drop_index(op.f('ix_ticket_ticket_number'), table_name='ticket')
    op.drop_column('ticket', 'ticket_number')
