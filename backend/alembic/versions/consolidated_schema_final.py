"""consolidated_schema_final

Revision ID: consolidated_final
Revises:
Create Date: 2025-12-09 19:35:00.000000

Consolidated migration that creates the complete database schema
including all tables, columns, and relationships from all previous migrations.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'consolidated_final'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create complete database schema with all features."""

    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create collections table
    op.create_table('collections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('embedding_model', sa.String(length=255), nullable=False, server_default='sentence-transformers/all-MiniLM-L6-v2'),
        # Additional columns from later migrations
        sa.Column('subject', sa.String(length=500), nullable=True),
        sa.Column('author', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_collections_id'), 'collections', ['id'], unique=False)
    op.create_index(op.f('ix_collections_name'), 'collections', ['name'], unique=False)
    op.create_index(op.f('ix_collections_subject'), 'collections', ['subject'], unique=False)
    op.create_index(op.f('ix_collections_author'), 'collections', ['author'], unique=False)

    # Create chat_sessions table (with AI settings and voice included)
    op.create_table('chat_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False, server_default='New Chat'),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('collection_id', sa.Integer(), nullable=False),
        sa.Column('llm_model', sa.String(length=100), nullable=False, server_default='ollama'),
        sa.Column('temperature', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('max_tokens', sa.Integer(), nullable=False, server_default='2000'),
        sa.Column('top_k', sa.Integer(), nullable=False, server_default='5'),
        # AI Settings columns
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('custom_instructions', sa.Text(), nullable=True),
        sa.Column('prompt_template', sa.String(length=100), nullable=True),
        sa.Column('ai_personality', sa.String(length=100), nullable=True),
        sa.Column('response_style', sa.String(length=100), nullable=True),
        # Voice column from latest migration
        sa.Column('voice', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['collection_id'], ['collections.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_sessions_id'), 'chat_sessions', ['id'], unique=False)

    # Create documents table
    op.create_table('documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=500), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),  # Added from later migration
        sa.Column('file_path', sa.String(length=1000), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('collection_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('chunk_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('doc_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['collection_id'], ['collections.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_title'), 'documents', ['title'], unique=False)

    # Create messages table (with audio and translation columns included)
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sources', sa.JSON(), nullable=True),
        sa.Column('llm_used', sa.String(length=100), nullable=True),
        # Audio and translation columns
        sa.Column('audio_url', sa.String(length=500), nullable=True),
        sa.Column('translated_content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index(op.f('ix_messages_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_documents_title'), table_name='documents')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')
    op.drop_index(op.f('ix_chat_sessions_id'), table_name='chat_sessions')
    op.drop_table('chat_sessions')
    op.drop_index(op.f('ix_collections_author'), table_name='collections')
    op.drop_index(op.f('ix_collections_subject'), table_name='collections')
    op.drop_index(op.f('ix_collections_name'), table_name='collections')
    op.drop_index(op.f('ix_collections_id'), table_name='collections')
    op.drop_table('collections')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')