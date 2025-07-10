#!/usr/bin/env python3
"""
Production Setup Script for KodeSQL
This script helps configure the application for production deployment.
"""

import os
import secrets
import subprocess
import sys
from pathlib import Path

def generate_secret_key():
    """Generate a new Django secret key."""
    return secrets.token_urlsafe(50)

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        'SECRET_KEY',
        'PRIMARY_DB_NAME',
        'PRIMARY_DB_USER',
        'PRIMARY_DB_PASSWORD',
        'QUERY_POSTGRES_DB_NAME',
        'QUERY_POSTGRES_USER',
        'QUERY_POSTGRES_PASSWORD',
        'QUERY_MYSQL_DB_NAME',
        'QUERY_MYSQL_USER',
        'QUERY_MYSQL_PASSWORD',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'RAZORPAY_KEY_ID',
        'RAZORPAY_KEY_SECRET',
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    return missing_vars

def run_production_checks():
    """Run Django production checks."""
    print("🔍 Running Django production checks...")
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'check', '--deploy'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Django production checks passed!")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ Django production checks failed!")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running production checks: {e}")
        return False
    
    return True

def collect_static_files():
    """Collect static files for production."""
    print("📦 Collecting static files...")
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'collectstatic', '--noinput'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Static files collected successfully!")
        else:
            print("❌ Failed to collect static files!")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error collecting static files: {e}")
        return False
    
    return True

def run_migrations():
    """Run database migrations."""
    print("🗄️ Running database migrations...")
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database migrations completed!")
        else:
            print("❌ Database migrations failed!")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False
    
    return True

def test_database_connections():
    """Test database connections."""
    print("🔗 Testing database connections...")
    try:
        result = subprocess.run([
            sys.executable, 'test_query_run.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database connections successful!")
            print(result.stdout)
        else:
            print("❌ Database connection test failed!")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error testing database connections: {e}")
        return False
    
    return True

def create_superuser():
    """Create superuser account."""
    print("👤 Creating superuser account...")
    print("Please enter superuser details:")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'createsuperuser'
        ])
        
        if result.returncode == 0:
            print("✅ Superuser created successfully!")
        else:
            print("❌ Failed to create superuser!")
            return False
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return False
    
    return True

def load_sample_data():
    """Load sample data (optional)."""
    response = input("📚 Do you want to load sample data? (y/N): ").lower()
    if response != 'y':
        return True
    
    print("📚 Loading sample data...")
    commands = [
        ['python', 'manage.py', 'create_sample_tutorials'],
        ['python', 'manage.py', 'create_sample_challenges'],
        ['python', 'manage.py', 'create_schema_templates'],
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {cmd[2]} completed!")
            else:
                print(f"❌ {cmd[2]} failed!")
                print(result.stderr)
        except Exception as e:
            print(f"❌ Error running {cmd[2]}: {e}")
    
    return True

def main():
    """Main setup function."""
    print("🚀 KodeSQL Production Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ manage.py not found. Please run this script from the Django project root.")
        sys.exit(1)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded from .env file")
    except ImportError:
        print("⚠️ python-dotenv not installed. Make sure environment variables are set manually.")
    
    # Check environment variables
    missing_vars = check_environment()
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        sys.exit(1)
    
    print("✅ All required environment variables are set")
    
    # Run setup steps
    steps = [
        ("Running production checks", run_production_checks),
        ("Running database migrations", run_migrations),
        ("Testing database connections", test_database_connections),
        ("Collecting static files", collect_static_files),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    # Optional steps
    print("\n" + "=" * 50)
    print("Optional Setup Steps")
    print("=" * 50)
    
    # Create superuser
    response = input("👤 Do you want to create a superuser account? (Y/n): ").lower()
    if response != 'n':
        create_superuser()
    
    # Load sample data
    load_sample_data()
    
    print("\n" + "=" * 50)
    print("🎉 Production setup completed successfully!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Configure your web server (Apache/Nginx)")
    print("2. Set up SSL certificate")
    print("3. Configure domain DNS")
    print("4. Test the application thoroughly")
    print("5. Set up monitoring and backups")
    print("\nYour KodeSQL application is ready for production! 🚀")

if __name__ == "__main__":
    main()
