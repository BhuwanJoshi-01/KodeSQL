#!/usr/bin/env python
"""
Test script to verify subscription plan features display correctly.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from challenges.models import ChallengeSubscriptionPlan


def test_subscription_features():
    """Test that subscription plan features are properly formatted."""
    print("🧪 Testing Subscription Plan Features Display")
    print("=" * 50)
    
    plans = ChallengeSubscriptionPlan.objects.filter(is_active=True).order_by('sort_order', 'price')
    
    if not plans.exists():
        print("❌ No active subscription plans found!")
        return False
    
    all_good = True
    
    for plan in plans:
        print(f"\n📋 Plan: {plan.name}")
        print(f"   Duration: {plan.get_duration_display()}")
        print(f"   Price: ${plan.effective_price}")
        print(f"   Features Type: {type(plan.features)}")
        print(f"   Features Count: {len(plan.features) if plan.features else 0}")
        
        if not plan.features:
            print("   ⚠️  No features defined - will use defaults")
        elif isinstance(plan.features, list):
            print("   ✅ Features are properly stored as list:")
            for i, feature in enumerate(plan.features, 1):
                if isinstance(feature, str) and not feature.startswith('['):
                    print(f"      {i}. {feature}")
                else:
                    print(f"      ❌ {i}. Invalid feature format: {feature}")
                    all_good = False
        else:
            print(f"   ❌ Features are not a list: {plan.features}")
            all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("✅ All subscription plans have properly formatted features!")
    else:
        print("❌ Some subscription plans have formatting issues!")
    
    return all_good


def test_template_rendering():
    """Test template rendering simulation."""
    print("\n🎨 Testing Template Rendering Simulation")
    print("=" * 50)
    
    plans = ChallengeSubscriptionPlan.objects.filter(is_active=True).order_by('sort_order', 'price')
    
    for plan in plans:
        print(f"\n📋 Plan: {plan.name}")
        print("   Features in template would render as:")
        
        if plan.features and len(plan.features) > 0:
            for feature in plan.features:
                if feature and feature != "[]" and feature != "":
                    print(f"      ✓ {feature}")
        else:
            print("      ✓ Access to all premium challenges")
            print("      ✓ Detailed solutions and explanations")
            print("      ✓ Progress tracking and analytics")
            if plan.duration == 'unlimited':
                print("      ✓ Lifetime access")


if __name__ == '__main__':
    success = test_subscription_features()
    test_template_rendering()
    
    if success:
        print("\n🎉 All tests passed! Subscription features are working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed! Please check the issues above.")
        sys.exit(1)
