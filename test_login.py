#!/usr/bin/env python
"""
Test script to debug login with existing user
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from users.forms import UserLoginForm
from users.models import User
from django.contrib.auth import authenticate

def test_login_with_existing_user():
    print("=== Testing Login with Existing User ===")
    
    # Get the first user
    user = User.objects.first()
    print(f"Testing with user: {user.email}")
    
    # Test authentication directly
    auth_user = authenticate(username=user.email, password='admin123')  # Try common password
    print(f"Direct authentication result: {auth_user}")
    
    # Test with the superuser we just created
    admin_user = User.objects.filter(email='admin@test.com').first()
    if admin_user:
        print(f"Testing with admin user: {admin_user.email}")
        auth_admin = authenticate(username=admin_user.email, password='admin123')
        print(f"Admin authentication result: {auth_admin}")
        
        # Test form with admin user
        form = UserLoginForm({
            'email': 'admin@test.com',
            'password': 'admin123'
        })
        print(f"Admin form valid: {form.is_valid()}")
        print(f"Admin form errors: {form.errors}")

if __name__ == '__main__':
    test_login_with_existing_user()
