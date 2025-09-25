"""Add bulk job table

Revision ID: add_bulk_job_table
Revises: 9f4a7c3e8b1d
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_bulk_job_table'
down_revision = '9f4a7c3e8b1d'
branch_labels = None
depends_on = None


def upgrade():
    # Create bulk_jobs table
    op.create_table('bulk_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('total_iocs', sa.Integer(), nullable=False),
        sa.Column('processed_iocs', sa.Integer(), nullable=False),
        sa.Column('completed_iocs', sa.Integer(), nullable=False),
        sa.Column('failed_iocs', sa.Integer(), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('ioc_list', sa.JSON(), nullable=False),
        sa.Column('results', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('force_refresh', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('bulk_jobs')
