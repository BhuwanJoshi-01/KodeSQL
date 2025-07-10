from django.core.management.base import BaseCommand
from challenges.models import Challenge, ChallengeTable


class Command(BaseCommand):
    help = 'Delete all existing challenges and create new comprehensive challenges with complete data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all existing challenges',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL existing challenges and create new ones.\n'
                    'Use --confirm to proceed.'
                )
            )
            return

        # Delete all existing challenges
        self.stdout.write('Deleting all existing challenges...')
        deleted_count = Challenge.objects.count()
        Challenge.objects.all().delete()
        self.stdout.write(f'Deleted {deleted_count} existing challenges.')

        # Create new challenges
        self.stdout.write('Creating new comprehensive challenges...')
        
        challenges_created = []
        
        # Challenge 1: Basic SELECT (Easy)
        challenge1 = Challenge.objects.create(
            title='Basic Employee Selection',
            description='<p>Learn the fundamentals of SQL SELECT statements by retrieving all employee records from a database table.</p>',
            difficulty='easy',
            subscription_type='free',
            question='<p><strong>Task:</strong> Write a SQL query to select all employees from the employees table.</p><p><strong>Expected Output:</strong> All columns and all rows from the employees table.</p>',
            hint='<p>Use the <code>SELECT *</code> statement to retrieve all columns from a table. The basic syntax is: <code>SELECT * FROM table_name;</code></p>',
            reference_query='SELECT * FROM employees;',
            company='TechCorp',
            tags=['select', 'basic', 'fundamentals'],
            xp=10,
            supported_engines=['mysql', 'postgresql'],
            is_active=True,
            order=1
        )
        
        # Add table for Challenge 1
        ChallengeTable.objects.create(
            challenge=challenge1,
            table_name='employees',
            schema_sql='''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
            run_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date, flag_id) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
(2, 'Jane Smith', 'Marketing', 65000.00, '2022-03-20', 1),
(3, 'Bob Johnson', 'Engineering', 80000.00, '2021-11-10', 1);''',
            submit_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date, flag_id) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15', 2),
(2, 'Jane Smith', 'Marketing', 65000.00, '2022-03-20', 2),
(3, 'Bob Johnson', 'Engineering', 80000.00, '2021-11-10', 2),
(4, 'Alice Brown', 'HR', 60000.00, '2023-02-14', 2),
(5, 'Charlie Wilson', 'Engineering', 85000.00, '2020-09-05', 2);''',
            order=10
        )
        challenges_created.append(challenge1)

        # Challenge 2: WHERE Clause (Easy)
        challenge2 = Challenge.objects.create(
            title='Filter Employees by Department',
            description='<p>Learn to use the WHERE clause to filter records based on specific conditions.</p>',
            difficulty='easy',
            subscription_type='free',
            question='<p><strong>Task:</strong> Write a SQL query to find all employees who work in the "Engineering" department.</p><p><strong>Expected Output:</strong> All employees where department = "Engineering".</p>',
            hint='<p>Use the WHERE clause to filter records: <code>SELECT * FROM table_name WHERE column_name = "value";</code></p>',
            reference_query='SELECT * FROM employees WHERE department = "Engineering";',
            company='Google',
            tags=['where', 'filter', 'conditions'],
            xp=15,
            supported_engines=['mysql', 'postgresql'],
            is_active=True,
            order=2
        )
        
        # Add table for Challenge 2
        ChallengeTable.objects.create(
            challenge=challenge2,
            table_name='employees',
            schema_sql='''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
            run_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date, flag_id) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15', 1),
