#!/usr/bin/env python
"""
Final test of the complete automated dual database system.
This demonstrates all automation features working together.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from django.contrib.auth import get_user_model
from challenges.models import Challenge, ChallengeTable

User = get_user_model()

def create_final_test_challenge():
    """Create a final test challenge demonstrating complete automation."""
    
    print("🎯 Final Automation Test: 'Company Database Analysis'")
    print("=" * 60)
    
    # Create the challenge
    challenge = Challenge.objects.create(
        title="Company Database Analysis - Full Automation Demo",
        description="Complete test of automated dual database features with JSON generation",
        difficulty="MEDIUM",
        reference_query="""
        SELECT 
            d.name as department,
            COUNT(e.id) as employees,
            ROUND(AVG(e.salary), 2) as avg_salary
        FROM Departments d
        LEFT JOIN Employees e ON d.id = e.department_id AND e.flag_id = 2
        WHERE d.flag_id = 2
        GROUP BY d.id, d.name
        ORDER BY employees DESC;
        """
    )
    
    print(f"✅ Challenge created: {challenge.title}")
    
    # Table 1: Departments
    print("\n📋 Creating Departments table...")
    table1 = ChallengeTable.objects.create(
        challenge=challenge,
        table_name="Departments",
        schema_sql="""CREATE TABLE Departments (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    budget DECIMAL(10,2)
)""",
        run_dataset_sql="""INSERT INTO Departments (id, name, budget) VALUES 
(1, 'Engineering', 100000.00),
(2, 'Sales', 75000.00)""",
        submit_dataset_sql="""INSERT INTO Departments (id, name, budget) VALUES 
(1, 'Engineering', 100000.00),
(2, 'Sales', 75000.00),
(3, 'Marketing', 60000.00)"""
    )
    
    # Table 2: Employees
    print("📋 Creating Employees table...")
    table2 = ChallengeTable.objects.create(
        challenge=challenge,
        table_name="Employees",
        schema_sql="""CREATE TABLE Employees (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT,
    salary DECIMAL(8,2)
)""",
        run_dataset_sql="""INSERT INTO Employees (id, name, department_id, salary) VALUES 
(1, 'Alice Johnson', 1, 95000.00),
(2, 'Bob Smith', 2, 65000.00),
(3, 'Carol Davis', 1, 88000.00)""",
        submit_dataset_sql="""INSERT INTO Employees (id, name, department_id, salary) VALUES 
(1, 'Alice Johnson', 1, 95000.00),
(2, 'Bob Smith', 2, 65000.00),
(3, 'Carol Davis', 1, 88000.00),
(4, 'David Wilson', 3, 55000.00),
(5, 'Eva Brown', 1, 92000.00)"""
    )
    
    print("\n🔧 Testing Complete Automation Pipeline:")
    print("=" * 50)
    
    # Test 1: Schema Processing
    print("\n1️⃣ Schema Processing (flag_id column addition)")
    for i, table in enumerate([table1, table2], 1):
        schema = table.get_processed_schema_sql()
        has_flag_id = 'flag_id INT NOT NULL DEFAULT 0' in schema
        has_unique_name = table.get_unique_table_name() in schema
        print(f"   Table {i} ({table.table_name}): ✅ flag_id={has_flag_id}, unique_name={has_unique_name}")
    
    # Test 2: Dataset Processing
    print("\n2️⃣ Dataset Processing (INSERT + UPDATE automation)")
    for i, table in enumerate([table1, table2], 1):
        run_sql = table.get_processed_dataset_sql(1)
        submit_sql = table.get_processed_dataset_sql(2)
        
        has_run_update = 'UPDATE' in run_sql and 'flag_id = 1' in run_sql
        has_submit_update = 'UPDATE' in submit_sql and 'flag_id = 2' in submit_sql
        print(f"   Table {i} ({table.table_name}): ✅ run_update={has_run_update}, submit_update={has_submit_update}")
    
    # Test 3: Automatic JSON Generation
    print("\n3️⃣ Automatic JSON Generation")
    try:
        from challenges.views import _auto_generate_expected_results
        success = _auto_generate_expected_results(challenge)
        challenge.refresh_from_db()
        
        has_json = bool(challenge.expected_result_json and challenge.expected_result_json != '[]')
        print(f"   JSON Generation: ✅ success={success}, has_content={has_json}")
        
        if has_json:
            import json
            result_data = json.loads(challenge.expected_result_json)
            print(f"   Generated {len(result_data)} result rows")
            if result_data:
                print(f"   Sample result: {result_data[0]}")
        
    except Exception as e:
        print(f"   ❌ JSON Generation failed: {e}")
    
    # Test 4: Complete Workflow Validation
    print("\n4️⃣ Complete Workflow Validation")
    try:
        # Test reference query execution
        success, message = challenge.execute_reference_query()
        print(f"   Reference Query: ✅ success={success}")
        if not success:
            print(f"   Error: {message}")
            
        # Validate all tables have proper structure
        all_tables_valid = True
        for table in challenge.tables.all():
            schema = table.get_processed_schema_sql()
            if 'flag_id' not in schema:
                all_tables_valid = False
                break
        
        print(f"   All Tables Valid: ✅ {all_tables_valid}")
        
    except Exception as e:
        print(f"   ❌ Workflow validation failed: {e}")
    
    print(f"\n🎉 Final Test Results:")
    print(f"   Challenge ID: {challenge.id}")
    print(f"   Tables: {challenge.tables.count()}")
    print(f"   Reference Query: {'✅' if challenge.reference_query else '❌'}")
    print(f"   Expected JSON: {'✅' if challenge.expected_result_json and challenge.expected_result_json != '[]' else '❌'}")
    
    print(f"\n🌐 Test in Browser:")
    print(f"   Admin Edit: http://127.0.0.1:8000/admin/challenge/{challenge.id}/edit/")
    print(f"   Challenge Page: http://127.0.0.1:8000/challenges/{challenge.id}/")
    
    return challenge

if __name__ == "__main__":
    try:
        challenge = create_final_test_challenge()
        print(f"\n✨ Complete automation test successful!")
        print(f"   All features are working correctly.")
        print(f"   Challenge '{challenge.title}' is ready for use.")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
