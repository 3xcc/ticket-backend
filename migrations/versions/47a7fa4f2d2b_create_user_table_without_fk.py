"""Create user table without FK

Revision ID: 47a7fa4f2d2b
Revises: 8ba0f855b6f4
Create Date: 2025-09-12 17:37:44.720518
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '47a7fa4f2d2b'
down_revision: Union[str, Sequence[str], None] = '8ba0f855b6f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'SUBADMIN', 'EDITOR', 'SCANNER', name='userrole'), nullable=False),
        sa.Column('token_version', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)

    op.drop_index(op.f('ix_adminuser_email'), table_name='adminuser')
    op.drop_table('adminuser')

    op.alter_column('ticket', 'event',
        existing_type=sa.Text(),
        type_=sa.String(),
        existing_nullable=True
    )
    op.alter_column('ticket', 'used',
        existing_type=sa.Boolean(),
        nullable=False
    )
    op.alter_column('ticket', 'scanned_by',
        existing_type=sa.Integer(),
        type_=sa.String(),
        existing_nullable=True
    )
    op.create_index(op.f('ix_ticket_ticket_id'), 'ticket', ['ticket_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_ticket_ticket_id'), table_name='ticket')

    op.alter_column('ticket', 'scanned_by',
        existing_type=sa.String(),
        type_=sa.Integer(),
        existing_nullable=True
    )
    op.alter_column('ticket', 'used',
        existing_type=sa.Boolean(),
        nullable=True
    )
    op.alter_column('ticket', 'event',
        existing_type=sa.String(),
        type_=sa.Text(),
        existing_nullable=True
    )

    op.create_table(
        'adminuser',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', postgresql.ENUM('ADMIN', 'SUBADMIN', 'EDITOR', 'SCANNER', name='adminrole'), nullable=False),
        sa.Column('token_version', sa.Integer(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=False),
        sa.Column('last_login', postgresql.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('adminuser_pkey'))
    )
    op.create_index(op.f('ix_adminuser_email'), 'adminuser', ['email'], unique=True)

    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
