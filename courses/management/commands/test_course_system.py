from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Course, UserCourseEnrollment, CourseLesson
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Test the course system by creating a test user and enrollment'

    def handle(self, *args, **options):
        self.stdout.write('Testing course system...')
        
        # Create a test user
        test_user, created = User.objects.get_or_create(
            email='testuser@example.com',
            defaults={
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User',
            }
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write(f'Created test user: {test_user.email}')
        else:
            self.stdout.write(f'Using existing test user: {test_user.email}')
        
        # Get the free course
        try:
            free_course = Course.objects.get(course_type='free', status='published')
            self.stdout.write(f'Found free course: {free_course.title}')
            
            # Enroll the test user
            enrollment, created = UserCourseEnrollment.objects.get_or_create(
                user=test_user,
                course=free_course,
                defaults={
                    'status': 'active',
                    'amount_paid': Decimal('0.00'),
                }
            )
            
            if created:
                self.stdout.write(f'Enrolled test user in: {free_course.title}')
                
                # Mark some lessons as completed
                lessons = CourseLesson.objects.filter(module__course=free_course)[:2]
                for lesson in lessons:
                    enrollment.completed_lessons.add(lesson)
                    self.stdout.write(f'Marked lesson as completed: {lesson.title}')
                
                # Update progress
                enrollment.update_progress()
                self.stdout.write(f'Updated progress: {enrollment.progress_percentage}%')
                
            else:
                self.stdout.write(f'Test user already enrolled in: {free_course.title}')
                self.stdout.write(f'Current progress: {enrollment.progress_percentage}%')
            
        except Course.DoesNotExist:
            self.stdout.write(self.style.ERROR('No free course found. Run create_sample_courses first.'))
            return
        
        # Test API endpoints
        self.stdout.write('\nTesting course system components:')
        
        # Check course counts
        total_courses = Course.objects.filter(status='published').count()
        self.stdout.write(f'✓ Total published courses: {total_courses}')
        
        # Check enrollments
        total_enrollments = UserCourseEnrollment.objects.count()
        self.stdout.write(f'✓ Total enrollments: {total_enrollments}')
        
        # Check user's enrollments
        user_enrollments = UserCourseEnrollment.objects.filter(user=test_user).count()
        self.stdout.write(f'✓ Test user enrollments: {user_enrollments}')
        
        self.stdout.write(self.style.SUCCESS('\nCourse system test completed!'))
        self.stdout.write('You can now:')
        self.stdout.write('1. Visit /courses/ to see the course listing')
        self.stdout.write('2. Login with testuser@example.com / testpass123')
        self.stdout.write('3. Visit /courses/my-courses/ to see enrolled courses')
        self.stdout.write('4. Test the course detail and enrollment flow')
