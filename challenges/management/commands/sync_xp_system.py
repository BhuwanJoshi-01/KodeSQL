from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Sum
from users.models import UserProfile
from challenges.models import UserChallengeProgress

User = get_user_model()


class Command(BaseCommand):
    help = 'Synchronize XP system between dashboard and profile displays'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Only check for discrepancies without fixing them',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each user',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 Starting XP system synchronization...'))
        
        check_only = options['check_only']
        verbose = options['verbose']
        
        # Get all users with challenge progress
        users_with_progress = User.objects.filter(
            challenge_progress__isnull=False
        ).distinct()
        
        discrepancies_found = 0
        users_fixed = 0
        
        for user in users_with_progress:
            # Calculate actual XP from challenges
            actual_xp = UserChallengeProgress.objects.filter(
                user=user,
                is_completed=True
            ).aggregate(total=Sum('xp_earned'))['total'] or 0
            
            # Get profile cached XP
            try:
                profile = user.profile
                cached_xp = profile.total_xp
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user)
                cached_xp = 0
            
            # Check for discrepancy
            if actual_xp != cached_xp:
                discrepancies_found += 1
                
                if verbose or check_only:
                    self.stdout.write(
                        f'❌ {user.email}: Cached={cached_xp} XP, Actual={actual_xp} XP (Diff: {actual_xp - cached_xp})'
                    )
                
                if not check_only:
                    # Fix the discrepancy
                    profile.total_xp = actual_xp
                    profile.save(update_fields=['total_xp', 'updated_at'])
                    users_fixed += 1
                    
                    if verbose:
                        self.stdout.write(f'✅ Fixed {user.email}: Updated to {actual_xp} XP')
            
            elif verbose:
                self.stdout.write(f'✅ {user.email}: XP synchronized ({actual_xp} XP)')
        
        # Summary
        if check_only:
            if discrepancies_found > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'🔍 Found {discrepancies_found} XP discrepancies. Run without --check-only to fix them.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ All XP values are synchronized!')
                )
        else:
            if users_fixed > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'🔧 Fixed XP discrepancies for {users_fixed} users.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ All XP values were already synchronized!')
                )
        
        # Additional statistics
        total_users = User.objects.count()
        users_with_xp = UserProfile.objects.filter(total_xp__gt=0).count()
        
        self.stdout.write('\n📊 XP System Statistics:')
        self.stdout.write(f'   Total Users: {total_users}')
        self.stdout.write(f'   Users with XP: {users_with_xp}')
        self.stdout.write(f'   Users with Challenge Progress: {users_with_progress.count()}')
        
        if discrepancies_found > 0:
            self.stdout.write(f'   Discrepancies Found: {discrepancies_found}')
            if not check_only:
                self.stdout.write(f'   Discrepancies Fixed: {users_fixed}')
