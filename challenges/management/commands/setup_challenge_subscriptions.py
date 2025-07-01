from django.core.management.base import BaseCommand
from challenges.models import Challenge, ChallengeSubscriptionPlan
import random


class Command(BaseCommand):
    help = 'Setup challenge subscription plans and update existing challenges with subscription data'

    def handle(self, *args, **options):
        self.stdout.write('Setting up challenge subscription system...')
        
        # Create subscription plans
        self.create_subscription_plans()
        
        # Update existing challenges
        self.update_challenges()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up challenge subscription system!')
        )

    def create_subscription_plans(self):
        """Create subscription plans for challenges"""
        plans_data = [
            {
                'name': 'Monthly Premium',
                'duration': '1_month',
                'price': 19.99,
                'original_price': 29.99,
                'description': 'Perfect for getting started with premium challenges',
                'features': [
                    'Access to all premium challenges',
                    'Detailed solutions and explanations',
                    'Progress tracking',
                    'Company-specific challenges'
                ],
                'is_recommended': False,
                'sort_order': 1
            },
            {
                'name': 'Quarterly Premium',
                'duration': '3_months',
                'price': 49.99,
                'original_price': 79.99,
                'description': 'Best value for serious learners',
                'features': [
                    'Access to all premium challenges',
                    'Detailed solutions and explanations',
                    'Progress tracking',
                    'Company-specific challenges',
                    'Priority support'
                ],
                'is_recommended': True,
                'sort_order': 2
            },
            {
                'name': 'Semi-Annual Premium',
                'duration': '6_months',
                'price': 89.99,
                'original_price': 149.99,
                'description': 'Extended access for comprehensive learning',
                'features': [
                    'Access to all premium challenges',
                    'Detailed solutions and explanations',
                    'Progress tracking',
                    'Company-specific challenges',
                    'Priority support',
                    'Advanced analytics'
                ],
                'is_recommended': False,
                'sort_order': 3
            },
            {
                'name': 'Lifetime Premium',
                'duration': 'unlimited',
                'price': 199.99,
                'original_price': 299.99,
                'description': 'One-time payment for lifetime access',
                'features': [
                    'Lifetime access to all premium challenges',
                    'Detailed solutions and explanations',
                    'Progress tracking',
                    'Company-specific challenges',
                    'Priority support',
                    'Advanced analytics',
                    'Future content included'
                ],
                'is_recommended': False,
                'sort_order': 4
            }
        ]

        for plan_data in plans_data:
            plan, created = ChallengeSubscriptionPlan.objects.get_or_create(
                duration=plan_data['duration'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(f'Created subscription plan: {plan.name}')
            else:
                self.stdout.write(f'Subscription plan already exists: {plan.name}')

    def update_challenges(self):
        """Update existing challenges with subscription and company data"""
        companies = [
            'Amazon', 'Google', 'Microsoft', 'Netflix', 'Apple', 
            'Meta', 'Tesla', 'Uber', 'Airbnb', 'Spotify',
            'TCS', 'Infosys', 'Wipro', 'Deloitte', 'Accenture'
        ]
        
        tags_options = [
            ['joins', 'aggregation'],
            ['subqueries', 'window-functions'],
            ['joins', 'subqueries'],
            ['aggregation', 'window-functions'],
            ['joins'],
            ['aggregation'],
            ['subqueries'],
            ['window-functions'],
            ['joins', 'aggregation', 'subqueries'],
            ['advanced-sql']
        ]

        challenges = Challenge.objects.all()
        
        for i, challenge in enumerate(challenges):
            # Assign subscription type (70% free, 30% paid)
            if random.random() < 0.3:
                challenge.subscription_type = 'paid'
            else:
                challenge.subscription_type = 'free'
            
            # Assign random company
            challenge.company = random.choice(companies)
            
            # Assign random tags
            challenge.tags = random.choice(tags_options)
            
            challenge.save()
            
            self.stdout.write(
                f'Updated challenge: {challenge.title} - '
                f'{challenge.subscription_type} - {challenge.company}'
            )

        self.stdout.write(f'Updated {challenges.count()} challenges')
