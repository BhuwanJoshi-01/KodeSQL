from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.contrib import messages
from django.core.paginator import Paginator
from django.middleware.csrf import get_token
from django.db import models
from datetime import timedelta
import json
import sqlite3
import os
import time

from .models import Challenge, UserChallengeProgress, ChallengeSubscriptionPlan, UserChallengeSubscription
from users.models import UserDatabase
from editor.views import execute_sql_query
from .utils import execute_sql_query_multi_engine, DatabaseEngineManager
from .forms import ChallengeForm, ChallengeFilterForm, UserChallengeSubscriptionForm, SubscriptionFilterForm, ChallengeSubscriptionPlanForm


def challenges_list(request):
    """
    Challenges list view with real data and subscription information.
    """
    challenges = Challenge.objects.filter(is_active=True).order_by('order', 'difficulty')

    # Get user progress if authenticated and attach to challenges
    user_subscription = None
    if request.user.is_authenticated:
        progress_data = UserChallengeProgress.objects.filter(
            user=request.user
        ).select_related('challenge')

        # Create a dictionary for quick lookup
        progress_dict = {}
        for progress in progress_data:
            progress_dict[progress.challenge.id] = progress

        # Attach progress to each challenge using a different attribute name
        for challenge in challenges:
            if challenge.id in progress_dict:
                challenge.progress_data = progress_dict[challenge.id]
            else:
                challenge.progress_data = None

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
        completed_challenges = len([c for c in challenges if c.progress_data and c.progress_data.is_completed])

        for challenge in challenges:
            if challenge.progress_data and challenge.progress_data.is_completed:
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
        'user_subscription': user_subscription,
        'has_active_subscription': user_subscription and user_subscription.is_active if user_subscription else False,
        'total_challenges': total_challenges,
        'free_challenges': free_challenges,
        'paid_challenges': paid_challenges,
        'completed_challenges': completed_challenges,
        'progress_stats': {
            'total': {
                'completed': completed_challenges,
                'total': total_challenges,
                'percentage': round((completed_challenges / total_challenges * 100) if total_challenges > 0 else 0)
            },
            'easy': {
                'completed': completed_easy,
                'total': easy_total,
                'percentage': round((completed_easy / easy_total * 100) if easy_total > 0 else 0)
            },
            'medium': {
                'completed': completed_medium,
                'total': medium_total,
                'percentage': round((completed_medium / medium_total * 100) if medium_total > 0 else 0)
            },
            'hard': {
                'completed': completed_hard,
                'total': hard_total,
                'percentage': round((completed_hard / hard_total * 100) if hard_total > 0 else 0)
            },
            'extreme': {
                'completed': completed_extreme,
                'total': extreme_total,
                'percentage': round((completed_extreme / extreme_total * 100) if extreme_total > 0 else 0)
            },
        }
    }
    return render(request, 'challenges/challenges_list.html', context)


