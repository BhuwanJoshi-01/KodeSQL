#!/usr/bin/env python
"""
Script to fix all Django template syntax to Jinja2 syntax
"""
import os
import re
import glob

def fix_jinja2_syntax(content):
    """Convert Django template syntax to Jinja2 syntax."""
    
    # Fix date filters: |date:"format" to |date("format")
    content = re.sub(r'\|date:"([^"]*)"', r'|date("\1")', content)
    
    # Fix default filters: |default:"value" to |default("value")
    content = re.sub(r'\|default:"([^"]*)"', r'|default("\1")', content)
    
    # Fix yesno filters: |yesno:"yes,no" to custom logic
    content = re.sub(r'\|yesno:"([^"]*)"', lambda m: f' and "{m.group(1).split(",")[0]}" or "{m.group(1).split(",")[1]}"', content)
    
    # Fix truncatewords: |truncatewords:n to |truncate(n, True, "")
    content = re.sub(r'\|truncatewords:(\d+)', r'|truncate(\1, True, "")', content)
    
    # Fix truncatechars: |truncatechars:n to |truncate(n)
    content = re.sub(r'\|truncatechars:(\d+)', r'|truncate(\1)', content)
    
    # Fix pluralize filter (remove it as Jinja2 doesn't have it)
    content = re.sub(r'\|pluralize', '', content)
    
    # Fix escapejs filter
    content = re.sub(r'\|escapejs', r'|e("js")', content)
    
    # Fix linebreaks filter
    content = re.sub(r'\|linebreaks', r'|linebreaks', content)
    
    # Fix urlencode filter
    content = re.sub(r'\|urlencode', r'|urlencode', content)
    
    # Fix striptags filter
    content = re.sub(r'\|striptags', r'|striptags', content)
    
    # Fix length filter (should work as is)
    # content = re.sub(r'\|length', r'|length', content)
    
    # Fix safe filter (should work as is)
    # content = re.sub(r'\|safe', r'|safe', content)
    
    return content

def fix_template_file(filepath):
    """Fix a single template file."""
    print(f"Fixing {filepath}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        fixed_content = fix_jinja2_syntax(content)
        
        # Only write if content changed
        if fixed_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Fixed {filepath}")
            return True
        else:
            print(f"⏭️  No changes needed for {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Main function to fix all admin templates."""
    
    print("🔧 Fixing Django template syntax to Jinja2 syntax...\n")
    
    # Find all template files
    template_patterns = [
        'templates/tutorials/admin/*.html',
        'templates/challenges/admin/*.html', 
        'templates/courses/admin/*.html',
        'templates/admin_base.html'
    ]
    
    total_files = 0
    fixed_files = 0
    
    for pattern in template_patterns:
        files = glob.glob(pattern)
        for filepath in files:
            if os.path.isfile(filepath):
                if fix_template_file(filepath):
                    fixed_files += 1
                total_files += 1
    
    print(f"\n🎉 Processed {total_files} template files!")
    print(f"📝 Fixed {fixed_files} files with syntax issues.")
    print("All admin templates should now work with Jinja2.")

if __name__ == '__main__':
    main()
