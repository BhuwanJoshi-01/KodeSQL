"""
Management command to automatically verify email for all superusers.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Mark all superusers as email verified (superusers do not need email verification)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        # Find superusers who are not email verified
        unverified_superusers = User.objects.filter(
            is_superuser=True, 
            is_email_verified=False
        )
        
        count = unverified_superusers.count()
        self.stdout.write(f'Found {count} unverified superusers')
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('All superusers are already email verified!')
            )
            return
        
        if not dry_run:
            updated_count = 0
            for user in unverified_superusers:
                user.is_email_verified = True
                user.save()
                updated_count += 1
                self.stdout.write(f'✅ Verified superuser: {user.email}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully verified {updated_count} superusers'
                )
            )
        else:
            # Show what would be updated
            self.stdout.write('Would verify the following superusers:')
            for user in unverified_superusers:
                self.stdout.write(f'  - {user.email}')
