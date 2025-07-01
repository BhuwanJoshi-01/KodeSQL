from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import models
from django.db.models import Count, Q, Avg, Prefetch, Sum
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from django.middleware.csrf import get_token
from decimal import Decimal
import json
import stripe
import uuid

from .models import (
    Course, CourseModule, CourseLesson, UserCourseEnrollment,
    CourseReview, CourseCertificate, CoursePayment, SubscriptionPlan, UserSubscription
)
from .forms import CourseForm, CourseModuleForm, CourseLessonForm, CourseFilterForm, SubscriptionPlanForm


def courses_list(request):
    """
    Public course listing page with search and filtering.
    """
    form = CourseFilterForm(request.GET)
    courses = Course.objects.filter(status='published').select_related('instructor')

    # Apply filters
    if form.is_valid():
        if form.cleaned_data.get('search'):
            search_term = form.cleaned_data['search']
            courses = courses.filter(
                Q(title__icontains=search_term) |
                Q(short_description__icontains=search_term) |
                Q(tags__icontains=search_term)
            )

        if form.cleaned_data.get('difficulty'):
            courses = courses.filter(difficulty=form.cleaned_data['difficulty'])

        if form.cleaned_data.get('course_type'):
            courses = courses.filter(course_type=form.cleaned_data['course_type'])

        if form.cleaned_data.get('category'):
            courses = courses.filter(category=form.cleaned_data['category'])

    # Annotate with enrollment count and average rating
    courses = courses.annotate(
        enrollment_count=Count('enrollments', filter=Q(enrollments__status__in=['active', 'completed'])),
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
    ).order_by('-is_featured', 'order', '-created_at')

    # Pagination
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get categories for filter
    categories = Course.objects.filter(status='published').values_list('category', flat=True).distinct()
    categories = [cat for cat in categories if cat]

    context = {
        'page_title': 'Courses',
        'courses': page_obj,
        'form': form,
        'categories': categories,
        'total_courses': courses.count(),
    }
    return render(request, 'courses/courses_list.html', context)


