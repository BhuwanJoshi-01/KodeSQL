#!/usr/bin/env python
"""
Test script to debug form issues
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from users.forms import UserLoginForm, UserRegistrationForm
from users.models import User

def test_login_form():
    print("=== Testing Login Form ===")
    
    # Test with empty data
    form = UserLoginForm({})
    print(f"Empty form valid: {form.is_valid()}")
    print(f"Empty form errors: {form.errors}")
    
    # Test with invalid email
    form = UserLoginForm({
        'email': 'invalid-email',
        'password': 'test123'
    })
    print(f"Invalid email form valid: {form.is_valid()}")
    print(f"Invalid email form errors: {form.errors}")
    
    # Test with valid data but non-existent user
    form = UserLoginForm({
        'email': 'test@example.com',
        'password': 'test123'
    })
    print(f"Non-existent user form valid: {form.is_valid()}")
    print(f"Non-existent user form errors: {form.errors}")

def test_registration_form():
    print("\n=== Testing Registration Form ===")
    
    # Test with empty data
    form = UserRegistrationForm({})
    print(f"Empty form valid: {form.is_valid()}")
    print(f"Empty form errors: {form.errors}")
    
    # Test with valid data
    form = UserRegistrationForm({
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'username': 'testuser',
        'password1': 'TestPassword123!',
        'password2': 'TestPassword123!'
    })
    print(f"Valid form valid: {form.is_valid()}")
    print(f"Valid form errors: {form.errors}")
    
    # Test with mismatched passwords
    form = UserRegistrationForm({
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test2@example.com',
        'username': 'testuser2',
        'password1': 'TestPassword123!',
        'password2': 'DifferentPassword123!'
    })
    print(f"Mismatched passwords form valid: {form.is_valid()}")
    print(f"Mismatched passwords form errors: {form.errors}")

def test_existing_users():
    print("\n=== Testing Existing Users ===")
    users = User.objects.all()
    print(f"Total users in database: {users.count()}")
    for user in users:
        print(f"User: {user.email}, Username: {user.username}, Verified: {user.is_email_verified}, Superuser: {user.is_superuser}")

if __name__ == '__main__':
    test_existing_users()
    test_login_form()
    test_registration_form()
