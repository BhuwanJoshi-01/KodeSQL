#!/usr/bin/env python
"""
Fix course completion data inconsistencies
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from courses.models import UserCourseEnrollment, Course
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

def fix_completion_data():
    print("🔧 Fixing Course Completion Data...")
    print("=" * 50)
    
    # Get all enrollments
    enrollments = UserCourseEnrollment.objects.all()
    fixed_count = 0
    
    for enrollment in enrollments:
        course = enrollment.course
        
        # Get total active lessons in the course
        total_lessons = course.modules.filter(is_active=True).aggregate(
            total=models.Count('lessons', filter=models.Q(lessons__is_active=True))
        )['total'] or 0
        
        # Get completed lessons count
        completed_lessons_count = enrollment.completed_lessons.count()
        
        # Calculate actual completion percentage
        if total_lessons > 0:
            actual_percentage = int((completed_lessons_count / total_lessons) * 100)
        else:
            actual_percentage = 0
        
        # Check if data needs fixing
        needs_fix = False
        old_values = {
            'completion_percentage': enrollment.completion_percentage,
            'is_completed': enrollment.is_completed,
            'certificate_issued': enrollment.certificate_issued
        }
        
        # Fix completion percentage
        if enrollment.completion_percentage != actual_percentage:
            enrollment.completion_percentage = actual_percentage
            needs_fix = True
        
        # Fix completion status
        should_be_completed = actual_percentage >= 100
        if enrollment.is_completed != should_be_completed:
            enrollment.is_completed = should_be_completed
            needs_fix = True
        
        # Fix certificate status (only issue if course is actually completed)
        if enrollment.certificate_issued and not should_be_completed:
            enrollment.certificate_issued = False
            enrollment.certificate_issued_at = None
            needs_fix = True
        
        # Update status field
        if should_be_completed:
            enrollment.status = 'completed'
        elif actual_percentage > 0:
            enrollment.status = 'active'
        else:
            enrollment.status = 'active'
        
        if needs_fix:
            print(f"\n🔧 Fixing enrollment for {enrollment.user.email} in '{course.title}':")
            print(f"   📖 Total lessons: {total_lessons}")
            print(f"   ✅ Completed lessons: {completed_lessons_count}")
            print(f"   📊 Completion: {old_values['completion_percentage']}% → {actual_percentage}%")
            print(f"   🏆 Is completed: {old_values['is_completed']} → {should_be_completed}")
            print(f"   📜 Certificate: {old_values['certificate_issued']} → {enrollment.certificate_issued}")
            
            enrollment.save()
            fixed_count += 1
    
    print(f"\n" + "=" * 50)
    print(f"🎉 Fixed {fixed_count} enrollment(s)")
    
    if fixed_count > 0:
        print("\n✅ Data Fixes Applied:")
        print("   1. Corrected completion percentages based on actual lesson progress")
        print("   2. Fixed completion status to match actual progress")
        print("   3. Removed invalid certificates for incomplete courses")
        print("   4. Updated enrollment status fields")
        
        print("\n🔄 Verification:")
        # Re-check the data
        problematic = 0
        for enrollment in UserCourseEnrollment.objects.all():
            course = enrollment.course
            total_lessons = course.modules.filter(is_active=True).aggregate(
                total=models.Count('lessons', filter=models.Q(lessons__is_active=True))
            )['total'] or 0
            
            completed_lessons_count = enrollment.completed_lessons.count()
            
            if total_lessons > 0:
                actual_percentage = int((completed_lessons_count / total_lessons) * 100)
                if (actual_percentage >= 100) != enrollment.is_completed:
                    problematic += 1
        
        if problematic == 0:
            print("   ✅ All enrollments now have consistent data")
        else:
            print(f"   ⚠️  {problematic} enrollment(s) still have issues")
    else:
        print("✅ No data inconsistencies found - all enrollments are correct")
    
    return fixed_count

if __name__ == '__main__':
    try:
        fix_completion_data()
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        import traceback
        traceback.print_exc()
