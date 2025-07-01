from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib import messages
from django.core.paginator import Paginator
import json
import sqlite3
import os

from .models import Challenge, UserChallengeProgress, ChallengeSubscriptionPlan, UserChallengeSubscription
from users.models import UserDatabase
from editor.views import execute_sql_query
from .forms import ChallengeForm, ChallengeFilterForm


def challenges_list(request):
    """
    Challenges list view with real data and subscription information.
    """
    challenges = Challenge.objects.filter(is_active=True).order_by('order', 'difficulty')

    # Get user progress if authenticated
    user_progress = {}
    user_subscription = None
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

        # Get user's active challenge subscription
        user_subscription = UserChallengeSubscription.objects.filter(
            user=request.user,
            status='active'
        ).first()

    # Calculate progress statistics
    total_challenges = challenges.count()
    free_challenges = challenges.filter(subscription_type='free').count()
    paid_challenges = challenges.filter(subscription_type='paid').count()

    completed_challenges = 0
    completed_easy = 0
    completed_medium = 0
    completed_hard = 0
    completed_extreme = 0

    if request.user.is_authenticated:
        completed_challenges = len([p for p in user_progress.values() if p['is_completed']])

        for challenge in challenges:
            if challenge.id in user_progress and user_progress[challenge.id]['is_completed']:
                if challenge.difficulty == 'easy':
                    completed_easy += 1
                elif challenge.difficulty == 'medium':
                    completed_medium += 1
                elif challenge.difficulty == 'hard':
                    completed_hard += 1
                elif challenge.difficulty == 'extreme':
                    completed_extreme += 1

    # Get challenge statistics by difficulty
    easy_total = challenges.filter(difficulty='easy').count()
    medium_total = challenges.filter(difficulty='medium').count()
    hard_total = challenges.filter(difficulty='hard').count()
    extreme_total = challenges.filter(difficulty='extreme').count()

    context = {
        'page_title': 'SQL Challenges',
        'challenges': challenges,
        'user_progress': user_progress,
        'user_subscription': user_subscription,
        'has_active_subscription': user_subscription and user_subscription.is_active if user_subscription else False,
        'total_challenges': total_challenges,
        'free_challenges': free_challenges,
        'paid_challenges': paid_challenges,
        'completed_challenges': completed_challenges,
        'progress_stats': {
            'total': {'completed': completed_challenges, 'total': total_challenges},
            'easy': {'completed': completed_easy, 'total': easy_total},
            'medium': {'completed': completed_medium, 'total': medium_total},
            'hard': {'completed': completed_hard, 'total': hard_total},
            'extreme': {'completed': completed_extreme, 'total': extreme_total},
        }
    }
    return render(request, 'challenges/challenges_list.html', context)


def challenge_detail(request, challenge_id):
    """
    Challenge detail view with content and access control.
    """
    challenge = get_object_or_404(Challenge, id=challenge_id, is_active=True)

    # Check if user has access to this challenge
    has_access = challenge.user_has_access(request.user)

    # If no access and it's a paid challenge, redirect to subscription plans
    if not has_access and challenge.is_premium:
        if request.user.is_authenticated:
            messages.warning(request, 'This is a premium challenge. Please subscribe to access it.')
            return redirect('challenges:subscription_plans')
        else:
            messages.warning(request, 'Please login and subscribe to access premium challenges.')
            return redirect('users:login')

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
        'has_access': has_access,
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


# Challenge Subscription Views
@login_required
def subscription_plans(request):
    """
    Display subscription plans for challenges.
    """
    # Clean up expired pending subscriptions first
    UserChallengeSubscription.cleanup_expired_pending()

    # Check if user already has an active subscription
    existing_subscription = UserChallengeSubscription.objects.filter(
        user=request.user,
        status='active'
    ).first()

    if existing_subscription and existing_subscription.is_active:
        messages.info(request, 'You already have an active challenge subscription.')
        return redirect('challenges:challenges_list')

    # Check for pending subscriptions that haven't expired
    pending_subscriptions = UserChallengeSubscription.objects.filter(
        user=request.user,
        status='pending'
    ).exclude(pending_expires_at__lt=timezone.now())

    # Get available subscription plans
    subscription_plans = ChallengeSubscriptionPlan.objects.filter(
        is_active=True
    ).order_by('sort_order', 'price')

    context = {
        'page_title': 'Challenge Subscription Plans',
        'subscription_plans': subscription_plans,
        'existing_subscription': existing_subscription,
        'pending_subscriptions': pending_subscriptions,
    }
    return render(request, 'challenges/subscription_plans.html', context)


