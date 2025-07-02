#!/usr/bin/env python
"""
Script to fix all old admin-btn classes to new btn classes
"""
import os
import re
import glob

def fix_button_classes(content):
    """Fix old admin-btn classes to new btn classes"""
    
    # Define the mapping of old classes to new classes
    class_mappings = [
        # Basic button classes
        ('class="admin-btn"', 'class="btn btn-primary"'),
        ('class="admin-btn primary"', 'class="btn btn-primary"'),
        ('class="admin-btn secondary"', 'class="btn btn-secondary"'),
        ('class="admin-btn success"', 'class="btn btn-success"'),
        ('class="admin-btn danger"', 'class="btn btn-danger"'),
        ('class="admin-btn warning"', 'class="btn btn-warning"'),
        ('class="admin-btn info"', 'class="btn btn-info"'),
        
        # With additional styling
        ('class="admin-btn secondary"', 'class="btn btn-secondary"'),
        ('class="admin-btn danger"', 'class="btn btn-danger"'),
        ('class="admin-btn warning"', 'class="btn btn-warning"'),
        ('class="admin-btn info"', 'class="btn btn-info"'),
        ('class="admin-btn success"', 'class="btn btn-success"'),
    ]
    
    # Apply the mappings
    for old_class, new_class in class_mappings:
        content = content.replace(old_class, new_class)
    
    return content

def fix_template_file(filepath):
    """Fix a single template file"""
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file needs fixing
        if 'admin-btn' not in content:
            return False
        
        # Apply fixes
        original_content = content
        content = fix_button_classes(content)
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {filepath}")
            return True
        else:
            print(f"⏭️  No changes needed: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False

def main():
    """Main function to fix all admin templates."""
    
    print("🔧 Fixing old admin-btn classes to new btn classes...\n")
    
    # Find all admin template files
    template_patterns = [
        'templates/tutorials/admin/*.html',
        'templates/challenges/admin/*.html', 
        'templates/courses/admin/*.html'
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
    print(f"📝 Fixed {fixed_files} files with button class issues.")
    print("All admin templates should now use the new button classes.")

if __name__ == '__main__':
    main()
