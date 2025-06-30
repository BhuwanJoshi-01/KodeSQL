from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib import messages
from django.core.paginator import Paginator
from django import forms
from .models import Tutorial, Lesson, UserTutorialProgress
from .forms import TutorialForm, LessonForm, LessonFormSet


def tutorials_list(request):
    """
    Tutorials list view with real data.
    """
    tutorials = Tutorial.objects.filter(is_active=True).annotate(
        total_lessons=Count('lessons', filter=Q(lessons__is_active=True))
    )

    # Get user progress if authenticated
    user_progress = {}
    if request.user.is_authenticated:
        progress_data = UserTutorialProgress.objects.filter(
            user=request.user
        ).select_related('tutorial')

        for progress in progress_data:
            user_progress[progress.tutorial.id] = {
                'completed_lessons': list(progress.completed_lessons.values_list('id', flat=True)),
                'is_completed': progress.is_completed,
                'progress_percentage': progress.progress_percentage
            }

    context = {
        'page_title': 'SQL Tutorials',
        'tutorials': tutorials,
        'user_progress': user_progress,
    }
    return render(request, 'tutorials/tutorials_list.html', context)


def tutorial_detail(request, tutorial_id):
    """
    Tutorial detail view with lessons.
    """
    tutorial = get_object_or_404(Tutorial, id=tutorial_id, is_active=True)
    lessons = tutorial.lessons.filter(is_active=True).order_by('order')

    # Get user progress if authenticated
    user_progress = None
    completed_lessons = []
    if request.user.is_authenticated:
        user_progress, created = UserTutorialProgress.objects.get_or_create(
            user=request.user,
            tutorial=tutorial
        )
        completed_lessons = list(user_progress.completed_lessons.values_list('id', flat=True))

    context = {
        'page_title': f'Tutorial: {tutorial.title}',
        'tutorial': tutorial,
        'lessons': lessons,
        'user_progress': user_progress,
        'completed_lessons': completed_lessons,
    }
    return render(request, 'tutorials/tutorial_detail.html', context)


def lesson_detail(request, tutorial_id, lesson_id):
    """
    Lesson detail view with content.
    """
    tutorial = get_object_or_404(Tutorial, id=tutorial_id, is_active=True)
    lesson = get_object_or_404(Lesson, id=lesson_id, tutorial=tutorial, is_active=True)

    # Get all lessons for navigation
    all_lessons = tutorial.lessons.filter(is_active=True).order_by('order')
    lesson_list = list(all_lessons)

    # Find current lesson index and navigation
    current_index = next((i for i, l in enumerate(lesson_list) if l.id == lesson.id), 0)
    prev_lesson = lesson_list[current_index - 1] if current_index > 0 else None
    next_lesson = lesson_list[current_index + 1] if current_index < len(lesson_list) - 1 else None

    # Get user progress if authenticated
    user_progress = None
    is_completed = False
    if request.user.is_authenticated:
        user_progress, created = UserTutorialProgress.objects.get_or_create(
            user=request.user,
            tutorial=tutorial
        )
        is_completed = user_progress.completed_lessons.filter(id=lesson.id).exists()

    context = {
        'page_title': f'{tutorial.title}: {lesson.title}',
        'tutorial': tutorial,
        'lesson': lesson,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'user_progress': user_progress,
        'is_completed': is_completed,
        'lesson_number': current_index + 1,
        'total_lessons': len(lesson_list),
    }
    return render(request, 'tutorials/lesson_detail.html', context)


