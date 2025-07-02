"""
Management command to fix corrupted subscription plan features.
"""

from django.core.management.base import BaseCommand
from challenges.models import ChallengeSubscriptionPlan
import ast


class Command(BaseCommand):
    help = 'Fix corrupted subscription plan features that are stored as string representations of lists'

    def handle(self, *args, **options):
        self.stdout.write('Fixing subscription plan features...')
        
        plans = ChallengeSubscriptionPlan.objects.all()
        fixed_count = 0
        
        for plan in plans:
            if isinstance(plan.features, list) and len(plan.features) == 1:
                feature_item = plan.features[0]
                
                # Check if it's a string representation of a list
                if isinstance(feature_item, str) and feature_item.startswith('[') and feature_item.endswith(']'):
                    try:
                        # Parse the string representation back to a list
                        actual_features = ast.literal_eval(feature_item)
                        
                        if isinstance(actual_features, list):
                            plan.features = actual_features
                            plan.save()
                            fixed_count += 1
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Fixed features for plan: {plan.name}'
                                )
                            )
                            self.stdout.write(f'  Old: {feature_item}')
                            self.stdout.write(f'  New: {actual_features}')
                        
                    except (ValueError, SyntaxError) as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'Could not parse features for plan {plan.name}: {e}'
                            )
                        )
        
        if fixed_count == 0:
            self.stdout.write(
                self.style.SUCCESS('No corrupted features found. All subscription plans are already correct.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully fixed {fixed_count} subscription plan(s).')
            )
