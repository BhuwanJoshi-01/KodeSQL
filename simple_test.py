import re

def test_parentheses_logic():
    """Test the parentheses counting logic"""
    
    test_query = "select *, row_number() over (partition by sname order by marks) as rn from students order by sname;"
    
    # Test the logic for finding ORDER BY outside parentheses
    pattern = r'\bORDER\s+BY\b'
    matches = list(re.finditer(pattern, test_query, re.IGNORECASE))
    
    print(f"Query: {test_query}")
    print(f"Found {len(matches)} ORDER BY matches:")
    
    for i, match in enumerate(matches):
        print(f"  Match {i+1}: '{match.group()}' at position {match.start()}-{match.end()}")
        
        # Check if this match is inside parentheses
        text_before = test_query[:match.start()]
        open_parens = text_before.count('(')
        close_parens = text_before.count(')')
        
        print(f"    Text before: '{text_before}'")
        print(f"    Open parens: {open_parens}, Close parens: {close_parens}")
        
        if open_parens == close_parens:
            print(f"    ✅ This ORDER BY is OUTSIDE parentheses (valid for WHERE insertion)")
        else:
            print(f"    ❌ This ORDER BY is INSIDE parentheses (should be ignored)")

if __name__ == '__main__':
    test_parentheses_logic()
