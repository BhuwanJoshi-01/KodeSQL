#!/usr/bin/env python3
"""
Script to convert Django template syntax to Jinja2 syntax in admin templates.
"""

import os
import re
import glob

def fix_jinja_syntax(content):
    """Convert Django template syntax to Jinja2 syntax."""

    # Fix CSRF token
    content = re.sub(r'\{% csrf_token %\}', r'<input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">', content)

    # Fix block.super
    content = re.sub(r'\{\{ block\.super \}\}', r'{{ super() }}', content)

    # Fix date filters
    content = re.sub(r'\|date:"([^"]*)"', lambda m: f".strftime('{convert_date_format(m.group(1))}')", content)

    # Fix pluralize filter
    content = re.sub(r'\|pluralize', '', content)  # Jinja2 doesn't have pluralize, we'll handle manually

    # Fix truncatewords filter
    content = re.sub(r'\|truncatewords:(\d+)', r'|truncate(\1, True, "")', content)

    # Fix truncatechars filter
    content = re.sub(r'\|truncatechars:(\d+)', r'|truncate(\1)', content)

    # Fix striptags filter
    content = re.sub(r'\|striptags', r'|striptags', content)

    # Fix safe filter
    content = re.sub(r'\|safe', r'|safe', content)

    # Fix default filter
    content = re.sub(r'\|default:"([^"]*)"', r'|default("\1")', content)

    # Fix length filter
    content = re.sub(r'\|length', r'|length', content)

    # Fix yesno filter
    content = re.sub(r'\|yesno:"([^"]*)"', lambda m: f" and '{m.group(1).split(',')[0]}' or '{m.group(1).split(',')[1]}'", content)

    # Fix escapejs filter
    content = re.sub(r'\|escapejs', r'|e("js")', content)

    # Fix pprint filter (custom filter, we'll use a simple replacement)
    content = re.sub(r'\|pprint', '', content)

    return content

def convert_date_format(django_format):
    """Convert Django date format to Python strftime format."""
    format_map = {
        'M': '%b',    # Month abbreviation
        'd': '%d',    # Day of month
        'Y': '%Y',    # 4-digit year
        'F': '%B',    # Full month name
        'y': '%y',    # 2-digit year
        'j': '%d',    # Day without leading zero
        'n': '%m',    # Month without leading zero
        'm': '%m',    # Month with leading zero
        'H': '%H',    # Hour 24-format
        'i': '%M',    # Minutes
        'A': '%p',    # AM/PM
        'g': '%I',    # Hour 12-format without leading zero
        's': '%S',    # Seconds
    }
    
    result = django_format
    for django_char, python_char in format_map.items():
        result = result.replace(django_char, python_char)
    
    return result

def fix_template_file(filepath):
    """Fix a single template file."""
    print(f"Fixing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply fixes
    fixed_content = fix_jinja_syntax(content)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"Fixed {filepath}")

def main():
    """Main function to fix all admin templates."""
    
    # Find all admin template files
    template_patterns = [
        'templates/tutorials/admin/*.html',
        'templates/challenges/admin/*.html', 
        'templates/schemas/admin/*.html',
        'templates/admin_base.html'
    ]
    
    for pattern in template_patterns:
        files = glob.glob(pattern)
        for filepath in files:
            if os.path.isfile(filepath):
                fix_template_file(filepath)
    
    print("All templates fixed!")

if __name__ == '__main__':
    main()