@login_required
def subscription_checkout(request, plan_id):
    """
    Handle subscription checkout with selected plan.
    """
    plan = get_object_or_404(ChallengeSubscriptionPlan, id=plan_id, is_active=True)

    # Clean up expired pending subscriptions first
    UserChallengeSubscription.cleanup_expired_pending()

    # Check if user already has an active subscription
    existing_subscription = UserChallengeSubscription.objects.filter(
        user=request.user,
        status='active'
    ).first()

    if existing_subscription and existing_subscription.is_active:
        messages.info(request, 'You already have an active challenge subscription.')
        return redirect('challenges:challenges_list')

    # Check if user has a non-expired pending subscription for this plan
    pending_subscription = UserChallengeSubscription.objects.filter(
        user=request.user,
        plan=plan,
        status='pending'
    ).exclude(pending_expires_at__lt=timezone.now()).first()

    if pending_subscription:
        # Use existing pending subscription
        subscription = pending_subscription
    else:
        # Cancel any other pending subscriptions for this user
        UserChallengeSubscription.objects.filter(
            user=request.user,
            status='pending'
        ).update(status='cancelled')

        # Create new subscription
        subscription = UserChallengeSubscription.objects.create(
            user=request.user,
            plan=plan,
            start_date=timezone.now(),
            status='pending',
            amount_paid=plan.effective_price,
        )
        # Set pending expiration (30 minutes)
        subscription.set_pending_expiration(30)

    context = {
        'page_title': f'Checkout - {plan.name}',
        'plan': plan,
        'subscription': subscription,
    }
    return render(request, 'challenges/subscription_checkout.html', context)


@login_required
@require_http_methods(["POST"])
def cancel_pending_subscription(request, subscription_id):
    """
    Cancel a pending subscription.
    """
    subscription = get_object_or_404(
        UserChallengeSubscription,
        id=subscription_id,
        user=request.user,
        status='pending'
    )

    subscription.cancel_pending()
    messages.success(request, 'Pending subscription cancelled successfully.')
    return redirect('challenges:subscription_plans')


@login_required
@require_http_methods(["POST"])
def create_stripe_checkout(request, subscription_id):
    """
    Create Stripe checkout session for subscription payment.
    """
    subscription = get_object_or_404(
        UserChallengeSubscription,
        id=subscription_id,
        user=request.user,
        status='pending'
    )

    try:
        from .stripe_service import StripeService

        # Create Stripe checkout session
        session = StripeService.create_checkout_session(subscription, request)

        # Redirect to Stripe checkout
        return redirect(session.url, code=303)

    except Exception as e:
        messages.error(request, f'Payment processing error: {str(e)}')
        return redirect('challenges:subscription_checkout', plan_id=subscription.plan.id)


@login_required
def payment_success(request, subscription_id):
    """
    Handle successful payment redirect from Stripe.
    """
    subscription = get_object_or_404(
        UserChallengeSubscription,
        id=subscription_id,
        user=request.user
    )

    try:
        from .stripe_service import StripeService

        # Retrieve the checkout session to verify payment
        if subscription.stripe_payment_intent_id:
            session = StripeService.retrieve_checkout_session(subscription.stripe_payment_intent_id)

            if session.payment_status == 'paid':
                # Activate subscription if not already active
                if subscription.status == 'pending':
                    subscription.activate()
                    subscription.payment_reference = session.payment_intent
                    subscription.save()

                messages.success(request, f'Payment successful! Your {subscription.plan.name} subscription is now active.')
            else:
                messages.warning(request, 'Payment is being processed. You will receive confirmation shortly.')
        else:
            messages.warning(request, 'Payment verification in progress.')

    except Exception as e:
        messages.error(request, f'Error verifying payment: {str(e)}')

    return redirect('challenges:challenges_list')


