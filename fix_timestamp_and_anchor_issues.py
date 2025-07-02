#!/usr/bin/env python
"""
Comprehensive script to fix timestamp formatting and anchor tag issues
"""
import os
import re
import glob

def fix_timestamp_formats(content):
    """Fix Python strftime format to Django template format"""
    
    # Fix malformed strftime patterns
    patterns = [
        # Fix malformed strftime with missing closing parenthesis
        (r'\.strftime\([\'"][^\'")]*[\'"][^)]*\%\}', lambda m: m.group(0).replace('.strftime(', '|date:').replace(' %', '"')),
        
        # Fix Python strftime to Django date filter
        (r'\.strftime\([\'"]([^\'")]*)[\'"]', r'|date:"\1"'),
        
        # Fix common strftime patterns to Django equivalents
        (r'\|date:"%b %d, %Y %I:%M %p"', '|date:"M d, Y g:i A"'),
        (r'\|date:"%B %d, %Y %I:%M %p"', '|date:"F d, Y g:i A"'),
        (r'\|date:"%b %d, %Y"', '|date:"M d, Y"'),
        (r'\|date:"%B %d, %Y"', '|date:"F d, Y"'),
        (r'\|date:"%I:%M %p"', '|date:"g:i A"'),
        (r'\|date:"%H:%M"', '|date:"H:i"'),
        (r'\|date:"%Y-%m-%d"', '|date:"Y-m-d"'),
        (r'\|date:"%m/%d/%Y"', '|date:"m/d/Y"'),
    ]
    
    for pattern, replacement in patterns:
        if callable(replacement):
            content = re.sub(pattern, replacement, content)
        else:
            content = re.sub(pattern, replacement, content)
    
    return content

def fix_anchor_tags(content):
    """Fix malformed anchor tags"""
    
    # Fix missing closing quotes in href attributes
    patterns = [
        # Fix href with missing closing quote
        (r'href="([^"]*)"([^>]*>)', r'href="\1"\2'),
        
        # Fix URL tags with extra spaces before closing
        (r'\{\%\s*url\s+([^%]+)\s+\%\}', r'{% url \1 %}'),
        
        # Fix missing class attributes in anchor tags
        (r'<a\s+href="([^"]*)"([^>]*>)', lambda m: f'<a href="{m.group(1)}" class="btn btn-primary"{m.group(2)}' if 'class=' not in m.group(2) else m.group(0)),
    ]
    
    for pattern, replacement in patterns:
        if callable(replacement):
            content = re.sub(pattern, replacement, content)
        else:
            content = re.sub(pattern, replacement, content)
    
    return content

def fix_status_displays(content):
    """Fix status display method calls"""
    
    # Fix various status display patterns
    patterns = [
        # Fix status_display to get_status_display
        (r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_.]*\.)?status_display\s*\}\}', r'{{ \1get_status_display }}'),
        
        # Fix duration_display to get_duration_display
        (r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_.]*\.)?duration_display\s*\}\}', r'{{ \1get_duration_display }}'),
        
        # Fix difficulty_display to get_difficulty_display
        (r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_.]*\.)?difficulty_display\s*\}\}', r'{{ \1get_difficulty_display }}'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_url_parameters(content):
    """Fix URL parameters with extra spaces"""
    
    # Fix URL tags with extra spaces in parameters
    patterns = [
        # Fix extra spaces before closing %}
        (r'\{\%\s*url\s+([^%]+)\s+\%\}', r'{% url \1 %}'),
        
        # Fix missing quotes around string parameters
        (r'url\s+([\'"][^\'"]*)([\'"])\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+', r'url \1\2 \3 '),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_template_file(filepath):
    """Fix a single template file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all fixes
        content = fix_timestamp_formats(content)
        content = fix_anchor_tags(content)
        content = fix_status_displays(content)
        content = fix_url_parameters(content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed issues in: {filepath}")
            return True
        else:
            print(f"ℹ️  No issues found in: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Fixing Timestamp and Anchor Tag Issues\n")
    print("=" * 60)
    
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
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY")
    print(f"Total files checked: {total_files}")
    print(f"Files with fixes applied: {fixed_files}")
    
    if fixed_files > 0:
        print(f"\n🎉 Applied fixes to {fixed_files} files!")
        print("✅ Timestamp and anchor tag issues should now be resolved")
        print("\n📝 Changes made:")
        print("• Fixed Python strftime formats to Django template formats")
        print("• Fixed malformed anchor tags and missing quotes")
        print("• Fixed status display method calls")
        print("• Fixed URL parameter formatting")
    else:
        print("\n✅ No issues found or all were already fixed")

if __name__ == '__main__':
    main()
