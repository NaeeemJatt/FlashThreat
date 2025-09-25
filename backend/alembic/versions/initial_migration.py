"""Initial migration

Revision ID: 9f4a7c3e8b1d
Revises: 
Create Date: 2023-09-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9f4a7c3e8b1d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user roles enum
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'analyst')")
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('admin', 'analyst', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    # Create IOC types enum
    op.execute("CREATE TYPE ioctypeenum AS ENUM ('ipv4', 'ipv6', 'domain', 'url', 'hash_md5', 'hash_sha1', 'hash_sha256')")
    
    # Create IOCs table
    op.create_table(
        'iocs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('ipv4', 'ipv6', 'domain', 'url', 'hash_md5', 'hash_sha1', 'hash_sha256', name='ioctypeenum'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    # Create index on IOC value and type
    op.create_index('ix_iocs_value_type', 'iocs', ['value', 'type'])
    op.create_index('ix_iocs_created_at', 'iocs', ['created_at'])
    
    # Create verdict enum
    op.execute("CREATE TYPE verdictenum AS ENUM ('malicious', 'suspicious', 'unknown', 'clean')")
    
    # Create lookups table
    op.create_table(
        'lookups',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ioc_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('iocs.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('finished_at', sa.DateTime(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('verdict', sa.Enum('malicious', 'suspicious', 'unknown', 'clean', name='verdictenum'), nullable=False),
        sa.Column('summary_json', postgresql.JSON(), nullable=True),
        sa.Column('raw_store_ref', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    # Create index on lookup creation time
    op.create_index('ix_lookups_created_at', 'lookups', ['created_at'])
    
    # Create provider results table
    op.create_table(
        'provider_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lookup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lookups.id'), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=False),
        sa.Column('normalized_json', postgresql.JSON(), nullable=False),
        sa.Column('raw_store_ref', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    # Create notes table
    op.create_table(
        'notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lookup_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lookups.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('notes')
    op.drop_table('provider_results')
    op.drop_table('lookups')
    op.drop_table('iocs')
    op.drop_table('users')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS verdictenum")
    op.execute("DROP TYPE IF EXISTS ioctypeenum")
    op.execute("DROP TYPE IF EXISTS userrole")

