from django.core.management.base import BaseCommand
from challenges.models import Challenge
from django.db import transaction


class Command(BaseCommand):
    help = 'Delete all existing challenges and create 20 new dual-dataset challenges'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all existing challenges'
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will DELETE ALL existing challenges and create 20 new ones.\n'
                    'Use --confirm to proceed.'
                )
            )
            return

        with transaction.atomic():
            # Delete all existing challenges
            existing_count = Challenge.objects.count()
            Challenge.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {existing_count} existing challenges')
            )

            # Create 20 new challenges
            created_count = self.create_dual_dataset_challenges()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} new challenges!')
            )

    def create_dual_dataset_challenges(self):
        """Create 20 comprehensive SQL challenges with dual-dataset structure"""
        
        challenges_data = [
            # Challenge 1: Basic SELECT
            {
                'title': 'Basic Employee Selection',
                'difficulty': 'easy',
                'subscription_type': 'free',
                'description': 'Learn to select all records from a table.',
                'question': 'Write a SQL query to select all employees from the employees table.',
                'hint': 'Use SELECT * FROM table_name to select all columns and rows.',
                'company': 'TechCorp',
                'tags': ['select', 'basic'],
                'xp': 10,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2);''',
                'reference_query': 'SELECT name, department, salary, hire_date FROM employees;'
            },
            
            # Challenge 2: WHERE clause
            {
                'title': 'High Salary Employees',
                'difficulty': 'easy',
                'subscription_type': 'free',
                'description': 'Filter employees based on salary criteria.',
                'question': 'Write a SQL query to find all employees with salary greater than 70000.',
                'hint': 'Use WHERE clause with comparison operator.',
                'company': 'DataTech',
                'tags': ['where', 'comparison'],
                'xp': 15,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2);''',
                'reference_query': 'SELECT name, department, salary FROM employees WHERE salary > 70000;'
            },
            
            # Challenge 3: LIKE pattern matching
            {
                'title': 'Names Starting with Specific Letter',
                'difficulty': 'easy',
                'subscription_type': 'free',
                'description': 'Use pattern matching to filter text data.',
                'question': 'Write a SQL query to find all employees whose names start with "S".',
                'hint': 'Use WHERE clause with LIKE operator and wildcard %.',
                'company': 'StartupCo',
                'tags': ['like', 'pattern', 'text'],
                'xp': 15,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Sarah Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Steve Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Sophie Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Sam Johnson', 'Marketing', 68000.00, '2022-02-15', 2);''',
                'reference_query': "SELECT name, department, salary FROM employees WHERE name LIKE 'S%';"
            },
        ]
        
        return self._create_challenges_batch_1(challenges_data)
    
    def _create_challenges_batch_1(self, challenges_data):
        """Create first batch of challenges"""
        created_count = 0
        
        for i, challenge_data in enumerate(challenges_data, 1):
            challenge = Challenge.objects.create(**challenge_data)
            
            # Execute reference query to generate expected results
            success, message = challenge.execute_reference_query()
            if success:
                self.stdout.write(f'✅ Created challenge {i}: {challenge.title}')
            else:
                self.stdout.write(f'⚠️  Created challenge {i}: {challenge.title} (Warning: {message})')
            
            created_count += 1
        
        # Continue with more challenges
        created_count += self._create_challenges_batch_2()
        return created_count

    def _create_challenges_batch_2(self):
        """Create second batch of challenges (4-10)"""
        challenges_data = [
            # Challenge 4: ORDER BY
            {
                'title': 'Sort Employees by Salary',
                'difficulty': 'easy',
                'subscription_type': 'free',
                'description': 'Learn to sort query results.',
                'question': 'Write a SQL query to list all employees sorted by salary in descending order.',
                'hint': 'Use ORDER BY clause with DESC keyword.',
                'company': 'FinTech',
                'tags': ['order_by', 'sorting'],
                'xp': 15,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2);''',
                'reference_query': 'SELECT name, department, salary FROM employees ORDER BY salary DESC;'
            },

            # Challenge 5: COUNT aggregation
            {
                'title': 'Count Employees by Department',
                'difficulty': 'medium',
                'subscription_type': 'paid',
                'description': 'Use aggregate functions to count records.',
                'question': 'Write a SQL query to count the number of employees in each department.',
                'hint': 'Use COUNT() function with GROUP BY clause.',
                'company': 'Google',
                'tags': ['count', 'group_by', 'aggregation'],
                'xp': 25,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2),
('Ryan Brown', 'Engineering', 79000.00, '2022-01-10', 2);''',
                'reference_query': 'SELECT department, COUNT(*) as employee_count FROM employees GROUP BY department;'
            },

            # Challenge 6: AVG aggregation
            {
                'title': 'Average Salary by Department',
                'difficulty': 'medium',
                'subscription_type': 'paid',
                'description': 'Calculate average values using aggregate functions.',
                'question': 'Write a SQL query to find the average salary for each department.',
                'hint': 'Use AVG() function with GROUP BY clause.',
                'company': 'Microsoft',
                'tags': ['avg', 'group_by', 'aggregation'],
                'xp': 25,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2),