@login_required
def payment_cancel(request, subscription_id):
    """
    Handle cancelled payment redirect from Stripe.
    """
    subscription = get_object_or_404(
        UserChallengeSubscription,
        id=subscription_id,
        user=request.user,
        status='pending'
    )

    messages.info(request, 'Payment was cancelled. You can try again or choose a different plan.')
    return redirect('challenges:subscription_checkout', plan_id=subscription.plan.id)


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Handle Stripe webhook events.
    """
    from .stripe_service import StripeService

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        # Construct the event
        event = StripeService.construct_webhook_event(payload, sig_header)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            StripeService.handle_payment_success(session)

        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            StripeService.handle_payment_success(payment_intent)

        else:
            print(f'Unhandled event type: {event["type"]}')

        return HttpResponse(status=200)

    except Exception as e:
        print(f'Webhook error: {e}')
        return HttpResponse(status=400)


@login_required
def analytics_dashboard(request):
    """
    Analytics dashboard for detailed progress tracking.
    """
    user = request.user

    # Get user's challenge progress
    user_progress = UserChallengeProgress.objects.filter(user=user).select_related('challenge')

    # Calculate detailed statistics
    total_challenges = Challenge.objects.filter(is_active=True).count()
    completed_challenges = user_progress.filter(is_completed=True).count()
    attempted_challenges = user_progress.count()

    # Progress by difficulty
    difficulty_stats = {}
    for difficulty in ['easy', 'medium', 'hard', 'extreme']:
        total = Challenge.objects.filter(difficulty=difficulty, is_active=True).count()
        completed = user_progress.filter(challenge__difficulty=difficulty, is_completed=True).count()
        attempted = user_progress.filter(challenge__difficulty=difficulty).count()

        difficulty_stats[difficulty] = {
            'total': total,
            'completed': completed,
            'attempted': attempted,
            'completion_rate': (completed / total * 100) if total > 0 else 0,
            'attempt_rate': (attempted / total * 100) if total > 0 else 0
        }

    # Progress by company
    company_stats = {}
    companies = Challenge.objects.filter(is_active=True).exclude(company='').values_list('company', flat=True).distinct()

    for company in companies:
        total = Challenge.objects.filter(company=company, is_active=True).count()
        completed = user_progress.filter(challenge__company=company, is_completed=True).count()

        if total > 0:
            company_stats[company] = {
                'total': total,
                'completed': completed,
                'completion_rate': (completed / total * 100)
            }

    # Recent activity
    recent_progress = user_progress.filter(is_completed=True).order_by('-completed_at')[:10]

    # Streak calculation
    streak_days = calculate_user_streak(user)

    # Time-based analytics
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta

    # Last 30 days activity
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_activity = user_progress.filter(
        completed_at__gte=thirty_days_ago,
        is_completed=True
    ).extra(
        select={'day': 'date(completed_at)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')

    # Subscription info
    user_subscription = UserChallengeSubscription.objects.filter(
        user=user,
        status='active'
    ).first()

    context = {
        'page_title': 'Analytics Dashboard',
        'total_challenges': total_challenges,
        'completed_challenges': completed_challenges,
        'attempted_challenges': attempted_challenges,
        'completion_percentage': (completed_challenges / total_challenges * 100) if total_challenges > 0 else 0,
        'difficulty_stats': difficulty_stats,
        'company_stats': sorted(company_stats.items(), key=lambda x: x[1]['completion_rate'], reverse=True)[:10],
        'recent_progress': recent_progress,
        'streak_days': streak_days,
        'daily_activity': list(daily_activity),
        'user_subscription': user_subscription,
    }

    return render(request, 'challenges/analytics_dashboard.html', context)


def calculate_user_streak(user):
    """Calculate user's current streak of consecutive days with completed challenges"""
    from django.utils import timezone
    from datetime import timedelta

    # Get all completion dates
    completion_dates = UserChallengeProgress.objects.filter(
        user=user,
        is_completed=True
    ).values_list('completed_at__date', flat=True).distinct().order_by('-completed_at__date')

    if not completion_dates:
        return 0

    streak = 0
    current_date = timezone.now().date()

    # Check if user completed something today or yesterday
    if completion_dates[0] == current_date:
        streak = 1
        check_date = current_date - timedelta(days=1)
    elif completion_dates[0] == current_date - timedelta(days=1):
        streak = 1
        check_date = current_date - timedelta(days=2)
    else:
        return 0

    # Count consecutive days
    for completion_date in completion_dates[1:]:
        if completion_date == check_date:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return streak
