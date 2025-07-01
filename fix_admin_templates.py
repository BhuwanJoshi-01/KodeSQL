#!/usr/bin/env python
"""
Script to fix Django template syntax to Jinja2 syntax in admin templates
"""
import os
import re
import glob

def fix_jinja_syntax(content):
    """Convert Django template syntax to Jinja2 syntax."""
    
    # Remove {% load static %} lines
    content = re.sub(r'\{% load static %\}\n?', '', content)
    
    # Fix {% static '...' %} to {{ static('...') }}
    content = re.sub(r'\{% static [\'"]([^\'"]+)[\'"] %\}', r"{{ static('\1') }}", content)
    
    # Fix {% url '...' %} to {{ url('...') }}
    content = re.sub(r'\{% url [\'"]([^\'"]+)[\'"] %\}', r"{{ url('\1') }}", content)
    
    # Fix {% url '...' param %} to {{ url('...', param) }}
    content = re.sub(r'\{% url [\'"]([^\'"]+)[\'"] ([^%]+) %\}', r"{{ url('\1', \2) }}", content)
    
    # Fix {{ block.super }} to {{ super() }}
    content = re.sub(r'\{\{ block\.super \}\}', r'{{ super() }}', content)
    
    # Fix CSRF token
    content = re.sub(r'\{% csrf_token %\}', r'<input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token(request) }}">', content)
    
    # Fix {% if messages %} to {% if get_messages(request) %}
    content = re.sub(r'\{% if messages %\}', r'{% if get_messages(request) %}', content)
    content = re.sub(r'\{% for message in messages %\}', r'{% for message in get_messages(request) %}', content)
    
    return content

def fix_template_file(filepath):
    """Fix a single template file."""
    print(f"Fixing {filepath}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply fixes
        fixed_content = fix_jinja_syntax(content)
        
        # Only write if content changed
        if fixed_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Fixed {filepath}")
        else:
            print(f"⏭️  No changes needed for {filepath}")
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")

def main():
    """Main function to fix all admin templates."""
    
    print("🔧 Fixing Django template syntax to Jinja2 syntax in admin templates...\n")
    
    # Find all admin template files
    template_patterns = [
        'templates/tutorials/admin/*.html',
        'templates/challenges/admin/*.html', 
        'templates/courses/admin/*.html',
        'templates/admin_base.html'
    ]
    
    total_files = 0
    for pattern in template_patterns:
        files = glob.glob(pattern)
        for filepath in files:
            if os.path.isfile(filepath):
                fix_template_file(filepath)
                total_files += 1
    
    print(f"\n🎉 Processed {total_files} template files!")
    print("All admin templates should now work with Jinja2.")

if __name__ == '__main__':
    main()