def course_detail(request, slug):
    """
    Course detail page with enrollment information.
    """
    course = get_object_or_404(
        Course.objects.select_related('instructor').prefetch_related(
            Prefetch('modules', queryset=CourseModule.objects.filter(is_active=True).order_by('order')),
            Prefetch('modules__lessons', queryset=CourseLesson.objects.filter(is_active=True).order_by('order')),
            'reviews__user'
        ),
        slug=slug,
        status='published'
    )

    # Check if user is enrolled
    user_enrollment = None
    if request.user.is_authenticated:
        try:
            user_enrollment = UserCourseEnrollment.objects.get(
                user=request.user,
                course=course,
                status__in=['active', 'completed']
            )
        except UserCourseEnrollment.DoesNotExist:
            pass

    # Get course statistics
    total_enrollments = course.enrollments.filter(status__in=['active', 'completed']).count()
    avg_rating = course.reviews.filter(is_approved=True).aggregate(avg=Avg('rating'))['avg'] or 0
    total_reviews = course.reviews.filter(is_approved=True).count()

    # Get recent reviews
    recent_reviews = course.reviews.filter(is_approved=True).select_related('user').order_by('-created_at')[:5]

    # Check if user can preview
    can_preview = course.allow_preview or (user_enrollment and user_enrollment.is_active_enrollment)

    context = {
        'page_title': course.title,
        'course': course,
        'user_enrollment': user_enrollment,
        'total_enrollments': total_enrollments,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
        'recent_reviews': recent_reviews,
        'can_preview': can_preview,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def my_courses(request):
    """
    User's enrolled courses dashboard - main implementation from reference code.
    """
    # Get user's enrollments with related data
    enrollments = UserCourseEnrollment.objects.filter(
        user=request.user,
        status__in=['active', 'completed']
    ).select_related('course', 'current_module', 'current_lesson').prefetch_related(
        'completed_lessons',
        'course__modules__lessons'
    ).order_by('-last_accessed')

    # Calculate statistics
    total_courses = enrollments.count()
    completed_courses = enrollments.filter(is_completed=True).count()
    in_progress_courses = enrollments.filter(
        completion_percentage__gt=0,
        completion_percentage__lt=100
    ).count()
    certificates_earned = enrollments.filter(certificate_issued=True).count()

    # Apply search and filters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.getlist('status')

    if search_query:
        enrollments = enrollments.filter(
            Q(course__title__icontains=search_query) |
            Q(course__short_description__icontains=search_query)
        )

    if status_filter:
        filter_q = Q()
        if 'completed' in status_filter:
            filter_q |= Q(is_completed=True)
        if 'in-progress' in status_filter:
            filter_q |= Q(completion_percentage__gt=0, completion_percentage__lt=100)
        if 'not-started' in status_filter:
            filter_q |= Q(completion_percentage=0)
        enrollments = enrollments.filter(filter_q)

    context = {
        'page_title': 'My Courses',
        'enrollments': enrollments,
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'in_progress_courses': in_progress_courses,
        'certificates_earned': certificates_earned,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'courses/my_courses.html', context)


@login_required
def api_my_courses(request):
    """
    API endpoint for user's enrolled courses (matches reference JavaScript expectations).
    """
    enrollments = UserCourseEnrollment.objects.filter(
        user=request.user,
        status__in=['active', 'completed']
    ).select_related('course').prefetch_related('completed_lessons')

    courses_data = []
    for enrollment in enrollments:
        course = enrollment.course
        courses_data.append({
            'id': course.id,
            'title': course.title,
            'description': course.short_description,
            'duration': f"{course.duration_hours}h" if course.duration_hours else "0h",
            'moduleCount': course.module_count,
            'level': course.get_difficulty_display(),
            'progress': enrollment.progress_percentage,
            'imageUrl': course.thumbnail.url if course.thumbnail else '',
            'status': 'completed' if enrollment.is_completed else ('in-progress' if enrollment.progress_percentage > 0 else 'not-started'),
            'enrolledAt': enrollment.enrolled_at.isoformat(),
            'lastAccessed': enrollment.last_accessed.isoformat(),
        })

    return JsonResponse({
        'courses': courses_data,
        'total': len(courses_data),
        'stats': {
            'total_courses': len(courses_data),
            'completed': len([c for c in courses_data if c['status'] == 'completed']),
            'in_progress': len([c for c in courses_data if c['status'] == 'in-progress']),
            'not_started': len([c for c in courses_data if c['status'] == 'not-started']),
        }
    })


def api_courses_list(request):
    """
    API endpoint for all available courses (for recommendations).
    """
    courses = Course.objects.filter(status='published').select_related('instructor')

    # Exclude courses user is already enrolled in
    if request.user.is_authenticated:
        enrolled_course_ids = UserCourseEnrollment.objects.filter(
            user=request.user,
            status__in=['active', 'completed']
        ).values_list('course_id', flat=True)
        courses = courses.exclude(id__in=enrolled_course_ids)

    courses_data = []
    for course in courses[:6]:  # Limit to 6 recommendations
        courses_data.append({
            'id': course.id,
            'title': course.title,
            'description': course.short_description,
            'duration': f"{course.duration_hours}h" if course.duration_hours else "0h",
            'moduleCount': course.module_count,
            'level': course.get_difficulty_display(),
            'imageUrl': course.thumbnail.url if course.thumbnail else '',
            'price': float(course.effective_price),
            'isFree': course.is_free,
            'rating': course.average_rating,
        })

    return JsonResponse({
        'courses': courses_data,
        'total': len(courses_data)
    })


@login_required
@require_POST
def api_course_enroll(request, slug):
    """
    API endpoint for course enrollment.
    """
    course = get_object_or_404(Course, slug=slug, status='published')

    # Check if already enrolled
    existing_enrollment = UserCourseEnrollment.objects.filter(
        user=request.user,
        course=course
    ).first()

    if existing_enrollment:
        if existing_enrollment.status in ['active', 'completed']:
            return JsonResponse({
                'success': False,
                'message': 'You are already enrolled in this course.'
            })

    # For free courses, create enrollment directly
    if course.is_free:
        enrollment, created = UserCourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'status': 'active',
                'amount_paid': 0.00,
            }
        )

        if created:
            return JsonResponse({
                'success': True,
                'message': 'Successfully enrolled in the course!',
                'redirect_url': reverse('courses:course_detail', kwargs={'slug': course.slug})
            })
        else:
            enrollment.status = 'active'
            enrollment.save()
            return JsonResponse({
                'success': True,
                'message': 'Enrollment reactivated!',
                'redirect_url': reverse('courses:course_detail', kwargs={'slug': course.slug})
            })

    # For paid courses, create pending enrollment and redirect to payment
    else:
        enrollment, created = UserCourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'status': 'pending',
                'amount_paid': 0.00,
            }
        )

        # Create payment record
        payment = CoursePayment.objects.create(
            enrollment=enrollment,
            amount=course.effective_price,
            payment_method='stripe',  # Default to Stripe
            status='pending'
        )

        return JsonResponse({
            'success': True,
            'message': 'Redirecting to payment...',
            'payment_required': True,
            'payment_url': f'/courses/payment/{payment.id}/',
            'amount': float(course.effective_price)
        })


