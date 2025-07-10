from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from challenges.models import Challenge, UserChallengeProgress
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Test the complete XP gamification system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎮 Testing XP Gamification System'))
        
        # Test 1: Check Challenge XP values
        self.stdout.write('\n📊 Challenge XP Values:')
        challenges = Challenge.objects.all()[:5]
        for challenge in challenges:
            self.stdout.write(f"  • {challenge.title}: {challenge.xp} XP ({challenge.difficulty})")
        
        # Test 2: Check User Progress with XP
        self.stdout.write('\n🏆 User Progress with XP:')
        progress_entries = UserChallengeProgress.objects.filter(
            is_completed=True, 
            xp_earned__gt=0
        ).select_related('user', 'challenge')[:10]
        
        for progress in progress_entries:
            self.stdout.write(
                f"  • {progress.user.username}: {progress.challenge.title} "
                f"({progress.xp_earned} XP) - {progress.completed_at.strftime('%Y-%m-%d')}"
            )
        
        # Test 3: Calculate Total XP per User
        self.stdout.write('\n🥇 User XP Leaderboard:')
        from django.db.models import Sum
        
        user_xp = UserChallengeProgress.objects.filter(
            is_completed=True
        ).values('user__username', 'user__first_name', 'user__last_name').annotate(
            total_xp=Sum('xp_earned')
        ).order_by('-total_xp')[:10]
        
        for i, entry in enumerate(user_xp, 1):
            name = entry['user__first_name'] or entry['user__username']
            self.stdout.write(f"  {i}. {name}: {entry['total_xp']} XP")
        
        # Test 4: Difficulty Distribution
        self.stdout.write('\n📈 Challenge Difficulty Distribution:')
        from django.db.models import Count
        
        difficulty_stats = Challenge.objects.values('difficulty').annotate(
            count=Count('id'),
            total_xp=Sum('xp')
        ).order_by('difficulty')
        
        for stat in difficulty_stats:
            avg_xp = stat['total_xp'] / stat['count'] if stat['count'] > 0 else 0
            self.stdout.write(
                f"  • {stat['difficulty'].title()}: {stat['count']} challenges, "
                f"avg {avg_xp:.1f} XP"
            )
        
        # Test 5: Recent Achievements
        self.stdout.write('\n🎯 Recent Achievements (Last 7 days):')
        from datetime import timedelta
        
        recent_achievements = UserChallengeProgress.objects.filter(
            is_completed=True,
            completed_at__gte=timezone.now() - timedelta(days=7)
        ).select_related('user', 'challenge').order_by('-completed_at')[:5]
        
        for achievement in recent_achievements:
            self.stdout.write(
                f"  • {achievement.user.username} completed "
                f"{achievement.challenge.title} (+{achievement.xp_earned} XP)"
            )
        
        self.stdout.write(self.style.SUCCESS('\n✅ XP System Test Complete!'))
