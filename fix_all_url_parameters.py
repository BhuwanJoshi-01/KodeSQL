#!/usr/bin/env python
"""
Comprehensive script to find and fix all URL parameter issues in Django templates
"""
import os
import re
import glob

def check_url_parameters(content, filepath):
    """Check for URLs that might be missing required parameters"""
    issues = []
    
    # Common patterns that usually require parameters
    url_patterns = [
        # Admin detail views that need IDs
        (r"url\s+'[^']*:admin_[^']*_detail'\s*%}", "detail views usually need ID parameters"),
        (r"url\s+'[^']*:admin_[^']*_edit'\s*%}", "edit views usually need ID parameters"),
        (r"url\s+'[^']*:admin_[^']*_delete'\s*%}", "delete views usually need ID parameters"),
        (r"url\s+'[^']*:admin_[^']*_confirm_delete'\s*%}", "confirm delete views usually need ID parameters"),
        
        # Specific problematic patterns we've seen
        (r"url\s+'challenges:admin_subscription_detail'\s*%}", "needs subscription.id"),
        (r"url\s+'challenges:admin_subscription_edit'\s*%}", "needs subscription.id"),
        (r"url\s+'challenges:admin_subscription_plan_edit'\s*%}", "needs plan.id"),
        (r"url\s+'courses:admin_subscription_plan_detail'\s*%}", "needs plan.id"),
        (r"url\s+'courses:admin_subscription_plan_edit'\s*%}", "needs plan.id"),
    ]
    
    for pattern, description in url_patterns:
        matches = re.findall(pattern, content)
        if matches:
            issues.append(f"{description}: {matches}")
    
    return issues

def fix_common_url_issues(content):
    """Fix common URL parameter issues"""
    
    # Fix subscription detail URLs
    content = re.sub(
        r"url\s+'challenges:admin_subscription_detail'\s*%}",
        "url 'challenges:admin_subscription_detail' subscription.id %}",
        content
    )
    
    # Fix subscription edit URLs
    content = re.sub(
        r"url\s+'challenges:admin_subscription_edit'\s*%}",
        "url 'challenges:admin_subscription_edit' subscription.id %}",
        content
    )
    
    # Fix subscription plan edit URLs
    content = re.sub(
        r"url\s+'challenges:admin_subscription_plan_edit'\s*%}",
        "url 'challenges:admin_subscription_plan_edit' plan.id %}",
        content
    )
    
    # Fix courses subscription plan detail URLs
    content = re.sub(
        r"url\s+'courses:admin_subscription_plan_detail'\s*%}",
        "url 'courses:admin_subscription_plan_detail' plan.id %}",
        content
    )
    
    # Fix courses subscription plan edit URLs
    content = re.sub(
        r"url\s+'courses:admin_subscription_plan_edit'\s*%}",
        "url 'courses:admin_subscription_plan_edit' plan.id %}",
        content
    )
    
    return content

def check_and_fix_template(filepath):
    """Check and fix a single template file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for issues first
        issues_before = check_url_parameters(content, filepath)
        
        if not issues_before:
            print(f"✅ No URL parameter issues in: {filepath}")
            return False
        
        print(f"⚠️  Issues found in {filepath}:")
        for issue in issues_before:
            print(f"   - {issue}")
        
        # Try to fix the content
        original_content = content
        content = fix_common_url_issues(content)
        
        # Check if anything was fixed
        issues_after = check_url_parameters(content, filepath)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if issues_after:
                print(f"🔧 Partially fixed: {filepath}")
                print(f"   Remaining issues: {issues_after}")
            else:
                print(f"✅ Fixed all issues in: {filepath}")
            return True
        else:
            print(f"❌ Could not auto-fix: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Comprehensive URL Parameter Fix\n")
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
                if check_and_fix_template(filepath):
                    fixed_files += 1
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY")
    print(f"Total files checked: {total_files}")
    print(f"Files with fixes applied: {fixed_files}")
    
    if fixed_files > 0:
        print(f"\n🎉 Applied fixes to {fixed_files} files!")
        print("✅ URL parameter issues should now be resolved")
        print("\n📝 Next steps:")
        print("1. Restart Django development server")
        print("2. Test the admin pages that were having issues")
        print("3. Check for any remaining errors in the console")
    else:
        print("\n✅ No URL parameter issues found or all were already fixed")

if __name__ == '__main__':
    main()
