from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib import messages
from django.core.paginator import Paginator
import json
import sqlite3
import os

from .models import Challenge, UserChallengeProgress
from users.models import UserDatabase
from editor.views import execute_sql_query
from .forms import ChallengeForm, ChallengeFilterForm


def challenges_list(request):
    """
    Challenges list view with real data.
    """
    challenges = Challenge.objects.filter(is_active=True).order_by('order', 'difficulty')

    # Get user progress if authenticated
    user_progress = {}
    if request.user.is_authenticated:
        progress_data = UserChallengeProgress.objects.filter(
            user=request.user
        ).select_related('challenge')

        for progress in progress_data:
            user_progress[progress.challenge.id] = {
                'is_completed': progress.is_completed,
                'attempts': progress.attempts,
                'completed_at': progress.completed_at
            }

    context = {
        'page_title': 'SQL Challenges',
        'challenges': challenges,
        'user_progress': user_progress,
    }
    return render(request, 'challenges/challenges_list.html', context)


def challenge_detail(request, challenge_id):
    """
    Challenge detail view with content.
    """
    challenge = get_object_or_404(Challenge, id=challenge_id, is_active=True)

    # Get user progress if authenticated
    user_progress = None
    if request.user.is_authenticated:
        user_progress, created = UserChallengeProgress.objects.get_or_create(
            user=request.user,
            challenge=challenge
        )

    context = {
        'page_title': f'Challenge: {challenge.title}',
        'challenge': challenge,
        'user_progress': user_progress,
    }
    return render(request, 'challenges/challenge_detail.html', context)


@login_required
@require_http_methods(["POST"])
def submit_challenge(request, challenge_id):
    """
    Submit challenge solution with auto-evaluation.
    """
    try:
        challenge = get_object_or_404(Challenge, id=challenge_id, is_active=True)
        user_query = request.POST.get('query', '').strip()

        if not user_query:
            return JsonResponse({
                'success': False,
                'error': 'Query is required'
            })

        # Get or create user progress
        user_progress, created = UserChallengeProgress.objects.get_or_create(
            user=request.user,
            challenge=challenge
        )

        # Increment attempts
        user_progress.attempts += 1

        # Get user database
        user_db = UserDatabase.objects.get(user=request.user)
        db_path = user_db.full_path

        if not os.path.exists(db_path):
            return JsonResponse({
                'success': False,
                'error': 'User database not found. Please run a query in the SQL editor first.'
            })

        # Execute user query
        result = execute_sql_query(db_path, user_query)

        if not result['success']:
            user_progress.save()
            return JsonResponse({
                'success': False,
                'error': f'Query execution failed: {result["error"]}',
                'attempts': user_progress.attempts
            })

        # Compare results with expected output
        user_result = result.get('results', [])
        expected_result = challenge.expected_result

        # Normalize results for comparison
        is_correct = compare_query_results(user_result, expected_result)

        if is_correct:
            user_progress.is_completed = True
            user_progress.completed_at = timezone.now()
            user_progress.best_query = user_query
            user_progress.save()

            return JsonResponse({
                'success': True,
                'correct': True,
                'message': 'Congratulations! Your solution is correct!',
                'attempts': user_progress.attempts,
                'user_result': user_result,
                'expected_result': expected_result
            })
        else:
            user_progress.save()
            return JsonResponse({
                'success': True,
                'correct': False,
                'message': 'Your query executed successfully, but the result doesn\'t match the expected output.',
                'attempts': user_progress.attempts,
                'user_result': user_result,
                'expected_result': expected_result,
                'hint': challenge.hint if user_progress.attempts >= 3 else None
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def compare_query_results(user_result, expected_result):
    """
    Compare user query result with expected result.
    """
    try:
        # Convert both to lists for comparison
        if isinstance(user_result, list) and isinstance(expected_result, list):
            # Sort both results to handle different ordering
            user_sorted = sorted([tuple(row.values()) if isinstance(row, dict) else tuple(row) for row in user_result])
            expected_sorted = sorted([tuple(row.values()) if isinstance(row, dict) else tuple(row) for row in expected_result])
            return user_sorted == expected_sorted

        return user_result == expected_result
    except:
        return False


# Admin Views for Challenge Management

@staff_member_required
def admin_challenges_list(request):
    """
    Admin view to list all challenges with management options.
    """
    challenges = Challenge.objects.all().order_by('-created_at')

    # Apply filters
    filter_form = ChallengeFilterForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data['difficulty']:
            challenges = challenges.filter(difficulty=filter_form.cleaned_data['difficulty'])

        if filter_form.cleaned_data['status']:
            is_active = filter_form.cleaned_data['status'] == 'active'
            challenges = challenges.filter(is_active=is_active)

        if filter_form.cleaned_data['search']:
            search_term = filter_form.cleaned_data['search']
            challenges = challenges.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term)
            )

    # Pagination
    paginator = Paginator(challenges, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'Manage Challenges',
        'challenges': page_obj,
        'filter_form': filter_form,
        'total_challenges': challenges.count(),
    }
    return render(request, 'challenges/admin/challenges_list.html', context)


