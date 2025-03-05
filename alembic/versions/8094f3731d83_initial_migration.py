"""Initial migration

Revision ID: 8094f3731d83
Revises: 
Create Date: 2025-02-09 12:23:10.146239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8094f3731d83'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('auth_user_groups_group_id_97559544', table_name='auth_user_groups')
    op.drop_index('auth_user_groups_user_id_6a12ed8b', table_name='auth_user_groups')
    op.drop_index('auth_user_groups_user_id_group_id_94350c0c_uniq', table_name='auth_user_groups')
    op.drop_table('auth_user_groups')
    op.drop_table('django_migrations')
    op.drop_index('api_securitygroup_securities_security_id_e3472a40', table_name='api_securitygroup_securities')
    op.drop_index('api_securitygroup_securities_securitygroup_id_2e09c76b', table_name='api_securitygroup_securities')
    op.drop_index('api_securitygroup_securities_securitygroup_id_security_id_c4cdfb60_uniq', table_name='api_securitygroup_securities')
    op.drop_table('api_securitygroup_securities')
    op.drop_index('auth_permission_content_type_id_2f476e4b', table_name='auth_permission')
    op.drop_index('auth_permission_content_type_id_codename_01ab375a_uniq', table_name='auth_permission')
    op.drop_table('auth_permission')
    op.drop_index('auth_user_user_permissions_permission_id_1fbb5f2c', table_name='auth_user_user_permissions')
    op.drop_index('auth_user_user_permissions_user_id_a95ead1b', table_name='auth_user_user_permissions')
    op.drop_index('auth_user_user_permissions_user_id_permission_id_14a6b632_uniq', table_name='auth_user_user_permissions')
    op.drop_table('auth_user_user_permissions')
    op.drop_index('auth_group_permissions_group_id_b120cbf9', table_name='auth_group_permissions')
    op.drop_index('auth_group_permissions_group_id_permission_id_0cd325b0_uniq', table_name='auth_group_permissions')
    op.drop_index('auth_group_permissions_permission_id_84c5c92e', table_name='auth_group_permissions')
    op.drop_table('auth_group_permissions')
    op.drop_table('auth_group')
    op.drop_index('api_deposit_account_id_83ae4386', table_name='api_deposit')
    op.drop_table('api_deposit')
    op.drop_index('api_account_account_broker_id_4ed4db29', table_name='api_account')
    op.drop_index('api_account_linked_account_id_c7c760cf', table_name='api_account')
    op.drop_table('api_account')
    op.drop_index('django_content_type_app_label_model_76bd3d3b_uniq', table_name='django_content_type')
    op.drop_table('django_content_type')
    op.drop_table('api_broker')
    op.drop_index('django_session_expire_date_a5c62663', table_name='django_session')
    op.drop_table('django_session')
    op.drop_index('api_activity_account_id_a1e901b1', table_name='api_activity')
    op.drop_index('api_activity_security_id_f7f9e99c', table_name='api_activity')
    op.drop_table('api_activity')
    op.drop_table('auth_user')
    op.drop_index('api_accountposition_account_id_f69428e0', table_name='api_accountposition')
    op.drop_index('api_accountposition_security_id_4b2c6668', table_name='api_accountposition')
    op.drop_table('api_accountposition')
    op.drop_table('api_securitygroup')
    op.drop_index('django_admin_log_content_type_id_c4bce8eb', table_name='django_admin_log')
    op.drop_index('django_admin_log_user_id_c564eba6', table_name='django_admin_log')
    op.drop_table('django_admin_log')
    op.drop_table('api_security')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('api_security',
    sa.Column('id', sa.VARCHAR(length=255), nullable=False),
    sa.Column('symbol', sa.VARCHAR(length=20), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), nullable=True),
    sa.Column('type', sa.VARCHAR(length=50), nullable=True),
    sa.Column('currency', sa.VARCHAR(length=50), nullable=True),
    sa.Column('status', sa.VARCHAR(length=50), nullable=True),
    sa.Column('exchange', sa.VARCHAR(length=50), nullable=True),
    sa.Column('active_date', sa.DATETIME(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.Column('last_synced', sa.DATETIME(), nullable=False),
    sa.Column('description', sa.VARCHAR(length=255), nullable=True),
    sa.Column('buyable', sa.BOOLEAN(), nullable=False),
    sa.Column('option_details', sa.TEXT(), nullable=True),
    sa.Column('options_eligible', sa.BOOLEAN(), nullable=False),
    sa.Column('order_subtypes', sa.TEXT(), nullable=True),
    sa.Column('sellable', sa.BOOLEAN(), nullable=False),
    sa.Column('trade_eligible', sa.BOOLEAN(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('django_admin_log',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('object_id', sa.TEXT(), nullable=True),
    sa.Column('object_repr', sa.VARCHAR(length=200), nullable=False),
    sa.Column('action_flag', sa.INTEGER(), nullable=False),
    sa.Column('change_message', sa.TEXT(), nullable=False),
    sa.Column('content_type_id', sa.INTEGER(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('action_time', sa.DATETIME(), nullable=False),
    sa.CheckConstraint('"action_flag" >= 0), "change_message" text NOT NULL, "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "action_time" datetime NOT NULL'),
    sa.ForeignKeyConstraint(['content_type_id'], ['django_content_type.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['auth_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('django_admin_log_user_id_c564eba6', 'django_admin_log', ['user_id'], unique=False)
    op.create_index('django_admin_log_content_type_id_c4bce8eb', 'django_admin_log', ['content_type_id'], unique=False)
    op.create_table('api_securitygroup',
    sa.Column('id', sa.VARCHAR(length=255), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), nullable=True),
    sa.Column('description', sa.VARCHAR(length=255), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('api_accountposition',
    sa.Column('id', sa.CHAR(length=32), nullable=False),
    sa.Column('quantity', sa.DECIMAL(), nullable=True),
    sa.Column('amount', sa.DECIMAL(), nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.Column('updated_at', sa.DATETIME(), nullable=False),
    sa.Column('account_id', sa.VARCHAR(length=20), nullable=False),
    sa.Column('security_id', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['api_account.account_number'], ),
    sa.ForeignKeyConstraint(['security_id'], ['api_security.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('security_id', 'account_id', name='account_security_key')
    )
    op.create_index('api_accountposition_security_id_4b2c6668', 'api_accountposition', ['security_id'], unique=False)
    op.create_index('api_accountposition_account_id_f69428e0', 'api_accountposition', ['account_id'], unique=False)
    op.create_table('auth_user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('password', sa.VARCHAR(length=128), nullable=False),
    sa.Column('last_login', sa.DATETIME(), nullable=True),
    sa.Column('is_superuser', sa.BOOLEAN(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=150), nullable=False),
    sa.Column('last_name', sa.VARCHAR(length=150), nullable=False),
    sa.Column('email', sa.VARCHAR(length=254), nullable=False),
    sa.Column('is_staff', sa.BOOLEAN(), nullable=False),
    sa.Column('is_active', sa.BOOLEAN(), nullable=False),
    sa.Column('date_joined', sa.DATETIME(), nullable=False),
    sa.Column('first_name', sa.VARCHAR(length=150), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('api_activity',
    sa.Column('id', sa.VARCHAR(length=255), nullable=False),
    sa.Column('currency', sa.VARCHAR(length=30), nullable=True),
    sa.Column('type', sa.VARCHAR(length=30), nullable=False),
    sa.Column('sub_type', sa.VARCHAR(length=30), nullable=True),
    sa.Column('action', sa.VARCHAR(length=30), nullable=True),
    sa.Column('stop_price', sa.DECIMAL(), nullable=True),
    sa.Column('price', sa.DECIMAL(), nullable=False),
    sa.Column('quantity', sa.DECIMAL(), nullable=False),
    sa.Column('amount', sa.DECIMAL(), nullable=True),
    sa.Column('commission', sa.DECIMAL(), nullable=False),
    sa.Column('option_multiplier', sa.VARCHAR(length=255), nullable=True),
    sa.Column('symbol', sa.VARCHAR(length=255), nullable=True),
    sa.Column('market_currency', sa.VARCHAR(length=20), nullable=True),
    sa.Column('status', sa.VARCHAR(length=20), nullable=True),
    sa.Column('cancelled_at', sa.DATETIME(), nullable=True),
    sa.Column('rejected_at', sa.DATETIME(), nullable=True),
    sa.Column('submitted_at', sa.DATETIME(), nullable=True),
    sa.Column('filled_at', sa.DATETIME(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.Column('last_synced', sa.DATETIME(), nullable=False),
    sa.Column('account_id', sa.VARCHAR(length=20), nullable=False),
    sa.Column('last_updated', sa.DATETIME(), nullable=False),
    sa.Column('security_id', sa.VARCHAR(length=255), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['api_account.account_number'], ),
    sa.ForeignKeyConstraint(['security_id'], ['api_security.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('api_activity_security_id_f7f9e99c', 'api_activity', ['security_id'], unique=False)
    op.create_index('api_activity_account_id_a1e901b1', 'api_activity', ['account_id'], unique=False)
    op.create_table('django_session',
    sa.Column('session_key', sa.VARCHAR(length=40), nullable=False),
    sa.Column('session_data', sa.TEXT(), nullable=False),
    sa.Column('expire_date', sa.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('session_key')
    )
    op.create_index('django_session_expire_date_a5c62663', 'django_session', ['expire_date'], unique=False)
    op.create_table('api_broker',
    sa.Column('id', sa.CHAR(length=32), nullable=False),
    sa.Column('name', sa.VARCHAR(length=20), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('django_content_type',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('app_label', sa.VARCHAR(length=100), nullable=False),
    sa.Column('model', sa.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('django_content_type_app_label_model_76bd3d3b_uniq', 'django_content_type', ['app_label', 'model'], unique=1)
    op.create_table('api_account',
    sa.Column('account_number', sa.VARCHAR(length=20), nullable=False),
    sa.Column('type', sa.VARCHAR(length=20), nullable=False),
    sa.Column('current_balance', sa.DECIMAL(), nullable=False),
    sa.Column('currency', sa.VARCHAR(length=10), nullable=False),
    sa.Column('status', sa.VARCHAR(length=10), nullable=False),
    sa.Column('is_primary', sa.BOOLEAN(), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.Column('updated_at', sa.DATETIME(), nullable=False),
    sa.Column('last_synced', sa.DATETIME(), nullable=False),
    sa.Column('account_broker_id', sa.VARCHAR(length=20), nullable=True),
    sa.Column('net_deposits', sa.DECIMAL(), nullable=False),
    sa.Column('linked_account_id', sa.VARCHAR(length=20), nullable=True),
    sa.ForeignKeyConstraint(['account_broker_id'], ['api_broker.name'], ),
    sa.ForeignKeyConstraint(['linked_account_id'], ['api_account.account_number'], ),
    sa.PrimaryKeyConstraint('account_number')
    )
    op.create_index('api_account_linked_account_id_c7c760cf', 'api_account', ['linked_account_id'], unique=False)
    op.create_index('api_account_account_broker_id_4ed4db29', 'api_account', ['account_broker_id'], unique=False)
    op.create_table('api_deposit',
    sa.Column('id', sa.VARCHAR(length=255), nullable=False),
    sa.Column('bank_account_id', sa.VARCHAR(length=255), nullable=True),
    sa.Column('status', sa.VARCHAR(length=255), nullable=True),
    sa.Column('currency', sa.VARCHAR(length=30), nullable=False),
    sa.Column('amount', sa.DECIMAL(), nullable=True),
    sa.Column('cancelled_at', sa.DATETIME(), nullable=True),
    sa.Column('rejected_at', sa.DATETIME(), nullable=True),
    sa.Column('accepted_at', sa.DATETIME(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.Column('last_synced', sa.DATETIME(), nullable=True),
    sa.Column('account_id', sa.VARCHAR(length=20), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['api_account.account_number'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('api_deposit_account_id_83ae4386', 'api_deposit', ['account_id'], unique=False)
    op.create_table('auth_group',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=150), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('auth_group_permissions',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('group_id', sa.INTEGER(), nullable=False),
    sa.Column('permission_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['auth_group.id'], ),
    sa.ForeignKeyConstraint(['permission_id'], ['auth_permission.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('auth_group_permissions_permission_id_84c5c92e', 'auth_group_permissions', ['permission_id'], unique=False)
    op.create_index('auth_group_permissions_group_id_permission_id_0cd325b0_uniq', 'auth_group_permissions', ['group_id', 'permission_id'], unique=1)
    op.create_index('auth_group_permissions_group_id_b120cbf9', 'auth_group_permissions', ['group_id'], unique=False)
    op.create_table('auth_user_user_permissions',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('permission_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['auth_permission.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['auth_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('auth_user_user_permissions_user_id_permission_id_14a6b632_uniq', 'auth_user_user_permissions', ['user_id', 'permission_id'], unique=1)
    op.create_index('auth_user_user_permissions_user_id_a95ead1b', 'auth_user_user_permissions', ['user_id'], unique=False)
    op.create_index('auth_user_user_permissions_permission_id_1fbb5f2c', 'auth_user_user_permissions', ['permission_id'], unique=False)
    op.create_table('auth_permission',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('content_type_id', sa.INTEGER(), nullable=False),
    sa.Column('codename', sa.VARCHAR(length=100), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['content_type_id'], ['django_content_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('auth_permission_content_type_id_codename_01ab375a_uniq', 'auth_permission', ['content_type_id', 'codename'], unique=1)
    op.create_index('auth_permission_content_type_id_2f476e4b', 'auth_permission', ['content_type_id'], unique=False)
    op.create_table('api_securitygroup_securities',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('securitygroup_id', sa.VARCHAR(length=255), nullable=False),
    sa.Column('security_id', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['security_id'], ['api_security.id'], ),
    sa.ForeignKeyConstraint(['securitygroup_id'], ['api_securitygroup.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('api_securitygroup_securities_securitygroup_id_security_id_c4cdfb60_uniq', 'api_securitygroup_securities', ['securitygroup_id', 'security_id'], unique=1)
    op.create_index('api_securitygroup_securities_securitygroup_id_2e09c76b', 'api_securitygroup_securities', ['securitygroup_id'], unique=False)
    op.create_index('api_securitygroup_securities_security_id_e3472a40', 'api_securitygroup_securities', ['security_id'], unique=False)
    op.create_table('django_migrations',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('app', sa.VARCHAR(length=255), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), nullable=False),
    sa.Column('applied', sa.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('auth_user_groups',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('group_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['auth_group.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['auth_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('auth_user_groups_user_id_group_id_94350c0c_uniq', 'auth_user_groups', ['user_id', 'group_id'], unique=1)
    op.create_index('auth_user_groups_user_id_6a12ed8b', 'auth_user_groups', ['user_id'], unique=False)
    op.create_index('auth_user_groups_group_id_97559544', 'auth_user_groups', ['group_id'], unique=False)
    # ### end Alembic commands ###
