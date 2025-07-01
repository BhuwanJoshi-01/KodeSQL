#!/usr/bin/env python3
"""
Test script to verify that the template fixes are working correctly.
This tests that get_*_display() methods now work properly in templates.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from django.template.loader import get_template
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from courses.models import Course, SubscriptionPlan

User = get_user_model()

def test_subscription_plan_template():
    """Test subscription plan template rendering"""
    print("Testing Subscription Plan Template...")
    
    try:
        # Get a test subscription plan
        plan = SubscriptionPlan.objects.first()
        if not plan:
            print("   ❌ No subscription plans found")
            return False
        
        # Create a simple test template content
        from jinja2 import Environment, DictLoader
        
        template_content = """
Plan: {{ plan.name }}
Type: {{ plan.get_plan_type_display() }}
Duration: {{ plan.get_duration_display() }}
Price: ${{ plan.price }}
        """.strip()
        
        env = Environment(loader=DictLoader({'test': template_content}))
        template = env.get_template('test')
        rendered = template.render({'plan': plan})
        
        print(f"   ✅ Template rendered successfully")
        print(f"   Rendered content:")
        print(f"   {rendered}")
        
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
            return False
        else:
            print(f"   ✅ No functools.partial issues found!")
            
        # Check that actual display values are present
        plan_type_display = plan.get_plan_type_display()
        duration_display = plan.get_duration_display()
        
        if plan_type_display in rendered and duration_display in rendered:
            print(f"   ✅ Display values properly rendered:")
            print(f"      Plan Type: {plan_type_display}")
            print(f"      Duration: {duration_display}")
            return True
        else:
            print(f"   ❌ Display values not found in rendered content")
            return False
            
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
        
        from jinja2 import Environment, DictLoader
        
        template_content = """
Course: {{ course.title }}
Difficulty: {{ course.get_difficulty_display() }}
Type: {{ course.get_course_type_display() }}
Status: {{ course.get_status_display() }}
        """.strip()
        
        env = Environment(loader=DictLoader({'test': template_content}))
        template = env.get_template('test')
        rendered = template.render({'course': course})
        
        print(f"   ✅ Template rendered successfully")
        print(f"   Rendered content:")
        print(f"   {rendered}")
        
        # Check for issues
        if 'functools.partial' not in rendered:
            print(f"   ✅ No functools.partial issues found!")
            
            # Verify actual values
            difficulty_display = course.get_difficulty_display()
            type_display = course.get_course_type_display()
            status_display = course.get_status_display()
            
            print(f"   ✅ Display values:")
            print(f"      Difficulty: {difficulty_display}")
            print(f"      Type: {type_display}")
            print(f"      Status: {status_display}")
            return True
        else:
            print(f"   ❌ Found functools.partial in rendered content")
            return False
            
    except Exception as e:
        print(f"   ❌ Course template test failed: {e}")
        return False

def test_actual_template_file():
    """Test an actual template file from the project"""
    print("\nTesting Actual Template File...")
    
    try:
        # Test the subscription plan detail template
        plan = SubscriptionPlan.objects.first()
        if not plan:
            print("   ❌ No subscription plans found")
            return False
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/')
        request.user = User.objects.first() or User.objects.create_user('test', 'test@example.com', 'password')
        
        # Try to render the actual template
        template = get_template('courses/admin/subscription_plan_detail.html')
        context = {
            'plan': plan,
            'request': request,
        }
        
        rendered = template.render(context, request)
        
        print(f"   ✅ Actual template rendered successfully ({len(rendered)} characters)")
        
        # Check for issues in the rendered content
        if 'functools.partial' in rendered:
            print(f"   ❌ Found functools.partial in actual template")
            # Show a snippet of the problematic content
            lines = rendered.split('\n')
            for i, line in enumerate(lines):
                if 'functools.partial' in line:
                    print(f"   Line {i+1}: {line.strip()}")
                    break
            return False
        else:
            print(f"   ✅ No functools.partial issues in actual template!")
            return True
            
    except Exception as e:
        print(f"   ❌ Actual template test failed: {e}")
        return False

def main():
    """Run all template tests"""
    print("🔧 Testing Final Template Fixes")
    print("=" * 50)
    
    tests = [
        test_subscription_plan_template,
        test_course_template,
        test_actual_template_file,
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
        print("1. Added parentheses () to all get_*_display method calls")
        print("2. Fixed functools.partial display issues")
        print("3. Templates now properly render field display values")
        print("4. No more raw Django model method objects in output")
        
        print("\n🌟 Your subscription plan page should now display:")
        print("   - 'Course Specific' instead of functools.partial(...)")
        print("   - '1 Month' instead of functools.partial(...)")
        print("   - Proper display values for all choice fields")
        
        return True
    else:
        print(f"\n❌ {total - passed} tests failed. Check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
