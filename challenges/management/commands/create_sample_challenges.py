"""
Management command to create sample challenges.
"""

from django.core.management.base import BaseCommand
from challenges.models import Challenge


class Command(BaseCommand):
    help = 'Create sample challenges'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample challenges...')
        
        # Easy Challenges
        Challenge.objects.get_or_create(
            title="Select All Employees",
            defaults={
                'description': "Your first SQL challenge! Write a query to select all employees from the employees table.",
                'difficulty': 'easy',
                'question': "Write a SQL query to retrieve all columns and all rows from the employees table.",
                'hint': "Use SELECT * FROM table_name to select all columns and rows.",
                'expected_query': "SELECT * FROM employees;",
                'expected_result': [
                    {'id': 1, 'name': 'John Doe', 'department': 'Engineering', 'salary': 75000},
                    {'id': 2, 'name': 'Jane Smith', 'department': 'Marketing', 'salary': 65000},
                    {'id': 3, 'name': 'Bob Johnson', 'department': 'Engineering', 'salary': 80000},
                    {'id': 4, 'name': 'Alice Brown', 'department': 'HR', 'salary': 55000},
                    {'id': 5, 'name': 'Charlie Wilson', 'department': 'Marketing', 'salary': 60000}
                ],
                'order': 1
            }
        )
        
        Challenge.objects.get_or_create(
            title="High Salary Employees",
            defaults={
                'description': "Find employees with high salaries using the WHERE clause.",
                'difficulty': 'easy',
                'question': "Write a SQL query to find all employees who earn more than $60,000.",
                'hint': "Use WHERE salary > 60000 to filter employees by salary.",
                'expected_query': "SELECT * FROM employees WHERE salary > 60000;",
                'expected_result': [
                    {'id': 1, 'name': 'John Doe', 'department': 'Engineering', 'salary': 75000},
                    {'id': 2, 'name': 'Jane Smith', 'department': 'Marketing', 'salary': 65000},
                    {'id': 3, 'name': 'Bob Johnson', 'department': 'Engineering', 'salary': 80000}
                ],
                'order': 2
            }
        )
        
        Challenge.objects.get_or_create(
            title="Engineering Department",
            defaults={
                'description': "Filter employees by department using string comparison.",
                'difficulty': 'easy',
                'question': "Write a SQL query to find all employees in the Engineering department.",
                'hint': "Use WHERE department = 'Engineering' to filter by department.",
                'expected_query': "SELECT * FROM employees WHERE department = 'Engineering';",
                'expected_result': [
                    {'id': 1, 'name': 'John Doe', 'department': 'Engineering', 'salary': 75000},
                    {'id': 3, 'name': 'Bob Johnson', 'department': 'Engineering', 'salary': 80000}
                ],
                'order': 3
            }
        )
        
        # Medium Challenges
        Challenge.objects.get_or_create(
            title="Count Employees by Department",
            defaults={
                'description': "Use GROUP BY and COUNT to analyze employee distribution.",
                'difficulty': 'medium',
                'question': "Write a SQL query to count the number of employees in each department.",
                'hint': "Use GROUP BY department and COUNT(*) to count employees by department.",
                'expected_query': "SELECT department, COUNT(*) as employee_count FROM employees GROUP BY department;",
                'expected_result': [
                    {'department': 'Engineering', 'employee_count': 2},
                    {'department': 'HR', 'employee_count': 1},
                    {'department': 'Marketing', 'employee_count': 2}
                ],
                'order': 4
            }
        )
        
        Challenge.objects.get_or_create(
            title="Average Salary by Department",
            defaults={
                'description': "Calculate average salaries using aggregate functions.",
                'difficulty': 'medium',
                'question': "Write a SQL query to find the average salary for each department.",
                'hint': "Use GROUP BY department and AVG(salary) to calculate average salaries.",
                'expected_query': "SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department;",
                'expected_result': [
                    {'department': 'Engineering', 'avg_salary': 77500.0},
                    {'department': 'HR', 'avg_salary': 55000.0},
                    {'department': 'Marketing', 'avg_salary': 62500.0}
                ],
                'order': 5
            }
        )
        
        Challenge.objects.get_or_create(
            title="Top 3 Highest Paid Employees",
            defaults={
                'description': "Use ORDER BY and LIMIT to find top earners.",
                'difficulty': 'medium',
                'question': "Write a SQL query to find the top 3 highest paid employees.",
                'hint': "Use ORDER BY salary DESC and LIMIT 3 to get the top 3 highest paid employees.",
                'expected_query': "SELECT * FROM employees ORDER BY salary DESC LIMIT 3;",
                'expected_result': [
                    {'id': 3, 'name': 'Bob Johnson', 'department': 'Engineering', 'salary': 80000},
                    {'id': 1, 'name': 'John Doe', 'department': 'Engineering', 'salary': 75000},
                    {'id': 2, 'name': 'Jane Smith', 'department': 'Marketing', 'salary': 65000}
                ],
                'order': 6
            }
        )
        
        # Hard Challenges
        Challenge.objects.get_or_create(
            title="Employees Above Average Salary",
            defaults={
                'description': "Use subqueries to find employees earning above average.",
                'difficulty': 'hard',
                'question': "Write a SQL query to find all employees who earn more than the average salary.",
                'hint': "Use a subquery with AVG(salary) in the WHERE clause.",
                'expected_query': "SELECT * FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);",
                'expected_result': [
                    {'id': 1, 'name': 'John Doe', 'department': 'Engineering', 'salary': 75000},
                    {'id': 3, 'name': 'Bob Johnson', 'department': 'Engineering', 'salary': 80000}
                ],
                'order': 7
            }
        )
        
        Challenge.objects.get_or_create(
            title="Department with Highest Average Salary",
            defaults={
                'description': "Combine multiple concepts to find the best-paying department.",
                'difficulty': 'hard',
                'question': "Write a SQL query to find the department with the highest average salary.",
                'hint': "Use GROUP BY, AVG(), and ORDER BY with LIMIT to find the department with highest average salary.",
                'expected_query': "SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department ORDER BY avg_salary DESC LIMIT 1;",
                'expected_result': [
                    {'department': 'Engineering', 'avg_salary': 77500.0}
                ],
                'order': 8
            }
        )
        
        Challenge.objects.get_or_create(
            title="Salary Range Analysis",
            defaults={
                'description': "Create salary ranges and count employees in each range.",
                'difficulty': 'hard',
                'question': "Write a SQL query to categorize employees into salary ranges: 'Low' (< 60000), 'Medium' (60000-70000), 'High' (> 70000) and count employees in each category.",
                'hint': "Use CASE WHEN to create salary categories, then GROUP BY the categories.",
                'expected_query': """SELECT 
    CASE 
        WHEN salary < 60000 THEN 'Low'
        WHEN salary BETWEEN 60000 AND 70000 THEN 'Medium'
        ELSE 'High'
    END as salary_range,
    COUNT(*) as employee_count
FROM employees 
GROUP BY salary_range;""",
                'expected_result': [
                    {'salary_range': 'High', 'employee_count': 3},
                    {'salary_range': 'Low', 'employee_count': 1},
                    {'salary_range': 'Medium', 'employee_count': 1}
                ],
                'order': 9
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample challenges!')
        )
