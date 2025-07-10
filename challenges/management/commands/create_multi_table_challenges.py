from django.core.management.base import BaseCommand
from challenges.models import Challenge, ChallengeTable


class Command(BaseCommand):
    help = 'Create 5 comprehensive multi-table SQL challenges with all fields properly filled'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            help='Delete existing challenges before creating new ones',
        )

    def handle(self, *args, **options):
        if options['delete_existing']:
            self.stdout.write('Deleting existing challenges...')
            Challenge.objects.all().delete()

        self.stdout.write('Creating 5 comprehensive multi-table SQL challenges...')

        challenges_created = []

        # Challenge 1: Basic Employee-Department Join (Easy)
        self.stdout.write('Creating Challenge 1: Basic Employee-Department Join...')
        challenge1 = Challenge.objects.create(
            title="Basic Employee-Department Join",
            description="<p>Learn the fundamentals of SQL JOIN operations by connecting employee and department data.</p><p>This challenge introduces you to INNER JOIN, one of the most important SQL concepts for working with relational databases.</p>",
            difficulty="easy",
            question="<p><strong>Task:</strong> Write a query to display all employees along with their department names.</p><p><strong>Requirements:</strong></p><ul><li>Show employee name and department name</li><li>Order results by department name, then by employee name</li><li>Use INNER JOIN to connect the tables</li></ul>",
            hint="<p><strong>Hint:</strong> Use INNER JOIN to connect employees and departments tables on department_id. The syntax is:</p><pre>SELECT columns FROM table1 t1 INNER JOIN table2 t2 ON t1.foreign_key = t2.primary_key</pre>",
            reference_query="SELECT e.name as employee_name, d.name as department_name FROM employees e INNER JOIN departments d ON e.department_id = d.id ORDER BY d.name, e.name",
            subscription_type="free",
            company="TechCorp Solutions",
            tags=["joins", "inner-join", "ordering", "basic", "beginner"],
            xp=15,
            is_active=True,
            order=10
        )

        # Add employees table for Challenge 1
        ChallengeTable.objects.create(
            challenge=challenge1,
            table_name="employees",
            schema_sql="""CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department_id INT NOT NULL,
    salary DECIMAL(10,2),
    hire_date DATE
)""",
            run_dataset_sql="""INSERT INTO employees (id, name, department_id, salary, hire_date) VALUES
(1, 'John Doe', 1, 75000.00, '2022-01-15'),
(2, 'Jane Smith', 2, 65000.00, '2022-02-20'),
(3, 'Bob Johnson', 1, 80000.00, '2021-11-10')""",
            submit_dataset_sql="""INSERT INTO employees (id, name, department_id, salary, hire_date) VALUES
(1, 'John Doe', 1, 75000.00, '2022-01-15'),
(2, 'Jane Smith', 2, 65000.00, '2022-02-20'),
(3, 'Bob Johnson', 1, 80000.00, '2021-11-10'),
(4, 'Alice Brown', 3, 55000.00, '2023-03-05'),
(5, 'Charlie Wilson', 2, 60000.00, '2023-01-12'),
(6, 'David Lee', 1, 85000.00, '2023-04-10')""",
            order=10
        )

        # Add departments table for Challenge 1
        ChallengeTable.objects.create(
            challenge=challenge1,
            table_name="departments",
            schema_sql="""CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    manager_id INT,
    budget DECIMAL(12,2)
)""",
            run_dataset_sql="""INSERT INTO departments (id, name, manager_id, budget) VALUES
(1, 'Engineering', 3, 500000.00),
(2, 'Marketing', 2, 200000.00),
(3, 'HR', 4, 150000.00)""",
            submit_dataset_sql="""INSERT INTO departments (id, name, manager_id, budget) VALUES
(1, 'Engineering', 3, 500000.00),
(2, 'Marketing', 2, 200000.00),
(3, 'HR', 4, 150000.00)""",
            order=20
        )
        challenges_created.append(challenge1)

        # Challenge 2: Customer Order Analysis (Medium)
        self.stdout.write('Creating Challenge 2: Customer Order Analysis...')
        challenge2 = Challenge.objects.create(
            title="Customer Order Analysis",
            description="<p>Dive into e-commerce analytics by analyzing customer orders and calculating revenue metrics.</p><p>This challenge teaches you how to work with multiple tables using JOINs and aggregate functions like SUM and COUNT.</p>",
            difficulty="medium",
            question="<p><strong>Task:</strong> Calculate the total revenue for each customer who has placed orders.</p><p><strong>Requirements:</strong></p><ul><li>Show customer name, email, and total revenue</li><li>Only include customers who have actually placed orders</li><li>Order results by total revenue (highest first)</li><li>Use proper JOINs and GROUP BY</li></ul>",
            hint="<p><strong>Hint:</strong> You need to join three tables: customers, orders, and order_items. Use SUM() to calculate total revenue and GROUP BY to group results by customer.</p><pre>SELECT customer_info, SUM(quantity * price) as total_revenue<br>FROM customers c<br>JOIN orders o ON ...<br>JOIN order_items oi ON ...<br>GROUP BY customer_info<br>ORDER BY total_revenue DESC</pre>",
            reference_query="SELECT c.name, c.email, SUM(oi.quantity * oi.price) as total_revenue FROM customers c INNER JOIN orders o ON c.id = o.customer_id INNER JOIN order_items oi ON o.id = oi.order_id GROUP BY c.id, c.name, c.email ORDER BY total_revenue DESC",
            subscription_type="free",
            company="ShopMart Inc",
            tags=["joins", "aggregation", "groupby", "sum", "revenue"],
            xp=30,
            is_active=True,
            order=20
        )

        # Add customers table for Challenge 2
        ChallengeTable.objects.create(
            challenge=challenge2,
            table_name="customers",
            schema_sql="""CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    registration_date DATE
)""",
            run_dataset_sql="""INSERT INTO customers (id, name, email, registration_date) VALUES
(1, 'Alice Johnson', 'alice@email.com', '2023-01-15'),
(2, 'Bob Smith', 'bob@email.com', '2023-02-20'),
(3, 'Carol Davis', 'carol@email.com', '2023-03-10')""",
            submit_dataset_sql="""INSERT INTO customers (id, name, email, registration_date) VALUES
(1, 'Alice Johnson', 'alice@email.com', '2023-01-15'),
(2, 'Bob Smith', 'bob@email.com', '2023-02-20'),
(3, 'Carol Davis', 'carol@email.com', '2023-03-10'),
(4, 'David Wilson', 'david@email.com', '2023-04-05'),
(5, 'Emma Brown', 'emma@email.com', '2023-05-12')""",
            order=10
        )

        # Add orders table
        ChallengeTable.objects.create(
            challenge=challenge2,
            table_name="orders",
            schema_sql="""CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending'
)""",
            run_dataset_sql="""INSERT INTO orders (id, customer_id, order_date, status) VALUES
(1, 1, '2023-06-01', 'completed'),
(2, 2, '2023-06-02', 'completed')""",
            submit_dataset_sql="""INSERT INTO orders (id, customer_id, order_date, status) VALUES
(1, 1, '2023-06-01', 'completed'),
(2, 2, '2023-06-02', 'completed'),
(3, 1, '2023-06-05', 'completed'),
(4, 3, '2023-06-07', 'pending')""",
            order=20
        )

        # Add order_items table
        ChallengeTable.objects.create(
            challenge=challenge2,
            table_name="order_items",
            schema_sql="""CREATE TABLE order_items (
    id INT PRIMARY KEY,
    order_id INT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL
)""",
            run_dataset_sql="""INSERT INTO order_items (id, order_id, product_name, quantity, price) VALUES
(1, 1, 'Laptop', 1, 999.99),
(2, 1, 'Mouse', 2, 25.50),
(3, 2, 'Keyboard', 1, 75.00)""",
            submit_dataset_sql="""INSERT INTO order_items (id, order_id, product_name, quantity, price) VALUES
(1, 1, 'Laptop', 1, 999.99),
(2, 1, 'Mouse', 2, 25.50),
(3, 2, 'Keyboard', 1, 75.00),
(4, 3, 'Monitor', 1, 299.99),
(5, 4, 'Headphones', 1, 150.00)""",
            order=30
        )

        # Generate expected results for all challenges
        self.stdout.write('Generating expected results...')
        for challenge in [challenge1, challenge2]:
            success, message = challenge.execute_reference_query()
            if success:
                self.stdout.write(f'✅ Generated expected results for: {challenge.title}')
            else:
                self.stdout.write(f'❌ Failed to generate results for {challenge.title}: {message}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {Challenge.objects.count()} multi-table challenges '
                f'with {ChallengeTable.objects.count()} total tables!'
            )
        )
