#!/usr/bin/env python
"""
Script to convert Jinja2 template syntax to Django template syntax
"""
import os
import re

def convert_jinja_to_django(content):
    """Convert Jinja2 syntax to Django template syntax"""
    
    # Convert {{ static('...') }} to {% static '...' %}
    content = re.sub(r'\{\{\s*static\([\'"]([^\'"]+)[\'"]\)\s*\}\}', r"{% static '\1' %}", content)
    
    # Convert {{ url('...', param=value) }} to {% url '...' value %}
    content = re.sub(r'\{\{\s*url\([\'"]([^\'",]+)[\'"],\s*([^=]+)=([^)]+)\)\s*\}\}', r"{% url '\1' \3 %}", content)
    
    # Convert {{ url('...') }} to {% url '...' %}
    content = re.sub(r'\{\{\s*url\([\'"]([^\'"]+)[\'"]\)\s*\}\}', r"{% url '\1' %}", content)
    
    # Convert {{ 'selected' if condition else '' }} to {% if condition %}selected{% endif %}
    content = re.sub(r'\{\{\s*[\'"]selected[\'"]\s+if\s+([^}]+)\s+else\s+[\'"][\'"]?\s*\}\}', r"{% if \1 %}selected{% endif %}", content)
    
    # Convert {{ 'class' if condition else '' }} to {% if condition %}class{% endif %}
    content = re.sub(r'\{\{\s*[\'"]([^\'\"]+)[\'"]\s+if\s+([^}]+)\s+else\s+[\'"][\'"]?\s*\}\}', r"{% if \2 %}\1{% endif %}", content)
    
    # Convert |truncatewords(20) to |truncatewords:20
    content = re.sub(r'\|truncatewords\((\d+)\)', r'|truncatewords:\1', content)
    
    # Convert |linebreaks to |linebreaks (already correct)
    
    # Convert {% csrf_token(request) %} to {% csrf_token %}
    content = re.sub(r'csrf_token\(request\)', 'csrf_token', content)
    
    return content

def fix_template_file(filepath):
    """Fix a single template file"""
    print(f"Fixing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add {% load static %} if not present and static is used
    if "{% static" in content and "{% load static %}" not in content:
        # Insert after extends line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('{% extends'):
                lines.insert(i + 1, '{% load static %}')
                break
        content = '\n'.join(lines)
    
    # Convert Jinja2 syntax to Django
    content = convert_jinja_to_django(content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed {filepath}")

def main():
    """Main function"""
    template_files = [
        'templates/courses/admin/subscription_plans_list.html',
        'templates/courses/admin/subscription_plan_form.html',
        'templates/courses/admin/subscription_plan_detail.html',
        'templates/courses/admin/subscription_plan_confirm_delete.html',
    ]
    
    for filepath in template_files:
        if os.path.exists(filepath):
            fix_template_file(filepath)
        else:
            print(f"File not found: {filepath}")

if __name__ == '__main__':
    main()
