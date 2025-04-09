"""Create schedules and time_slots tables

Revision ID: 2023_schedule_tables
Revises: 
Create Date: 2023-12-18 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '2023_schedule_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Создание типа данных для ролей пользователей
    conn = op.get_bind()
    res = conn.execute("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole')")
    if not res.scalar():
        op.execute("CREATE TYPE userrole AS ENUM ('ADMIN', 'USER', 'MANAGER', 'OPERATOR')")
    
    # Создание таблицы пользователей
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('avatar', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('role', sa.Enum('ADMIN', 'USER', 'MANAGER', 'OPERATOR', name='userrole'), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('telegram_id', sa.String(50), nullable=True),
        sa.Column('telegram_username', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=False)
    
    # Создание таблицы компаний
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('business_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('contact_name', sa.String(100), nullable=True),
        sa.Column('contact_phone', sa.String(20), nullable=True),
        sa.Column('contact_email', sa.String(100), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('social_links', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('logo_url', sa.String(255), nullable=True),
        sa.Column('cover_image_url', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('company_metadata', JSONB(), nullable=True),
        sa.Column('moderation_status', sa.String(20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('moderation_comment', sa.Text(), nullable=True),
        sa.Column('moderated_at', sa.DateTime(), nullable=True),
        sa.Column('moderated_by', sa.Integer(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('ratings_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['moderated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companies_id'), 'companies', ['id'], unique=False)
    op.create_index(op.f('ix_companies_name'), 'companies', ['name'], unique=False)

    # Создание таблицы услуг
    op.create_table(
        'services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('service_metadata', JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_services_id'), 'services', ['id'], unique=False)
    op.create_index(op.f('ix_services_company_id'), 'services', ['company_id'], unique=False)

    # Создание таблицы расписаний
    op.create_table(
        'schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Создание таблицы временных слотов
    op.create_table(
        'time_slots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('schedule_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('max_clients', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('booked_clients', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default=sa.text("'available'")),
        sa.Column('is_blocked', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['schedule_id'], ['schedules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Создание индексов для быстрого поиска
    op.create_index(op.f('ix_schedules_company_id'), 'schedules', ['company_id'], unique=False)
    op.create_index(op.f('ix_schedules_service_id'), 'schedules', ['service_id'], unique=False)
    op.create_index(op.f('ix_time_slots_schedule_id'), 'time_slots', ['schedule_id'], unique=False)
    op.create_index(op.f('ix_time_slots_start_time'), 'time_slots', ['start_time'], unique=False)


def downgrade():
    # Удаление таблиц
    op.drop_index(op.f('ix_time_slots_start_time'), table_name='time_slots')
    op.drop_index(op.f('ix_time_slots_schedule_id'), table_name='time_slots')
    op.drop_index(op.f('ix_schedules_service_id'), table_name='schedules')
    op.drop_index(op.f('ix_schedules_company_id'), table_name='schedules')
    op.drop_table('time_slots')
    op.drop_table('schedules')
    op.drop_index(op.f('ix_services_company_id'), table_name='services')
    op.drop_index(op.f('ix_services_id'), table_name='services')
    op.drop_table('services')
    op.drop_index(op.f('ix_companies_name'), table_name='companies')
    op.drop_index(op.f('ix_companies_id'), table_name='companies')
    op.drop_table('companies')
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Удаление типа userrole с проверкой существования
    conn = op.get_bind()
    res = conn.execute("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole')")
    if res.scalar():
        op.execute('DROP TYPE userrole')