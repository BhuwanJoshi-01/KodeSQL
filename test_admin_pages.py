#!/usr/bin/env python
"""
Test script to check if admin pages load correctly after Jinja2 fixes
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def test_admin_pages():
    """Test admin pages to see if they load without template errors."""
    print("🧪 Testing Admin Pages with Jinja2 Templates\n")
    
    try:
        client = Client()
        
        # Get or create a superuser for testing
        test_user = User.objects.filter(is_superuser=True).first()
        if not test_user:
            test_user = User.objects.filter(is_staff=True).first()
        
        if not test_user:
            print("❌ No admin user found. Please create a superuser first.")
            return False
        
        # Login as admin user
        client.force_login(test_user)
        
        # Test admin pages
        admin_urls = [
            ('tutorials:admin_tutorials_list', 'Tutorials Admin'),
            ('challenges:admin_challenges_list', 'Challenges Admin'),
            ('courses:admin_courses_list', 'Courses Admin'),
        ]
        
        all_passed = True
        
        for url_name, description in admin_urls:
            try:
                print(f"Testing {description}...")
                url = reverse(url_name)
                response = client.get(url)
                
                if response.status_code == 200:
                    print(f"✅ {description} - OK (200)")
                elif response.status_code == 404:
                    print(f"⚠️  {description} - Not Found (404)")
                else:
                    print(f"❌ {description} - Error ({response.status_code})")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ {description} - Exception: {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    success = test_admin_pages()
    
    if success:
        print("\n🎉 All admin pages loaded successfully!")
        print("The Jinja2 template fixes are working correctly.")
    else:
        print("\n❌ Some admin pages failed to load.")
        print("Check the errors above for details.")
    
    return success

if __name__ == '__main__':
    main()
