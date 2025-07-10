from django.core.management.base import BaseCommand
from challenges.models import Challenge, UserChallengeProgress
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Test XP functionality'

    def handle(self, *args, **options):
        # Check challenges
        challenges = Challenge.objects.all()[:3]
        self.stdout.write(f"Total challenges: {Challenge.objects.count()}")
        
        for challenge in challenges:
            self.stdout.write(f"Challenge: {challenge.title}, XP: {challenge.xp}")
        
        # Check if any users have XP
        progress_with_xp = UserChallengeProgress.objects.filter(xp_earned__gt=0)
        self.stdout.write(f"Progress entries with XP: {progress_with_xp.count()}")
        
        for progress in progress_with_xp[:5]:
            self.stdout.write(f"User: {progress.user.username}, Challenge: {progress.challenge.title}, XP: {progress.xp_earned}")
