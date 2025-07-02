#!/usr/bin/env python
"""
Script to fix CSRF token issues in Django templates
"""
import os
import re
import glob

def fix_csrf_tokens(content):
    """Fix CSRF token syntax in templates"""
    
    # Replace incorrect CSRF token format with proper Django template tag
    content = re.sub(
        r'<input type="hidden" name="csrfmiddlewaretoken" value="\{\%\s*csrf_token\s*\%\}">',
        r'{% csrf_token %}',
        content
    )
    
    # Replace Jinja2 style CSRF token
    content = re.sub(
        r'<input type="hidden" name="csrfmiddlewaretoken" value="\{\{\s*csrf_token\([^}]*\)\s*\}\}">',
        r'{% csrf_token %}',
        content
    )
    
    return content

def fix_template_file(filepath):
    """Fix a single template file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        content = fix_csrf_tokens(content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed CSRF tokens in: {filepath}")
            return True
        else:
            print(f"ℹ️  No CSRF token issues in: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False

def main():
    """Main function to fix all templates"""
    
    print("🔧 Fixing CSRF token issues in Django templates...\n")
    
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
    print("\nAll CSRF token issues should now be resolved.")

if __name__ == '__main__':
    main()
