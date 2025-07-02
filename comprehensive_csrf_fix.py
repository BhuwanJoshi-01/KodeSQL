#!/usr/bin/env python
"""
Comprehensive script to fix ALL CSRF token issues in Django templates
"""
import os
import re
import glob

def fix_all_csrf_issues(content):
    """Fix all possible CSRF token syntax issues"""
    
    # Pattern 1: Standard incorrect format
    content = re.sub(
        r'<input type="hidden" name="csrfmiddlewaretoken" value="\{\%\s*csrf_token\s*\%\}">',
        r'{% csrf_token %}',
        content
    )
    
    # Pattern 2: Jinja2 style with request
    content = re.sub(
        r'<input type="hidden" name="csrfmiddlewaretoken" value="\{\{\s*csrf_token\([^}]*\)\s*\}\}">',
        r'{% csrf_token %}',
        content
    )
    
    # Pattern 3: Malformed with missing value attribute
    content = re.sub(
        r'<input type="hidden" name="csrfmiddlewaretoken" "\{\{\s*csrf_token\([^}]*\}\}">',
        r'{% csrf_token %}',
        content
    )
    
    # Pattern 4: Any other malformed CSRF input
    content = re.sub(
        r'<input[^>]*name="csrfmiddlewaretoken"[^>]*>',
        r'{% csrf_token %}',
        content
    )
    
    # Pattern 5: Fix any remaining {{ csrf_token }} references
    content = re.sub(
        r'\{\{\s*csrf_token\s*\}\}',
        r'{% csrf_token %}',
        content
    )
    
    return content

def check_csrf_issues(content):
    """Check for any remaining CSRF issues"""
    issues = []
    
    # Check for any remaining csrfmiddlewaretoken inputs
    if re.search(r'<input[^>]*name="csrfmiddlewaretoken"', content):
        issues.append("Manual CSRF input found")
    
    # Check for Jinja2 style csrf_token
    if re.search(r'\{\{\s*csrf_token\(', content):
        issues.append("Jinja2 style csrf_token() found")
    
    # Check for malformed CSRF tokens
    if re.search(r'csrf_token[^}]*\}\}"', content):
        issues.append("Malformed CSRF token found")
    
    return issues

def fix_template_file(filepath):
    """Fix a single template file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for issues first
        issues_before = check_csrf_issues(content)
        
        if not issues_before:
            print(f"✅ No CSRF issues in: {filepath}")
            return False
        
        # Fix the content
        original_content = content
        content = fix_all_csrf_issues(content)
        
        # Check if anything was fixed
        issues_after = check_csrf_issues(content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if issues_after:
                print(f"⚠️  Partially fixed: {filepath} (remaining issues: {issues_after})")
            else:
                print(f"🔧 Fixed CSRF tokens in: {filepath}")
            return True
        else:
            print(f"❌ Could not fix: {filepath} (issues: {issues_before})")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False

def main():
    """Main function to fix all templates"""
    
    print("🔧 Comprehensive CSRF token fix for Django templates...\n")
    
    # Find all template files
    template_patterns = [
        'templates/**/*.html',
    ]
    
    total_files = 0
    fixed_files = 0
    
    for pattern in template_patterns:
        files = glob.glob(pattern, recursive=True)
        for filepath in files:
            if os.path.isfile(filepath):
                total_files += 1
                if fix_template_file(filepath):
                    fixed_files += 1
    
    print(f"\n🎉 Processed {total_files} template files!")
    print(f"🔧 Fixed CSRF tokens in {fixed_files} files!")
    
    if fixed_files > 0:
        print("\n✅ All CSRF token issues should now be resolved.")
        print("\n📝 Next steps:")
        print("1. Clear your browser cache and cookies")
        print("2. Restart your Django development server")
        print("3. Try submitting the forms again")
    else:
        print("\n🤔 No CSRF token issues found in templates.")
        print("The issue might be elsewhere. Check:")
        print("1. Django settings (CSRF middleware)")
        print("2. Browser cookies")
        print("3. Form submission method")

if __name__ == '__main__':
    main()
