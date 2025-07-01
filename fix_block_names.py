#!/usr/bin/env python
"""
Script to fix block names in admin templates to use admin_content instead of content
"""
import os
import re
import glob

def fix_block_names(content):
    """Fix block names from content to admin_content."""
    
    # Fix {% block content %} to {% block admin_content %}
    content = re.sub(r'\{% block content %\}', r'{% block admin_content %}', content)
    
    return content

def fix_template_file(filepath):
    """Fix a single template file."""
    print(f"Checking {filepath}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if this file has {% block content %}
        if '{% block content %}' in content:
            print("  Found block content - fixing...")

            # Apply fixes
            fixed_content = fix_block_names(content)

            # Write the fixed content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Fixed {filepath}")
        else:
            print(f"⏭️  No content block found in {filepath}")
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")

def main():
    """Main function to fix all admin templates."""
    
    print("🔧 Fixing block names in admin templates...\n")
    
    # Find all admin template files
    template_patterns = [
        'templates/tutorials/admin/*.html',
        'templates/challenges/admin/*.html', 
        'templates/courses/admin/*.html',
    ]
    
    total_files = 0
    fixed_files = 0
    
    for pattern in template_patterns:
        files = glob.glob(pattern)
        for filepath in files:
            if os.path.isfile(filepath):
                # Read the file to check if it needs fixing
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if '{% block content %}' in content:
                    fix_template_file(filepath)
                    fixed_files += 1
                else:
                    print(f"⏭️  {filepath} - no content block to fix")
                
                total_files += 1
    
    print(f"\n🎉 Processed {total_files} template files!")
    print(f"📝 Fixed {fixed_files} files with block name issues.")
    print("All admin templates should now use the correct block names.")

if __name__ == '__main__':
    main()
