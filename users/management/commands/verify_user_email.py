"""
Management command to verify a user's email address.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import sys

User = get_user_model()


class Command(BaseCommand):
    help = 'Verify a user\'s email address'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address of the user to verify',
        )

    def handle(self, *args, **options):
        email = options['email']

        try:
            user = User.objects.get(email=email)
            
            if user.is_email_verified:
                self.stdout.write(
                    self.style.WARNING(f'User {email} is already verified.')
                )
            else:
                user.is_email_verified = True
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Email verified for user: {email}')
                )
                
                # Clean up any unused verification tokens
                from users.models import EmailVerificationToken
                tokens_deleted = EmailVerificationToken.objects.filter(
                    user=user, 
                    is_used=False
                ).delete()
                
                if tokens_deleted[0] > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Cleaned up {tokens_deleted[0]} unused verification tokens')
                    )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ User with email {email} does not exist.')
            )
            sys.exit(1)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to verify user: {e}')
            )
            sys.exit(1)
