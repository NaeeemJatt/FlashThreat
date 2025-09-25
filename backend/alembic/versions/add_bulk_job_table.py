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
    # Create job status enum
    op.execute("CREATE TYPE jobstatus AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled')")
    
    # Create bulk_jobs table
    op.create_table('bulk_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', 'cancelled', name='jobstatus'), nullable=False),
        sa.Column('total_iocs', sa.Integer(), nullable=False, default=0),
        sa.Column('processed_iocs', sa.Integer(), nullable=False, default=0),
        sa.Column('completed_iocs', sa.Integer(), nullable=False, default=0),
        sa.Column('failed_iocs', sa.Integer(), nullable=False, default=0),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('ioc_list', postgresql.JSON(), nullable=False),
        sa.Column('results', postgresql.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('force_refresh', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add foreign key constraint
    op.create_foreign_key('fk_bulk_jobs_user_id', 'bulk_jobs', 'users', ['user_id'], ['id'])
    
    # Create indexes
    op.create_index('ix_bulk_jobs_user_id', 'bulk_jobs', ['user_id'])
    op.create_index('ix_bulk_jobs_status', 'bulk_jobs', ['status'])
    op.create_index('ix_bulk_jobs_created_at', 'bulk_jobs', ['created_at'])


def downgrade():
    # Drop indexes first
    op.drop_index('ix_bulk_jobs_created_at', 'bulk_jobs')
    op.drop_index('ix_bulk_jobs_status', 'bulk_jobs')
    op.drop_index('ix_bulk_jobs_user_id', 'bulk_jobs')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_bulk_jobs_user_id', 'bulk_jobs', type_='foreignkey')
    
    # Drop table
    op.drop_table('bulk_jobs')
    
    # Drop enum
    op.execute("DROP TYPE IF EXISTS jobstatus")