('Ryan Brown', 'Engineering', 79000.00, '2022-01-10', 2);''',
                'reference_query': 'SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department;'
            },
        ]

        created_count = 0
        for i, challenge_data in enumerate(challenges_data, 4):
            challenge = Challenge.objects.create(**challenge_data)

            # Execute reference query to generate expected results
            success, message = challenge.execute_reference_query()
            if success:
                self.stdout.write(f'✅ Created challenge {i}: {challenge.title}')
            else:
                self.stdout.write(f'⚠️  Created challenge {i}: {challenge.title} (Warning: {message})')

            created_count += 1

        # Continue with more challenges
        created_count += self._create_challenges_batch_3()
        return created_count

    def _create_challenges_batch_3(self):
        """Create third batch of challenges (7-13)"""
        challenges_data = [
            # Challenge 7: BETWEEN operator
            {
                'title': 'Salary Range Analysis',
                'difficulty': 'medium',
                'subscription_type': 'paid',
                'description': 'Filter data using range conditions.',
                'question': 'Write a SQL query to find employees with salary between 65000 and 80000.',
                'hint': 'Use WHERE clause with BETWEEN operator.',
                'company': 'Amazon',
                'tags': ['between', 'range', 'where'],
                'xp': 20,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2),
('Ryan Brown', 'Engineering', 79000.00, '2022-01-10', 2);''',
                'reference_query': 'SELECT name, department, salary FROM employees WHERE salary BETWEEN 65000 AND 80000;'
            },

            # Challenge 8: INNER JOIN
            {
                'title': 'Employee Department Details',
                'difficulty': 'medium',
                'subscription_type': 'paid',
                'description': 'Join tables to combine related data.',
                'question': 'Write a SQL query to show employee names with their department details.',
                'hint': 'Use INNER JOIN to combine employees and departments tables.',
                'company': 'Meta',
                'tags': ['join', 'inner_join', 'relationships'],
                'xp': 30,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);

CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department_id, salary, hire_date, flag_id) VALUES
('John Doe', 1, 75000.00, '2022-01-15', 1),
('Jane Smith', 2, 65000.00, '2022-02-20', 1),
('Bob Johnson', 1, 80000.00, '2021-12-10', 1),
('Alice Brown', 3, 60000.00, '2022-03-05', 1);

INSERT INTO departments (name, location, flag_id) VALUES
('Engineering', 'Building A', 1),
('Marketing', 'Building B', 1),
('HR', 'Building C', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department_id, salary, hire_date, flag_id) VALUES
('Mike Wilson', 1, 78000.00, '2022-01-20', 2),
('Sarah Davis', 2, 67000.00, '2022-02-25', 2),
('Tom Anderson', 1, 82000.00, '2021-11-15', 2),
('Lisa Garcia', 3, 62000.00, '2022-03-10', 2),
('David Miller', 4, 72000.00, '2022-01-30', 2);