@login_required
@require_http_methods(["POST"])
def complete_lesson(request):
    """
    Complete lesson API with real functionality.
    """
    try:
        lesson_id = request.POST.get('lesson_id')
        if not lesson_id:
            return JsonResponse({
                'success': False,
                'error': 'Lesson ID is required'
            })

        lesson = get_object_or_404(Lesson, id=lesson_id, is_active=True)
        tutorial = lesson.tutorial

        # Get or create user progress
        user_progress, created = UserTutorialProgress.objects.get_or_create(
            user=request.user,
            tutorial=tutorial
        )

        # Add lesson to completed lessons if not already completed
        if not user_progress.completed_lessons.filter(id=lesson.id).exists():
            user_progress.completed_lessons.add(lesson)
            user_progress.current_lesson = lesson

            # Check if tutorial is completed
            total_lessons = tutorial.lessons.filter(is_active=True).count()
            completed_count = user_progress.completed_lessons.count()

            if completed_count >= total_lessons:
                user_progress.is_completed = True
                user_progress.completed_at = timezone.now()

            user_progress.save()

        return JsonResponse({
            'success': True,
            'message': 'Lesson completed successfully!',
            'progress_percentage': user_progress.progress_percentage,
            'is_tutorial_completed': user_progress.is_completed
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# Admin Views for Content Management

@staff_member_required
def admin_tutorials_list(request):
    """
    Admin view to list all tutorials with management options.
    """
    tutorials = Tutorial.objects.all().annotate(
        total_lessons=Count('lessons')
    ).order_by('-created_at')

    # Pagination
    paginator = Paginator(tutorials, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'Manage Tutorials',
        'tutorials': page_obj,
        'total_tutorials': tutorials.count(),
    }
    return render(request, 'tutorials/admin/tutorials_list.html', context)


@staff_member_required
def admin_tutorial_create(request):
    """
    Admin view to create a new tutorial with lessons.
    """
    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES)
        formset = LessonFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            tutorial = form.save()
            formset.instance = tutorial
            formset.save()

            messages.success(request, f'Tutorial "{tutorial.title}" created successfully!')
            return redirect('tutorials:admin_tutorial_detail', tutorial_id=tutorial.id)
    else:
        form = TutorialForm()
        formset = LessonFormSet()

    context = {
        'page_title': 'Create Tutorial',
        'form': form,
        'formset': formset,
        'is_edit': False,
    }
    return render(request, 'tutorials/admin/tutorial_form.html', context)


@staff_member_required
def admin_tutorial_edit(request, tutorial_id):
    """
    Admin view to edit an existing tutorial.
    """
    tutorial = get_object_or_404(Tutorial, id=tutorial_id)

    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES, instance=tutorial)
        formset = LessonFormSet(request.POST, request.FILES, instance=tutorial)

        if form.is_valid() and formset.is_valid():
            tutorial = form.save()
            formset.save()

            messages.success(request, f'Tutorial "{tutorial.title}" updated successfully!')
            return redirect('tutorials:admin_tutorial_detail', tutorial_id=tutorial.id)
    else:
        form = TutorialForm(instance=tutorial)
        formset = LessonFormSet(instance=tutorial)

    context = {
        'page_title': f'Edit Tutorial: {tutorial.title}',
        'form': form,
        'formset': formset,
        'tutorial': tutorial,
        'is_edit': True,
    }
    return render(request, 'tutorials/admin/tutorial_form.html', context)


@staff_member_required
def admin_tutorial_detail(request, tutorial_id):
    """
    Admin view to view tutorial details and manage lessons.
    """
    tutorial = get_object_or_404(Tutorial, id=tutorial_id)
    lessons = tutorial.lessons.all().order_by('order')

    context = {
        'page_title': f'Tutorial: {tutorial.title}',
        'tutorial': tutorial,
        'lessons': lessons,
    }
    return render(request, 'tutorials/admin/tutorial_detail.html', context)


@staff_member_required
def admin_tutorial_delete(request, tutorial_id):
    """
    Admin view to delete a tutorial.
    """
    tutorial = get_object_or_404(Tutorial, id=tutorial_id)

    if request.method == 'POST':
        tutorial_title = tutorial.title
        tutorial.delete()
        messages.success(request, f'Tutorial "{tutorial_title}" deleted successfully!')
        return redirect('tutorials:admin_tutorials_list')

    context = {
        'page_title': f'Delete Tutorial: {tutorial.title}',
        'tutorial': tutorial,
    }
    return render(request, 'tutorials/admin/tutorial_confirm_delete.html', context)


@staff_member_required
def admin_lesson_create(request, tutorial_id):
    """
    Admin view to create a new lesson for a tutorial.
    """
    tutorial = get_object_or_404(Tutorial, id=tutorial_id)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.tutorial = tutorial
            lesson.save()

            messages.success(request, f'Lesson "{lesson.title}" created successfully!')
            return redirect('tutorials:admin_tutorial_detail', tutorial_id=tutorial.id)
    else:
        form = LessonForm(initial={'tutorial': tutorial})
        form.fields['tutorial'].widget = forms.HiddenInput()

    context = {
        'page_title': f'Create Lesson for: {tutorial.title}',
        'form': form,
        'tutorial': tutorial,
        'is_edit': False,
    }
    return render(request, 'tutorials/admin/lesson_form.html', context)


@staff_member_required
def admin_lesson_edit(request, lesson_id):
    """
    Admin view to edit an existing lesson.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            lesson = form.save()

            messages.success(request, f'Lesson "{lesson.title}" updated successfully!')
            return redirect('tutorials:admin_tutorial_detail', tutorial_id=lesson.tutorial.id)
    else:
        form = LessonForm(instance=lesson)

    context = {
        'page_title': f'Edit Lesson: {lesson.title}',
        'form': form,
        'lesson': lesson,
        'tutorial': lesson.tutorial,
        'is_edit': True,
    }
    return render(request, 'tutorials/admin/lesson_form.html', context)


@staff_member_required
def admin_lesson_delete(request, lesson_id):
    """
    Admin view to delete a lesson.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    tutorial = lesson.tutorial

    if request.method == 'POST':
        lesson_title = lesson.title
        lesson.delete()
        messages.success(request, f'Lesson "{lesson_title}" deleted successfully!')
        return redirect('tutorials:admin_tutorial_detail', tutorial_id=tutorial.id)

    context = {
        'page_title': f'Delete Lesson: {lesson.title}',
        'lesson': lesson,
        'tutorial': tutorial,
    }
    return render(request, 'tutorials/admin/lesson_confirm_delete.html', context)
