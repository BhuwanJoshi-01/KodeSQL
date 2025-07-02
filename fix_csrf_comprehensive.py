#!/usr/bin/env python
"""
Comprehensive CSRF fix script for Django admin forms
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from django.test import RequestFactory
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model

def test_csrf_token_generation():
    """Test if CSRF tokens are being generated correctly"""
    print("🔍 Testing CSRF token generation...\n")
    
    try:
        # Create a test request
        factory = RequestFactory()
        request = factory.get('/')
        
        # Add session middleware data
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        # Generate CSRF token
        token = get_token(request)
        
        print(f"✅ CSRF token generated successfully: {token[:10]}...")
        print(f"   Token length: {len(token)} characters")
        
        if len(token) != 64:
            print(f"⚠️  Warning: CSRF token length is {len(token)}, expected 64")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating CSRF token: {e}")
        return False

def check_django_settings():
    """Check Django settings for CSRF configuration"""
    print("\n🔍 Checking Django settings...\n")
    
    issues = []
    
    # Check CSRF middleware
    if 'django.middleware.csrf.CsrfViewMiddleware' not in settings.MIDDLEWARE:
        issues.append("CSRF middleware not found in MIDDLEWARE setting")
    else:
        print("✅ CSRF middleware is properly configured")
    
    # Check SECRET_KEY
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 50:
        issues.append("SECRET_KEY is too short or missing")
    else:
        print("✅ SECRET_KEY is properly configured")
    
    # Check session configuration
    if not hasattr(settings, 'SESSION_COOKIE_AGE'):
        print("⚠️  SESSION_COOKIE_AGE not set, using default")
    else:
        print(f"✅ Session cookie age: {settings.SESSION_COOKIE_AGE} seconds")
    
    # Check CSRF settings
    csrf_settings = [
        'CSRF_COOKIE_AGE',
        'CSRF_COOKIE_DOMAIN',
        'CSRF_COOKIE_HTTPONLY',
        'CSRF_COOKIE_NAME',
        'CSRF_COOKIE_PATH',
        'CSRF_COOKIE_SAMESITE',
        'CSRF_COOKIE_SECURE',
        'CSRF_FAILURE_VIEW',
        'CSRF_HEADER_NAME',
        'CSRF_TRUSTED_ORIGINS',
        'CSRF_USE_SESSIONS',
    ]
    
    for setting in csrf_settings:
        if hasattr(settings, setting):
            value = getattr(settings, setting)
            print(f"ℹ️  {setting}: {value}")
    
    return issues

def create_csrf_debug_view():
    """Create a debug view to test CSRF tokens"""
    debug_view_content = '''
from django.shortcuts import render
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
import json

def csrf_debug(request):
    """Debug view to check CSRF token"""
    context = {
        'csrf_token': get_token(request),
        'method': request.method,
        'has_session': hasattr(request, 'session'),
        'session_key': getattr(request.session, 'session_key', None) if hasattr(request, 'session') else None,
    }
    
    if request.method == 'POST':
        context.update({
            'post_data': dict(request.POST),
            'csrf_token_from_post': request.POST.get('csrfmiddlewaretoken', 'Not found'),
        })
    
    return JsonResponse(context, indent=2)

@csrf_exempt
def csrf_test_form(request):
    """Test form for CSRF debugging"""
    if request.method == 'POST':
        return JsonResponse({
            'status': 'success',
            'message': 'Form submitted successfully',
            'csrf_token_received': request.POST.get('csrfmiddlewaretoken', 'Not found')
        })
    
    return render(request, 'csrf_test.html')
'''
    
    # Write debug view
    with open('csrf_debug_views.py', 'w') as f:
        f.write(debug_view_content)
    
    # Create test template
    test_template = '''<!DOCTYPE html>
<html>
<head>
    <title>CSRF Test</title>
</head>
<body>
    <h1>CSRF Token Test</h1>
    <form method="post">
        {% csrf_token %}
        <input type="text" name="test_field" value="test">
        <button type="submit">Submit</button>
    </form>
    
    <script>
    // Log CSRF token for debugging
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        console.log('CSRF Token found:', csrfToken.value);
        console.log('Token length:', csrfToken.value.length);
    } else {
        console.error('CSRF Token not found!');
    }
    </script>
</body>
</html>'''
    
    os.makedirs('templates', exist_ok=True)
    with open('templates/csrf_test.html', 'w') as f:
        f.write(test_template)
    
    print("✅ Created CSRF debug files:")
    print("   - csrf_debug_views.py")
    print("   - templates/csrf_test.html")

def main():
    """Main function"""
    print("🔧 Comprehensive CSRF Debugging and Fix\n")
    print("=" * 50)
    
    # Test CSRF token generation
    token_ok = test_csrf_token_generation()
    
    # Check Django settings
    setting_issues = check_django_settings()
    
    # Create debug tools
    create_csrf_debug_view()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY AND RECOMMENDATIONS\n")
    
    if token_ok and not setting_issues:
        print("✅ Django CSRF configuration appears to be correct.")
        print("\n🔧 Try these solutions:")
        print("1. Clear browser cache and cookies completely")
        print("2. Restart Django development server")
        print("3. Try in incognito/private browsing mode")
        print("4. Check browser console for JavaScript errors")
        print("5. Ensure you're not submitting forms via AJAX without proper CSRF handling")
    else:
        print("❌ Issues found:")
        if not token_ok:
            print("   - CSRF token generation failed")
        for issue in setting_issues:
            print(f"   - {issue}")
    
    print("\n🛠️  Additional debugging steps:")
    print("1. Add these URLs to your urlpatterns for debugging:")
    print("   path('csrf-debug/', csrf_debug, name='csrf_debug'),")
    print("   path('csrf-test/', csrf_test_form, name='csrf_test'),")
    print("2. Visit /csrf-debug/ to see CSRF token details")
    print("3. Visit /csrf-test/ to test form submission")
    
    print("\n💡 Common causes of CSRF errors:")
    print("   - Browser blocking cookies")
    print("   - Multiple tabs with different sessions")
    print("   - Form submitted via JavaScript without CSRF token")
    print("   - Cached pages with expired tokens")
    print("   - Middleware order issues")

if __name__ == '__main__':
    main()