INSERT INTO departments (name, location, flag_id) VALUES
('Engineering', 'Building A', 2),
('Marketing', 'Building B', 2),
('HR', 'Building C', 2),
('Sales', 'Building D', 2);''',
                'reference_query': 'SELECT e.name, d.name as department_name, d.location FROM employees e INNER JOIN departments d ON e.department_id = d.id;'
            },

            # Challenge 9: MAX/MIN aggregation
            {
                'title': 'Highest and Lowest Salaries',
                'difficulty': 'medium',
                'subscription_type': 'paid',
                'description': 'Find maximum and minimum values.',
                'question': 'Write a SQL query to find the highest and lowest salary in the company.',
                'hint': 'Use MAX() and MIN() functions in the same query.',
                'company': 'Apple',
                'tags': ['max', 'min', 'aggregation'],
                'xp': 25,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2),
('Ryan Brown', 'Engineering', 79000.00, '2022-01-10', 2);''',
                'reference_query': 'SELECT MAX(salary) as highest_salary, MIN(salary) as lowest_salary FROM employees;'
            },
        ]

        created_count = 0
        for i, challenge_data in enumerate(challenges_data, 7):
            challenge = Challenge.objects.create(**challenge_data)

            # Execute reference query to generate expected results
            success, message = challenge.execute_reference_query()
            if success:
                self.stdout.write(f'✅ Created challenge {i}: {challenge.title}')
            else:
                self.stdout.write(f'⚠️  Created challenge {i}: {challenge.title} (Warning: {message})')

            created_count += 1

        # Continue with more challenges
        created_count += self._create_challenges_batch_4()
        return created_count

    def _create_challenges_batch_4(self):
        """Create fourth batch of challenges (10-20)"""
        challenges_data = [
            # Challenge 10: HAVING clause
            {
                'title': 'Departments with High Average Salary',
                'difficulty': 'hard',
                'subscription_type': 'paid',
                'description': 'Filter grouped results using HAVING clause.',
                'question': 'Write a SQL query to find departments with average salary greater than 70000.',
                'hint': 'Use GROUP BY with HAVING clause to filter aggregated results.',
                'company': 'Netflix',
                'tags': ['having', 'group_by', 'aggregation'],
                'xp': 35,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2),
('Ryan Brown', 'Engineering', 79000.00, '2022-01-10', 2),
('Sophie Clark', 'Engineering', 74000.00, '2022-02-05', 2);''',
                'reference_query': 'SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department HAVING AVG(salary) > 70000;'
            },

            # Challenge 11: DISTINCT
            {
                'title': 'Unique Departments',
                'difficulty': 'easy',
                'subscription_type': 'free',
                'description': 'Remove duplicate values from query results.',
                'question': 'Write a SQL query to list all unique departments in the company.',
                'hint': 'Use DISTINCT keyword to eliminate duplicates.',
                'company': 'Spotify',
                'tags': ['distinct', 'unique'],
                'xp': 15,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2),
('Ryan Brown', 'Engineering', 79000.00, '2022-01-10', 2);''',
                'reference_query': 'SELECT DISTINCT department FROM employees;'
            },

            # Challenge 12: LIMIT
            {
                'title': 'Top 3 Highest Paid Employees',
                'difficulty': 'medium',
                'subscription_type': 'paid',
                'description': 'Limit query results to specific number of rows.',
                'question': 'Write a SQL query to find the top 3 highest paid employees.',
                'hint': 'Use ORDER BY with LIMIT clause.',
                'company': 'Tesla',
                'tags': ['limit', 'order_by', 'top_n'],
                'xp': 25,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2),
