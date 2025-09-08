"""Add scanned_by to Ticket

Revision ID: 8ba0f855b6f4
Revises: a269f8450e55
Create Date: 2025-09-08 18:08:37.970455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ba0f855b6f4'
down_revision: Union[str, Sequence[str], None] = 'a269f8450e55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('ticket', sa.Column('scanned_by', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('ticket', 'scanned_by')
