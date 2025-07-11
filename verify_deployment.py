#!/usr/bin/env python3
"""
KodeSQL Deployment Verification Script
This script verifies that the Django application is properly configured for production.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_status(message, status):
    """Print a status message with emoji."""
    emoji = "✅" if status else "❌"
    print(f"{emoji} {message}")

def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print_status(f"{description} - SUCCESS", True)
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print_status(f"{description} - FAILED", False)
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print_status(f"{description} - TIMEOUT", False)
        return False
    except Exception as e:
        print_status(f"{description} - ERROR: {e}", False)
        return False

def check_file_exists(file_path, description):
    """Check if a file exists."""
    exists = Path(file_path).exists()
    print_status(f"{description}: {file_path}", exists)
    return exists

def check_environment_variables():
    """Check critical environment variables."""
    print_header("Environment Variables Check")
    
    required_vars = [
        'SECRET_KEY',
        'DEBUG',
        'ALLOWED_HOSTS',
        'PRIMARY_DB_NAME',
        'PRIMARY_DB_USER',
        'PRIMARY_DB_PASSWORD',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'SITE_URL',
        'EMAIL_BASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print_status(f"{var} is set", True)
        else:
            print_status(f"{var} is missing", False)
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def check_files():
    """Check if required files exist."""
    print_header("Required Files Check")
    
    files = [
        ('manage.py', 'Django management script'),
        ('.env', 'Environment variables file'),
        ('requirements.txt', 'Python dependencies'),
        ('passenger_wsgi.py', 'WSGI configuration'),
        ('.htaccess', 'Apache configuration'),
        ('sqlplayground/settings.py', 'Django settings'),
    ]
    
    all_exist = True
    for file_path, description in files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_django_configuration():
    """Check Django configuration."""
    print_header("Django Configuration Check")
    
    checks = [
        ('python manage.py check', 'Django system check'),
        ('python manage.py check --deploy', 'Django deployment check'),
    ]
    
    all_passed = True
    for command, description in checks:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed

def check_database_connections():
    """Check database connections."""
    print_header("Database Connection Check")
    
    # Check if test script exists
    if Path('test_query_run.py').exists():
        return run_command('python test_query_run.py', 'Database connection test')
    else:
        print_status("test_query_run.py not found - skipping database test", False)
        return False

def check_static_files():
    """Check static files configuration."""
    print_header("Static Files Check")
    
    return run_command('python manage.py collectstatic --noinput --dry-run', 'Static files collection test')

def check_dependencies():
    """Check if all dependencies are installed."""
    print_header("Dependencies Check")
    
    return run_command('pip check', 'Python dependencies check')

def main():
    """Main verification function."""
    print_header("KodeSQL Deployment Verification")
    print("This script will verify your Django application configuration.")
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print_status("manage.py not found. Please run this script from the Django project root.", False)
        sys.exit(1)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print_status("Environment variables loaded from .env", True)
    except ImportError:
        print_status("python-dotenv not installed - environment variables should be set manually", False)
    
    # Run all checks
    checks = [
        ("Environment Variables", check_environment_variables),
        ("Required Files", check_files),
        ("Dependencies", check_dependencies),
        ("Django Configuration", check_django_configuration),
        ("Static Files", check_static_files),
        ("Database Connections", check_database_connections),
    ]
    
    results = {}
    for check_name, check_function in checks:
        try:
            results[check_name] = check_function()
        except Exception as e:
            print_status(f"{check_name} check failed with error: {e}", False)
            results[check_name] = False
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for check_name, result in results.items():
        print_status(check_name, result)
    
    print(f"\n📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your application is ready for deployment.")
        return True
    else:
        print(f"\n⚠️ {total - passed} checks failed. Please fix the issues before deploying.")
        print("\nRecommended actions:")
        
        for check_name, result in results.items():
            if not result:
                if check_name == "Environment Variables":
                    print("- Update your .env file with missing variables")
                elif check_name == "Required Files":
                    print("- Ensure all required files are present")
                elif check_name == "Dependencies":
                    print("- Install missing dependencies: pip install -r requirements.txt")
                elif check_name == "Django Configuration":
                    print("- Fix Django configuration errors")
                elif check_name == "Static Files":
                    print("- Fix static files configuration")
                elif check_name == "Database Connections":
                    print("- Fix database connection issues")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
