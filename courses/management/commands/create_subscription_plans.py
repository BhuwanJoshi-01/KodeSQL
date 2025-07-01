from django.core.management.base import BaseCommand
from courses.models import Course, SubscriptionPlan
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample subscription plans for courses'

    def handle(self, *args, **options):
        # Get paid courses
        paid_courses = Course.objects.filter(course_type__in=['paid', 'premium'], status='published')
        
        if not paid_courses.exists():
            self.stdout.write(self.style.WARNING('No paid courses found. Creating subscription plans for all courses.'))
            courses = Course.objects.filter(status='published')
        else:
            courses = paid_courses
        
        plans_created = 0
        
        for course in courses:
            # Create 1-month plan
            plan_1m, created = SubscriptionPlan.objects.get_or_create(
                course=course,
                duration='1_month',
                plan_type='course_specific',
                defaults={
                    'name': 'Monthly Access',
                    'price': course.effective_price * Decimal('0.4'),  # 40% of course price
                    'original_price': course.effective_price * Decimal('0.5'),
                    'description': f'Get 1 month access to {course.title}',
                    'features': [
                        'Full course access for 30 days',
                        'All video lessons',
                        'Downloadable resources',
                        'Community support'
                    ],
                    'is_active': True,
                    'is_recommended': False,
                    'sort_order': 1
                }
            )
            if created:
                plans_created += 1
                self.stdout.write(f'Created 1-month plan for {course.title}')
            
            # Create 3-month plan (recommended)
            plan_3m, created = SubscriptionPlan.objects.get_or_create(
                course=course,
                duration='3_months',
                plan_type='course_specific',
                defaults={
                    'name': 'Quarterly Access',
                    'price': course.effective_price * Decimal('0.7'),  # 70% of course price
                    'original_price': course.effective_price * Decimal('1.2'),
                    'description': f'Get 3 months access to {course.title}',
                    'features': [
                        'Full course access for 90 days',
                        'All video lessons',
                        'Downloadable resources',
                        'Priority community support',
                        'Extended practice time'
                    ],
                    'is_active': True,
                    'is_recommended': True,
                    'sort_order': 2
                }
            )
            if created:
                plans_created += 1
                self.stdout.write(f'Created 3-month plan for {course.title}')
            
            # Create unlimited plan
            plan_unlimited, created = SubscriptionPlan.objects.get_or_create(
                course=course,
                duration='unlimited',
                plan_type='course_specific',
                defaults={
                    'name': 'Lifetime Access',
                    'price': course.effective_price,  # Full course price
                    'description': f'Get unlimited access to {course.title}',
                    'features': [
                        'Lifetime course access',
                        'All video lessons',
                        'Downloadable resources',
                        'Priority community support',
                        'Future course updates',
                        'Certificate of completion'
                    ],
                    'is_active': True,
                    'is_recommended': False,
                    'sort_order': 3
                }
            )
            if created:
                plans_created += 1
                self.stdout.write(f'Created unlimited plan for {course.title}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {plans_created} subscription plans')
        )
