#!/usr/bin/env python
"""
Test script to check email verification system functionality.
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from users.models import User, EmailVerificationToken
from users.views import send_verification_email
from django.test import RequestFactory

def test_email_configuration():
    """Test email configuration settings."""
    print("🔧 Testing Email Configuration...")
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"Email Port: {settings.EMAIL_PORT}")
    print(f"Email Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"Email Host User: {settings.EMAIL_HOST_USER}")
    print(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")
    print(f"Email Base URL: {settings.EMAIL_BASE_URL}")
    print()

def test_simple_email():
    """Test sending a simple email."""
    print("📧 Testing Simple Email Sending...")
    try:
        send_mail(
            'Test Email from KodeSQL',
            'This is a test email to verify SMTP configuration.',
            settings.DEFAULT_FROM_EMAIL,
            ['test@example.com'],
            fail_silently=False,
        )
        print("✅ Simple email sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Simple email sending failed: {e}")
        return False

def test_verification_email():
    """Test verification email functionality."""
    print("🔐 Testing Verification Email System...")
    
    # Create a test user (or get existing one)
    test_email = "test@example.com"
    try:
        user = User.objects.get(email=test_email)
        print(f"📝 Using existing test user: {user.email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username="testuser",
            email=test_email,
            password="testpass123",
            first_name="Test",
            last_name="User",
            is_email_verified=False
        )
        print(f"📝 Created test user: {user.email}")
    
    # Test verification email sending
    factory = RequestFactory()
    request = factory.get('/')
    
    try:
        result = send_verification_email(request, user)
        if result:
            print("✅ Verification email sent successfully!")
            
            # Check if token was created
            token = EmailVerificationToken.objects.filter(user=user, is_used=False).first()
            if token:
                print(f"🔑 Verification token created: {token.token}")
                print(f"⏰ Token expires at: {token.expires_at}")
                print(f"✅ Token is valid: {token.is_valid}")
                return True
            else:
                print("❌ No verification token found!")
                return False
        else:
            print("❌ Verification email sending failed!")
            return False
    except Exception as e:
        print(f"❌ Verification email test failed: {e}")
        return False

def test_message_system():
    """Test Django messages framework."""
    print("💬 Testing Message System...")
    from django.contrib.messages import get_messages
    from django.contrib.messages.storage.fallback import FallbackStorage
    from django.test import RequestFactory
    from django.contrib import messages
    
    factory = RequestFactory()
    request = factory.get('/')
    
    # Add messages storage to request
    setattr(request, 'session', {})
    setattr(request, '_messages', FallbackStorage(request))
    
    # Test different message types
    messages.success(request, "✅ Test success message")
    messages.error(request, "❌ Test error message")
    messages.warning(request, "⚠️ Test warning message")
    messages.info(request, "ℹ️ Test info message")
    
    # Check if messages were added
    message_list = list(get_messages(request))
    if message_list:
        print(f"✅ Messages system working! Found {len(message_list)} messages:")
        for msg in message_list:
            print(f"  - {msg.tags}: {msg}")
        return True
    else:
        print("❌ Messages system not working!")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Email Verification System Tests...\n")
    
    tests = [
        ("Email Configuration", test_email_configuration),
        ("Simple Email", test_simple_email),
        ("Verification Email", test_verification_email),
        ("Message System", test_message_system),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        
        try:
            if test_name == "Email Configuration":
                test_func()  # This test doesn't return a boolean
                results.append((test_name, True))
            else:
                result = test_func()
                results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
        
        print()
    
    # Summary
    print(f"{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        if test_name == "Email Configuration":
            print(f"📋 {test_name}: Configuration displayed")
        else:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} {test_name}")
            if result:
                passed += 1
    
    print(f"\nOverall: {passed}/{total-1} tests passed")  # -1 because config test doesn't count
    
    if passed == total - 1:
        print("🎉 All tests passed! Email verification system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()