@login_required
@require_POST
def api_lesson_complete(request, lesson_id):
    """
    Mark a lesson as completed and update progress.
    """
    lesson = get_object_or_404(CourseLesson, id=lesson_id)

    # Get user's enrollment
    try:
        enrollment = UserCourseEnrollment.objects.get(
            user=request.user,
            course=lesson.module.course,
            status__in=['active', 'completed']
        )
    except UserCourseEnrollment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'You are not enrolled in this course.'
        })

    # Mark lesson as completed
    enrollment.completed_lessons.add(lesson)

    # Update current lesson and module
    enrollment.current_lesson = lesson
    enrollment.current_module = lesson.module

    # Update progress
    enrollment.update_progress()

    return JsonResponse({
        'success': True,
        'message': 'Lesson marked as completed!',
        'progress': enrollment.progress_percentage,
        'is_completed': enrollment.is_completed,
        'certificate_issued': enrollment.certificate_issued
    })


@login_required
def course_enroll(request, slug):
    """
    Course enrollment page with Razorpay integration.
    """
    course = get_object_or_404(Course, slug=slug, status='published')

    # Check if already enrolled
    existing_enrollment = UserCourseEnrollment.objects.filter(
        user=request.user,
        course=course
    ).first()

    if existing_enrollment and existing_enrollment.status in ['active', 'completed']:
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('courses:course_detail', slug=course.slug)

    if request.method == 'POST':
        # Handle enrollment
        if course.is_free:
            enrollment, created = UserCourseEnrollment.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={
                    'status': 'active',
                    'amount_paid': 0.00,
                }
            )

            if not created:
                enrollment.status = 'active'
                enrollment.save()

            messages.success(request, f'Successfully enrolled in {course.title}!')
            return redirect('courses:course_detail', slug=course.slug)
        else:
            # For paid courses, redirect to subscription plans
            return redirect('courses:subscription_plans', slug=course.slug)

    context = {
        'page_title': f'Enroll in {course.title}',
        'course': course,
        'existing_enrollment': existing_enrollment,
    }
    return render(request, 'courses/course_enroll.html', context)


def certificate_view(request, certificate_id):
    """
    Display course completion certificate.
    """
    certificate = get_object_or_404(CourseCertificate, certificate_id=certificate_id, is_valid=True)

    # Check if user has access to this certificate
    if request.user.is_authenticated:
        if certificate.enrollment.user != request.user and not request.user.is_staff:
            raise Http404("Certificate not found")

    context = {
        'page_title': f'Certificate - {certificate.course_title}',
        'certificate': certificate,
    }
    return render(request, 'courses/certificate.html', context)


# Admin Views (Staff Only)
@staff_member_required
def admin_courses_list(request):
    """
    Admin course management list.
    """
    courses = Course.objects.select_related('instructor').annotate(
        enrollment_count=Count('enrollments', filter=Q(enrollments__status__in=['active', 'completed']))
    ).order_by('-created_at')

    # Apply filters
    search = request.GET.get('search')
    if search:
        courses = courses.filter(
            Q(title__icontains=search) |
            Q(instructor__email__icontains=search)
        )

    status_filter = request.GET.get('status')
    if status_filter:
        courses = courses.filter(status=status_filter)

    # Pagination
    paginator = Paginator(courses, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'Manage Courses',
        'courses': page_obj,
        'search': search,
        'status_filter': status_filter,
    }
    return render(request, 'courses/admin/courses_list.html', context)


