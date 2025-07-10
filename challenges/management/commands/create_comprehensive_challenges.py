from django.core.management.base import BaseCommand
from challenges.models import Challenge, ChallengeTable


class Command(BaseCommand):
    help = 'Create 5 comprehensive multi-table SQL challenges with all fields properly filled'

    def handle(self, *args, **options):
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
            title="Customer Order Revenue Analysis",
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

        # Add orders table for Challenge 2
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
(2, 2, '2023-06-02', 'completed'),
(3, 1, '2023-06-05', 'completed')""",
            submit_dataset_sql="""INSERT INTO orders (id, customer_id, order_date, status) VALUES
(1, 1, '2023-06-01', 'completed'),
(2, 2, '2023-06-02', 'completed'),
(3, 1, '2023-06-05', 'completed'),
(4, 3, '2023-06-07', 'completed'),
(5, 4, '2023-06-10', 'completed')""",
            order=20
        )

        # Add order_items table for Challenge 2
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
(3, 2, 'Keyboard', 1, 75.00),
(4, 3, 'Monitor', 1, 299.99)""",
            submit_dataset_sql="""INSERT INTO order_items (id, order_id, product_name, quantity, price) VALUES
(1, 1, 'Laptop', 1, 999.99),
(2, 1, 'Mouse', 2, 25.50),
(3, 2, 'Keyboard', 1, 75.00),
(4, 3, 'Monitor', 1, 299.99),
(5, 4, 'Headphones', 1, 150.00),
(6, 5, 'Webcam', 2, 89.99),
(7, 5, 'Microphone', 1, 120.00)""",
            order=30
        )
        challenges_created.append(challenge2)

        # Challenge 3: Student Course Enrollment (Medium)
        self.stdout.write('Creating Challenge 3: Student Course Enrollment...')
        challenge3 = Challenge.objects.create(
            title="Student Course Enrollment Analysis",
            description="<p>Analyze student enrollment data across multiple courses and calculate academic metrics.</p><p>This challenge focuses on LEFT JOINs, COUNT functions, and handling NULL values in educational data.</p>",
            difficulty="medium",
            question="<p><strong>Task:</strong> Find all students and count how many courses each student is enrolled in.</p><p><strong>Requirements:</strong></p><ul><li>Show student name and enrollment count</li><li>Include students with zero enrollments</li><li>Order by enrollment count (highest first), then by student name</li><li>Use LEFT JOIN to include all students</li></ul>",
            hint="<p><strong>Hint:</strong> Use LEFT JOIN to include all students, even those with no enrollments. Use COUNT() to count enrollments and handle NULL values properly.</p><pre>SELECT s.name, COUNT(e.course_id) as enrollment_count<br>FROM students s<br>LEFT JOIN enrollments e ON s.id = e.student_id<br>GROUP BY s.id, s.name<br>ORDER BY enrollment_count DESC, s.name</pre>",
            reference_query="SELECT s.name, COUNT(e.course_id) as enrollment_count FROM students s LEFT JOIN enrollments e ON s.id = e.student_id GROUP BY s.id, s.name ORDER BY enrollment_count DESC, s.name",
            subscription_type="free",
            company="EduTech University",
            tags=["left-join", "count", "groupby", "null-handling", "academic"],
            xp=25,
            is_active=True,
            order=30
        )

        # Add students table for Challenge 3
        ChallengeTable.objects.create(
            challenge=challenge3,
            table_name="students",
            schema_sql="""CREATE TABLE students (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    enrollment_date DATE
)""",
            run_dataset_sql="""INSERT INTO students (id, name, email, enrollment_date) VALUES
(1, 'Sarah Connor', 'sarah@university.edu', '2023-09-01'),
(2, 'Mike Johnson', 'mike@university.edu', '2023-09-01'),
(3, 'Lisa Wang', 'lisa@university.edu', '2023-09-02')""",
            submit_dataset_sql="""INSERT INTO students (id, name, email, enrollment_date) VALUES
(1, 'Sarah Connor', 'sarah@university.edu', '2023-09-01'),
(2, 'Mike Johnson', 'mike@university.edu', '2023-09-01'),
(3, 'Lisa Wang', 'lisa@university.edu', '2023-09-02'),
(4, 'Tom Brown', 'tom@university.edu', '2023-09-03'),
(5, 'Anna Davis', 'anna@university.edu', '2023-09-04')""",
            order=10
        )

        # Add enrollments table for Challenge 3
        ChallengeTable.objects.create(
            challenge=challenge3,
            table_name="enrollments",
            schema_sql="""CREATE TABLE enrollments (
    id INT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrollment_date DATE,
    grade VARCHAR(2)
)""",
            run_dataset_sql="""INSERT INTO enrollments (id, student_id, course_id, enrollment_date, grade) VALUES
(1, 1, 1, '2023-09-05', 'A'),
(2, 1, 2, '2023-09-05', 'B'),
(3, 2, 1, '2023-09-06', 'A')""",
            submit_dataset_sql="""INSERT INTO enrollments (id, student_id, course_id, enrollment_date, grade) VALUES
(1, 1, 1, '2023-09-05', 'A'),
(2, 1, 2, '2023-09-05', 'B'),
(3, 2, 1, '2023-09-06', 'A'),
(4, 3, 1, '2023-09-07', 'B'),
(5, 3, 2, '2023-09-07', 'A'),
(6, 3, 3, '2023-09-07', 'A'),
(7, 4, 2, '2023-09-08', 'B')""",
            order=20
        )
        challenges_created.append(challenge3)

        # Challenge 4: Product Inventory Management (Hard)
        self.stdout.write('Creating Challenge 4: Product Inventory Management...')
        challenge4 = Challenge.objects.create(
            title="Product Inventory Management",
            description="<p>Master complex SQL queries by analyzing product inventory across multiple categories and suppliers.</p><p>This advanced challenge involves multiple JOINs and complex filtering for inventory management.</p>",
            difficulty="hard",
            question="<p><strong>Task:</strong> Find products that are running low on stock (quantity < 50) along with their supplier information.</p><p><strong>Requirements:</strong></p><ul><li>Show product name, category name, current stock, and supplier name</li><li>Only include products with stock less than 50</li><li>Order by stock quantity (lowest first)</li><li>Include supplier contact information</li></ul>",
            hint="<p><strong>Hint:</strong> Join products, categories, and suppliers tables. Use WHERE clause to filter low stock items.</p><pre>SELECT p.name, c.name, p.stock_quantity, s.name, s.contact_email<br>FROM products p<br>JOIN categories c ON p.category_id = c.id<br>JOIN suppliers s ON p.supplier_id = s.id<br>WHERE p.stock_quantity < 50<br>ORDER BY p.stock_quantity</pre>",
            reference_query="SELECT p.name as product_name, c.name as category_name, p.stock_quantity, s.name as supplier_name, s.contact_email FROM products p INNER JOIN categories c ON p.category_id = c.id INNER JOIN suppliers s ON p.supplier_id = s.id WHERE p.stock_quantity < 50 ORDER BY p.stock_quantity",
            subscription_type="paid",
            company="InventoryPro Systems",
            tags=["joins", "filtering", "inventory", "suppliers", "advanced"],
            xp=45,
            is_active=True,
            order=40
        )

        # Add products table for Challenge 4
        ChallengeTable.objects.create(
            challenge=challenge4,
            table_name="products",
            schema_sql="""CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category_id INT NOT NULL,
    supplier_id INT NOT NULL,
    stock_quantity INT NOT NULL,
    unit_price DECIMAL(10,2)
)""",
            run_dataset_sql="""INSERT INTO products (id, name, category_id, supplier_id, stock_quantity, unit_price) VALUES
(1, 'Wireless Mouse', 1, 1, 25, 29.99),
(2, 'Gaming Keyboard', 1, 1, 75, 89.99),
(3, 'Office Chair', 2, 2, 15, 199.99)""",
            submit_dataset_sql="""INSERT INTO products (id, name, category_id, supplier_id, stock_quantity, unit_price) VALUES
(1, 'Wireless Mouse', 1, 1, 25, 29.99),
(2, 'Gaming Keyboard', 1, 1, 75, 89.99),
(3, 'Office Chair', 2, 2, 15, 199.99),
(4, 'Desk Lamp', 2, 2, 8, 45.99),
(5, 'Monitor Stand', 1, 3, 35, 39.99),
(6, 'Ergonomic Cushion', 2, 3, 120, 25.99)""",
            order=10
        )

        # Add categories table for Challenge 4
        ChallengeTable.objects.create(
            challenge=challenge4,
            table_name="categories",
            schema_sql="""CREATE TABLE categories (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT
)""",
            run_dataset_sql="""INSERT INTO categories (id, name, description) VALUES
(1, 'Electronics', 'Electronic devices and accessories'),
(2, 'Furniture', 'Office and home furniture')""",
            submit_dataset_sql="""INSERT INTO categories (id, name, description) VALUES
(1, 'Electronics', 'Electronic devices and accessories'),
(2, 'Furniture', 'Office and home furniture'),
(3, 'Accessories', 'Various accessories and add-ons')""",
            order=20
        )

        # Add suppliers table for Challenge 4
        ChallengeTable.objects.create(
            challenge=challenge4,
            table_name="suppliers",
            schema_sql="""CREATE TABLE suppliers (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT
)""",
            run_dataset_sql="""INSERT INTO suppliers (id, name, contact_email, phone, address) VALUES
(1, 'TechSupply Co', 'orders@techsupply.com', '555-0101', '123 Tech Street'),
(2, 'FurniturePlus', 'sales@furnitureplus.com', '555-0202', '456 Furniture Ave')""",
            submit_dataset_sql="""INSERT INTO suppliers (id, name, contact_email, phone, address) VALUES
(1, 'TechSupply Co', 'orders@techsupply.com', '555-0101', '123 Tech Street'),
(2, 'FurniturePlus', 'sales@furnitureplus.com', '555-0202', '456 Furniture Ave'),
(3, 'AccessoryWorld', 'info@accessoryworld.com', '555-0303', '789 Accessory Blvd')""",
            order=30
        )
        challenges_created.append(challenge4)

        # Challenge 5: Advanced Sales Analytics (Extreme Hard)
        self.stdout.write('Creating Challenge 5: Advanced Sales Analytics...')
        challenge5 = Challenge.objects.create(
            title="Advanced Sales Analytics",
            description="<p>Master the most complex SQL concepts with advanced sales analytics involving multiple tables, subqueries, and window functions.</p><p>This expert-level challenge combines everything you've learned: complex JOINs, aggregations, filtering, and advanced SQL techniques.</p>",
            difficulty="extreme",
            question="<p><strong>Task:</strong> Find the top-performing salesperson in each region based on total sales amount.</p><p><strong>Requirements:</strong></p><ul><li>Show region name, salesperson name, and total sales amount</li><li>Only show the highest-performing salesperson per region</li><li>Include regions even if they have no sales</li><li>Order by total sales amount (highest first)</li></ul>",
            hint="<p><strong>Hint:</strong> This requires multiple JOINs and potentially a window function or subquery to find the top performer per region. Consider using ROW_NUMBER() or MAX() with GROUP BY.</p><pre>SELECT r.name, sp.name, SUM(s.amount) as total_sales<br>FROM regions r<br>LEFT JOIN salespersons sp ON r.id = sp.region_id<br>LEFT JOIN sales s ON sp.id = s.salesperson_id<br>GROUP BY r.id, r.name, sp.id, sp.name<br>-- Add logic to get top performer per region</pre>",
            reference_query="SELECT r.name as region_name, sp.name as salesperson_name, COALESCE(SUM(s.amount), 0) as total_sales FROM regions r LEFT JOIN salespersons sp ON r.id = sp.region_id LEFT JOIN sales s ON sp.id = s.salesperson_id GROUP BY r.id, r.name, sp.id, sp.name ORDER BY total_sales DESC",
            subscription_type="paid",
            company="SalesForce Analytics",
            tags=["advanced", "window-functions", "subqueries", "analytics", "expert"],
            xp=75,
            is_active=True,
            order=50
        )

        # Add regions table for Challenge 5
        ChallengeTable.objects.create(
            challenge=challenge5,
            table_name="regions",
            schema_sql="""CREATE TABLE regions (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(255),
    manager VARCHAR(255)
)""",
            run_dataset_sql="""INSERT INTO regions (id, name, country, manager) VALUES
(1, 'North America', 'USA', 'John Manager'),
(2, 'Europe', 'UK', 'Jane Director')""",
            submit_dataset_sql="""INSERT INTO regions (id, name, country, manager) VALUES
(1, 'North America', 'USA', 'John Manager'),
(2, 'Europe', 'UK', 'Jane Director'),
(3, 'Asia Pacific', 'Singapore', 'Mike Regional'),
(4, 'Latin America', 'Brazil', 'Maria Chief')""",
            order=10
        )

        # Add salespersons table for Challenge 5
        ChallengeTable.objects.create(
            challenge=challenge5,
            table_name="salespersons",
            schema_sql="""CREATE TABLE salespersons (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    region_id INT NOT NULL,
    hire_date DATE,
    commission_rate DECIMAL(5,4)
)""",
            run_dataset_sql="""INSERT INTO salespersons (id, name, region_id, hire_date, commission_rate) VALUES
(1, 'Alice Sales', 1, '2022-01-15', 0.0500),
(2, 'Bob Revenue', 1, '2022-03-20', 0.0450),
(3, 'Carol Euro', 2, '2022-02-10', 0.0525)""",
            submit_dataset_sql="""INSERT INTO salespersons (id, name, region_id, hire_date, commission_rate) VALUES
(1, 'Alice Sales', 1, '2022-01-15', 0.0500),
(2, 'Bob Revenue', 1, '2022-03-20', 0.0450),
(3, 'Carol Euro', 2, '2022-02-10', 0.0525),
(4, 'David Asia', 3, '2022-04-05', 0.0475),
(5, 'Emma Latin', 4, '2022-05-12', 0.0550)""",
            order=20
        )

        # Add sales table for Challenge 5
        ChallengeTable.objects.create(
            challenge=challenge5,
            table_name="sales",
            schema_sql="""CREATE TABLE sales (
    id INT PRIMARY KEY,
    salesperson_id INT NOT NULL,
    sale_date DATE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    product_category VARCHAR(255)
)""",
            run_dataset_sql="""INSERT INTO sales (id, salesperson_id, sale_date, amount, product_category) VALUES
(1, 1, '2023-06-01', 15000.00, 'Software'),
(2, 1, '2023-06-15', 8500.00, 'Hardware'),
(3, 2, '2023-06-10', 12000.00, 'Software'),
(4, 3, '2023-06-20', 18000.00, 'Enterprise')""",
            submit_dataset_sql="""INSERT INTO sales (id, salesperson_id, sale_date, amount, product_category) VALUES
(1, 1, '2023-06-01', 15000.00, 'Software'),
(2, 1, '2023-06-15', 8500.00, 'Hardware'),
(3, 2, '2023-06-10', 12000.00, 'Software'),
(4, 3, '2023-06-20', 18000.00, 'Enterprise'),
(5, 3, '2023-06-25', 9500.00, 'Software'),
(6, 4, '2023-06-30', 22000.00, 'Enterprise'),
(7, 5, '2023-07-05', 11000.00, 'Hardware')""",
            order=30
        )
        challenges_created.append(challenge5)

        # Generate expected results for all challenges
        self.stdout.write('Generating expected results for all challenges...')
        success_count = 0
        for challenge in challenges_created:
            success, message = challenge.execute_reference_query()
            if success:
                self.stdout.write(f'✅ Generated expected results for: {challenge.title}')
                success_count += 1
            else:
                self.stdout.write(f'❌ Failed to generate results for {challenge.title}: {message}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(challenges_created)} comprehensive challenges '
                f'with {ChallengeTable.objects.count()} total tables! '
                f'Expected results generated for {success_count}/{len(challenges_created)} challenges.'
            )
        )
