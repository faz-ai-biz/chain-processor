"""Initial database schema

Revision ID: 001_initial
Create Date: 2025-05-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("is_superuser", sa.Boolean(), default=False, nullable=False),
        sa.Column("roles", postgresql.ARRAY(sa.String()), default=[], nullable=False),
        sa.Column("preferences", postgresql.JSONB(), default={}, nullable=False),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("version", sa.Integer(), default=1, nullable=False),
    )
    
    # Create nodes table
    op.create_table(
        "nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("is_builtin", sa.Boolean(), default=False, nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("metadata", postgresql.JSONB(), default={}, nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String()), default=[], nullable=False),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("version", sa.Integer(), default=1, nullable=False),
    )
    
    # Create chain strategies table
    op.create_table(
        "chain_strategies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String()), default=[], nullable=False),
        sa.Column("metadata", postgresql.JSONB(), default={}, nullable=False),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("version", sa.Integer(), default=1, nullable=False),
    )
    
    # Create strategy nodes table
    op.create_table(
        "strategy_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("strategy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chain_strategies.id"), nullable=False),
        sa.Column("node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("nodes.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("config", postgresql.JSONB(), default={}, nullable=False),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create chain executions table
    op.create_table(
        "chain_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("strategy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chain_strategies.id"), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), default="pending", nullable=False),
        sa.Column("started_at", sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("execution_time_ms", sa.Integer(), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), default={}, nullable=False),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("version", sa.Integer(), default=1, nullable=False),
    )
    
    # Create node executions table
    op.create_table(
        "node_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chain_executions.id"), nullable=False),
        sa.Column("node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("nodes.id"), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), default="pending", nullable=False),
        sa.Column("started_at", sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("execution_time_ms", sa.Integer(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), default={}, nullable=False),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create indexes
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_nodes_name"), "nodes", ["name"], unique=False)
    op.create_index(op.f("ix_chain_strategies_name"), "chain_strategies", ["name"], unique=False)
    op.create_index(op.f("ix_strategy_nodes_strategy_id"), "strategy_nodes", ["strategy_id"], unique=False)
    op.create_index(op.f("ix_strategy_nodes_node_id"), "strategy_nodes", ["node_id"], unique=False)
    op.create_index(op.f("ix_chain_executions_strategy_id"), "chain_executions", ["strategy_id"], unique=False)
    op.create_index(op.f("ix_chain_executions_status"), "chain_executions", ["status"], unique=False)
    op.create_index(op.f("ix_node_executions_execution_id"), "node_executions", ["execution_id"], unique=False)
    op.create_index(op.f("ix_node_executions_node_id"), "node_executions", ["node_id"], unique=False)
    op.create_index(op.f("ix_node_executions_status"), "node_executions", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_node_executions_status"), table_name="node_executions")
    op.drop_index(op.f("ix_node_executions_node_id"), table_name="node_executions")
    op.drop_index(op.f("ix_node_executions_execution_id"), table_name="node_executions")
    op.drop_index(op.f("ix_chain_executions_status"), table_name="chain_executions")
    op.drop_index(op.f("ix_chain_executions_strategy_id"), table_name="chain_executions")
    op.drop_index(op.f("ix_strategy_nodes_node_id"), table_name="strategy_nodes")
    op.drop_index(op.f("ix_strategy_nodes_strategy_id"), table_name="strategy_nodes")
    op.drop_index(op.f("ix_chain_strategies_name"), table_name="chain_strategies")
    op.drop_index(op.f("ix_nodes_name"), table_name="nodes")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    
    op.drop_table("node_executions")
    op.drop_table("chain_executions")
    op.drop_table("strategy_nodes")
    op.drop_table("chain_strategies")
    op.drop_table("nodes")
    op.drop_table("users") 