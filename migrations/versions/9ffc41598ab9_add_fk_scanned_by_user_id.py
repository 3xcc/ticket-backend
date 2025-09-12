"""Add FK scanned_by → user.id"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9ffc41598ab9'
down_revision = '47a7fa4f2d2b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(
        constraint_name="ticket_scanned_by_fkey",
        source_table="ticket",
        referent_table="user",
        local_cols=["scanned_by"],
        remote_cols=["id"]
    )


def downgrade():
    op.drop_constraint("ticket_scanned_by_fkey", "ticket", type_="foreignkey")