@staff_member_required
def admin_course_create(request):
    """
    Create new course (admin).
    """
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course "{course.title}" created successfully!')
            return redirect('courses:admin_course_detail', slug=course.slug)
    else:
        form = CourseForm(user=request.user)

    context = {
        'page_title': 'Create Course',
        'form': form,
    }
    return render(request, 'courses/admin/course_form.html', context)


@staff_member_required
def admin_course_detail(request, slug):
    """
    Admin course detail view.
    """
    course = get_object_or_404(
        Course.objects.select_related('instructor').prefetch_related(
            'modules__lessons',
            'enrollments__user'
        ),
        slug=slug
    )

    # Get course statistics
    total_enrollments = course.enrollments.count()
    active_enrollments = course.enrollments.filter(status='active').count()
    completed_enrollments = course.enrollments.filter(status='completed').count()
    total_revenue = course.enrollments.aggregate(
        total=models.Sum('amount_paid')
    )['total'] or 0

    context = {
        'page_title': f'Manage: {course.title}',
        'course': course,
        'total_enrollments': total_enrollments,
        'active_enrollments': active_enrollments,
        'completed_enrollments': completed_enrollments,
        'total_revenue': total_revenue,
    }
    return render(request, 'courses/admin/course_detail.html', context)


@staff_member_required
def admin_course_edit(request, slug):
    """
    Edit course (admin).
    """
    course = get_object_or_404(Course, slug=slug)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course, user=request.user)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course "{course.title}" updated successfully!')
            return redirect('courses:admin_course_detail', slug=course.slug)
    else:
        form = CourseForm(instance=course, user=request.user)

    context = {
        'page_title': f'Edit: {course.title}',
        'form': form,
        'course': course,
    }
    return render(request, 'courses/admin/course_form.html', context)


@staff_member_required
@require_POST
def admin_course_delete(request, slug):
    """
    Delete course (admin).
    """
    course = get_object_or_404(Course, slug=slug)
    course_title = course.title
    course.delete()
    messages.success(request, f'Course "{course_title}" deleted successfully!')
    return redirect('courses:admin_courses_list')


# Payment Views
@login_required
def payment_page(request, payment_id):
    """
    Stripe payment page.
    """
    payment = get_object_or_404(CoursePayment, id=payment_id, enrollment__user=request.user)

    if payment.status != 'pending':
        messages.info(request, 'This payment has already been processed.')
        return redirect('courses:course_detail', slug=payment.enrollment.course.slug)

    # Get the client secret from the payment intent
    stripe.api_key = settings.STRIPE_SECRET_KEY
    intent = stripe.PaymentIntent.retrieve(payment.transaction_id)

    context = {
        'page_title': f'Payment - {payment.enrollment.course.title}',
        'payment': payment,
        'course': payment.enrollment.course,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'client_secret': intent.client_secret,
        'amount_in_cents': int(float(payment.amount) * 100),
    }
    return render(request, 'courses/payment.html', context)


@login_required
def payment_success(request):
    """
    Handle successful Stripe payment (both GET and POST).
    """
    try:
        # Get payment intent ID from request (GET or POST)
        payment_intent_id = request.GET.get('payment_intent') or request.POST.get('payment_intent_id')

        if not payment_intent_id:
            messages.error(request, 'Invalid payment data received.')
            return redirect('courses:courses_list')

        # Find the payment record
        payment = get_object_or_404(
            CoursePayment,
            transaction_id=payment_intent_id,
            enrollment__user=request.user
        )

        # Check if payment is already processed
        if payment.status == 'completed':
            messages.info(request, f'You are already enrolled in {payment.enrollment.course.title}.')
            return redirect('courses:course_detail', slug=payment.enrollment.course.slug)

        # Verify payment with Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if intent.status == 'succeeded':
            # Payment is valid, update records
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.gateway_response = intent
            payment.save()

            # Update enrollment
            enrollment = payment.enrollment
            enrollment.status = 'active'
            enrollment.amount_paid = payment.amount
            enrollment.payment_method = 'stripe'
            enrollment.payment_reference = payment_intent_id
            enrollment.save()

            # Check if this is a subscription payment
            subscription_id = intent.metadata.get('subscription_id')
            if subscription_id:
                try:
                    subscription = UserSubscription.objects.get(id=subscription_id)
                    subscription.activate()
                    subscription.payment_reference = payment_intent_id
                    subscription.save()

                    messages.success(request, f'Subscription activated! You now have {subscription.plan.name} access to {enrollment.course.title}.')
                except UserSubscription.DoesNotExist:
                    messages.success(request, f'Payment successful! You are now enrolled in {enrollment.course.title}.')
            else:
                messages.success(request, f'Payment successful! You are now enrolled in {enrollment.course.title}.')

            return redirect('courses:course_detail', slug=enrollment.course.slug)
        else:
            messages.error(request, 'Payment was not successful. Please try again.')
            return redirect('courses:courses_list')

    except Exception as e:
        messages.error(request, f'Payment processing failed: {str(e)}')
        return redirect('courses:courses_list')