@staff_member_required
def admin_challenge_create(request):
    """
    Admin view to create a new challenge.
    """
    if request.method == 'POST':
        form = ChallengeForm(request.POST, request.FILES)
        if form.is_valid():
            challenge = form.save()
            messages.success(request, f'Challenge "{challenge.title}" created successfully!')
            return redirect('challenges:admin_challenge_detail', challenge_id=challenge.id)
    else:
        form = ChallengeForm()

    context = {
        'page_title': 'Create Challenge',
        'form': form,
        'is_edit': False,
    }
    return render(request, 'challenges/admin/challenge_form.html', context)


@staff_member_required
def admin_challenge_edit(request, challenge_id):
    """
    Admin view to edit an existing challenge.
    """
    challenge = get_object_or_404(Challenge, id=challenge_id)

    if request.method == 'POST':
        form = ChallengeForm(request.POST, request.FILES, instance=challenge)
        if form.is_valid():
            challenge = form.save()
            messages.success(request, f'Challenge "{challenge.title}" updated successfully!')
            return redirect('challenges:admin_challenge_detail', challenge_id=challenge.id)
    else:
        form = ChallengeForm(instance=challenge)

    context = {
        'page_title': f'Edit Challenge: {challenge.title}',
        'form': form,
        'challenge': challenge,
        'is_edit': True,
    }
    return render(request, 'challenges/admin/challenge_form.html', context)


@staff_member_required
def admin_challenge_detail(request, challenge_id):
    """
    Admin view to view challenge details.
    """
    challenge = get_object_or_404(Challenge, id=challenge_id)

    # Get challenge statistics
    total_attempts = UserChallengeProgress.objects.filter(challenge=challenge).count()
    completed_attempts = UserChallengeProgress.objects.filter(
        challenge=challenge, is_completed=True
    ).count()

    completion_rate = (completed_attempts / total_attempts * 100) if total_attempts > 0 else 0

    context = {
        'page_title': f'Challenge: {challenge.title}',
        'challenge': challenge,
        'stats': {
            'total_attempts': total_attempts,
            'completed_attempts': completed_attempts,
            'completion_rate': round(completion_rate, 1),
        }
    }
    return render(request, 'challenges/admin/challenge_detail.html', context)


@staff_member_required
def admin_challenge_delete(request, challenge_id):
    """
    Admin view to delete a challenge.
    """
    challenge = get_object_or_404(Challenge, id=challenge_id)

    if request.method == 'POST':
        challenge_title = challenge.title
        challenge.delete()
        messages.success(request, f'Challenge "{challenge_title}" deleted successfully!')
        return redirect('challenges:admin_challenges_list')

    context = {
        'page_title': f'Delete Challenge: {challenge.title}',
        'challenge': challenge,
    }
    return render(request, 'challenges/admin/challenge_confirm_delete.html', context)
