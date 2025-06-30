from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.middleware.csrf import get_token
from editor.models import QueryHistory, SavedQuery
from challenges.models import UserChallengeProgress
from tutorials.models import UserTutorialProgress


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
    User dashboard with statistics and progress.
    """
    user = request.user

    # Get user statistics
    total_queries = QueryHistory.objects.filter(user=user).count()
    successful_queries = QueryHistory.objects.filter(user=user, success=True).count()
    saved_queries_count = SavedQuery.objects.filter(user=user).count()

    # Get challenge progress
    completed_challenges = UserChallengeProgress.objects.filter(
        user=user, is_completed=True
    ).count()
    total_challenges = UserChallengeProgress.objects.filter(user=user).count()

    # Get tutorial progress
    completed_tutorials = UserTutorialProgress.objects.filter(
        user=user, is_completed=True
    ).count()
    in_progress_tutorials = UserTutorialProgress.objects.filter(
        user=user, is_completed=False
    ).count()

    # Recent query history
    recent_queries = QueryHistory.objects.filter(user=user).order_by('-executed_at')[:5]

    context = {
        'page_title': 'Dashboard',
        'stats': {
            'total_queries': total_queries,
            'successful_queries': successful_queries,
            'saved_queries_count': saved_queries_count,
            'completed_challenges': completed_challenges,
            'total_challenges': total_challenges,
            'completed_tutorials': completed_tutorials,
            'in_progress_tutorials': in_progress_tutorials,
        },
        'recent_queries': recent_queries,
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
