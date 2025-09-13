"""Add composite indexes for export filters"""

from alembic import op
import sqlalchemy as sa

revision = 'c4714aaaa904'
down_revision = '9ffc41598ab9'
branch_labels = None
depends_on = None

def upgrade():
    op.create_index("ix_ticket_event_used", "ticket", ["event", "used"])
    op.create_index("ix_ticket_event_scanned_by", "ticket", ["event", "scanned_by"])

def downgrade():
    op.drop_index("ix_ticket_event_used", table_name="ticket")
    op.drop_index("ix_ticket_event_scanned_by", table_name="ticket")
