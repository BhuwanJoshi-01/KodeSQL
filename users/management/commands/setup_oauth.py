import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Set up Google OAuth application properly'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up Google OAuth...'))
        
        # Get credentials from environment
        client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            self.stdout.write(
                self.style.ERROR('Google OAuth credentials not found in environment variables')
            )
            return
        
        # Get or create the current site
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': '127.0.0.1:8007',
                'name': 'NamasteSQL Development'
            }
        )
        
        if not created:
            site.domain = '127.0.0.1:8007'
            site.name = 'NamasteSQL Development'
            site.save()
        
        self.stdout.write(f'Site configured: {site.domain}')
        
        # Create or update Google OAuth app
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth',
                'client_id': client_id,
                'secret': client_secret,
            }
        )
        
        if not created:
            google_app.name = 'Google OAuth'
            google_app.client_id = client_id
            google_app.secret = client_secret
            google_app.save()
        
        # Add the site to the app
        google_app.sites.clear()  # Clear existing sites
        google_app.sites.add(site)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Google OAuth app {"created" if created else "updated"} successfully!'
            )
        )
        self.stdout.write(f'App ID: {google_app.id}')
        self.stdout.write(f'Provider: {google_app.provider}')
        self.stdout.write(f'Client ID: {google_app.client_id[:20]}...')
        self.stdout.write(f'Connected to site: {site.domain}')
        
        # Verify setup
        total_apps = SocialApp.objects.count()
        google_apps = SocialApp.objects.filter(provider='google').count()
        
        self.stdout.write(f'Total social apps: {total_apps}')
        self.stdout.write(f'Google apps: {google_apps}')
        
        if google_apps == 1:
            self.stdout.write(self.style.SUCCESS('✅ OAuth setup completed successfully!'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  Found {google_apps} Google apps, expected 1'))
