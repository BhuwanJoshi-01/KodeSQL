"""
Management command to fix database table issues, particularly for custom User model.
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Fix database table issues, particularly missing many-to-many tables for custom User model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Only check for issues without fixing them',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database table fix...'))

        check_only = options['check_only']

        # Check and fix user model tables
        self.check_user_model_tables(check_only)

        # Check and fix admin log foreign key
        self.fix_admin_log_foreign_key(check_only)

        # Check and fix admin permissions
        self.fix_admin_permissions(check_only)

        if check_only:
            self.stdout.write(self.style.SUCCESS('Database check completed.'))
        else:
            self.stdout.write(self.style.SUCCESS('Database fix completed successfully!'))

    def check_user_model_tables(self, check_only=False):
        """Check and fix custom user model many-to-many tables"""
        self.stdout.write('Checking custom user model tables...')
        
        User = get_user_model()
        table_name = User._meta.db_table
        
        with connection.cursor() as cursor:
            # Check if users_user_groups table exists
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}_groups;")
                count = cursor.fetchone()[0]
                self.stdout.write(f"✓ {table_name}_groups table exists with {count} records")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"✗ {table_name}_groups table missing: {e}"))
                
                if not check_only:
                    self.create_user_groups_table(cursor, table_name)
            
            # Check if users_user_user_permissions table exists
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}_user_permissions;")
                count = cursor.fetchone()[0]
                self.stdout.write(f"✓ {table_name}_user_permissions table exists with {count} records")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"✗ {table_name}_user_permissions table missing: {e}"))
                
                if not check_only:
                    self.create_user_permissions_table(cursor, table_name)

    def create_user_groups_table(self, cursor, table_name):
        """Create the missing users_user_groups table"""
        try:
            self.stdout.write(f'Creating {table_name}_groups table...')
            
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name}_groups (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES {table_name}(id) ON DELETE CASCADE,
                    group_id INTEGER NOT NULL REFERENCES auth_group(id) ON DELETE CASCADE,
                    UNIQUE(user_id, group_id)
                );
            """)
            
            # Create indexes
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {table_name}_groups_user_id_idx 
                ON {table_name}_groups(user_id);
            """)
            
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {table_name}_groups_group_id_idx 
                ON {table_name}_groups(group_id);
            """)
            
            self.stdout.write(self.style.SUCCESS(f'✓ Created {table_name}_groups table'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error creating {table_name}_groups table: {e}'))

    def create_user_permissions_table(self, cursor, table_name):
        """Create the missing users_user_user_permissions table"""
        try:
            self.stdout.write(f'Creating {table_name}_user_permissions table...')
            
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name}_user_permissions (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES {table_name}(id) ON DELETE CASCADE,
                    permission_id INTEGER NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,
                    UNIQUE(user_id, permission_id)
                );
            """)
            
            # Create indexes
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {table_name}_user_permissions_user_id_idx 
                ON {table_name}_user_permissions(user_id);
            """)
            
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {table_name}_user_permissions_permission_id_idx 
                ON {table_name}_user_permissions(permission_id);
            """)
            
            self.stdout.write(self.style.SUCCESS(f'✓ Created {table_name}_user_permissions table'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error creating {table_name}_user_permissions table: {e}'))

    def fix_admin_permissions(self, check_only=False):
        """Fix admin permissions for superusers"""
        self.stdout.write('Checking admin permissions...')
        
        try:
            User = get_user_model()
            superusers = User.objects.filter(is_superuser=True)
            
            self.stdout.write(f'Found {superusers.count()} superusers')
            
            for user in superusers:
                issues_fixed = 0
                
                if not user.is_staff:
                    if not check_only:
                        user.is_staff = True
                        user.save()
                    self.stdout.write(f'{"✓ Fixed" if not check_only else "✗ Issue:"} is_staff=False for {user.email}')
                    issues_fixed += 1
                
                if not user.is_active:
                    if not check_only:
                        user.is_active = True
                        user.save()
                    self.stdout.write(f'{"✓ Fixed" if not check_only else "✗ Issue:"} is_active=False for {user.email}')
                    issues_fixed += 1
                
                if issues_fixed == 0:
                    self.stdout.write(f'✓ {user.email} permissions are correct')
            
            if not check_only:
                self.stdout.write(self.style.SUCCESS('✓ Admin permissions fixed'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error fixing admin permissions: {e}'))

    def fix_admin_log_foreign_key(self, check_only=False):
        """Fix django_admin_log foreign key constraint to point to custom user model"""
        self.stdout.write('Checking django_admin_log foreign key constraint...')

        User = get_user_model()
        user_table = User._meta.db_table

        with connection.cursor() as cursor:
            try:
                # Check current foreign key constraints
                cursor.execute("""
                    SELECT tc.constraint_name, ccu.table_name AS foreign_table_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_name='django_admin_log'
                        AND tc.constraint_name LIKE '%user_id%';
                """)

                constraints = cursor.fetchall()

                # Check if constraint points to wrong table
                wrong_constraint = None
                for constraint_name, foreign_table in constraints:
                    if foreign_table == 'auth_user':
                        wrong_constraint = constraint_name
                        self.stdout.write(f'✗ Found incorrect constraint: {constraint_name} -> auth_user')
                        break
                    elif foreign_table == user_table:
                        self.stdout.write(f'✓ Correct constraint found: {constraint_name} -> {user_table}')
                        return

                if wrong_constraint and not check_only:
                    # Fix the constraint
                    self.stdout.write('Fixing django_admin_log foreign key constraint...')

                    # Check for invalid entries first
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM django_admin_log
                        WHERE user_id NOT IN (SELECT id FROM {user_table});
                    """)

                    invalid_entries = cursor.fetchone()[0]
                    if invalid_entries > 0:
                        self.stdout.write(f'Cleaning up {invalid_entries} invalid admin log entries...')
                        cursor.execute(f"""
                            DELETE FROM django_admin_log
                            WHERE user_id NOT IN (SELECT id FROM {user_table});
                        """)

                    # Drop the wrong constraint
                    cursor.execute(f"ALTER TABLE django_admin_log DROP CONSTRAINT IF EXISTS {wrong_constraint};")

                    # Add the correct constraint
                    cursor.execute(f"""
                        ALTER TABLE django_admin_log
                        ADD CONSTRAINT django_admin_log_user_id_fk_{user_table}_id
                        FOREIGN KEY (user_id) REFERENCES {user_table}(id) ON DELETE CASCADE;
                    """)

                    self.stdout.write(self.style.SUCCESS('✓ Fixed django_admin_log foreign key constraint'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error fixing admin log constraint: {e}'))
