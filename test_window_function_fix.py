#!/usr/bin/env python
"""
Test script to verify the window function fix in challenge query processing.
This script tests various SQL queries with window functions to ensure the 
WHERE flag_id clause is correctly placed.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from challenges.models import Challenge
from challenges.utils import _process_user_query

def test_window_function_queries():
    """Test various window function queries to ensure proper WHERE clause placement"""
    
    # Get a challenge with multi-table setup for testing
    try:
        challenge = Challenge.objects.get(id=173)  # Find Top N Records challenge
    except Challenge.DoesNotExist:
        print("❌ Challenge 173 not found. Please ensure the challenge exists.")
        return False
    
    test_cases = [
        {
            'name': 'Basic ROW_NUMBER with PARTITION BY and ORDER BY',
            'query': 'SELECT *, ROW_NUMBER() OVER (PARTITION BY sname ORDER BY marks) as rn FROM students;',
            'expected_pattern': 'WHERE flag_id = 1;'
        },
        {
            'name': 'RANK function with window',
            'query': 'SELECT *, RANK() OVER (PARTITION BY sname ORDER BY marks DESC) as rank FROM students;',
            'expected_pattern': 'WHERE flag_id = 1;'
        },
        {
            'name': 'Multiple window functions',
            'query': 'SELECT *, ROW_NUMBER() OVER (PARTITION BY sname ORDER BY marks) as rn, RANK() OVER (ORDER BY marks DESC) as overall_rank FROM students;',
            'expected_pattern': 'WHERE flag_id = 1;'
        },
        {
            'name': 'Window function with existing WHERE clause',
            'query': 'SELECT *, ROW_NUMBER() OVER (PARTITION BY sname ORDER BY marks) as rn FROM students WHERE marks > 70;',
            'expected_pattern': 'WHERE flag_id = 1 AND marks > 70;'
        },
        {
            'name': 'Window function with ORDER BY at query level',
            'query': 'SELECT *, ROW_NUMBER() OVER (PARTITION BY sname ORDER BY marks) as rn FROM students ORDER BY sname, marks;',
            'expected_pattern': 'WHERE flag_id = 1 ORDER BY sname, marks;'
        },
        {
            'name': 'Window function with GROUP BY',
            'query': 'SELECT sname, AVG(marks), ROW_NUMBER() OVER (ORDER BY AVG(marks) DESC) as rn FROM students GROUP BY sname;',
            'expected_pattern': 'WHERE flag_id = 1 GROUP BY sname;'
        },
        {
            'name': 'LAG function',
            'query': 'SELECT *, LAG(marks) OVER (PARTITION BY sname ORDER BY sid) as prev_marks FROM students;',
            'expected_pattern': 'WHERE flag_id = 1;'
        },
        {
            'name': 'LEAD function',
            'query': 'SELECT *, LEAD(marks) OVER (PARTITION BY sname ORDER BY sid) as next_marks FROM students;',
            'expected_pattern': 'WHERE flag_id = 1;'
        }
    ]
    
    print("🧪 Testing Window Function Query Processing Fix")
    print("=" * 60)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Query: {test_case['query']}")
        
        try:
            processed_query = _process_user_query(test_case['query'], challenge, 1)
            print(f"   Processed: {processed_query}")
            
            # Check if the expected pattern is in the processed query
            if test_case['expected_pattern'] in processed_query:
                print("   ✅ PASS - WHERE clause correctly placed")
            else:
                print(f"   ❌ FAIL - Expected pattern '{test_case['expected_pattern']}' not found")
                all_passed = False
                
            # Additional check: ensure ORDER BY inside OVER() is not affected
            if 'OVER (' in test_case['query'].upper() and 'ORDER BY' in test_case['query'].upper():
                # Check that ORDER BY inside OVER() is preserved
                over_clause_start = processed_query.upper().find('OVER (')
                if over_clause_start != -1:
                    # Find the matching closing parenthesis
                    paren_count = 0
                    over_clause_end = over_clause_start + 5  # Start after 'OVER ('
                    for j, char in enumerate(processed_query[over_clause_start + 5:], over_clause_start + 5):
                        if char == '(':
                            paren_count += 1
                        elif char == ')':
                            if paren_count == 0:
                                over_clause_end = j
                                break
                            paren_count -= 1
                    
                    over_clause = processed_query[over_clause_start:over_clause_end + 1]
                    if 'WHERE flag_id' not in over_clause:
                        print("   ✅ PASS - OVER clause not corrupted")
                    else:
                        print("   ❌ FAIL - WHERE clause incorrectly inserted in OVER clause")
                        all_passed = False
                        
        except Exception as e:
            print(f"   ❌ ERROR - Exception occurred: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests PASSED! Window function fix is working correctly.")
    else:
        print("❌ Some tests FAILED. Please review the implementation.")
    
    return all_passed

if __name__ == '__main__':
    success = test_window_function_queries()
    sys.exit(0 if success else 1)
