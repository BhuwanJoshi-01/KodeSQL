#!/usr/bin/env python
"""
Final comprehensive check for template syntax issues
"""
import os
import re
import glob

def check_template_syntax(content, filepath):
    """Check for various template syntax issues"""
    issues = []
    
    # Check for malformed URL tags
    malformed_urls = re.findall(r'\{\%\s*url\s+[^%]*\%\}\s*[^%]*\%\}', content)
    if malformed_urls:
        issues.append(f"Malformed URL tags: {malformed_urls}")
    
    # Check for method calls with parentheses
    method_calls = re.findall(r'\.get_[a-zA-Z_]+_display\(\)', content)
    if method_calls:
        issues.append(f"Method calls with parentheses: {method_calls}")
    
    # Check for malformed template expressions
    malformed_expressions = re.findall(r'\{\{[^}]*\|[^}]*\|[^}]*\}\}', content)
    if malformed_expressions:
        issues.append(f"Malformed template expressions: {malformed_expressions}")
    
    # Check for incomplete template tags
    incomplete_tags = re.findall(r'\{\{[^}]*\%[^}]*\}\}', content)
    if incomplete_tags:
        issues.append(f"Incomplete template tags: {incomplete_tags}")
    
    # Check for missing quotes in URL parameters
    missing_quotes = re.findall(r'\{\%\s*url\s+[^%]*\s+[a-zA-Z_][a-zA-Z0-9_.]*\s+\%\}', content)
    if missing_quotes:
        # Filter out valid cases
        valid_cases = []
        for match in missing_quotes:
            if 'plan.id' in match or 'course.id' in match or 'subscription.id' in match:
                continue  # These are valid variable references
            valid_cases.append(match)
        if valid_cases:
            issues.append(f"Possibly missing quotes in URL parameters: {valid_cases}")
    
    # Check for CSRF token issues
    csrf_issues = re.findall(r'<input[^>]*name="csrfmiddlewaretoken"[^>]*>', content)
    if csrf_issues:
        issues.append(f"Manual CSRF token inputs found: {csrf_issues}")
    
    # Check for Jinja2 syntax
    jinja2_syntax = []
    if re.search(r'\{\{\s*csrf_token\(', content):
        jinja2_syntax.append("csrf_token() function calls")
    if re.search(r'\bloop\.', content):
        jinja2_syntax.append("loop variables")
    if jinja2_syntax:
        issues.append(f"Jinja2 syntax found: {jinja2_syntax}")
    
    return issues

def check_template_file(filepath):
    """Check a single template file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = check_template_syntax(content, filepath)
        
        if issues:
            print(f"❌ Issues in {filepath}:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print(f"✅ No issues in {filepath}")
            return True
            
    except Exception as e:
        print(f"❌ Error checking {filepath}: {e}")
        return False

def main():
    """Main function"""
    print("🔍 Final Template Syntax Check\n")
    print("=" * 60)
    
    # Find all template files
    template_patterns = [
        'templates/**/*.html',
    ]
    
    total_files = 0
    clean_files = 0
    
    for pattern in template_patterns:
        files = glob.glob(pattern, recursive=True)
        for filepath in files:
            if os.path.isfile(filepath):
                total_files += 1
                if check_template_file(filepath):
                    clean_files += 1
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY")
    print(f"Total files checked: {total_files}")
    print(f"Clean files: {clean_files}")
    print(f"Files with issues: {total_files - clean_files}")
    
    if clean_files == total_files:
        print("\n🎉 All templates are clean!")
        print("✅ No syntax issues found")
        print("✅ Ready for production")
    else:
        print(f"\n⚠️  {total_files - clean_files} files need attention")
        print("Please fix the issues listed above")
    
    return clean_files == total_files

if __name__ == '__main__':
    main()
