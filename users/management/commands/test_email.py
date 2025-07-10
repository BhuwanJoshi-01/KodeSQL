"""
Management command to test email sending functionality.
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email sending functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to',
            required=True
        )

    def handle(self, *args, **options):
        to_email = options['to']
        
        self.stdout.write(f"Testing email sending to: {to_email}")
        self.stdout.write(f"Using SMTP settings:")
        self.stdout.write(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        try:
            send_mail(
                subject='KodeSQL - Test Email',
                message='This is a test email from KodeSQL. If you received this, email sending is working correctly!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Test email sent successfully to {to_email}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to send test email: {e}')
            )
            self.stdout.write(
                self.style.WARNING('Please check your email configuration in settings.py or .env file')
            )