@login_required
def payment_failed(request):
    """
    Handle failed Stripe payment.
    """
    payment_intent_id = request.GET.get('payment_intent_id')

    if payment_intent_id:
        try:
            payment = CoursePayment.objects.get(
                transaction_id=payment_intent_id,
                enrollment__user=request.user
            )
            payment.status = 'failed'
            payment.save()

            course_title = payment.enrollment.course.title
            messages.error(request, f'Payment failed for {course_title}. Please try again.')
            return redirect('courses:course_detail', slug=payment.enrollment.course.slug)

        except CoursePayment.DoesNotExist:
            pass

    messages.error(request, 'Payment failed. Please try again.')
    return redirect('courses:courses_list')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhooks for payment status updates.
    """
    try:
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        # Verify webhook signature if secret is configured
        if settings.STRIPE_WEBHOOK_SECRET:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        else:
            # For development without webhook secret
            event = json.loads(payload)

        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            # Handle successful payment
            payment_intent = event['data']['object']
            payment_intent_id = payment_intent['id']

            try:
                payment = CoursePayment.objects.get(transaction_id=payment_intent_id)
                if payment.status == 'pending':
                    payment.status = 'completed'
                    payment.completed_at = timezone.now()
                    payment.gateway_response = payment_intent
                    payment.save()

                    # Update enrollment
                    enrollment = payment.enrollment
                    enrollment.status = 'active'
                    enrollment.amount_paid = payment.amount
                    enrollment.save()

            except CoursePayment.DoesNotExist:
                pass

        elif event['type'] == 'payment_intent.payment_failed':
            # Handle failed payment
            payment_intent = event['data']['object']
            payment_intent_id = payment_intent['id']

            try:
                payment = CoursePayment.objects.get(transaction_id=payment_intent_id)
                payment.status = 'failed'
                payment.gateway_response = payment_intent
                payment.save()

            except CoursePayment.DoesNotExist:
                pass

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# Subscription Views
@login_required
def subscription_plans(request, slug):
    """
    Display subscription plans for a course.
    """
    course = get_object_or_404(Course, slug=slug, status='published')

    # Check if user is already enrolled
    existing_enrollment = UserCourseEnrollment.objects.filter(
        user=request.user,
        course=course,
        status__in=['active', 'completed']
    ).first()

    if existing_enrollment:
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('courses:course_detail', slug=course.slug)

    # Get subscription plans for this course
    subscription_plans = SubscriptionPlan.objects.filter(
        course=course,
        is_active=True
    ).order_by('sort_order', 'price')

    if not subscription_plans.exists():
        messages.error(request, 'No subscription plans available for this course.')
        return redirect('courses:course_detail', slug=course.slug)

    context = {
        'page_title': f'Choose Your Plan - {course.title}',
        'course': course,
        'subscription_plans': subscription_plans,
    }
    return render(request, 'courses/subscription_plans.html', context)


@login_required
def subscription_checkout(request, course_slug, plan_id):
    """
    Handle subscription checkout with selected plan.
    """
    course = get_object_or_404(Course, slug=course_slug, status='published')
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, course=course, is_active=True)

    # Check if user is already enrolled with active status
    existing_enrollment = UserCourseEnrollment.objects.filter(
        user=request.user,
        course=course,
        status__in=['active', 'completed']
    ).first()

    if existing_enrollment:
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('courses:course_detail', slug=course.slug)

    # Check if user already has a subscription for this course (any plan)
    existing_subscription = UserSubscription.objects.filter(
        user=request.user,
        course=course,
        status__in=['active', 'pending']
    ).first()

    if existing_subscription:
        if existing_subscription.status == 'pending':
            messages.info(request, 'You have a pending payment for this course. Please complete the payment.')
            # Find the payment record and redirect to payment page
            payment = CoursePayment.objects.filter(
                enrollment__user=request.user,
                enrollment__course=course,
                status='pending'
            ).first()
            if payment:
                return redirect('courses:payment_page', payment_id=payment.id)
        else:
            messages.info(request, 'You already have an active subscription for this course.')
            return redirect('courses:course_detail', slug=course.slug)

    # Create or get enrollment (update existing pending ones)
    enrollment, created = UserCourseEnrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={
            'status': 'pending',
            'amount_paid': 0.00,
        }
    )

    # If enrollment exists but is not pending, update it
    if not created and enrollment.status not in ['pending']:
        enrollment.status = 'pending'
        enrollment.amount_paid = 0.00
        enrollment.save()

    # Check if enrollment already has an active subscription for this plan
    existing_enrollment_subscription = UserSubscription.objects.filter(
        enrollment=enrollment,
        plan=plan,
        status__in=['active', 'pending']
    ).first()

    if existing_enrollment_subscription:
        # Update existing subscription instead of creating new one
        existing_enrollment_subscription.status = 'pending'
        existing_enrollment_subscription.amount_paid = plan.effective_price
        existing_enrollment_subscription.start_date = timezone.now()
        existing_enrollment_subscription.save()
        subscription = existing_enrollment_subscription
    else:
        # Create new subscription
        subscription = UserSubscription.objects.create(
            user=request.user,
            course=course,
            plan=plan,
            enrollment=enrollment,
            start_date=timezone.now(),
            status='pending',
            amount_paid=plan.effective_price,
        )

    # Create Stripe payment intent
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Convert price to cents (Stripe uses smallest currency unit)
        amount_in_cents = int(float(plan.effective_price) * 100)

        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency=settings.STRIPE_CURRENCY,
            metadata={
                'course_id': course.id,
                'user_id': request.user.id,
                'enrollment_id': enrollment.id,
                'subscription_id': subscription.id,
                'plan_id': plan.id,
            },
            description=f'Subscription: {plan.name} - {course.title}',
        )

        # Create payment record
        payment = CoursePayment.objects.create(
            enrollment=enrollment,
            amount=plan.effective_price,
            currency=settings.STRIPE_CURRENCY.upper(),
            payment_method='stripe',
            status='pending',
            transaction_id=intent.id,
            gateway_response=intent
        )

        # Redirect to payment page
        return redirect('courses:payment_page', payment_id=payment.id)

    except Exception as e:
        # Clean up created records on error (only if they were newly created)
        try:
            if 'subscription' in locals() and subscription and subscription.status == 'pending':
                subscription.delete()
            if created and enrollment and enrollment.status == 'pending':
                enrollment.delete()
        except:
            pass  # Ignore cleanup errors
        messages.error(request, f'Payment initialization failed: {str(e)}')
        return redirect('courses:subscription_plans', slug=course.slug)


# Subscription Plan Admin Views (Staff Only)
@staff_member_required
def admin_subscription_plans_list(request):
    """
    Admin subscription plan management list.
    """
    plans = SubscriptionPlan.objects.select_related('course').annotate(
        subscription_count=Count('subscriptions', filter=Q(subscriptions__status='active'))
    ).order_by('-created_at')

    # Apply filters
    search = request.GET.get('search')
    if search:
        plans = plans.filter(
            Q(name__icontains=search) |
            Q(course__title__icontains=search) |
            Q(description__icontains=search)
        )

    plan_type_filter = request.GET.get('plan_type')
    if plan_type_filter:
        plans = plans.filter(plan_type=plan_type_filter)

    duration_filter = request.GET.get('duration')
    if duration_filter:
        plans = plans.filter(duration=duration_filter)

    is_active_filter = request.GET.get('is_active')
    if is_active_filter:
        plans = plans.filter(is_active=is_active_filter == 'true')

    # Pagination
    paginator = Paginator(plans, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get statistics
    total_plans = SubscriptionPlan.objects.count()
    active_plans = SubscriptionPlan.objects.filter(is_active=True).count()
    global_plans = SubscriptionPlan.objects.filter(plan_type='global').count()
    course_specific_plans = SubscriptionPlan.objects.filter(plan_type='course_specific').count()

    context = {
        'page_title': 'Manage Subscription Plans',
        'plans': page_obj,
        'search': search,
        'plan_type_filter': plan_type_filter,
        'duration_filter': duration_filter,
        'is_active_filter': is_active_filter,
        'total_plans': total_plans,
        'active_plans': active_plans,
        'global_plans': global_plans,
        'course_specific_plans': course_specific_plans,
    }
    return render(request, 'courses/admin/subscription_plans_list.html', context)


@staff_member_required
def admin_subscription_plan_create(request):
    """
    Create new subscription plan (admin).
    """
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Subscription plan "{plan.name}" created successfully!')
            return redirect('courses:admin_subscription_plan_detail', plan_id=plan.id)
    else:
        form = SubscriptionPlanForm()

    context = {
        'page_title': 'Create Subscription Plan',
        'form': form,
        'csrf_token': get_token(request),
    }
    return render(request, 'courses/admin/subscription_plan_form.html', context)


@staff_member_required
def admin_subscription_plan_detail(request, plan_id):
    """
    Admin subscription plan detail view.
    """
    plan = get_object_or_404(
        SubscriptionPlan.objects.select_related('course').prefetch_related(
            'subscriptions__user',
            'subscriptions__enrollment'
        ),
        id=plan_id
    )

    # Get plan statistics
    total_subscriptions = plan.subscriptions.count()
    active_subscriptions = plan.subscriptions.filter(status='active').count()
    expired_subscriptions = plan.subscriptions.filter(status='expired').count()
    total_revenue = plan.subscriptions.filter(status='active').aggregate(
        total=models.Sum('amount_paid')
    )['total'] or 0

    # Get recent subscriptions
    recent_subscriptions = plan.subscriptions.select_related('user', 'course').order_by('-created_at')[:10]

    context = {
        'page_title': f'Manage Plan: {plan.name}',
        'plan': plan,
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        'total_revenue': total_revenue,
        'recent_subscriptions': recent_subscriptions,
    }
    return render(request, 'courses/admin/subscription_plan_detail.html', context)


@staff_member_required
def admin_subscription_plan_edit(request, plan_id):
    """
    Edit subscription plan (admin).
    """
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST, instance=plan)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Subscription plan "{plan.name}" updated successfully!')
            return redirect('courses:admin_subscription_plan_detail', plan_id=plan.id)
    else:
        form = SubscriptionPlanForm(instance=plan)

    context = {
        'page_title': f'Edit Plan: {plan.name}',
        'form': form,
        'plan': plan,
        'csrf_token': get_token(request),
    }
    return render(request, 'courses/admin/subscription_plan_form.html', context)


@staff_member_required
@require_POST
def admin_subscription_plan_delete(request, plan_id):
    """
    Delete subscription plan (admin).
    """
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    # Check if plan has active subscriptions
    active_subscriptions = plan.subscriptions.filter(status='active').count()
    if active_subscriptions > 0:
        messages.error(request, f'Cannot delete plan "{plan.name}" because it has {active_subscriptions} active subscriptions.')
        return redirect('courses:admin_subscription_plan_detail', plan_id=plan.id)

    plan_name = plan.name
    plan.delete()
    messages.success(request, f'Subscription plan "{plan_name}" deleted successfully!')
    return redirect('courses:admin_subscription_plans_list')


@staff_member_required
def admin_subscription_plan_confirm_delete(request, plan_id):
    """
    Confirm subscription plan deletion (admin).
    """
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    # Check if plan has active subscriptions
    active_subscriptions = plan.subscriptions.filter(status='active').count()
    total_subscriptions = plan.subscriptions.count()

    context = {
        'page_title': f'Delete Plan: {plan.name}',
        'plan': plan,
        'active_subscriptions': active_subscriptions,
        'total_subscriptions': total_subscriptions,
        'can_delete': active_subscriptions == 0,
    }
    return render(request, 'courses/admin/subscription_plan_confirm_delete.html', context)
