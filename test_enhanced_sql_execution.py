#!/usr/bin/env python3
"""
Test Enhanced SQL Execution - Validates the new enhanced SQL execution functions
This script tests CTEs, multiple statements, complex queries, and other advanced SQL constructs.
"""

import os
import sys
import django
import tempfile

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from challenges.utils import execute_sql_query_enhanced
from editor.views import execute_sql_query_enhanced as execute_sqlite_enhanced


class EnhancedSQLTester:
    """
    Test class for enhanced SQL execution functionality.
    """
    
    def __init__(self):
        self.test_results = []
    
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
    
    def test_postgresql_cte(self):
        """Test Common Table Expressions (CTEs) on PostgreSQL"""
        print("\n🔍 Testing PostgreSQL CTEs...")
        
        try:
            # Test CTE query that was failing before
            cte_query = """
            WITH employee_stats AS (
                SELECT 
                    'Engineering' as department,
                    75000 as avg_salary,
                    5 as employee_count
                UNION ALL
                SELECT 
                    'Marketing' as department,
                    65000 as avg_salary,
                    3 as employee_count
            )
            SELECT * FROM employee_stats WHERE avg_salary > 60000;
            """
            
            db_config = {'database': 'test_enhanced_sql'}
            result = execute_sql_query_enhanced('postgresql', db_config, cte_query)
            
            if result['success']:
                self.log_test("PostgreSQL CTE Execution", True, f"Returned {result.get('row_count', 0)} rows")
            else:
                self.log_test("PostgreSQL CTE Execution", False, result.get('error', 'Unknown error'))
                
        except Exception as e:
            self.log_test("PostgreSQL CTE Execution", False, f"Exception: {str(e)}")
    
    def test_mysql_cte(self):
        """Test Common Table Expressions (CTEs) on MySQL"""
        print("\n🔍 Testing MySQL CTEs...")
        
        try:
            # Test CTE query that was failing before
            cte_query = """
            WITH employee_stats AS (
                SELECT 
                    'Engineering' as department,
                    75000 as avg_salary,
                    5 as employee_count
                UNION ALL
                SELECT 
                    'Marketing' as department,
                    65000 as avg_salary,
                    3 as employee_count
            )
            SELECT * FROM employee_stats WHERE avg_salary > 60000;
            """
            
            db_config = {'database': 'test_enhanced_sql'}
            result = execute_sql_query_enhanced('mysql', db_config, cte_query)
            
            if result['success']:
                self.log_test("MySQL CTE Execution", True, f"Returned {result.get('row_count', 0)} rows")
            else:
                self.log_test("MySQL CTE Execution", False, result.get('error', 'Unknown error'))
                
        except Exception as e:
            self.log_test("MySQL CTE Execution", False, f"Exception: {str(e)}")
    
    def test_multiple_statements(self):
        """Test multiple SQL statements"""
        print("\n🔍 Testing Multiple Statements...")
        
        try:
            # Test multiple statements
            multi_query = """
            SELECT 'First Query' as message, 1 as query_number;
            SELECT 'Second Query' as message, 2 as query_number;
            SELECT 'Third Query' as message, 3 as query_number;
            """
            
            db_config = {'database': 'test_enhanced_sql'}
            result = execute_sql_query_enhanced('postgresql', db_config, multi_query)
            
            if result['success']:
                multiple_flag = result.get('multiple_statements', False)
                self.log_test("Multiple Statements", True, f"Multiple statements flag: {multiple_flag}")
            else:
                self.log_test("Multiple Statements", False, result.get('error', 'Unknown error'))
                
        except Exception as e:
            self.log_test("Multiple Statements", False, f"Exception: {str(e)}")
    
    def test_sqlite_cte(self):
        """Test CTEs with SQLite (editor functionality)"""
        print("\n🔍 Testing SQLite CTEs...")
        
        try:
            # Create a temporary SQLite database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
                db_path = tmp_db.name
            
            # Initialize with some test data
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE employees (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    department TEXT,
                    salary INTEGER
                )
            """)
            cursor.execute("""
                INSERT INTO employees (name, department, salary) VALUES
                ('John', 'Engineering', 75000),
                ('Jane', 'Marketing', 65000),
                ('Bob', 'Engineering', 80000)
            """)
            conn.commit()
            conn.close()
            
            # Test CTE query
            cte_query = """
            WITH dept_stats AS (
                SELECT department, AVG(salary) as avg_salary, COUNT(*) as emp_count
                FROM employees
                GROUP BY department
            )
            SELECT * FROM dept_stats WHERE avg_salary > 70000;
            """
            
            result = execute_sqlite_enhanced(db_path, cte_query)
            
            if result['success']:
                self.log_test("SQLite CTE Execution", True, f"Returned {result.get('row_count', 0)} rows")
            else:
                self.log_test("SQLite CTE Execution", False, result.get('error', 'Unknown error'))
            
            # Clean up
            os.unlink(db_path)
                
        except Exception as e:
            self.log_test("SQLite CTE Execution", False, f"Exception: {str(e)}")
    
    def test_complex_subqueries(self):
        """Test complex subqueries and window functions"""
        print("\n🔍 Testing Complex Subqueries...")
        
        try:
            # Test complex query with subqueries
            complex_query = """
            SELECT 
                department,
                avg_salary,
                (SELECT COUNT(*) FROM (
                    SELECT 'Engineering' as dept, 75000 as sal
                    UNION ALL
                    SELECT 'Marketing' as dept, 65000 as sal
                    UNION ALL
                    SELECT 'Sales' as dept, 70000 as sal
                ) sub WHERE sub.sal > 65000) as high_salary_count
            FROM (
                SELECT 'Engineering' as department, 75000 as avg_salary
                UNION ALL
                SELECT 'Marketing' as department, 65000 as avg_salary
            ) dept_data;
            """
            
            db_config = {'database': 'test_enhanced_sql'}
            result = execute_sql_query_enhanced('postgresql', db_config, complex_query)
            
            if result['success']:
                self.log_test("Complex Subqueries", True, f"Returned {result.get('row_count', 0)} rows")
            else:
                self.log_test("Complex Subqueries", False, result.get('error', 'Unknown error'))
                
        except Exception as e:
            self.log_test("Complex Subqueries", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all enhanced SQL execution tests"""
        print("🚀 Starting Enhanced SQL Execution Tests...")
        print("This will test CTEs, multiple statements, complex queries, and other advanced SQL constructs.")
        
        # Test PostgreSQL functionality
        self.test_postgresql_cte()
        
        # Test MySQL functionality
        self.test_mysql_cte()
        
        # Test multiple statements
        self.test_multiple_statements()
        
        # Test SQLite functionality
        self.test_sqlite_cte()
        
        # Test complex subqueries
        self.test_complex_subqueries()
        
        # Summary
        print("\n" + "="*60)
        print("ENHANCED SQL EXECUTION TEST SUMMARY")
        print("="*60)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        
        for result in self.test_results:
            status = "✅ PASSED" if result['success'] else "❌ FAILED"
            print(f"{status}: {result['test']}")
            if not result['success'] and result['details']:
                print(f"   Error: {result['details']}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Enhanced SQL execution is working correctly.")
        else:
            print("⚠️  Some tests failed. Please review the errors above.")


def main():
    """Main function to run the enhanced SQL execution tests"""
    print("📊 Enhanced SQL Execution Tester")
    print("This script will test the new enhanced SQL execution functionality.")
    
    # Create tester instance and run tests
    tester = EnhancedSQLTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
