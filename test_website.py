#!/usr/bin/env python
"""
Simple test script to check if the Django website is working.
"""

import requests
import sys

def test_website():
    """Test basic website functionality."""
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Test home page
        print("Testing home page...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Home page loads successfully!")
        else:
            print(f"❌ Home page failed with status {response.status_code}")
            return False
        
        # Test login page
        print("Testing login page...")
        response = requests.get(f"{base_url}/auth/login/")
        if response.status_code == 200:
            print("✅ Login page loads successfully!")
        else:
            print(f"❌ Login page failed with status {response.status_code}")
            return False
        
        # Test register page
        print("Testing register page...")
        response = requests.get(f"{base_url}/auth/register/")
        if response.status_code == 200:
            print("✅ Register page loads successfully!")
        else:
            print(f"❌ Register page failed with status {response.status_code}")
            return False
        
        # Test about page
        print("Testing about page...")
        response = requests.get(f"{base_url}/about/")
        if response.status_code == 200:
            print("✅ About page loads successfully!")
        else:
            print(f"❌ About page failed with status {response.status_code}")
            return False
        
        print("\n🎉 All basic pages are working!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure Django is running on http://127.0.0.1:8000")
        return False
    except Exception as e:
        print(f"❌ Error testing website: {e}")
        return False

if __name__ == "__main__":
    success = test_website()
    sys.exit(0 if success else 1)
