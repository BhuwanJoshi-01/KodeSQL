from django.core.management.base import BaseCommand
from challenges.models import Challenge, ChallengeTable


class Command(BaseCommand):
    help = 'Delete all existing challenges and create new comprehensive challenges with complete data and flag_id columns'

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
        
        ChallengeTable.objects.create(
            challenge=challenge3,
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
        
        ChallengeTable.objects.create(
            challenge=challenge4,
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
(6, 'Diana Lee', 'Marketing', 55000.00, '2023-01-10', 2),
(7, 'Eva Garcia', 'HR', 58000.00, '2022-12-01', 2);''',
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
        
        ChallengeTable.objects.create(
            challenge=challenge5,
            table_name='employees',
            schema_sql='''CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    flag_id INT NOT NULL
);''',
            run_dataset_sql='''INSERT INTO employees (id, name, department_id, salary, hire_date, flag_id) VALUES
(1, 'John Doe', 1, 75000.00, '2022-01-15', 1),
(2, 'Jane Smith', 2, 65000.00, '2022-03-20', 1),
(3, 'Bob Johnson', 1, 80000.00, '2021-11-10', 1);''',
            submit_dataset_sql='''INSERT INTO employees (id, name, department_id, salary, hire_date, flag_id) VALUES
(1, 'John Doe', 1, 75000.00, '2022-01-15', 2),
(2, 'Jane Smith', 2, 65000.00, '2022-03-20', 2),
(3, 'Bob Johnson', 1, 80000.00, '2021-11-10', 2),
(4, 'Alice Brown', 3, 60000.00, '2023-02-14', 2),
(5, 'Charlie Wilson', 1, 85000.00, '2020-09-05', 2);''',
            order=10
        )
        
        ChallengeTable.objects.create(
            challenge=challenge5,
            table_name='departments',
            schema_sql='''CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    budget DECIMAL(12,2) NOT NULL,
    manager_id INT,
    flag_id INT NOT NULL
);''',
            run_dataset_sql='''INSERT INTO departments (id, name, budget, manager_id, flag_id) VALUES
(1, 'Engineering', 500000.00, 3, 1),
(2, 'Marketing', 200000.00, 2, 1),
(3, 'HR', 150000.00, 4, 1);''',
            submit_dataset_sql='''INSERT INTO departments (id, name, budget, manager_id, flag_id) VALUES
(1, 'Engineering', 500000.00, 3, 2),
(2, 'Marketing', 200000.00, 2, 2),
(3, 'HR', 150000.00, 4, 2),
(4, 'Sales', 300000.00, 6, 2);''',
            order=20
        )
        challenges_created.append(challenge5)

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