def challenge_detail(request, challenge_id):
    """
    Enhanced challenge detail view with integrated SQL editor.
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

        # Initialize challenge database for this user if they have access
        if has_access:
            try:
                challenge.initialize_challenge_database(request.user)
            except Exception as e:
                messages.error(request, f'Error initializing challenge database: {str(e)}')

    # Get database schema configuration from the simplified system
    schema_config = challenge.get_database_schema_config()
    database_schema = schema_config.get('schema', {})

    context = {
        'page_title': f'Challenge: {challenge.title}',
        'challenge': challenge,
        'user_progress': user_progress,
        'has_access': has_access,
        'database_schema': database_schema,
        'schema_config': schema_config,
    }
    return render(request, 'challenges/challenge_solve.html', context)


@require_http_methods(["POST"])
@login_required
def execute_challenge_query(request, challenge_id):
    """
    Execute a SQL query for a specific challenge with multi-engine support.
    """
    challenge = get_object_or_404(Challenge, id=challenge_id, is_active=True)

    # Check if user has access to this challenge
    if not challenge.user_has_access(request.user):
        return JsonResponse({
            'success': False,
            'error': 'You do not have access to this challenge.'
        })

    try:
        data = json.loads(request.body)
        user_query = data.get('query', '').strip()
        engine = data.get('engine', 'sqlite')  # Get selected database engine

        if not user_query:
            return JsonResponse({
                'success': False,
                'error': 'Query cannot be empty.'
            })

        # Validate that challenge supports the selected engine
        if not challenge.supports_engine(engine):
            return JsonResponse({
                'success': False,
                'error': f'This challenge does not support {engine.upper()} database engine.'
            })

        # Initialize database for the selected engine
        try:
            challenge.initialize_challenge_database(request.user, engine)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Failed to initialize {engine} database: {str(e)}'
            })

        # Execute user query with selected engine
        start_time = time.time()

        if engine == 'sqlite':
            # Use existing SQLite logic
            db_path = challenge.get_challenge_database_path(request.user, engine)
            result = execute_sql_query(db_path, user_query)
        else:
            # Use multi-engine logic for PostgreSQL/MySQL
            db_config = {
                'database': f"challenge_{challenge.id}_user_{request.user.id}"
            }
            result = execute_sql_query_multi_engine(engine, db_config, user_query)

        execution_time = int((time.time() - start_time) * 1000)

        if not result['success']:
            return JsonResponse({
                'success': False,
                'error': f'Query execution failed: {result["error"]}',
                'execution_time': execution_time
            })

        user_results = result.get('results', [])
        columns = result.get('columns', [])
        row_count = result.get('row_count', 0)

        return JsonResponse({
            'success': True,
            'results': user_results,
            'columns': columns,
            'row_count': row_count,
            'execution_time': execution_time,
            'message': f'Query executed successfully. {row_count} row(s) returned.'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def submit_challenge(request, challenge_id):
    """
    Submit challenge solution with auto-evaluation and multi-engine support.
    """
    try:
        challenge = get_object_or_404(Challenge, id=challenge_id, is_active=True)
        user_query = request.POST.get('query', '').strip()
        engine = request.POST.get('engine', 'sqlite')  # Get selected database engine

        if not user_query:
            return JsonResponse({
                'success': False,
                'error': 'Query is required'
            })

        # Validate that challenge supports the selected engine
        if not challenge.supports_engine(engine):
            return JsonResponse({
                'success': False,
                'error': f'This challenge does not support {engine.upper()} database engine.'
            })

        # Get or create user progress
        user_progress, created = UserChallengeProgress.objects.get_or_create(
            user=request.user,
            challenge=challenge
        )

        # Increment attempts
        user_progress.attempts += 1

        # Initialize database for the selected engine
        try:
            challenge.initialize_challenge_database(request.user, engine)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Failed to initialize {engine} database: {str(e)}'
            })

        # Execute user query with selected engine
        if engine == 'sqlite':
            # Use existing SQLite logic
            db_path = challenge.get_challenge_database_path(request.user, engine)
            result = execute_sql_query(db_path, user_query)
        else:
            # Use multi-engine logic for PostgreSQL/MySQL
            db_config = {
                'database': f"challenge_{challenge.id}_user_{request.user.id}"
            }
            result = execute_sql_query_multi_engine(engine, db_config, user_query)

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
    failed_attempts = total_attempts - completed_attempts

    context = {
        'page_title': f'Challenge: {challenge.title}',
        'challenge': challenge,
        'stats': {
            'total_attempts': total_attempts,
            'completed_attempts': completed_attempts,
            'failed_attempts': failed_attempts,
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


# Challenge Subscription Admin Views (Superuser Only)
@staff_member_required
def admin_subscriptions_list(request):
    """
    Admin view to list all challenge subscriptions with management options.
    """
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access subscription management.')
        return redirect('challenges:admin_challenges_list')

    subscriptions = UserChallengeSubscription.objects.select_related(
        'user', 'plan'
    ).order_by('-created_at')

    # Apply filters
    filter_form = SubscriptionFilterForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data['status']:
            subscriptions = subscriptions.filter(status=filter_form.cleaned_data['status'])

        if filter_form.cleaned_data['plan']:
            subscriptions = subscriptions.filter(plan=filter_form.cleaned_data['plan'])

        if filter_form.cleaned_data['search']:
            search_term = filter_form.cleaned_data['search']
            subscriptions = subscriptions.filter(
                Q(user__email__icontains=search_term) |
                Q(user__first_name__icontains=search_term) |
                Q(user__last_name__icontains=search_term) |
                Q(plan__name__icontains=search_term) |
                Q(payment_reference__icontains=search_term)
            )

    # Get statistics
    total_subscriptions = subscriptions.count()
    active_subscriptions = subscriptions.filter(status='active').count()
    pending_subscriptions = subscriptions.filter(status='pending').count()
    expired_subscriptions = subscriptions.filter(status='expired').count()

    # Pagination
    paginator = Paginator(subscriptions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Add convenience attributes for templates
    for subscription in page_obj:
        subscription.user.full_name_or_email = subscription.user.get_full_name() or subscription.user.email

    context = {
        'page_title': 'Manage Challenge Subscriptions',
        'subscriptions': page_obj,
        'filter_form': filter_form,
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'pending_subscriptions': pending_subscriptions,
        'expired_subscriptions': expired_subscriptions,
    }
    return render(request, 'challenges/admin/subscriptions_list.html', context)


@staff_member_required
def admin_subscription_create(request):
    """
    Admin view to create a new challenge subscription for a user.
    """
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access subscription management.')
        return redirect('challenges:admin_challenges_list')

    if request.method == 'POST':
        form = UserChallengeSubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)

            # Set default values if not provided
            if not subscription.start_date:
                subscription.start_date = timezone.now()

            # Set end date based on plan duration if not provided and not unlimited
            if not subscription.end_date and subscription.plan.duration != 'unlimited':
                duration_days = subscription.plan.get_duration_days()
                if duration_days:
                    subscription.end_date = subscription.start_date + timedelta(days=duration_days)

            subscription.save()
            messages.success(request, f'Subscription created successfully for {subscription.user.email}!')
            return redirect('challenges:admin_subscription_detail', subscription_id=subscription.id)
    else:
        form = UserChallengeSubscriptionForm()

    context = {
        'page_title': 'Create Challenge Subscription',
        'form': form,
    }
    return render(request, 'challenges/admin/subscription_form.html', context)


@staff_member_required
def admin_subscription_detail(request, subscription_id):
    """
    Admin view to view challenge subscription details.
    """
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access subscription management.')
        return redirect('challenges:admin_challenges_list')

    subscription = get_object_or_404(
        UserChallengeSubscription.objects.select_related('user', 'plan'),
        id=subscription_id
    )

    # Add convenience attributes for templates
    subscription.user.full_name_or_email = subscription.user.get_full_name() or subscription.user.email

    context = {
        'page_title': f'Subscription: {subscription.user.email}',
        'subscription': subscription,
    }
    return render(request, 'challenges/admin/subscription_detail.html', context)


@staff_member_required
def admin_subscription_edit(request, subscription_id):
    """
    Admin view to edit an existing challenge subscription.
    """
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access subscription management.')
        return redirect('challenges:admin_challenges_list')

    subscription = get_object_or_404(UserChallengeSubscription, id=subscription_id)

    if request.method == 'POST':
        form = UserChallengeSubscriptionForm(request.POST, instance=subscription)
        if form.is_valid():
            subscription = form.save()
            messages.success(request, f'Subscription for {subscription.user.email} updated successfully!')
            return redirect('challenges:admin_subscription_detail', subscription_id=subscription.id)
    else:
        form = UserChallengeSubscriptionForm(instance=subscription)

    context = {
        'page_title': f'Edit Subscription: {subscription.user.email}',
        'form': form,
        'subscription': subscription,
    }
    return render(request, 'challenges/admin/subscription_form.html', context)


@staff_member_required
def admin_subscription_cancel(request, subscription_id):
    """
    Admin view to cancel a challenge subscription.
    """
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access subscription management.')
        return redirect('challenges:admin_challenges_list')

    subscription = get_object_or_404(UserChallengeSubscription, id=subscription_id)

    if request.method == 'POST':
        subscription.status = 'cancelled'
        subscription.save()
        messages.success(request, f'Subscription for {subscription.user.email} cancelled successfully!')
        return redirect('challenges:admin_subscription_detail', subscription_id=subscription.id)

    context = {
        'page_title': f'Cancel Subscription: {subscription.user.email}',
        'subscription': subscription,
    }
    return render(request, 'challenges/admin/subscription_confirm_delete.html', context)


@staff_member_required
def admin_subscription_confirm_delete(request, subscription_id):
    """
    Admin view to confirm deletion of a challenge subscription.
    """
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access subscription management.')
        return redirect('challenges:admin_challenges_list')

    subscription = get_object_or_404(UserChallengeSubscription, id=subscription_id)

    # Add convenience attributes for templates
    subscription.user.full_name_or_email = subscription.user.get_full_name() or subscription.user.email

    context = {
        'page_title': f'Delete Subscription: {subscription.user.email}',
        'subscription': subscription,
    }
    return render(request, 'challenges/admin/subscription_confirm_delete.html', context)


@staff_member_required
def admin_subscription_delete(request, subscription_id):
    """
    Admin view to permanently delete a challenge subscription.
    """
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access subscription management.')
        return redirect('challenges:admin_challenges_list')

    subscription = get_object_or_404(UserChallengeSubscription, id=subscription_id)

    if request.method == 'POST':
        user_email = subscription.user.email
        subscription.delete()
        messages.success(request, f'Subscription for {user_email} deleted successfully!')
        return redirect('challenges:admin_subscriptions_list')

    # If not POST, redirect to confirm delete page
    return redirect('challenges:admin_subscription_confirm_delete', subscription_id=subscription_id)


# Challenge Subscription Plan Admin Views (Staff Only)
@staff_member_required
def admin_subscription_plans_list(request):
    """
    Admin subscription plan management list.
    """
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access subscription plan management.')
        return redirect('challenges:admin_challenges_list')

    plans = ChallengeSubscriptionPlan.objects.annotate(
        subscription_count=Count('subscriptions', filter=Q(subscriptions__status='active'))
    ).order_by('sort_order', 'price')

    # Apply filters
    search = request.GET.get('search')
    if search:
        plans = plans.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    duration_filter = request.GET.get('duration')
    if duration_filter:
        plans = plans.filter(duration=duration_filter)

    is_active_filter = request.GET.get('is_active')
    if is_active_filter:
        plans = plans.filter(is_active=is_active_filter == 'true')

    # Pagination
    paginator = Paginator(plans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_plans = ChallengeSubscriptionPlan.objects.count()
    active_plans = ChallengeSubscriptionPlan.objects.filter(is_active=True).count()
    total_subscriptions = UserChallengeSubscription.objects.filter(status='active').count()

    context = {
        'page_title': 'Manage Challenge Subscription Plans',
        'plans': page_obj,
        'total_plans': total_plans,
        'active_plans': active_plans,
        'total_subscriptions': total_subscriptions,
        'search': search,
        'duration_filter': duration_filter,
        'is_active_filter': is_active_filter,
        'duration_choices': ChallengeSubscriptionPlan.DURATION_CHOICES,
    }
    return render(request, 'challenges/admin/subscription_plans_list.html', context)


@staff_member_required
def admin_subscription_plan_create(request):
    """
    Create subscription plan (admin).
    """
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access subscription plan management.')
        return redirect('challenges:admin_challenges_list')

    if request.method == 'POST':
        form = ChallengeSubscriptionPlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Subscription plan "{plan.name}" created successfully!')
            return redirect('challenges:admin_subscription_plan_detail', plan_id=plan.id)
    else:
        form = ChallengeSubscriptionPlanForm()

    context = {
        'page_title': 'Create Challenge Subscription Plan',
        'form': form,
        'csrf_token': get_token(request),
    }
    return render(request, 'challenges/admin/subscription_plan_form.html', context)


@staff_member_required
def admin_subscription_plan_detail(request, plan_id):
    """
    Admin subscription plan detail view.
    """
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access subscription plan management.')
        return redirect('challenges:admin_challenges_list')

    plan = get_object_or_404(
        ChallengeSubscriptionPlan.objects.prefetch_related(
            'subscriptions__user'
        ),
        id=plan_id
    )

    # Get plan statistics
    total_subscriptions = plan.subscriptions.count()
    active_subscriptions = plan.subscriptions.filter(status='active').count()
    expired_subscriptions = plan.subscriptions.filter(status='expired').count()
    pending_subscriptions = plan.subscriptions.filter(status='pending').count()
    total_revenue = plan.subscriptions.filter(status='active').aggregate(
        total=models.Sum('amount_paid')
    )['total'] or 0

    # Calculate average revenue per user
    average_revenue_per_user = 0
    if active_subscriptions > 0:
        average_revenue_per_user = total_revenue / active_subscriptions

    # Recent subscriptions
    recent_subscriptions = plan.subscriptions.select_related('user').order_by('-created_at')[:10]

    # Add convenience attributes for templates
    for subscription in recent_subscriptions:
        subscription.user.full_name_or_email = subscription.user.get_full_name() or subscription.user.email

    context = {
        'page_title': f'Plan: {plan.name}',
        'plan': plan,
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        'pending_subscriptions': pending_subscriptions,
        'total_revenue': total_revenue,
        'average_revenue_per_user': average_revenue_per_user,
        'recent_subscriptions': recent_subscriptions,
    }
    return render(request, 'challenges/admin/subscription_plan_detail.html', context)


@staff_member_required
def admin_subscription_plan_edit(request, plan_id):
    """
    Edit subscription plan (admin).
    """
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access subscription plan management.')
        return redirect('challenges:admin_challenges_list')

    plan = get_object_or_404(ChallengeSubscriptionPlan, id=plan_id)

    if request.method == 'POST':
        form = ChallengeSubscriptionPlanForm(request.POST, instance=plan)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Subscription plan "{plan.name}" updated successfully!')
            return redirect('challenges:admin_subscription_plan_detail', plan_id=plan.id)
    else:
        form = ChallengeSubscriptionPlanForm(instance=plan)

    context = {
        'page_title': f'Edit Plan: {plan.name}',
        'form': form,
        'plan': plan,
        'csrf_token': get_token(request),
    }
    return render(request, 'challenges/admin/subscription_plan_form.html', context)


@staff_member_required
def admin_subscription_plan_confirm_delete(request, plan_id):
    """
    Confirm deletion of subscription plan (admin).
    """
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access subscription plan management.')
        return redirect('challenges:admin_challenges_list')

    plan = get_object_or_404(ChallengeSubscriptionPlan, id=plan_id)

    # Check if plan has active subscriptions
    active_subscriptions = plan.subscriptions.filter(status='active').count()

    context = {
        'page_title': f'Delete Plan: {plan.name}',
        'plan': plan,
        'active_subscriptions': active_subscriptions,
    }
    return render(request, 'challenges/admin/subscription_plan_confirm_delete.html', context)


@staff_member_required
def admin_subscription_plan_delete(request, plan_id):
    """
    Delete subscription plan (admin).
    """
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access subscription plan management.')
        return redirect('challenges:admin_challenges_list')

    plan = get_object_or_404(ChallengeSubscriptionPlan, id=plan_id)

    if request.method == 'POST':
        # Check if plan has active subscriptions
        active_subscriptions = plan.subscriptions.filter(status='active').count()
        if active_subscriptions > 0:
            messages.error(request, f'Cannot delete plan "{plan.name}" because it has {active_subscriptions} active subscriptions.')
            return redirect('challenges:admin_subscription_plan_detail', plan_id=plan_id)

        plan_name = plan.name
        plan.delete()
        messages.success(request, f'Subscription plan "{plan_name}" deleted successfully!')
        return redirect('challenges:admin_subscription_plans_list')

    # If not POST, redirect to confirm delete page
    return redirect('challenges:admin_subscription_plan_confirm_delete', plan_id=plan_id)
