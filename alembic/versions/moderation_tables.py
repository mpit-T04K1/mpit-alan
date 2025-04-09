"""Create moderation_records table

Revision ID: 2023_moderation_tables
Revises: 
Create Date: 2023-12-18 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2023_moderation_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Создание таблицы записей модерации
    op.create_table(
        'moderation_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('moderator_id', sa.Integer(), nullable=True),
        sa.Column('auto_check_passed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('moderation_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['moderator_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Создание индексов для быстрого поиска
    op.create_index(op.f('ix_moderation_records_company_id'), 'moderation_records', ['company_id'], unique=False)
    op.create_index(op.f('ix_moderation_records_moderator_id'), 'moderation_records', ['moderator_id'], unique=False)


def downgrade():
    # Удаление таблицы
    op.drop_index(op.f('ix_moderation_records_moderator_id'), table_name='moderation_records')
    op.drop_index(op.f('ix_moderation_records_company_id'), table_name='moderation_records')
    op.drop_table('moderation_records') 