#!/usr/bin/env python
"""
Script to fix template formatting issues (date formats and status displays)
"""
import os
import re
import glob

def fix_date_formats(content):
    """Fix Python strftime format to Django template format"""
    
    # Common date format replacements
    replacements = [
        # Full date with time
        (r'date:"%B %d, %Y \\a\\t %I:%M %p"', 'date:"F d, Y \\a\\t g:i A"'),
        (r'date:"%b %d, %Y %I:%M %p"', 'date:"M d, Y g:i A"'),
        (r'date:"%B %d, %Y at %I:%M %p"', 'date:"F d, Y \\a\\t g:i A"'),
        
        # Date only
        (r'date:"%B %d, %Y"', 'date:"F d, Y"'),
        (r'date:"%b %d, %Y"', 'date:"M d, Y"'),
        
        # Time only
        (r'date:"%I:%M %p"', 'date:"g:i A"'),
        (r'date:"%H:%M"', 'date:"H:i"'),
        
        # Month/Year
        (r'date:"%b %Y"', 'date:"M Y"'),
        (r'date:"%B %Y"', 'date:"F Y"'),
    ]
    
    for old_format, new_format in replacements:
        content = re.sub(old_format, new_format, content)
    
    return content

def fix_status_displays(content):
    """Fix status display method calls"""
    
    # Fix status_display to get_status_display
    content = re.sub(
        r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_.]*\.)?status_display\s*\}\}',
        r'{{ \1get_status_display }}',
        content
    )
    
    return content

def fix_template_file(filepath):
    """Fix a single template file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        content = fix_date_formats(content)
        content = fix_status_displays(content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed formatting in: {filepath}")
            return True
        else:
            print(f"ℹ️  No formatting issues in: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Fixing Template Formatting Issues\n")
    print("=" * 50)
    
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
    
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY")
    print(f"Total files checked: {total_files}")
    print(f"Files with fixes applied: {fixed_files}")
    
    if fixed_files > 0:
        print(f"\n🎉 Applied formatting fixes to {fixed_files} files!")
        print("✅ Date formats and status displays should now work correctly")
        print("\n📝 Changes made:")
        print("• Fixed Python strftime formats to Django template formats")
        print("• Fixed status_display to get_status_display method calls")
        print("• Ensured consistent date/time formatting across all templates")
    else:
        print("\n✅ No formatting issues found or all were already fixed")

if __name__ == '__main__':
    main()
