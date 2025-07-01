#!/usr/bin/env python3
"""
Script to restore the working template fixes by adding parentheses back to get_*_display methods.
The original fixes were working correctly.
"""

import os
import re
import glob

def fix_template_file(filepath):
    """Add parentheses back to get_*_display methods in a template file."""
    print(f"Fixing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add parentheses to get_*_display calls
    # Pattern: get_*_display -> get_*_display()
    content = re.sub(r'\.get_(\w+)_display(?!\()', r'.get_\1_display()', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed {filepath}")

def main():
    """Main function to fix all template files."""
    
    # Find all template files
    template_patterns = [
        'templates/**/*.html',
    ]
    
    files_processed = 0
    
    for pattern in template_patterns:
        files = glob.glob(pattern, recursive=True)
        for filepath in files:
            if os.path.isfile(filepath):
                fix_template_file(filepath)
                files_processed += 1
    
    print(f"\nFixed {files_processed} template files!")
    print("Templates now have parentheses for get_*_display() methods")

if __name__ == '__main__':
    main()
