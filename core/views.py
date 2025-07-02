from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.middleware.csrf import get_token
from editor.models import QueryHistory, SavedQuery
from challenges.models import UserChallengeProgress
from tutorials.models import UserTutorialProgress


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
