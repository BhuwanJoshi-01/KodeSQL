#!/usr/bin/env python3
"""
WSGI configuration for KodeSQL Django application on cPanel.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

For cPanel hosting, this file should be placed in the root directory of your
Django project (same directory as manage.py).
"""

import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# Add the project directory to the Python path
sys.path.insert(0, str(BASE_DIR))

# Add the parent directory to the Python path (if needed)
sys.path.insert(0, str(BASE_DIR.parent))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from {env_path}")
    else:
        print(f"⚠️ .env file not found at {env_path}")
except ImportError:
    print("⚠️ python-dotenv not installed, environment variables should be set manually")

# Import Django's WSGI application
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print("✅ Django WSGI application loaded successfully")
except Exception as e:
    print(f"❌ Error loading Django WSGI application: {e}")
    raise

# For debugging purposes in cPanel (remove in production if not needed)
def application_debug(environ, start_response):
    """
    Debug wrapper for WSGI application.
    This can help troubleshoot issues in cPanel environment.
    """
    try:
        return application(environ, start_response)
    except Exception as e:
        import traceback
        error_msg = f"WSGI Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_msg)
        
        # Return a simple error response
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [error_msg.encode('utf-8')]

# Uncomment the line below if you need debugging in cPanel
# application = application_debug
