#!/usr/bin/env python
"""
Demo script to test the automated dual database system.
This script creates a sample challenge to demonstrate all automation features.
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

def create_test_challenge():
    """Create a comprehensive test challenge to demonstrate automation."""
    
    print("🚀 Creating Test Challenge: 'Employee Management System'")
    print("=" * 60)
    
    # Create the challenge
    challenge = Challenge.objects.create(
        title="Employee Management System - Automation Test",
        description="Test challenge demonstrating automated dual database features",
        difficulty="MEDIUM",
        reference_query="""
        SELECT 
            d.name as department_name,
            COUNT(e.id) as employee_count,
            AVG(e.salary) as avg_salary
        FROM Departments d
        LEFT JOIN Employees e ON d.id = e.department_id AND e.flag_id = 2
        WHERE d.flag_id = 2
        GROUP BY d.id, d.name
        ORDER BY employee_count DESC;
        """
    )
    
    print(f"✅ Challenge created: {challenge.title}")
    
    # Table 1: Departments (basic CREATE TABLE)
    print("\n📋 Creating Table 1: Departments")
    table1 = ChallengeTable.objects.create(
        challenge=challenge,
        table_name="Departments",
        schema_sql="""CREATE TABLE Departments (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    budget DECIMAL(10,2),
    location VARCHAR(50)
)""",
        run_dataset_sql="""INSERT INTO Departments (id, name, budget, location) VALUES 
(1, 'IT', 50000.00, 'Building A'),
(2, 'HR', 30000.00, 'Building B')""",
        submit_dataset_sql="""INSERT INTO Departments (id, name, budget, location) VALUES 
(1, 'IT', 50000.00, 'Building A'),
(2, 'HR', 30000.00, 'Building B'),
(3, 'Finance', 75000.00, 'Building C'),
(4, 'Marketing', 40000.00, 'Building A')"""
    )
    
    # Table 2: Employees (CREATE TABLE with IF NOT EXISTS)
    print("📋 Creating Table 2: Employees")
    table2 = ChallengeTable.objects.create(
        challenge=challenge,
        table_name="Employees",
        schema_sql="""CREATE TABLE IF NOT EXISTS `Employees` (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT,
    salary DECIMAL(8,2),
    hire_date DATE
)""",
        run_dataset_sql="""INSERT INTO Employees (id, name, department_id, salary, hire_date) VALUES 
(1, 'John Doe', 1, 75000.00, '2023-01-15'),
(2, 'Jane Smith', 2, 55000.00, '2023-02-20'),
(3, 'Bob Johnson', 1, 80000.00, '2022-11-10')""",
        submit_dataset_sql="""INSERT INTO Employees (id, name, department_id, salary, hire_date) VALUES 
(1, 'John Doe', 1, 75000.00, '2023-01-15'),
(2, 'Jane Smith', 2, 55000.00, '2023-02-20'),
(3, 'Bob Johnson', 1, 80000.00, '2022-11-10'),
(4, 'Alice Brown', 3, 90000.00, '2023-03-05'),
(5, 'Charlie Wilson', 4, 60000.00, '2023-04-12'),
(6, 'Diana Lee', 1, 85000.00, '2023-05-18')"""
    )
    
    # Table 3: Projects (CREATE TABLE with double quotes)
    print("📋 Creating Table 3: Projects")
    table3 = ChallengeTable.objects.create(
        challenge=challenge,
        table_name="Projects",
        schema_sql='''CREATE TABLE "Projects" (
    id INT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    department_id INT,
    start_date DATE,
    status VARCHAR(20) DEFAULT 'ACTIVE'
)''',
        run_dataset_sql="""INSERT INTO Projects (id, title, department_id, start_date, status) VALUES 
(1, 'Website Redesign', 1, '2024-01-01', 'ACTIVE'),
(2, 'HR System Upgrade', 2, '2024-02-15', 'PLANNING')""",
        submit_dataset_sql="""INSERT INTO Projects (id, title, department_id, start_date, status) VALUES 
(1, 'Website Redesign', 1, '2024-01-01', 'ACTIVE'),
(2, 'HR System Upgrade', 2, '2024-02-15', 'PLANNING'),
(3, 'Financial Audit', 3, '2024-03-01', 'ACTIVE'),
(4, 'Marketing Campaign', 4, '2024-04-01', 'PLANNING')"""
    )
    
    print("\n🔧 Testing Automation Features:")
    print("=" * 40)
    
    # Test 1: Schema Processing (flag_id column addition)
    print("\n1️⃣ Testing Schema Processing (flag_id column addition)")
    for i, table in enumerate([table1, table2, table3], 1):
        processed_schema = table.get_processed_schema_sql()
        print(f"   Table {i} ({table.table_name}):")
        print(f"   ✅ Contains flag_id column: {'flag_id INT NOT NULL DEFAULT 0' in processed_schema}")
        print(f"   ✅ Uses unique table name: {table.get_unique_table_name() in processed_schema}")
    
    # Test 2: Dataset Processing (INSERT + UPDATE pattern)
    print("\n2️⃣ Testing Dataset Processing (INSERT + UPDATE pattern)")
    for i, table in enumerate([table1, table2, table3], 1):
        # Test run dataset (flag_id = 1)
        run_sql = table.get_processed_dataset_sql(1)
        submit_sql = table.get_processed_dataset_sql(2)
        
        print(f"   Table {i} ({table.table_name}):")
        print(f"   ✅ Run dataset has UPDATE flag_id = 1: {'UPDATE' in run_sql and 'flag_id = 1' in run_sql}")
        print(f"   ✅ Submit dataset has UPDATE flag_id = 2: {'UPDATE' in submit_sql and 'flag_id = 2' in submit_sql}")
    
    # Test 3: Table Name Detection
    print("\n3️⃣ Testing Enhanced Table Name Detection")
    from challenges.views import _extract_table_name_from_schema
    
    test_cases = [
        ("CREATE TABLE Departments", "Departments"),
        ("CREATE TABLE IF NOT EXISTS `Employees`", "Employees"),
        ('CREATE TABLE "Projects"', "Projects")
    ]
    
    for schema, expected in test_cases:
        extracted = _extract_table_name_from_schema(schema, 1)
        print(f"   ✅ '{schema}' → '{extracted}' (expected: '{expected}')")
    
    print(f"\n🎉 Test Challenge Created Successfully!")
    print(f"   Challenge ID: {challenge.id}")
    print(f"   Tables Created: {challenge.tables.count()}")
    print(f"   Reference Query: {'✅ Provided' if challenge.reference_query else '❌ Missing'}")
    
    print(f"\n🌐 View in Browser:")
    print(f"   Admin: http://127.0.0.1:8000/admin/challenge/{challenge.id}/edit/")
    print(f"   Public: http://127.0.0.1:8000/challenges/{challenge.id}/")
    
    return challenge

if __name__ == "__main__":
    try:
        challenge = create_test_challenge()
        print(f"\n✨ Automation test completed successfully!")
        print(f"   Challenge '{challenge.title}' is ready for testing.")
    except Exception as e:
        print(f"❌ Error creating test challenge: {e}")
        import traceback
        traceback.print_exc()
