from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model
from editor.models import QueryHistory, SavedQuery
from challenges.models import UserChallengeProgress
from tutorials.models import UserTutorialProgress

User = get_user_model()


def landing_page(request):
    """
    Landing page for new visitors.
    """
    from courses.models import Course
    from django.db.models import Count, Avg, Q

    # Get featured courses (limit to 3 for landing page)
    featured_courses = Course.objects.filter(
        status='published',
        is_featured=True
    ).select_related('instructor').annotate(
        enrollment_count=Count('enrollments', filter=Q(enrollments__status__in=['active', 'completed'])),
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
    ).order_by('order')[:3]

    # If no featured courses, get the latest published courses
    if not featured_courses:
        featured_courses = Course.objects.filter(
            status='published'
        ).select_related('instructor').annotate(
            enrollment_count=Count('enrollments', filter=Q(enrollments__status__in=['active', 'completed'])),
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
        ).order_by('-created_at')[:3]

    context = {
        'page_title': 'SQL Master - Learn SQL the Right Way',
        'featured_courses': featured_courses,
    }
    return render(request, 'core/landing_page.html', context)


def home(request):
    """
    Home page with SQL editor.
    """
    context = {
        'page_title': 'SQL Editor',
        'csrf_token': get_token(request),
    }
    return render(request, 'core/home.html', context)


@login_required
def dashboard(request):
    """
    User dashboard with gamification and challenge-focused statistics.
    """
    from challenges.models import Challenge, UserChallengeProgress, UserChallengeSubscription
    from django.db.models import Sum, Count, Q, Avg
    from django.utils import timezone
    from datetime import timedelta

    user = request.user

    # Ensure user has a profile and XP is up-to-date
    from users.models import UserProfile
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)

    # Update total XP to ensure consistency
    profile.update_total_xp()

    # Challenge Statistics
    total_challenges = Challenge.objects.filter(is_active=True).count()
    user_progress = UserChallengeProgress.objects.filter(user=user)
    completed_challenges = user_progress.filter(is_completed=True).count()
    attempted_challenges = user_progress.count()

    # XP Statistics - use updated profile XP for consistency
    total_xp = profile.total_xp

    # Calculate current streak using the proven algorithm
    from challenges.views import calculate_user_streak
    current_streak = calculate_user_streak(user)

    # Difficulty breakdown
    difficulty_stats = {}
    for difficulty in ['easy', 'medium', 'hard', 'extreme']:
        total_diff = Challenge.objects.filter(is_active=True, difficulty=difficulty).count()
        completed_diff = user_progress.filter(
            is_completed=True,
            challenge__difficulty=difficulty
        ).count()
        difficulty_stats[difficulty] = {
            'total': total_diff,
            'completed': completed_diff,
            'percentage': (completed_diff / total_diff * 100) if total_diff > 0 else 0
        }

    # Leaderboard (top 10 users by XP) with profile pictures
    # Get user IDs first, then fetch full user objects for profile pictures
    # Exclude superusers from leaderboard
    top_user_ids = UserChallengeProgress.objects.filter(
        is_completed=True,
        user__is_superuser=False  # Exclude superusers
    ).values('user_id').annotate(
        total_xp=Sum('xp_earned'),
        challenges_completed=Count('id')
    ).order_by('-total_xp')[:10]

    # Create leaderboard with full user objects
    leaderboard = []
    for entry in top_user_ids:
        try:
            user = User.objects.select_related('profile').get(id=entry['user_id'])
            leaderboard.append({
                'user': user,
                'total_xp': entry['total_xp'],
                'challenges_completed': entry['challenges_completed']
            })
        except User.DoesNotExist:
            continue

    # Add current user rank (excluding superusers)
    user_rank = None
    if total_xp > 0:
        higher_xp_users = UserChallengeProgress.objects.filter(
            is_completed=True,
            user__is_superuser=False  # Exclude superusers from ranking
        ).values('user').annotate(
            total_xp=Sum('xp_earned')
        ).filter(total_xp__gt=total_xp).count()
        user_rank = higher_xp_users + 1

    # Recent achievements (last 5 completed challenges)
    recent_achievements = user_progress.filter(
        is_completed=True
    ).select_related('challenge').order_by('-completed_at')[:5]

    # Subscription status
    user_subscription = UserChallengeSubscription.objects.filter(
        user=user, status='active'
    ).first()

    context = {
        'page_title': 'Dashboard',
        'total_challenges': total_challenges,
        'completed_challenges': completed_challenges,
        'attempted_challenges': attempted_challenges,
        'completion_percentage': (completed_challenges / total_challenges * 100) if total_challenges > 0 else 0,
        'total_xp': total_xp,
        'current_streak': current_streak,
        'user_rank': user_rank,
        'difficulty_stats': difficulty_stats,
        'leaderboard': leaderboard,
        'recent_achievements': recent_achievements,
        'user_subscription': user_subscription,
    }
    return render(request, 'core/dashboard.html', context)


def about(request):
    """
    About page.
    """
    context = {
        'page_title': 'About SQL Playground',
    }
    return render(request, 'core/about.html', context)


def contribute(request):
    """
    Contribute page.
    """
    context = {
        'page_title': 'Contribute',
    }
    return render(request, 'core/contribute.html', context)


def csrf_debug(request):
    """Debug view to check CSRF token generation and validation"""
    csrf_token = get_token(request)

    context = {
        'csrf_token': csrf_token,
        'csrf_token_length': len(csrf_token),
        'method': request.method,
        'has_session': hasattr(request, 'session'),
        'session_key': getattr(request.session, 'session_key', None) if hasattr(request, 'session') else None,
        'cookies': dict(request.COOKIES),
        'meta_csrf': request.META.get('CSRF_COOKIE', 'Not found'),
    }

    if request.method == 'POST':
        context.update({
            'post_data': dict(request.POST),
            'csrf_token_from_post': request.POST.get('csrfmiddlewaretoken', 'Not found'),
            'csrf_token_matches': request.POST.get('csrfmiddlewaretoken') == csrf_token,
        })

    return JsonResponse(context, indent=2)


@csrf_exempt
def csrf_test_form(request):
    """Test form for CSRF debugging"""
    if request.method == 'POST':
        return JsonResponse({
            'status': 'success',
            'message': 'Form submitted successfully without CSRF protection',
            'csrf_token_received': request.POST.get('csrfmiddlewaretoken', 'Not found')
        })

    return render(request, 'core/csrf_test.html')


def terms_of_service(request):
    """
    Terms of Service page.
    """
    context = {
        'page_title': 'Terms of Service - SQLMaster',
    }
    return render(request, 'core/terms_of_service.html', context)


def privacy_policy(request):
    """
    Privacy Policy page.
    """
    context = {
        'page_title': 'Privacy Policy - SQLMaster',
    }
    return render(request, 'core/privacy_policy.html', context)
