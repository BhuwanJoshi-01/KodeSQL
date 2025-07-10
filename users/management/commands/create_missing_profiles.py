"""
Management command to create missing user profiles and databases.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserProfile, UserDatabase

User = get_user_model()


class Command(BaseCommand):
    help = 'Create missing user profiles and databases for existing users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating anything',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        # Find users without profiles
        users_without_profiles = User.objects.filter(profile__isnull=True)
        profile_count = users_without_profiles.count()
        
        # Find users without databases
        users_without_databases = User.objects.filter(database__isnull=True)
        database_count = users_without_databases.count()
        
        self.stdout.write(f'Found {profile_count} users without profiles')
        self.stdout.write(f'Found {database_count} users without databases')
        
        if not dry_run:
            # Create missing profiles
            profiles_created = 0
            for user in users_without_profiles:
                profile, created = UserProfile.objects.get_or_create(user=user)
                if created:
                    profiles_created += 1
                    self.stdout.write(f'Created profile for user: {user.email}')

            # Create missing databases
            databases_created = 0
            for user in users_without_databases:
                database, created = UserDatabase.objects.get_or_create(user=user)
                if created:
                    databases_created += 1
                    self.stdout.write(f'Created database for user: {user.email}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {profiles_created} profiles and {databases_created} databases'
                )
            )
        else:
            # Show what would be created
            if profile_count > 0:
                self.stdout.write('Would create profiles for:')
                for user in users_without_profiles:
                    self.stdout.write(f'  - {user.email}')
            
            if database_count > 0:
                self.stdout.write('Would create databases for:')
                for user in users_without_databases:
                    self.stdout.write(f'  - {user.email}')
