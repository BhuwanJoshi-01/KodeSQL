"""
Management command to set up Google OAuth application.
"""

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os


class Command(BaseCommand):
    help = 'Set up Google OAuth application'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Setting up Google OAuth application...')

        # Get OAuth credentials from environment
        client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')

        if not client_id or not client_secret:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Google OAuth credentials not found in environment variables.\n'
                    'Please set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET in your .env file.'
                )
            )
            return

        # Get or create the default site
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={
                'domain': '127.0.0.1:8007',
                'name': 'SQL Master'
            }
        )

        if created:
            self.stdout.write(f'✅ Created site: {site.domain}')
        else:
            self.stdout.write(f'🔍 Using existing site: {site.domain}')

        # Create or update Google OAuth app
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth',
                'client_id': client_id,
                'secret': client_secret,
            }
        )

        if created:
            self.stdout.write('✅ Created Google OAuth application')
        else:
            # Update existing app with new credentials
            google_app.client_id = client_id
            google_app.secret = client_secret
            google_app.save()
            self.stdout.write('✅ Updated Google OAuth application')

        # Connect the app to the site
        google_app.sites.add(site)
        self.stdout.write(f'✅ Connected Google OAuth app to site: {site.domain}')

        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 Google OAuth setup complete!\n'
                'You can now use Google OAuth for authentication.\n'
                f'Make sure your Google Cloud Console is configured with:\n'
                f'- Authorized JavaScript origins: http://{site.domain}\n'
                f'- Authorized redirect URIs: http://{site.domain}/accounts/google/login/callback/'
            )
        )
