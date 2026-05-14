"""create logs table

Revision ID: a1b2c3d4e5f6
Revises: 3594fe773255
Create Date: 2026-05-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '3594fe773255'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Create UserAction enum
    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'useraction')"))
    if not result.scalar():
        op.execute("""CREATE TYPE useraction AS ENUM (
            'Login','Logout','Signup','Profile View','Profile Update',
            'Referral Link Create','Referral Link View','Click Track',
            'Conversion Record','Resource View','Resource Upload','Admin Action'
        )""")

    # Create ActionStatus enum
    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'actionstatus')"))
    if not result.scalar():
        op.execute("CREATE TYPE actionstatus AS ENUM ('Success', 'Failed')")

    # Create LogFailureReason enum
    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'logfailurereason')"))
    if not result.scalar():
        op.execute("""CREATE TYPE logfailurereason AS ENUM (
            'Invalid Credentials','Account Locked','Email Not Verified','Invalid OTP',
            'OTP Expired','Weak Password','Password Mismatch','Email Already Exists',
            'Invalid Input','Rate Limit Exceeded','Network Error','Database Error',
            'Kafka Error','Token Expired','Insufficient Permissions'
        )""")

    # Create logs table (guarded)
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'logs')"
    ))
    if not result.scalar():
        useraction_type = postgresql.ENUM(
            'Login', 'Logout', 'Signup', 'Profile View', 'Profile Update',
            'Referral Link Create', 'Referral Link View', 'Click Track',
            'Conversion Record', 'Resource View', 'Resource Upload', 'Admin Action',
            name='useraction', create_type=False,
        )
        actionstatus_type = postgresql.ENUM(
            'Success', 'Failed',
            name='actionstatus', create_type=False,
        )
        logfailurereason_type = postgresql.ENUM(
            'Invalid Credentials', 'Account Locked', 'Email Not Verified', 'Invalid OTP',
            'OTP Expired', 'Weak Password', 'Password Mismatch', 'Email Already Exists',
            'Invalid Input', 'Rate Limit Exceeded', 'Network Error', 'Database Error',
            'Kafka Error', 'Token Expired', 'Insufficient Permissions',
            name='logfailurereason', create_type=False,
        )
        op.create_table(
            'logs',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('email', sa.String(320), nullable=True),
            sa.Column('responsibility_category', sa.String(50), nullable=True),
            sa.Column('action', useraction_type, nullable=False),
            sa.Column('status', actionstatus_type, nullable=False),
            sa.Column('failure_reason', logfailurereason_type, nullable=True),
            sa.Column('ip_address', sa.String(45), nullable=True),
            sa.Column('location', sa.String(100), nullable=True),
            sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('synced_to_kafka', sa.Boolean(), nullable=False, server_default=sa.text('false')),
            sa.Column('retry_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_logs_id', 'logs', ['id'])
        op.create_index('ix_logs_user_id', 'logs', ['user_id'])
        op.create_index('ix_logs_email', 'logs', ['email'])
        op.create_index('ix_logs_action', 'logs', ['action'])
        op.create_index('ix_logs_status', 'logs', ['status'])
        op.create_index('ix_logs_timestamp', 'logs', ['timestamp'])
        op.create_index('ix_logs_synced_to_kafka', 'logs', ['synced_to_kafka'])


def downgrade() -> None:
    op.drop_index('ix_logs_synced_to_kafka', table_name='logs')
    op.drop_index('ix_logs_timestamp', table_name='logs')
    op.drop_index('ix_logs_status', table_name='logs')
    op.drop_index('ix_logs_action', table_name='logs')
    op.drop_index('ix_logs_email', table_name='logs')
    op.drop_index('ix_logs_user_id', table_name='logs')
    op.drop_index('ix_logs_id', table_name='logs')
    op.drop_table('logs')
    op.execute("DROP TYPE IF EXISTS logfailurereason")
    op.execute("DROP TYPE IF EXISTS actionstatus")
    op.execute("DROP TYPE IF EXISTS useraction")
