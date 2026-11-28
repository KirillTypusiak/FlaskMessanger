"""Enable user autoincrement

Revision ID: db21260c7aa6
Revises: 527f578d62a0
Create Date: 2026-11-28 14:08:49.429612

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db21260c7aa6'
down_revision = '527f578d62a0'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table(
        "user",
        recreate="always",
        table_kwargs={"sqlite_autoincrement": True}
    ):
        pass


def downgrade():
    with op.batch_alter_table(
        "user",
        recreate="always",
        table_kwargs={"sqlite_autoincrement": False}
    ):
        pass