(2, 'Jane Smith', 'Marketing', 65000.00, '2022-03-20', 1),
(3, 'Bob Johnson', 'Engineering', 80000.00, '2021-11-10', 1),
(4, 'Alice Brown', 'HR', 60000.00, '2023-02-14', 1);''',
            submit_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date, flag_id) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15', 2),
(2, 'Jane Smith', 'Marketing', 65000.00, '2022-03-20', 2),
(3, 'Bob Johnson', 'Engineering', 80000.00, '2021-11-10', 2),
(4, 'Alice Brown', 'HR', 60000.00, '2023-02-14', 2),
(5, 'Charlie Wilson', 'Engineering', 85000.00, '2020-09-05', 2),
(6, 'Diana Lee', 'Sales', 55000.00, '2023-01-10', 2);''',
            order=10
        )
        challenges_created.append(challenge2)

        # Challenge 3: ORDER BY (Easy)
        challenge3 = Challenge.objects.create(
            title='Sort Employees by Salary',
            description='<p>Learn to sort query results using the ORDER BY clause.</p>',
            difficulty='easy',
            subscription_type='free',
            question='<p><strong>Task:</strong> Write a SQL query to select all employees and sort them by salary in descending order (highest to lowest).</p>',
            hint='<p>Use ORDER BY with DESC for descending order: <code>SELECT * FROM table_name ORDER BY column_name DESC;</code></p>',
            reference_query='SELECT * FROM employees ORDER BY salary DESC;',
            company='Microsoft',
            tags=['order_by', 'sorting', 'desc'],
            xp=15,
            supported_engines=['mysql', 'postgresql'],
            is_active=True,
            order=3
        )
        
        # Add table for Challenge 3
        ChallengeTable.objects.create(
            challenge=challenge3,
            table_name='employees',
            schema_sql='''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL
);''',
            run_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15'),
(2, 'Jane Smith', 'Marketing', 65000.00, '2022-03-20'),
(3, 'Bob Johnson', 'Engineering', 80000.00, '2021-11-10');''',
            submit_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15'),
(2, 'Jane Smith', 'Marketing', 65000.00, '2022-03-20'),
(3, 'Bob Johnson', 'Engineering', 80000.00, '2021-11-10'),
(4, 'Alice Brown', 'HR', 60000.00, '2023-02-14'),
(5, 'Charlie Wilson', 'Engineering', 85000.00, '2020-09-05');''',
            order=10
        )
        challenges_created.append(challenge3)

        # Challenge 4: COUNT and GROUP BY (Medium)
        challenge4 = Challenge.objects.create(
            title='Count Employees by Department',
            description='<p>Learn to use aggregate functions and GROUP BY to summarize data.</p>',
            difficulty='medium',
            subscription_type='free',
            question='<p><strong>Task:</strong> Write a SQL query to count the number of employees in each department.</p><p><strong>Expected Output:</strong> Department name and count of employees.</p>',
            hint='<p>Use COUNT() with GROUP BY: <code>SELECT column_name, COUNT(*) FROM table_name GROUP BY column_name;</code></p>',
            reference_query='SELECT department, COUNT(*) as employee_count FROM employees GROUP BY department;',
            company='Amazon',
            tags=['count', 'group_by', 'aggregation'],
            xp=20,
            supported_engines=['mysql', 'postgresql'],
            is_active=True,
            order=4
        )
        
        # Add table for Challenge 4
        ChallengeTable.objects.create(
            challenge=challenge4,
            table_name='employees',
            schema_sql='''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL
);''',
            run_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15'),
(2, 'Jane Smith', 'Marketing', 65000.00, '2022-03-20'),
(3, 'Bob Johnson', 'Engineering', 80000.00, '2021-11-10'),
(4, 'Alice Brown', 'HR', 60000.00, '2023-02-14');''',
            submit_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15'),
(2, 'Jane Smith', 'Marketing', 65000.00, '2022-03-20'),
(3, 'Bob Johnson', 'Engineering', 80000.00, '2021-11-10'),
(4, 'Alice Brown', 'HR', 60000.00, '2023-02-14'),
(5, 'Charlie Wilson', 'Engineering', 85000.00, '2020-09-05'),
(6, 'Diana Lee', 'Marketing', 55000.00, '2023-01-10'),
(7, 'Eva Garcia', 'HR', 58000.00, '2022-12-01');''',
            order=10
        )
        challenges_created.append(challenge4)

        # Challenge 5: INNER JOIN (Medium)
        challenge5 = Challenge.objects.create(
            title='Employee Department Details',
            description='<p>Learn to join tables to combine related data from multiple tables.</p>',
            difficulty='medium',
            subscription_type='paid',
            question='<p><strong>Task:</strong> Write a SQL query to show employee names along with their department names and department budgets.</p><p><strong>Expected Output:</strong> Employee name, department name, and department budget.</p>',
            hint='<p>Use INNER JOIN to combine tables: <code>SELECT columns FROM table1 INNER JOIN table2 ON table1.column = table2.column;</code></p>',
            reference_query='SELECT e.name, d.name as department_name, d.budget FROM employees e INNER JOIN departments d ON e.department_id = d.id;',
            company='Meta',
            tags=['join', 'inner_join', 'relationships'],
            xp=25,
            supported_engines=['mysql', 'postgresql'],
            is_active=True,
            order=5
        )
        
        # Add employees table for Challenge 5
        ChallengeTable.objects.create(
            challenge=challenge5,
            table_name='employees',
            schema_sql='''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL
);''',
            run_dataset_sql='''INSERT INTO employees (id, name, department_id, salary, hire_date) VALUES
(1, 'John Doe', 1, 75000.00, '2022-01-15'),
(2, 'Jane Smith', 2, 65000.00, '2022-03-20'),
(3, 'Bob Johnson', 1, 80000.00, '2021-11-10');''',
            submit_dataset_sql='''INSERT INTO employees (id, name, department_id, salary, hire_date) VALUES
(1, 'John Doe', 1, 75000.00, '2022-01-15'),
(2, 'Jane Smith', 2, 65000.00, '2022-03-20'),
(3, 'Bob Johnson', 1, 80000.00, '2021-11-10'),
(4, 'Alice Brown', 3, 60000.00, '2023-02-14'),
(5, 'Charlie Wilson', 1, 85000.00, '2020-09-05');''',
            order=10
        )
        
        # Add departments table for Challenge 5
        ChallengeTable.objects.create(
            challenge=challenge5,
            table_name='departments',
            schema_sql='''CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    budget DECIMAL(12,2) NOT NULL,
    manager_id INT
);''',
            run_dataset_sql='''INSERT INTO departments (id, name, budget, manager_id) VALUES
(1, 'Engineering', 500000.00, 3),
(2, 'Marketing', 200000.00, 2),
(3, 'HR', 150000.00, 4);''',
            submit_dataset_sql='''INSERT INTO departments (id, name, budget, manager_id) VALUES
(1, 'Engineering', 500000.00, 3),
(2, 'Marketing', 200000.00, 2),
(3, 'HR', 150000.00, 4),
(4, 'Sales', 300000.00, 6);''',
            order=20
        )
        challenges_created.append(challenge5)

        # Challenge 6: AVG and HAVING (Medium)
        challenge6 = Challenge.objects.create(
            title='Departments with High Average Salary',
            description='<p>Learn to use aggregate functions with HAVING clause to filter grouped results.</p>',
            difficulty='medium',
            subscription_type='paid',
            question='<p><strong>Task:</strong> Write a SQL query to find departments where the average salary is greater than 70000.</p><p><strong>Expected Output:</strong> Department and average salary for departments with avg salary > 70000.</p>',
            hint='<p>Use AVG() with GROUP BY and HAVING: <code>SELECT column, AVG(column) FROM table GROUP BY column HAVING AVG(column) > value;</code></p>',
            reference_query='SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department HAVING AVG(salary) > 70000;',
            company='Apple',
            tags=['avg', 'having', 'aggregation', 'group_by'],
            xp=25,
            supported_engines=['mysql', 'postgresql'],
            is_active=True,
            order=6
        )

        # Add table for Challenge 6
        ChallengeTable.objects.create(
            challenge=challenge6,
            table_name='employees',
            schema_sql='''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL
);''',
            run_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15'),
(2, 'Jane Smith', 'Marketing', 65000.00, '2022-03-20'),
(3, 'Bob Johnson', 'Engineering', 80000.00, '2021-11-10'),
(4, 'Alice Brown', 'HR', 60000.00, '2023-02-14');''',
            submit_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15'),
(2, 'Jane Smith', 'Marketing', 65000.00, '2022-03-20'),
(3, 'Bob Johnson', 'Engineering', 80000.00, '2021-11-10'),
(4, 'Alice Brown', 'HR', 60000.00, '2023-02-14'),
(5, 'Charlie Wilson', 'Engineering', 85000.00, '2020-09-05'),
(6, 'Diana Lee', 'Marketing', 55000.00, '2023-01-10'),
(7, 'Eva Garcia', 'HR', 58000.00, '2022-12-01'),
(8, 'Frank Miller', 'Sales', 90000.00, '2021-08-15'),
(9, 'Grace Chen', 'Sales', 88000.00, '2022-05-20');''',
            order=10
        )
        challenges_created.append(challenge6)

        # Challenge 7: LIKE Pattern Matching (Medium)
        challenge7 = Challenge.objects.create(
            title='Find Employees by Name Pattern',
            description='<p>Learn to use LIKE operator for pattern matching in text searches.</p>',
            difficulty='medium',
            subscription_type='free',
            question='<p><strong>Task:</strong> Write a SQL query to find all employees whose names start with "J".</p><p><strong>Expected Output:</strong> All employees with names beginning with "J".</p>',
            hint='<p>Use LIKE with wildcards: <code>SELECT * FROM table WHERE column LIKE "pattern%";</code> The % symbol matches any sequence of characters.</p>',
            reference_query='SELECT * FROM employees WHERE name LIKE "J%";',
            company='Netflix',
            tags=['like', 'pattern_matching', 'wildcards'],
            xp=20,
            supported_engines=['mysql', 'postgresql'],
            is_active=True,
            order=7
        )

        # Add table for Challenge 7
        ChallengeTable.objects.create(
            challenge=challenge7,
            table_name='employees',
            schema_sql='''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL
);''',
            run_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15'),
(2, 'Jane Smith', 'Marketing', 65000.00, '2022-03-20'),
(3, 'Bob Johnson', 'Engineering', 80000.00, '2021-11-10'),
(4, 'Alice Brown', 'HR', 60000.00, '2023-02-14');''',
            submit_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15'),
(2, 'Jane Smith', 'Marketing', 65000.00, '2022-03-20'),
(3, 'Bob Johnson', 'Engineering', 80000.00, '2021-11-10'),
(4, 'Alice Brown', 'HR', 60000.00, '2023-02-14'),
(5, 'Charlie Wilson', 'Engineering', 85000.00, '2020-09-05'),
(6, 'Diana Lee', 'Marketing', 55000.00, '2023-01-10'),
(7, 'James Rodriguez', 'Sales', 70000.00, '2022-11-08'),
(8, 'Julia Anderson', 'HR', 62000.00, '2023-03-15');''',
            order=10
        )
        challenges_created.append(challenge7)

        # Challenge 8: Subqueries (Hard)
        challenge8 = Challenge.objects.create(
            title='Employees Above Average Salary',
            description='<p>Learn to use subqueries to create complex filtering conditions.</p>',
            difficulty='hard',
            subscription_type='paid',
            question='<p><strong>Task:</strong> Write a SQL query to find all employees who earn more than the average salary of all employees.</p><p><strong>Expected Output:</strong> All employees with salary greater than the company average.</p>',
            hint='<p>Use a subquery in WHERE clause: <code>SELECT * FROM table WHERE column > (SELECT AVG(column) FROM table);</code></p>',
            reference_query='SELECT * FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);',
            company='Tesla',
            tags=['subquery', 'avg', 'advanced'],
            xp=30,
            supported_engines=['mysql', 'postgresql'],
            is_active=True,
            order=8
        )

        # Add table for Challenge 8
        ChallengeTable.objects.create(
            challenge=challenge8,
            table_name='employees',
            schema_sql='''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL
);''',
            run_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15'),
(2, 'Jane Smith', 'Marketing', 65000.00, '2022-03-20'),
(3, 'Bob Johnson', 'Engineering', 80000.00, '2021-11-10'),
(4, 'Alice Brown', 'HR', 60000.00, '2023-02-14'),
(5, 'Charlie Wilson', 'Engineering', 85000.00, '2020-09-05');''',
            submit_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15'),
(2, 'Jane Smith', 'Marketing', 65000.00, '2022-03-20'),
(3, 'Bob Johnson', 'Engineering', 80000.00, '2021-11-10'),
(4, 'Alice Brown', 'HR', 60000.00, '2023-02-14'),
(5, 'Charlie Wilson', 'Engineering', 85000.00, '2020-09-05'),
(6, 'Diana Lee', 'Marketing', 55000.00, '2023-01-10'),
(7, 'Eva Garcia', 'HR', 58000.00, '2022-12-01'),
(8, 'Frank Miller', 'Sales', 90000.00, '2021-08-15'),
(9, 'Grace Chen', 'Sales', 88000.00, '2022-05-20'),
(10, 'Henry Davis', 'Engineering', 92000.00, '2020-06-10');''',
            order=10
        )
        challenges_created.append(challenge8)

        # Challenge 9: LEFT JOIN (Hard)
        challenge9 = Challenge.objects.create(
            title='All Employees with Department Info',
            description='<p>Learn to use LEFT JOIN to include all records from the left table, even when there are no matches in the right table.</p>',
            difficulty='hard',
            subscription_type='paid',
            question='<p><strong>Task:</strong> Write a SQL query to show all employees along with their department information. Include employees even if they don\'t have a department assigned.</p><p><strong>Expected Output:</strong> All employees with department details, showing NULL for employees without departments.</p>',
            hint='<p>Use LEFT JOIN to include all records from the left table: <code>SELECT columns FROM table1 LEFT JOIN table2 ON condition;</code></p>',
            reference_query='SELECT e.name, e.salary, d.name as department_name, d.budget FROM employees e LEFT JOIN departments d ON e.department_id = d.id;',
            company='Spotify',
            tags=['left_join', 'outer_join', 'null_handling'],
            xp=35,
            supported_engines=['mysql', 'postgresql'],
            is_active=True,
            order=9
        )

        # Add employees table for Challenge 9
        ChallengeTable.objects.create(
            challenge=challenge9,
            table_name='employees',
            schema_sql='''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL
);''',
            run_dataset_sql='''INSERT INTO employees (id, name, department_id, salary, hire_date) VALUES
(1, 'John Doe', 1, 75000.00, '2022-01-15'),
(2, 'Jane Smith', 2, 65000.00, '2022-03-20'),
(3, 'Bob Johnson', NULL, 80000.00, '2021-11-10');''',
            submit_dataset_sql='''INSERT INTO employees (id, name, department_id, salary, hire_date) VALUES
(1, 'John Doe', 1, 75000.00, '2022-01-15'),
(2, 'Jane Smith', 2, 65000.00, '2022-03-20'),
(3, 'Bob Johnson', NULL, 80000.00, '2021-11-10'),
(4, 'Alice Brown', 3, 60000.00, '2023-02-14'),
(5, 'Charlie Wilson', NULL, 85000.00, '2020-09-05');''',
            order=10
        )

        # Add departments table for Challenge 9
        ChallengeTable.objects.create(
            challenge=challenge9,
            table_name='departments',
            schema_sql='''CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    budget DECIMAL(12,2) NOT NULL,
    manager_id INT
);''',
            run_dataset_sql='''INSERT INTO departments (id, name, budget, manager_id) VALUES
(1, 'Engineering', 500000.00, 1),
(2, 'Marketing', 200000.00, 2),
(3, 'HR', 150000.00, 4);''',
            submit_dataset_sql='''INSERT INTO departments (id, name, budget, manager_id) VALUES
(1, 'Engineering', 500000.00, 1),
(2, 'Marketing', 200000.00, 2),
(3, 'HR', 150000.00, 4),
(4, 'Sales', 300000.00, NULL);''',
            order=20
        )
        challenges_created.append(challenge9)

        # Challenge 10: CASE WHEN (Hard)
        challenge10 = Challenge.objects.create(
            title='Categorize Employees by Salary Range',
            description='<p>Learn to use CASE WHEN statements to create conditional logic in SQL queries.</p>',
            difficulty='hard',
            subscription_type='paid',
            question='<p><strong>Task:</strong> Write a SQL query to categorize employees into salary ranges: "Low" (< 60000), "Medium" (60000-80000), "High" (> 80000).</p><p><strong>Expected Output:</strong> Employee name, salary, and salary category.</p>',
            hint='<p>Use CASE WHEN for conditional logic: <code>SELECT column, CASE WHEN condition THEN value WHEN condition THEN value ELSE value END FROM table;</code></p>',
            reference_query='''SELECT name, salary,
CASE
    WHEN salary < 60000 THEN 'Low'
    WHEN salary BETWEEN 60000 AND 80000 THEN 'Medium'
    ELSE 'High'
END as salary_category
FROM employees;''',
            company='Uber',
            tags=['case_when', 'conditional', 'categorization'],
            xp=35,
            supported_engines=['mysql', 'postgresql'],
            is_active=True,
            order=10
        )

        # Add table for Challenge 10
        ChallengeTable.objects.create(
            challenge=challenge10,
            table_name='employees',
            schema_sql='''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL
);''',
            run_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15'),
(2, 'Jane Smith', 'Marketing', 55000.00, '2022-03-20'),
(3, 'Bob Johnson', 'Engineering', 90000.00, '2021-11-10'),
(4, 'Alice Brown', 'HR', 65000.00, '2023-02-14');''',
            submit_dataset_sql='''INSERT INTO employees (id, name, department, salary, hire_date) VALUES
(1, 'John Doe', 'Engineering', 75000.00, '2022-01-15'),
(2, 'Jane Smith', 'Marketing', 55000.00, '2022-03-20'),
(3, 'Bob Johnson', 'Engineering', 90000.00, '2021-11-10'),
(4, 'Alice Brown', 'HR', 65000.00, '2023-02-14'),
(5, 'Charlie Wilson', 'Engineering', 85000.00, '2020-09-05'),
(6, 'Diana Lee', 'Marketing', 45000.00, '2023-01-10'),
(7, 'Eva Garcia', 'HR', 78000.00, '2022-12-01'),
(8, 'Frank Miller', 'Sales', 95000.00, '2021-08-15');''',
            order=10
        )
        challenges_created.append(challenge10)

        self.stdout.write(f'Created {len(challenges_created)} new challenges.')

        # Generate expected results for all challenges
        self.stdout.write('Generating expected results...')
        for challenge in challenges_created:
            try:
                success, message = challenge.execute_reference_query()
                if success:
                    self.stdout.write(f'✅ Generated results for: {challenge.title}')
                else:
                    self.stdout.write(f'⚠️ Failed to generate results for {challenge.title}: {message}')
            except Exception as e:
                self.stdout.write(f'❌ Error generating results for {challenge.title}: {str(e)}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(challenges_created)} comprehensive challenges!')
        )
