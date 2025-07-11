#!/usr/bin/env python3
"""
Quick deployment fix script for KodeSQL on cPanel
Run this script to install missing dependencies and test configuration
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    print("🚀 KodeSQL Deployment Fix Script")
    print("=" * 50)
    
    # Install missing dependencies
    dependencies = [
        "psycopg2-binary==2.9.10",
        "PyJWT==2.8.0", 
        "pytz==2025.2",
        "cryptography>=3.1"
    ]
    
    for dep in dependencies:
        run_command(f"pip install {dep}", f"Installing {dep}")
    
    # Test Django configuration
    print("\n" + "=" * 50)
    print("Testing Django Configuration")
    print("=" * 50)
    
    if run_command("python manage.py check", "Django system check"):
        print("\n✅ Django configuration is working!")
        
        # Try to run migrations
        if run_command("python manage.py migrate --dry-run", "Testing migrations"):
            print("\n✅ Migrations are ready to run!")
            print("\nNext steps:")
            print("1. Run: python manage.py migrate")
            print("2. Run: python manage.py collectstatic --noinput")
            print("3. Run: python manage.py createsuperuser")
        else:
            print("\n⚠️ Migration issues detected. Check database configuration.")
    else:
        print("\n❌ Django configuration issues detected.")
        print("Check the error messages above and fix configuration.")

if __name__ == "__main__":
    main()
