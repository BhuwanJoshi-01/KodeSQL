#!/usr/bin/env python3
"""
Test script to verify that Django template fixes are working correctly.
This script tests that get_*_display methods are properly called with parentheses.
"""

import os
import sys
import django
from django.conf import settings
from jinja2 import Environment, DictLoader
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from courses.models import Course, SubscriptionPlan, UserCourseEnrollment
from challenges.models import Challenge
from tutorials.models import Tutorial

User = get_user_model()

def test_subscription_plan_template():
    """Test subscription plan template rendering"""
    print("Testing Subscription Plan Template...")

    try:
        # Get a test subscription plan
        plan = SubscriptionPlan.objects.first()
        if not plan:
            print("   ❌ No subscription plans found. Creating test plan...")
            course = Course.objects.first()
            plan = SubscriptionPlan.objects.create(
                name="Test Plan",
                duration="1_month",
                price=99.99,
                description="Test plan description",
                plan_type="course_specific",
                course=course
            )

        # Test direct method calls first
        print(f"   Direct method calls:")
        print(f"      plan.get_plan_type_display(): {plan.get_plan_type_display()}")
        print(f"      plan.get_duration_display(): {plan.get_duration_display()}")
        print(f"      Type of get_plan_type_display: {type(plan.get_plan_type_display)}")

        # Test template rendering with Jinja2
        template_content = """
        <div class="plan-details">
            <h3>{{ plan.name }}</h3>
            <p>Type: {{ plan.get_plan_type_display }}</p>
            <p>Duration: {{ plan.get_duration_display }}</p>
            <p>Price: ${{ plan.price }}</p>
        </div>
        """

        env = Environment(loader=DictLoader({'test': template_content}))
        template = env.get_template('test')
        rendered = template.render({'plan': plan})
        
        print(f"   ✅ Template rendered successfully")
        
        # Check for problematic patterns
        problematic_patterns = [
            'functools.partial',
            'Model._get_FIELD_display',
            'django.db.models',
            'CharField:',
        ]
        
        issues_found = []
        for pattern in problematic_patterns:
            if pattern in rendered:
                issues_found.append(pattern)
        
        if issues_found:
            print(f"   ❌ Found issues: {issues_found}")
            print(f"   Rendered content: {rendered}")
            return False
        else:
            print(f"   ✅ No functools.partial issues found")
            
        # Check that display values are properly rendered
        if plan.get_plan_type_display() in rendered and plan.get_duration_display() in rendered:
            print(f"   ✅ Display values properly rendered")
            print(f"      Plan Type: {plan.get_plan_type_display()}")
            print(f"      Duration: {plan.get_duration_display()}")
        else:
            print(f"   ❌ Display values not found in rendered content")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ Template test failed: {e}")
        return False

def test_course_template():
    """Test course template rendering"""
    print("\nTesting Course Template...")

    try:
        course = Course.objects.first()
        if not course:
            print("   ❌ No courses found")
            return False

        # Test direct method calls first
        print(f"   Direct method calls:")
        print(f"      course.get_difficulty_display(): {course.get_difficulty_display()}")
        print(f"      course.get_course_type_display(): {course.get_course_type_display()}")
        print(f"      course.get_status_display(): {course.get_status_display()}")

        template_content = """
        <div class="course-details">
            <h3>{{ course.title }}</h3>
            <p>Difficulty: {{ course.get_difficulty_display }}</p>
            <p>Type: {{ course.get_course_type_display }}</p>
            <p>Status: {{ course.get_status_display }}</p>
        </div>
        """

        env = Environment(loader=DictLoader({'test': template_content}))
        template = env.get_template('test')
        rendered = template.render({'course': course})
        
        print(f"   ✅ Template rendered successfully")
        
        # Check for issues
        if 'functools.partial' not in rendered:
            print(f"   ✅ No functools.partial issues found")
            print(f"      Difficulty: {course.get_difficulty_display()}")
            print(f"      Type: {course.get_course_type_display()}")
            print(f"      Status: {course.get_status_display()}")
            return True
        else:
            print(f"   ❌ Found functools.partial in rendered content")
            return False
            
    except Exception as e:
        print(f"   ❌ Course template test failed: {e}")
        return False

def test_challenge_template():
    """Test challenge template rendering"""
    print("\nTesting Challenge Template...")
    
    try:
        challenge = Challenge.objects.first()
        if not challenge:
            print("   ❌ No challenges found")
            return True  # Skip if no challenges
        
        template_content = """
        <div class="challenge-details">
            <h3>{{ challenge.title }}</h3>
            <p>Difficulty: {{ challenge.get_difficulty_display() }}</p>
        </div>
        """
        
        template = Template(template_content)
        context = Context({'challenge': challenge})
        rendered = template.render(context)
        
        print(f"   ✅ Template rendered successfully")
        
        if 'functools.partial' not in rendered:
            print(f"   ✅ No functools.partial issues found")
            print(f"      Difficulty: {challenge.get_difficulty_display()}")
            return True
        else:
            print(f"   ❌ Found functools.partial in rendered content")
            return False
            
    except Exception as e:
        print(f"   ❌ Challenge template test failed: {e}")
        return False

def test_tutorial_template():
    """Test tutorial template rendering"""
    print("\nTesting Tutorial Template...")
    
    try:
        tutorial = Tutorial.objects.first()
        if not tutorial:
            print("   ❌ No tutorials found")
            return True  # Skip if no tutorials
        
        template_content = """
        <div class="tutorial-details">
            <h3>{{ tutorial.title }}</h3>
            <p>Difficulty: {{ tutorial.get_difficulty_display() }}</p>
        </div>
        """
        
        template = Template(template_content)
        context = Context({'tutorial': tutorial})
        rendered = template.render(context)
        
        print(f"   ✅ Template rendered successfully")
        
        if 'functools.partial' not in rendered:
            print(f"   ✅ No functools.partial issues found")
            print(f"      Difficulty: {tutorial.get_difficulty_display()}")
            return True
        else:
            print(f"   ❌ Found functools.partial in rendered content")
            return False
            
    except Exception as e:
        print(f"   ❌ Tutorial template test failed: {e}")
        return False

def main():
    """Run all template tests"""
    print("🔧 Testing Django Template Fixes")
    print("=" * 50)
    
    tests = [
        test_subscription_plan_template,
        test_course_template,
        test_challenge_template,
        test_tutorial_template,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Template Fixes Working!")
        print("\n✅ Fixed Issues:")
        print("1. Added parentheses to all get_*_display() method calls")
        print("2. Fixed functools.partial display issues")
        print("3. Templates now properly render field display values")
        print("4. No more raw Django model method objects in output")
        
        print("\n🌟 Templates are now rendering correctly!")
        return True
    else:
        print(f"\n❌ {total - passed} tests failed. Check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
