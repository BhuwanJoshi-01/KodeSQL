"""
Custom adapters for django-allauth integration.
"""

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.sites.shortcuts import get_current_site
from .models import User, UserProfile, UserDatabase


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter to handle OAuth user creation and conflicts.
    Includes fix for MultipleObjectsReturned error.
    """

    def get_app(self, request, provider, client_id=None):
        """
        Override to fix MultipleObjectsReturned error.
        This method ensures we get exactly one SocialApp for the provider.
        """
        try:
            # Get current site
            site = get_current_site(request)

            # Try to get the app with site filter first
            if client_id:
                app = SocialApp.objects.filter(
                    provider=provider,
                    client_id=client_id,
                    sites=site
                ).first()
            else:
                app = SocialApp.objects.filter(
                    provider=provider,
                    sites=site
                ).first()

            # If no app found with site filter, try without site filter
            if not app:
                if client_id:
                    app = SocialApp.objects.filter(
                        provider=provider,
                        client_id=client_id
                    ).first()
                else:
                    app = SocialApp.objects.filter(
                        provider=provider
                    ).first()

            return app

        except Exception as e:
            # Fallback to default behavior if our fix fails
            return super().get_app(request, provider, client_id)
    
    def pre_social_login(self, request, sociallogin):
        """
        Handle pre-social login logic including email conflicts.
        """
        # Check if user is already authenticated
        if request.user.is_authenticated:
            return
        
        # Get email from social account
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return
        
        try:
            # Check if user with this email already exists
            existing_user = User.objects.get(email=email)
            
            # If user exists but hasn't connected this social account
            if not sociallogin.is_existing:
                # Connect the social account to existing user
                sociallogin.connect(request, existing_user)
                messages.success(
                    request, 
                    f'Your Google account has been connected to your existing {existing_user.email} account.'
                )
        except User.DoesNotExist:
            # User doesn't exist, will be created normally
            pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save the social account user and create associated profiles.
        """
        user = super().save_user(request, sociallogin, form)
        
        # Set email as verified for social accounts
        user.is_email_verified = True
        
        # Extract additional info from social account
        extra_data = sociallogin.account.extra_data
        
        # Set names if not already set
        if not user.first_name and extra_data.get('given_name'):
            user.first_name = extra_data.get('given_name', '')
        
        if not user.last_name and extra_data.get('family_name'):
            user.last_name = extra_data.get('family_name', '')
        
        # Generate username from email if not set
        if not user.username:
            base_username = user.email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user.username = username
        
        user.save()
        
        # Create user profile if it doesn't exist
        UserProfile.objects.get_or_create(user=user)
        
        # Create user database if it doesn't exist
        UserDatabase.objects.get_or_create(user=user)
        
        return user
    
    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """
        Handle authentication errors gracefully.
        """
        messages.error(
            request,
            f'Authentication with {provider_id.title()} failed. Please try again or use email/password login.'
        )
        # Redirect to login page instead of raising exception
        raise ImmediateHttpResponse(redirect(reverse('users:login')))


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter for additional account handling.
    """
    
    def save_user(self, request, user, form, commit=True):
        """
        Save user with additional profile creation.
        """
        user = super().save_user(request, user, form, commit=False)
        
        if commit:
            user.save()
            # Create associated profiles
            UserProfile.objects.get_or_create(user=user)
            UserDatabase.objects.get_or_create(user=user)
        
        return user
    
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Override to use our custom email sending logic if needed.
        """
        # Use default allauth email sending for now
        super().send_confirmation_mail(request, emailconfirmation, signup)
