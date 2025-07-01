#!/usr/bin/env python
"""
Debug script for subscription plan form
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from courses.models import Course, SubscriptionPlan
from courses.forms import SubscriptionPlanForm
from django.contrib.auth import get_user_model

def debug_form():
    """Debug the subscription plan form"""
    print("🔍 Debugging Subscription Plan Form...")
    
    # Get or create a test course
    User = get_user_model()
    staff_user, created = User.objects.get_or_create(
        email='admin@test.com',
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    
    test_course = None
    if Course.objects.exists():
        test_course = Course.objects.first()
        print(f"✅ Using existing course: {test_course.title}")
    else:
        test_course = Course.objects.create(
            title="Test Course",
            slug="test-course",
            short_description="A test course",
            description="This is a test course for subscription plans",
            instructor=staff_user,
            difficulty="beginner",
            course_type="paid",
            price=99.99,
            status="published"
        )
        print(f"✅ Created test course: {test_course.title}")
    
    # Test form data
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    form_data = {
        'name': f'Test Premium Plan {unique_suffix}',
        'duration': '1_month',  # Use different duration to avoid constraint
        'price': '49.99',
        'description': 'A test premium subscription plan',
        'features': '• Access to all lessons\n• Priority support\n• Certificate included',
        'plan_type': 'course_specific',
        'course': test_course.id,
        'is_active': True,
        'is_recommended': True,
        'sort_order': 1,
    }
    
    # Check existing plans to avoid conflicts
    existing_plans = SubscriptionPlan.objects.filter(
        course=test_course,
        plan_type='course_specific'
    ).values_list('duration', flat=True)
    print(f"Existing plan durations for this course: {list(existing_plans)}")

    # Use a duration that doesn't exist
    available_durations = ['1_month', '3_months', 'unlimited']
    chosen_duration = None
    for duration in available_durations:
        if duration not in existing_plans:
            chosen_duration = duration
            break

    if chosen_duration:
        form_data['duration'] = chosen_duration
        print(f"Using duration: {chosen_duration}")
    else:
        # Try global plan instead
        form_data['plan_type'] = 'global'
        form_data['course'] = None
        print("Switching to global plan to avoid conflicts")

    print("\n📝 Testing form validation...")
    form = SubscriptionPlanForm(data=form_data)
    
    print(f"Form is valid: {form.is_valid()}")
    
    if not form.is_valid():
        print("❌ Form validation errors:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        
        print("\nNon-field errors:")
        for error in form.non_field_errors():
            print(f"  {error}")
    else:
        print("✅ Form is valid!")
        
        # Try to save
        try:
            plan = form.save()
            print(f"✅ Plan saved successfully: {plan.id}")
            print(f"   Name: {plan.name}")
            print(f"   Features: {plan.features}")
            print(f"   Features type: {type(plan.features)}")
        except Exception as e:
            print(f"❌ Error saving plan: {e}")
    
    return form.is_valid()

if __name__ == '__main__':
    success = debug_form()
    if success:
        print("\n✅ Form debugging completed successfully")
    else:
        print("\n❌ Form debugging found issues")
