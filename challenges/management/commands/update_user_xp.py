from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserProfile
from challenges.models import UserChallengeProgress, XPTransaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Update user profile total XP and create missing XP transactions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-transactions',
            action='store_true',
            help='Create missing XP transactions for existing completed challenges',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting XP update process...'))
        
        # Get all users
        users = User.objects.all()
        updated_count = 0
        transaction_count = 0
        
        for user in users:
            # Ensure user has a profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                self.stdout.write(f'Created profile for user: {user.email}')
            
            # Get completed challenges
            completed_progress = UserChallengeProgress.objects.filter(
                user=user,
                is_completed=True
            ).select_related('challenge')
            
            # Create missing XP transactions if requested
            if options['create_transactions']:
                for progress in completed_progress:
                    # Check if transaction already exists
                    existing_transaction = XPTransaction.objects.filter(
                        user=user,
                        challenge=progress.challenge,
                        transaction_type='challenge_completion'
                    ).first()
                    
                    if not existing_transaction and progress.xp_earned > 0:
                        XPTransaction.objects.create(
                            user=user,
                            challenge=progress.challenge,
                            transaction_type='challenge_completion',
                            xp_amount=progress.xp_earned,
                            description=f"Completed challenge: {progress.challenge.title}"
                        )
                        transaction_count += 1
                        self.stdout.write(f'Created XP transaction for {user.email} - {progress.challenge.title}')
            
            # Update total XP
            old_xp = profile.total_xp
            new_xp = profile.update_total_xp()
            
            if old_xp != new_xp:
                updated_count += 1
                self.stdout.write(f'Updated {user.email}: {old_xp} -> {new_xp} XP')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'XP update complete! Updated {updated_count} user profiles.'
            )
        )
        
        if options['create_transactions']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {transaction_count} missing XP transactions.'
                )
            )
