#!/usr/bin/env python3
"""
Script to revert the parentheses changes in Jinja2 templates.
Since this project uses Jinja2, methods should be called WITHOUT parentheses.
"""

import os
import re
import glob

def revert_template_file(filepath):
    """Revert parentheses in a single template file."""
    print(f"Reverting {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove parentheses from get_*_display() calls
    # Pattern: get_*_display() -> get_*_display
    content = re.sub(r'\.get_(\w+)_display\(\)', r'.get_\1_display', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Reverted {filepath}")

def main():
    """Main function to revert all template files."""
    
    # Find all template files
    template_patterns = [
        'templates/**/*.html',
    ]
    
    files_processed = 0
    
    for pattern in template_patterns:
        files = glob.glob(pattern, recursive=True)
        for filepath in files:
            if os.path.isfile(filepath):
                revert_template_file(filepath)
                files_processed += 1
    
    print(f"\nReverted {files_processed} template files!")
    print("Templates are now compatible with Jinja2 (methods without parentheses)")

if __name__ == '__main__':
    main()