('Ryan Brown', 'Engineering', 79000.00, '2022-01-10', 2);''',
                'reference_query': 'SELECT name, department, salary FROM employees ORDER BY salary DESC LIMIT 3;'
            },
        ]

        created_count = 0
        for i, challenge_data in enumerate(challenges_data, 10):
            challenge = Challenge.objects.create(**challenge_data)

            # Execute reference query to generate expected results
            success, message = challenge.execute_reference_query()
            if success:
                self.stdout.write(f'✅ Created challenge {i}: {challenge.title}')
            else:
                self.stdout.write(f'⚠️  Created challenge {i}: {challenge.title} (Warning: {message})')

            created_count += 1

        # Continue with final challenges
        created_count += self._create_challenges_batch_5()
        return created_count

    def _create_challenges_batch_5(self):
        """Create final batch of challenges (13-20)"""
        challenges_data = [
            # Challenge 13: NULL handling
            {
                'title': 'Employees with Missing Data',
                'difficulty': 'medium',
                'subscription_type': 'paid',
                'description': 'Handle NULL values in database queries.',
                'question': 'Write a SQL query to find employees who have NULL values in any column.',
                'hint': 'Use IS NULL operator to check for missing values.',
                'company': 'Uber',
                'tags': ['null', 'is_null', 'data_quality'],
                'xp': 25,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2),
    hire_date DATE,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', NULL, 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', NULL, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, NULL, 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', NULL, 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', NULL, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, NULL, 2),
(NULL, 'Marketing', 68000.00, '2022-02-15', 2);''',
                'reference_query': 'SELECT name, department, salary, hire_date FROM employees WHERE name IS NULL OR department IS NULL OR salary IS NULL OR hire_date IS NULL;'
            },

            # Challenge 14: Date functions
            {
                'title': 'Recent Hires Analysis',
                'difficulty': 'hard',
                'subscription_type': 'paid',
                'description': 'Work with date functions and comparisons.',
                'question': 'Write a SQL query to find employees hired in the last 6 months from 2022-06-01.',
                'hint': 'Use DATE_SUB() or INTERVAL to calculate date ranges.',
                'company': 'Airbnb',
                'tags': ['date', 'date_functions', 'interval'],
                'xp': 35,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2),
