from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Course, UserCourseEnrollment
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a test user and enroll them in the sample course'

    def handle(self, *args, **options):
        self.stdout.write('Creating test user...')
        
        # Create test user
        user, created = User.objects.get_or_create(
            email='student@example.com',
            defaults={
                'username': 'student',
                'first_name': 'Test',
                'last_name': 'Student',
                'is_staff': False,
                'is_superuser': False
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(f'Created test user: {user.email}')
        else:
            self.stdout.write(f'Test user already exists: {user.email}')
        
        # Get the sample course
        try:
            course = Course.objects.get(slug='sql-fundamentals-course')
        except Course.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Sample course not found. Run create_sample_course first.')
            )
            return
        
        # Enroll user in course
        enrollment, created = UserCourseEnrollment.objects.get_or_create(
            user=user,
            course=course,
            defaults={
                'status': 'active',
                'enrolled_at': timezone.now(),
                'amount_paid': 0.00,
                'payment_method': 'free'
            }
        )
        
        if created:
            self.stdout.write(f'Enrolled {user.email} in {course.title}')
        else:
            self.stdout.write(f'{user.email} is already enrolled in {course.title}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Test user created successfully!\n'
                f'Email: {user.email}\n'
                f'Password: password123\n'
                f'Course: {course.title}\n'
                f'You can now login and test the course watch system.'
            )
        )
