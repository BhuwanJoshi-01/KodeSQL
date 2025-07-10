#!/usr/bin/env python
"""
Test script to check dashboard functionality
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from users.models import User

def test_dashboard():
    print("=== Testing Dashboard ===")
    
    # Create a test client
    client = Client()
    
    # Get a user to login with
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("No superuser found!")
        return
    
    print(f"Testing with user: {user.email}")
    
    # Try to access dashboard without login
    response = client.get('/dashboard/')
    print(f"Dashboard without login - Status: {response.status_code}")
    print(f"Redirected to: {response.url if hasattr(response, 'url') else 'No redirect'}")
    
    # Login the user
    client.force_login(user)
    print(f"Logged in user: {user.username}")
    
    # Try to access dashboard with login
    response = client.get('/dashboard/')
    print(f"Dashboard with login - Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Dashboard loaded successfully!")
        # Check if the template rendered correctly
        content = response.content.decode('utf-8')
        if 'Welcome back,' in content:
            print("✅ Welcome message found")
        else:
            print("❌ Welcome message not found")
            
        if 'military_tech' in content:
            print("❌ Template syntax error still present")
        else:
            print("✅ No template syntax errors found")
            
        if '{{ request.user.username }}' in content:
            print("❌ Unrendered template variables found")
        else:
            print("✅ All template variables rendered correctly")
    else:
        print(f"❌ Dashboard failed to load: {response.status_code}")

if __name__ == '__main__':
    test_dashboard()