('Ryan Brown', 'Engineering', 79000.00, '2022-05-10', 2),
('Sophie Clark', 'Engineering', 74000.00, '2022-04-05', 2);''',
                'reference_query': "SELECT name, department, hire_date FROM employees WHERE hire_date >= '2022-06-01'::date - INTERVAL '6 months';"
            },

            # Challenge 15: Subqueries
            {
                'title': 'Above Average Salary Employees',
                'difficulty': 'hard',
                'subscription_type': 'paid',
                'description': 'Use subqueries to compare against calculated values.',
                'question': 'Write a SQL query to find employees whose salary is above the company average.',
                'hint': 'Use a subquery with AVG() function in WHERE clause.',
                'company': 'LinkedIn',
                'tags': ['subquery', 'avg', 'comparison'],
                'xp': 40,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2),
('Ryan Brown', 'Engineering', 79000.00, '2022-01-10', 2);''',
                'reference_query': 'SELECT name, department, salary FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);'
            },
        ]

        created_count = 0
        for i, challenge_data in enumerate(challenges_data, 13):
            challenge = Challenge.objects.create(**challenge_data)

            # Execute reference query to generate expected results
            success, message = challenge.execute_reference_query()
            if success:
                self.stdout.write(f'✅ Created challenge {i}: {challenge.title}')
            else:
                self.stdout.write(f'⚠️  Created challenge {i}: {challenge.title} (Warning: {message})')

            created_count += 1

        # Continue with final challenges
        created_count += self._create_challenges_batch_6()
        return created_count

    def _create_challenges_batch_6(self):
        """Create final batch of challenges (16-20)"""
        challenges_data = [
            # Challenge 16: CASE statements
            {
                'title': 'Salary Categories',
                'difficulty': 'hard',
                'subscription_type': 'paid',
                'description': 'Use conditional logic in SQL queries.',
                'question': 'Write a SQL query to categorize employees as "High", "Medium", or "Low" salary based on their pay.',
                'hint': 'Use CASE WHEN statements to create conditional categories.',
                'company': 'Salesforce',
                'tags': ['case', 'conditional', 'categories'],
                'xp': 35,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2);''',
                'reference_query': '''SELECT name, salary,
    CASE
        WHEN salary >= 75000 THEN 'High'
        WHEN salary >= 65000 THEN 'Medium'
        ELSE 'Low'
    END as salary_category
FROM employees;'''
            },

            # Challenge 17: String functions
            {
                'title': 'Employee Name Formatting',
                'difficulty': 'medium',
                'subscription_type': 'paid',
                'description': 'Use string functions to manipulate text data.',
                'question': 'Write a SQL query to display employee names in uppercase and their email domains.',
                'hint': 'Use UPPER() function and string manipulation functions.',
                'company': 'Slack',
                'tags': ['string_functions', 'upper', 'text_manipulation'],
                'xp': 25,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, email, department, salary, flag_id) VALUES
('John Doe', 'john.doe@company.com', 'Engineering', 75000.00, 1),
('Jane Smith', 'jane.smith@company.com', 'Marketing', 65000.00, 1),
('Bob Johnson', 'bob.johnson@company.com', 'Engineering', 80000.00, 1),
('Alice Brown', 'alice.brown@company.com', 'HR', 60000.00, 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, email, department, salary, flag_id) VALUES
('Mike Wilson', 'mike.wilson@company.com', 'Engineering', 78000.00, 2),
('Sarah Davis', 'sarah.davis@company.com', 'Marketing', 67000.00, 2),
('Tom Anderson', 'tom.anderson@company.com', 'Engineering', 82000.00, 2),
('Lisa Garcia', 'lisa.garcia@company.com', 'HR', 62000.00, 2),
('David Miller', 'david.miller@company.com', 'Sales', 72000.00, 2);''',
                'reference_query': "SELECT UPPER(name) as name_upper, SPLIT_PART(email, '@', 2) as email_domain FROM employees;"
            },

            # Challenge 18: Multiple JOINs
            {
                'title': 'Employee Project Assignments',
                'difficulty': 'extreme',
                'subscription_type': 'paid',
                'description': 'Join multiple tables to get comprehensive data.',
                'question': 'Write a SQL query to show employees with their department and current project details.',
                'hint': 'Use multiple INNER JOINs to connect employees, departments, and projects.',
                'company': 'GitHub',
                'tags': ['multiple_joins', 'complex_query', 'relationships'],
                'xp': 50,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    project_id INT NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    flag_id INT NOT NULL
);

CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    flag_id INT NOT NULL
);

CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department_id, project_id, salary, flag_id) VALUES
('John Doe', 1, 1, 75000.00, 1),
('Jane Smith', 2, 2, 65000.00, 1),
('Bob Johnson', 1, 1, 80000.00, 1),
('Alice Brown', 3, 3, 60000.00, 1);

INSERT INTO departments (name, location, flag_id) VALUES
('Engineering', 'Building A', 1),
('Marketing', 'Building B', 1),
('HR', 'Building C', 1);

INSERT INTO projects (name, status, flag_id) VALUES
('Web Platform', 'Active', 1),
('Marketing Campaign', 'Planning', 1),
('HR System', 'Active', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department_id, project_id, salary, flag_id) VALUES
('Mike Wilson', 1, 1, 78000.00, 2),
('Sarah Davis', 2, 2, 67000.00, 2),
('Tom Anderson', 1, 4, 82000.00, 2),
('Lisa Garcia', 3, 3, 62000.00, 2);

