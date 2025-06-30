"""
Management command to send verification email to a user.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from users.models import EmailVerificationToken
from users.views import send_verification_email
import sys

User = get_user_model()


class Command(BaseCommand):
    help = 'Send verification email to a user'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address of the user',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Send email even if user is already verified',
        )

    def handle(self, *args, **options):
        email = options['email']
        force = options.get('force', False)

        try:
            user = User.objects.get(email=email)
            
            if user.is_email_verified and not force:
                self.stdout.write(
                    self.style.WARNING(f'User {email} is already verified. Use --force to send anyway.')
                )
                return
            
            # Create a mock request object for the email function
            class MockRequest:
                def build_absolute_uri(self, path):
                    # You'll need to update this with your actual domain
                    base_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8007')
                    return f"{base_url}{path}"
            
            mock_request = MockRequest()
            
            # Delete old unused tokens
            EmailVerificationToken.objects.filter(user=user, is_used=False).delete()
            
            # Send verification email
            if send_verification_email(mock_request, user):
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Verification email sent to: {email}')
                )
                
                # Show the verification token for manual verification if needed
                token = EmailVerificationToken.objects.filter(user=user, is_used=False).first()
                if token:
                    verification_url = mock_request.build_absolute_uri(
                        reverse('users:verify_email', args=[str(token.token)])
                    )
                    self.stdout.write(
                        self.style.WARNING(f'🔗 Verification URL: {verification_url}')
                    )
                    self.stdout.write(
                        self.style.WARNING(f'🎫 Token: {token.token}')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Failed to send verification email to: {email}')
                )
                self.stdout.write(
                    self.style.WARNING('Please check your email configuration.')
                )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ User with email {email} does not exist.')
            )
            sys.exit(1)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to send verification email: {e}')
            )
            sys.exit(1)
