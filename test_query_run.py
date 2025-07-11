#!/usr/bin/env python3
"""
Test Query Runner - Demonstrates database connections and query execution
This script creates an employee table and runs sample queries to test database connectivity.
"""

import os
import sys
import django
import psycopg2
import mysql.connector
from django.db import connections, transaction
from django.conf import settings

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()


class DatabaseTester:
    """
    A class to test database connections and run sample queries.
    """
    
    def __init__(self):
        self.postgres_config = {
            'host': os.environ.get('QUERY_POSTGRES_HOST', 'localhost'),
            'port': os.environ.get('QUERY_POSTGRES_PORT', '5432'),
            'database': os.environ.get('QUERY_POSTGRES_DB_NAME', 'sqlplayground_queries_pg'),
            'user': os.environ.get('QUERY_POSTGRES_USER', 'postgres'),
            'password': os.environ.get('QUERY_POSTGRES_PASSWORD', '')
        }
        
        self.mysql_config = {
            'host': os.environ.get('QUERY_MYSQL_HOST', 'localhost'),
            'port': int(os.environ.get('QUERY_MYSQL_PORT', '3306')),
            'database': os.environ.get('QUERY_MYSQL_DB_NAME', 'sqlplayground_queries_mysql'),
            'user': os.environ.get('QUERY_MYSQL_USER', 'root'),
            'password': os.environ.get('QUERY_MYSQL_PASSWORD', 'forgex99')
        }

    def test_postgres_connection(self):
        """Test PostgreSQL connection and run sample queries"""
        print("\n" + "="*60)
        print("TESTING POSTGRESQL CONNECTION")
        print("="*60)
        
        try:
            # Connect using psycopg2 directly
            conn = psycopg2.connect(**self.postgres_config)
            cursor = conn.cursor()
            print("[OK] PostgreSQL connection successful!")

            # Create employee table
            print("\n[INFO] Creating employee table...")
           
         
            conn.commit()
            print("[OK] Employee table created successfully!")


            print("[OK] Sample data inserted successfully!")

            # Run sample queries
            print("\n[QUERY] Running sample queries...")
            
            # Query 1: Get all employees
            print("\n1. All employees:")
            n = """
            with cte as (select * from employees) 
            
            select * from cte;
            
            """
            
            
            cursor.execute(n)
            results = cursor.fetchall()
            print(results) 
     
            # for row in results:
            #     print(f"   ID: {row[0]}, Name: {row[1]}, Dept: {row[2]}, Salary: ${row[3]}")
            results = cursor.fetchall()
            for row in results:
                print(f"   {row[0]}: ${row[1]:.2f} (Count: {row[2]})")
        
        except Exception as e:
            print(f"[ERROR] PostgreSQL Error: {str(e)}")
            return False
        
        return True

    def test_mysql_connection(self):
        """Test MySQL connection and run sample queries"""
        print("\n" + "="*60)
        print("TESTING MYSQL CONNECTION")
        print("="*60)
        
        try:
            # Connect using mysql-connector-python
            conn = mysql.connector.connect(**self.mysql_config)
            cursor = conn.cursor()
            print("[OK] MySQL connection successful!")

            # Create employee table
            print("\n[INFO] Creating employee table...")
            create_table_sql = """
            DROP TABLE IF EXISTS employees;
            CREATE TABLE employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                department VARCHAR(50),
                salary DECIMAL(10,2),
                hire_date DATE,
                email VARCHAR(100) UNIQUE
            );
            """
            cursor.execute(create_table_sql)
            conn.commit()
            print("[OK] Employee table created successfully!")

            # Insert sample data
            print("\n[INFO] Inserting sample employee data...")
            insert_sql = """
            INSERT INTO employees (name, department, salary, hire_date, email) VALUES
            ('John Doe', 'Engineering', 75000.00, '2023-01-15', 'john.doe@company.com'),
            ('Jane Smith', 'Marketing', 65000.00, '2023-02-20', 'jane.smith@company.com'),
            ('Mike Johnson', 'Engineering', 80000.00, '2022-11-10', 'mike.johnson@company.com'),
            ('Sarah Wilson', 'HR', 60000.00, '2023-03-05', 'sarah.wilson@company.com'),
            ('David Brown', 'Sales', 70000.00, '2023-01-30', 'david.brown@company.com');
            """
            cursor.execute(insert_sql)
            conn.commit()
            print("[OK] Sample data inserted successfully!")

            # Run sample queries
            print("\n[QUERY] Running sample queries...")
            
            # Query 1: Get all employees
            print("\n1. All employees:")
            cursor.execute("SELECT * FROM employees ORDER BY id;")
            results = cursor.fetchall()
            for row in results:
                print(f"   ID: {row[0]}, Name: {row[1]}, Dept: {row[2]}, Salary: ${row[3]}")
            
            # Query 2: Get employees by department
            print("\n2. Engineering department employees:")
            cursor.execute("SELECT name, salary FROM employees WHERE department = 'Engineering';")
            results = cursor.fetchall()
            for row in results:
                print(f"   {row[0]} - ${row[1]}")
            
            # Query 3: Average salary by department
            print("\n3. Average salary by department:")
            cursor.execute("""
                SELECT department, AVG(salary) as avg_salary, COUNT(*) as employee_count 
                FROM employees 
                GROUP BY department 
                ORDER BY avg_salary DESC;
            """)
            results = cursor.fetchall()
            for row in results:
                print(f"   {row[0]}: ${row[1]:.2f} (Count: {row[2]})")
            
            # Query 4: Highest paid employee
            print("\n4. Highest paid employee:")
            cursor.execute("SELECT name, department, salary FROM employees ORDER BY salary DESC LIMIT 1;")
            result = cursor.fetchone()
            if result:
                print(f"   {result[0]} from {result[1]} department - ${result[2]}")
            
            cursor.close()
            conn.close()
            print("\n[OK] MySQL testing completed successfully!")

        except Exception as e:
            print(f"[ERROR] MySQL Error: {str(e)}")
            return False
        
        return True

    def test_django_orm_connection(self):
        """Test Django ORM connection using the configured databases"""
        print("\n" + "="*60)
        print("TESTING DJANGO ORM CONNECTIONS")
        print("="*60)
        
        try:
            # Test PostgreSQL connection through Django
            print("\n[CONNECT] Testing Django PostgreSQL connection...")
            pg_conn = connections['query_postgres']
            with pg_conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"[OK] PostgreSQL version: {version[0]}")

            # Test MySQL connection through Django
            print("\n[CONNECT] Testing Django MySQL connection...")
            mysql_conn = connections['query_mysql']
            with mysql_conn.cursor() as cursor:
                cursor.execute("SELECT VERSION();")
                version = cursor.fetchone()
                print(f"[OK] MySQL version: {version[0]}")

            print("\n[OK] Django ORM connections tested successfully!")
            return True
            
        except Exception as e:
            print(f"[ERROR] Django ORM Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all database tests"""
        print("Starting Database Connection Tests...")
        print("This will test PostgreSQL and MySQL connections and run sample queries.")
        
        # Test Django ORM connections first
        django_success = self.test_django_orm_connection()
        
        # Test direct PostgreSQL connection
        postgres_success = self.test_postgres_connection()
        
        # Test direct MySQL connection
        mysql_success = self.test_mysql_connection()
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Django ORM Connections: {'[OK] PASSED' if django_success else '[ERROR] FAILED'}")
        print(f"PostgreSQL Direct Connection: {'[OK] PASSED' if postgres_success else '[ERROR] FAILED'}")
        print(f"MySQL Direct Connection: {'[OK] PASSED' if mysql_success else '[ERROR] FAILED'}")
        print("\n[TIP] Tips:")
        print("   - Make sure your database servers are running")
        print("   - Check your environment variables or settings.py for correct database configs")
        print("   - Install required packages: pip install psycopg2 mysql-connector-python")


def main():
    """Main function to run the database tests"""
    print("SQL Playground Database Tester")
    print("This script will test your database connections and run sample queries.")
    
    # Create tester instance and run tests
    tester = DatabaseTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
