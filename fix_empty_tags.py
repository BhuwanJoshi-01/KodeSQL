#!/usr/bin/env python
"""
Script to fix {% empty %} tags in Jinja2 templates
"""
import os
import re
import glob

def fix_empty_tags(content):
    """Fix {% empty %} tags to proper Jinja2 syntax."""
    
    # Pattern to match {% for ... %} ... {% empty %} ... {% endfor %}
    # and convert to {% if items %} {% for ... %} ... {% endfor %} {% else %} ... {% endif %}
    
    # This is a complex pattern, so we'll do it step by step
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Look for {% for ... %} pattern
        for_match = re.search(r'(\s*){% for (\w+) in (\w+) %}', line)
        if for_match:
            indent = for_match.group(1)
            item_var = for_match.group(2)
            collection_var = for_match.group(3)
            
            # Look ahead for {% empty %} tag
            empty_found = False
            for_content = []
            empty_content = []
            j = i + 1
            
            while j < len(lines):
                if '{% empty %}' in lines[j]:
                    empty_found = True
                    j += 1
                    # Collect empty content
                    while j < len(lines) and '{% endfor %}' not in lines[j]:
                        empty_content.append(lines[j])
                        j += 1
                    break
                elif '{% endfor %}' in lines[j]:
                    break
                else:
                    for_content.append(lines[j])
                    j += 1
            
            if empty_found:
                # Convert to if/else structure
                fixed_lines.append(f'{indent}' + '{% if ' + collection_var + ' %}')
                fixed_lines.append(line)  # Original for line
                fixed_lines.extend(for_content)
                fixed_lines.append(f'{indent}    ' + '{% endfor %}')
                fixed_lines.append(f'{indent}' + '{% else %}')
                fixed_lines.extend(empty_content)
                fixed_lines.append(f'{indent}' + '{% endif %}')
                i = j + 1  # Skip to after {% endfor %}
            else:
                fixed_lines.append(line)
                i += 1
        else:
            fixed_lines.append(line)
            i += 1
    
    return '\n'.join(fixed_lines)

def fix_template_file(filepath):
    """Fix a single template file."""
    print(f"Checking {filepath}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '{% empty %}' in content:
            print(f"  Found {% empty %} tag - fixing...")
            
            # Apply fixes
            fixed_content = fix_empty_tags(content)
            
            # Write the fixed content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Fixed {filepath}")
            return True
        else:
            print(f"⏭️  No empty tags found in {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Main function to fix all admin templates."""
    
    print("🔧 Fixing {% empty %} tags in admin templates...\n")
    
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
                if fix_template_file(filepath):
                    fixed_files += 1
                total_files += 1
    
    print(f"\n🎉 Processed {total_files} template files!")
    print(f"📝 Fixed {fixed_files} files with empty tag issues.")
    print("All admin templates should now work with Jinja2.")

if __name__ == '__main__':
    main()
