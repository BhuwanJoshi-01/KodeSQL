"""
Management command to clean up orphaned social accounts.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Clean up orphaned social accounts and tokens'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Clean up social accounts for a specific email address',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        target_email = options.get('email')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Find orphaned social accounts
        orphaned_accounts = []
        orphaned_tokens = []
        
        self.stdout.write('Checking for orphaned social accounts...')
        
        for account in SocialAccount.objects.all():
            try:
                user = User.objects.get(id=account.user_id)
                if target_email and user.email != target_email:
                    continue
            except User.DoesNotExist:
                orphaned_accounts.append(account)
                self.stdout.write(
                    self.style.ERROR(
                        f'Found orphaned social account: User ID {account.user_id}, '
                        f'Provider: {account.provider}, UID: {account.uid}'
                    )
                )
        
        # Find orphaned social tokens
        self.stdout.write('Checking for orphaned social tokens...')
        
        for token in SocialToken.objects.all():
            try:
                account = SocialAccount.objects.get(id=token.account_id)
                try:
                    User.objects.get(id=account.user_id)
                    if target_email:
                        user = User.objects.get(id=account.user_id)
                        if user.email != target_email:
                            continue
                except User.DoesNotExist:
                    orphaned_tokens.append(token)
            except SocialAccount.DoesNotExist:
                orphaned_tokens.append(token)
                self.stdout.write(
                    self.style.ERROR(
                        f'Found orphaned social token: Account ID {token.account_id}, '
                        f'App: {token.app.name if token.app else "Unknown"}'
                    )
                )
        
        # Find duplicate social accounts for the same user/provider
        self.stdout.write('Checking for duplicate social accounts...')
        duplicate_accounts = []
        
        if target_email:
            try:
                user = User.objects.get(email=target_email)
                users_to_check = [user]
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with email {target_email} not found'))
                users_to_check = []
        else:
            users_to_check = User.objects.all()
        
        for user in users_to_check:
            providers = {}
            for account in SocialAccount.objects.filter(user=user):
                if account.provider in providers:
                    duplicate_accounts.append(account)
                    self.stdout.write(
                        self.style.WARNING(
                            f'Found duplicate social account for {user.email}: '
                            f'Provider: {account.provider}, UID: {account.uid}'
                        )
                    )
                else:
                    providers[account.provider] = account
        
        # Summary
        total_to_delete = len(orphaned_accounts) + len(orphaned_tokens) + len(duplicate_accounts)
        
        if total_to_delete == 0:
            self.stdout.write(self.style.SUCCESS('No orphaned or duplicate social accounts found!'))
            return
        
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'  Orphaned social accounts: {len(orphaned_accounts)}')
        self.stdout.write(f'  Orphaned social tokens: {len(orphaned_tokens)}')
        self.stdout.write(f'  Duplicate social accounts: {len(duplicate_accounts)}')
        self.stdout.write(f'  Total items to clean up: {total_to_delete}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No changes made'))
            return
        
        # Perform cleanup
        with transaction.atomic():
            deleted_accounts = 0
            deleted_tokens = 0
            deleted_duplicates = 0
            
            # Delete orphaned tokens first
            for token in orphaned_tokens:
                token.delete()
                deleted_tokens += 1
            
            # Delete orphaned accounts
            for account in orphaned_accounts:
                account.delete()
                deleted_accounts += 1
            
            # Delete duplicate accounts (keep the first one)
            for account in duplicate_accounts:
                account.delete()
                deleted_duplicates += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCleanup completed successfully!\n'
                f'  Deleted orphaned social accounts: {deleted_accounts}\n'
                f'  Deleted orphaned social tokens: {deleted_tokens}\n'
                f'  Deleted duplicate social accounts: {deleted_duplicates}'
            )
        )
