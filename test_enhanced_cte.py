#!/usr/bin/env python3
"""
Test Enhanced CTE Execution - Validates that CTEs work with the enhanced SQL execution
This script tests the specific CTE query that was failing before the enhancement.
"""

import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from challenges.utils import execute_sql_query_enhanced


def test_cte_with_enhanced_execution():
    """Test the specific CTE query that was failing before"""
    print("🔍 Testing Enhanced CTE Execution")
    print("This tests the exact CTE query that was failing with 'MySQL Error: Unread result found'")
    
    # The CTE query that was failing before
    cte_query = """
    with cte as (
        select 'Engineering' as department, 75000 as avg_salary, 5 as employee_count
        union all
        select 'Marketing' as department, 65000 as avg_salary, 3 as employee_count
        union all
        select 'Sales' as department, 70000 as avg_salary, 4 as employee_count
    )
    select * from cte where avg_salary > 65000;
    """
    
    # Test with PostgreSQL configuration from test_query_run.py
    postgres_config = {
        'host': os.environ.get('QUERY_POSTGRES_HOST', 'localhost'),
        'port': os.environ.get('QUERY_POSTGRES_PORT', '5432'),
        'database': os.environ.get('QUERY_POSTGRES_DB_NAME', 'sqlplayground_queries_pg'),
        'user': os.environ.get('QUERY_POSTGRES_USER', 'postgres'),
        'password': os.environ.get('QUERY_POSTGRES_PASSWORD', '')
    }
    
    # Test with MySQL configuration from test_query_run.py
    mysql_config = {
        'host': os.environ.get('QUERY_MYSQL_HOST', 'localhost'),
        'port': int(os.environ.get('QUERY_MYSQL_PORT', '3306')),
        'database': os.environ.get('QUERY_MYSQL_DB_NAME', 'sqlplayground_queries_mysql'),
        'user': os.environ.get('QUERY_MYSQL_USER', 'root'),
        'password': os.environ.get('QUERY_MYSQL_PASSWORD', 'forgex99')
    }
    
    print("\n📊 Testing PostgreSQL CTE...")
    try:
        result = execute_sql_query_enhanced('postgresql', postgres_config, cte_query)
        if result['success']:
            print("✅ PostgreSQL CTE executed successfully!")
            print(f"   Returned {result.get('row_count', 0)} rows")
            print(f"   Columns: {result.get('columns', [])}")
            if result.get('results'):
                print("   Sample results:")
                for i, row in enumerate(result['results'][:2]):  # Show first 2 rows
                    print(f"     Row {i+1}: {row}")
        else:
            print(f"❌ PostgreSQL CTE failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ PostgreSQL CTE exception: {str(e)}")
    
    print("\n📊 Testing MySQL CTE...")
    try:
        result = execute_sql_query_enhanced('mysql', mysql_config, cte_query)
        if result['success']:
            print("✅ MySQL CTE executed successfully!")
            print(f"   Returned {result.get('row_count', 0)} rows")
            print(f"   Columns: {result.get('columns', [])}")
            if result.get('results'):
                print("   Sample results:")
                for i, row in enumerate(result['results'][:2]):  # Show first 2 rows
                    print(f"     Row {i+1}: {row}")
        else:
            print(f"❌ MySQL CTE failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ MySQL CTE exception: {str(e)}")


def test_multiple_statements():
    """Test multiple SQL statements"""
    print("\n🔍 Testing Multiple Statements")
    
    # Multiple statements that should work
    multi_query = """
    select 'First Query' as message, 1 as query_number;
    select 'Second Query' as message, 2 as query_number;
    select 'Final Query' as message, 3 as query_number;
    """
    
    mysql_config = {
        'host': os.environ.get('QUERY_MYSQL_HOST', 'localhost'),
        'port': int(os.environ.get('QUERY_MYSQL_PORT', '3306')),
        'database': os.environ.get('QUERY_MYSQL_DB_NAME', 'sqlplayground_queries_mysql'),
        'user': os.environ.get('QUERY_MYSQL_USER', 'root'),
        'password': os.environ.get('QUERY_MYSQL_PASSWORD', 'forgex99')
    }
    
    print("\n📊 Testing MySQL Multiple Statements...")
    try:
        result = execute_sql_query_enhanced('mysql', mysql_config, multi_query)
        if result['success']:
            print("✅ MySQL Multiple Statements executed successfully!")
            print(f"   Multiple statements flag: {result.get('multiple_statements', False)}")
            print(f"   Returned {result.get('row_count', 0)} rows from final query")
            if result.get('results'):
                print("   Final query results:")
                for i, row in enumerate(result['results']):
                    print(f"     Row {i+1}: {row}")
        else:
            print(f"❌ MySQL Multiple Statements failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ MySQL Multiple Statements exception: {str(e)}")


def test_complex_cte():
    """Test a more complex CTE with joins and aggregations"""
    print("\n🔍 Testing Complex CTE with Aggregations")
    
    complex_cte = """
    with department_stats as (
        select 'Engineering' as dept, 'John' as emp_name, 75000 as salary
        union all
        select 'Engineering' as dept, 'Jane' as emp_name, 80000 as salary
        union all
        select 'Marketing' as dept, 'Bob' as emp_name, 65000 as salary
        union all
        select 'Marketing' as dept, 'Alice' as emp_name, 70000 as salary
    ),
    dept_summary as (
        select 
            dept,
            count(*) as employee_count,
            avg(salary) as avg_salary,
            max(salary) as max_salary,
            min(salary) as min_salary
        from department_stats
        group by dept
    )
    select 
        dept as department,
        employee_count,
        round(avg_salary, 2) as average_salary,
        max_salary,
        min_salary,
        (max_salary - min_salary) as salary_range
    from dept_summary
    where avg_salary > 65000
    order by avg_salary desc;
    """
    
    mysql_config = {
        'host': os.environ.get('QUERY_MYSQL_HOST', 'localhost'),
        'port': int(os.environ.get('QUERY_MYSQL_PORT', '3306')),
        'database': os.environ.get('QUERY_MYSQL_DB_NAME', 'sqlplayground_queries_mysql'),
        'user': os.environ.get('QUERY_MYSQL_USER', 'root'),
        'password': os.environ.get('QUERY_MYSQL_PASSWORD', 'forgex99')
    }
    
    print("\n📊 Testing MySQL Complex CTE...")
    try:
        result = execute_sql_query_enhanced('mysql', mysql_config, complex_cte)
        if result['success']:
            print("✅ MySQL Complex CTE executed successfully!")
            print(f"   Returned {result.get('row_count', 0)} rows")
            print(f"   Columns: {result.get('columns', [])}")
            if result.get('results'):
                print("   Results:")
                for i, row in enumerate(result['results']):
                    print(f"     Row {i+1}: {row}")
        else:
            print(f"❌ MySQL Complex CTE failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ MySQL Complex CTE exception: {str(e)}")


def main():
    """Main function to run enhanced CTE tests"""
    print("🚀 Enhanced CTE and Complex Query Tester")
    print("This script tests the enhanced SQL execution with CTEs and complex queries.")
    print("It uses the same database configurations as test_query_run.py")
    
    # Run the tests
    test_cte_with_enhanced_execution()
    test_multiple_statements()
    test_complex_cte()
    
    print("\n" + "="*60)
    print("✅ Enhanced CTE Testing Complete!")
    print("If the tests above passed, the enhanced SQL execution is working correctly.")
    print("The Monaco editor should now be able to handle CTEs, multiple statements,")
    print("and other complex SQL constructs without 'Unread result found' errors.")
    print("="*60)


if __name__ == "__main__":
    main()