INSERT INTO departments (name, location, flag_id) VALUES
('Engineering', 'Building A', 2),
('Marketing', 'Building B', 2),
('HR', 'Building C', 2);

INSERT INTO projects (name, status, flag_id) VALUES
('Web Platform', 'Active', 2),
('Marketing Campaign', 'Planning', 2),
('HR System', 'Active', 2),
('Mobile App', 'Development', 2);''',
                'reference_query': '''SELECT e.name, d.name as department_name, p.name as project_name, p.status as project_status
FROM employees e
INNER JOIN departments d ON e.department_id = d.id
INNER JOIN projects p ON e.project_id = p.id;'''
            },
        ]

        created_count = 0
        for i, challenge_data in enumerate(challenges_data, 16):
            challenge = Challenge.objects.create(**challenge_data)

            # Execute reference query to generate expected results
            success, message = challenge.execute_reference_query()
            if success:
                self.stdout.write(f'✅ Created challenge {i}: {challenge.title}')
            else:
                self.stdout.write(f'⚠️  Created challenge {i}: {challenge.title} (Warning: {message})')

            created_count += 1

        # Final challenges
        created_count += self._create_final_challenges()
        return created_count

    def _create_final_challenges(self):
        """Create the final two challenges (19-20)"""
        challenges_data = [
            # Challenge 19: Window functions
            {
                'title': 'Employee Salary Ranking',
                'difficulty': 'extreme',
                'subscription_type': 'paid',
                'description': 'Use window functions to rank employees.',
                'question': 'Write a SQL query to rank employees by salary within each department.',
                'hint': 'Use ROW_NUMBER() or RANK() window function with PARTITION BY.',
                'company': 'Oracle',
                'tags': ['window_functions', 'rank', 'partition'],
                'xp': 50,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2),
('Ryan Brown', 'Engineering', 79000.00, '2022-01-10', 2);''',
                'reference_query': '''SELECT name, department, salary
FROM employees
ORDER BY department, salary DESC;'''
            },

            # Challenge 20: Complex aggregation with conditions
            {
                'title': 'Department Performance Analysis',
                'difficulty': 'extreme',
                'subscription_type': 'paid',
                'description': 'Perform complex analysis with multiple aggregations and conditions.',
                'question': 'Write a SQL query to show department statistics: total employees, average salary, and highest salary.',
                'hint': 'Use multiple aggregate functions (COUNT, AVG, MAX) with GROUP BY.',
                'company': 'IBM',
                'tags': ['complex_aggregation', 'multiple_functions', 'analysis'],
                'xp': 50,
                'supported_engines': ['mysql', 'postgresql'],
                'schema_sql': '''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
                'run_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20', 1),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10', 1),
('Alice Brown', 'HR', 60000.00, '2022-03-05', 1);''',
                'submit_dataset_sql': '''INSERT INTO employees (name, department, salary, hire_date, flag_id) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20', 2),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25', 2),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15', 2),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10', 2),
('David Miller', 'Sales', 72000.00, '2022-01-30', 2),
('Emma Johnson', 'Marketing', 68000.00, '2022-02-15', 2),
('Ryan Brown', 'Engineering', 79000.00, '2022-01-10', 2),
('Sophie Clark', 'Engineering', 74000.00, '2022-02-05', 2);''',
                'reference_query': '''SELECT department,
    COUNT(*) as total_employees,
    AVG(salary) as avg_salary,
    MAX(salary) as highest_salary
FROM employees
GROUP BY department;'''
            }
        ]

        created_count = 0
        for i, challenge_data in enumerate(challenges_data, 19):
            challenge = Challenge.objects.create(**challenge_data)

            # Execute reference query to generate expected results
            success, message = challenge.execute_reference_query()
            if success:
                self.stdout.write(f'✅ Created challenge {i}: {challenge.title}')
            else:
                self.stdout.write(f'⚠️  Created challenge {i}: {challenge.title} (Warning: {message})')

            created_count += 1

        return created_count
