from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods, require_POST
from django.utils import timezone
from django.db import models
from django.db.models import Count, Q, Avg, Prefetch, Sum
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils.text import slugify
from decimal import Decimal
import json

from .models import (
    Course, CourseModule, CourseLesson, UserCourseEnrollment,
    CourseReview, CourseCertificate, CoursePayment
)
from .forms import CourseForm, CourseModuleForm, CourseLessonForm, CourseFilterForm


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
    Course enrollment page.
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
            # For paid courses, redirect to payment
            enrollment, created = UserCourseEnrollment.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={
                    'status': 'pending',
                    'amount_paid': 0.00,
                }
            )

            messages.info(request, 'Please complete payment to access the course.')
            return redirect('courses:course_detail', slug=course.slug)

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
