"""Create all initial tables

Revision ID: 2023_initial_tables
Revises: 
Create Date: 2023-10-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '2023_initial_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
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
        sa.Column('role', sa.String(), nullable=False),
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

    # Создание таблицы локаций
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('region', sa.String(), nullable=True),
        sa.Column('postal_code', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=False, server_default=sa.text("'Россия'")),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('additional_info', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_locations_id'), 'locations', ['id'], unique=False)

    # Создание таблицы рабочих часов
    op.create_table(
        'working_hours',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('day', sa.String(), nullable=False),
        sa.Column('open_time', sa.Time(), nullable=True),
        sa.Column('close_time', sa.Time(), nullable=True),
        sa.Column('is_working_day', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_working_hours_id'), 'working_hours', ['id'], unique=False)

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
        sa.Column('type', sa.String(), nullable=False, server_default=sa.text("'regular'")),
        sa.Column('start_date', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_schedules_id'), 'schedules', ['id'], unique=False)
    op.create_index(op.f('ix_schedules_company_id'), 'schedules', ['company_id'], unique=False)
    op.create_index(op.f('ix_schedules_service_id'), 'schedules', ['service_id'], unique=False)

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
    op.create_index(op.f('ix_time_slots_id'), 'time_slots', ['id'], unique=False)
    op.create_index(op.f('ix_time_slots_schedule_id'), 'time_slots', ['schedule_id'], unique=False)
    op.create_index(op.f('ix_time_slots_start_time'), 'time_slots', ['start_time'], unique=False)

    # Создание таблицы бронирований
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('staff_id', sa.Integer(), nullable=True),
        sa.Column('time_slot_id', sa.Integer(), nullable=True),
        sa.Column('client_name', sa.String(), nullable=True),
        sa.Column('client_phone', sa.String(), nullable=True),
        sa.Column('client_email', sa.String(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('is_paid', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('payment_id', sa.String(), nullable=True),
        sa.Column('payment_status', sa.String(), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['staff_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['time_slot_id'], ['time_slots.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)
    op.create_index(op.f('ix_bookings_company_id'), 'bookings', ['company_id'], unique=False)
    op.create_index(op.f('ix_bookings_start_time'), 'bookings', ['start_time'], unique=False)

    # Создание таблицы мультимедиа
    op.create_table(
        'media',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False, server_default=sa.text("'image'")),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_media_id'), 'media', ['id'], unique=False)

    # Создание таблицы аналитики
    op.create_table(
        'analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('date_range_start', sa.DateTime(), nullable=False),
        sa.Column('date_range_end', sa.DateTime(), nullable=False),
        sa.Column('total_revenue', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('total_bookings', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('average_booking_value', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('completion_rate', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('cancellation_rate', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('most_popular_service_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('service_statistics', JSONB(), nullable=True),
        sa.Column('time_statistics', JSONB(), nullable=True),
        sa.Column('client_statistics', JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['most_popular_service_id'], ['services.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analytics_id'), 'analytics', ['id'], unique=False)


def downgrade():
    # Удаление таблиц в обратном порядке
    op.drop_index(op.f('ix_analytics_id'), table_name='analytics')
    op.drop_table('analytics')
    
    op.drop_index(op.f('ix_media_id'), table_name='media')
    op.drop_table('media')
    
    op.drop_index(op.f('ix_bookings_start_time'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_company_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_table('bookings')
    
    op.drop_index(op.f('ix_time_slots_start_time'), table_name='time_slots')
    op.drop_index(op.f('ix_time_slots_schedule_id'), table_name='time_slots')
    op.drop_index(op.f('ix_time_slots_id'), table_name='time_slots')
    op.drop_table('time_slots')
    
    op.drop_index(op.f('ix_schedules_service_id'), table_name='schedules')
    op.drop_index(op.f('ix_schedules_company_id'), table_name='schedules')
    op.drop_index(op.f('ix_schedules_id'), table_name='schedules')
    op.drop_table('schedules')
    
    op.drop_index(op.f('ix_services_company_id'), table_name='services')
    op.drop_index(op.f('ix_services_id'), table_name='services')
    op.drop_table('services')
    
    op.drop_index(op.f('ix_working_hours_id'), table_name='working_hours')
    op.drop_table('working_hours')
    
    op.drop_index(op.f('ix_locations_id'), table_name='locations')
    op.drop_table('locations')
    
    op.drop_index(op.f('ix_companies_name'), table_name='companies')
    op.drop_index(op.f('ix_companies_id'), table_name='companies')
    op.drop_table('companies')
    
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users') 