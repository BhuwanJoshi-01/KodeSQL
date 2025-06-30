"""
Management command to create a verified superuser.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from getpass import getpass
import sys

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser with email verification already completed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for the superuser',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the superuser',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the superuser (not recommended for security)',
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Do not prompt for input (requires all fields to be provided)',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        username = options.get('username')
        password = options.get('password')
        noinput = options.get('noinput')

        # Get email
        if not email:
            if noinput:
                self.stdout.write(
                    self.style.ERROR('Email is required when using --noinput')
                )
                sys.exit(1)
            
            while True:
                email = input('Email address: ').strip()
                if email:
                    try:
                        validate_email(email)
                        break
                    except ValidationError:
                        self.stdout.write(
                            self.style.ERROR('Please enter a valid email address.')
                        )
                else:
                    self.stdout.write(
                        self.style.ERROR('Email address is required.')
                    )

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'User with email {email} already exists.')
            )
            sys.exit(1)

        # Get username
        if not username:
            if noinput:
                # Use email as username if not provided
                username = email.split('@')[0]
            else:
                username = input(f'Username (default: {email.split("@")[0]}): ').strip()
                if not username:
                    username = email.split('@')[0]

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'User with username {username} already exists.')
            )
            sys.exit(1)

        # Get password
        if not password:
            if noinput:
                self.stdout.write(
                    self.style.ERROR('Password is required when using --noinput')
                )
                sys.exit(1)
            
            while True:
                password = getpass('Password: ')
                if not password:
                    self.stdout.write(
                        self.style.ERROR('Password cannot be empty.')
                    )
                    continue
                
                password_confirm = getpass('Password (again): ')
                if password != password_confirm:
                    self.stdout.write(
                        self.style.ERROR('Passwords do not match.')
                    )
                    continue
                
                if len(password) < 8:
                    self.stdout.write(
                        self.style.ERROR('Password must be at least 8 characters long.')
                    )
                    continue
                
                break

        try:
            # Create the superuser
            user = User.objects.create_superuser(
                email=email,
                username=username,
                password=password
            )
            
            # Mark email as verified
            user.is_email_verified = True
            user.save()

            # Create user profile if it doesn't exist
            from users.models import UserProfile, UserDatabase
            
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user)
                self.stdout.write(
                    self.style.SUCCESS('✅ User profile created')
                )

            # Create user database if it doesn't exist
            if not hasattr(user, 'database'):
                UserDatabase.objects.create(user=user)
                self.stdout.write(
                    self.style.SUCCESS('✅ User database created')
                )

            self.stdout.write(
                self.style.SUCCESS(f'✅ Verified superuser created successfully!')
            )
            self.stdout.write(f'   Email: {email}')
            self.stdout.write(f'   Username: {username}')
            self.stdout.write(f'   Email Verified: {user.is_email_verified}')
            self.stdout.write(f'   Is Superuser: {user.is_superuser}')
            self.stdout.write(f'   Is Staff: {user.is_staff}')
            
            self.stdout.write(
                self.style.WARNING('\n🔐 You can now login with these credentials.')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to create superuser: {e}')
            )
            sys.exit(1)
