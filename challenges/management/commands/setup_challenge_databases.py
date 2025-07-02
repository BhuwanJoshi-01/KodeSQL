from django.core.management.base import BaseCommand
from challenges.models import Challenge


class Command(BaseCommand):
    help = 'Setup database schemas and initialization SQL for existing challenges'

    def handle(self, *args, **options):
        self.stdout.write('Setting up challenge databases...')
        
        # Define sample database schema for employee challenges
        employee_schema = {
            "tables": {
                "employees": {
                    "columns": [
                        {"name": "id", "type": "INTEGER PRIMARY KEY"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "department", "type": "TEXT"},
                        {"name": "salary", "type": "INTEGER"}
                    ]
                }
            }
        }
        
        employee_init_sql = """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary INTEGER
        );
        
        INSERT OR REPLACE INTO employees (id, name, department, salary) VALUES
        (1, 'John Doe', 'Engineering', 75000),
        (2, 'Jane Smith', 'Marketing', 65000),
        (3, 'Bob Johnson', 'Engineering', 80000),
        (4, 'Alice Brown', 'HR', 55000),
        (5, 'Charlie Wilson', 'Marketing', 60000);
        """
        
        # Update challenges with employee-related content
        employee_challenges = Challenge.objects.filter(
            title__icontains='employee'
        ) | Challenge.objects.filter(
            expected_query__icontains='employees'
        )
        
        for challenge in employee_challenges:
            challenge.database_schema = employee_schema
            challenge.initialization_sql = employee_init_sql
            challenge.save()
            self.stdout.write(f'Updated challenge: {challenge.title}')
        
        # Define sample schema for order/return challenges
        ecommerce_schema = {
            "tables": {
                "orders": {
                    "columns": [
                        {"name": "customer_name", "type": "TEXT"},
                        {"name": "order_date", "type": "DATE"},
                        {"name": "order_id", "type": "INTEGER PRIMARY KEY"},
                        {"name": "sales", "type": "INTEGER"}
                    ]
                },
                "returns": {
                    "columns": [
                        {"name": "order_id", "type": "INTEGER PRIMARY KEY"},
                        {"name": "return_date", "type": "DATE"}
                    ]
                }
            }
        }
        
        ecommerce_init_sql = """
        CREATE TABLE IF NOT EXISTS orders (
            customer_name TEXT,
            order_date DATE,
            order_id INTEGER PRIMARY KEY,
            sales INTEGER
        );
        
        CREATE TABLE IF NOT EXISTS returns (
            order_id INTEGER PRIMARY KEY,
            return_date DATE
        );
        
        INSERT OR REPLACE INTO orders (customer_name, order_date, order_id, sales) VALUES
        ('Alexa', '2023-01-15', 1, 100),
        ('Alexa', '2023-02-20', 2, 150),
        ('Alexa', '2023-03-10', 3, 200),
        ('Alexa', '2023-04-05', 4, 120),
        ('Ankit', '2023-01-20', 5, 300),
        ('Ankit', '2023-02-15', 6, 250),
        ('Priya', '2023-01-25', 7, 180),
        ('Priya', '2023-02-28', 8, 220),
        ('Priya', '2023-03-15', 9, 160);
        
        INSERT OR REPLACE INTO returns (order_id, return_date) VALUES
        (1, '2023-01-20'),
        (2, '2023-02-25'),
        (3, '2023-03-15'),
        (5, '2023-01-25'),
        (6, '2023-02-20'),
        (7, '2023-01-30'),
        (9, '2023-03-20');
        """
        
        # Update challenges with order/return content
        order_challenges = Challenge.objects.filter(
            title__icontains='return'
        ) | Challenge.objects.filter(
            expected_query__icontains='orders'
        ) | Challenge.objects.filter(
            expected_query__icontains='returns'
        )
        
        for challenge in order_challenges:
            challenge.database_schema = ecommerce_schema
            challenge.initialization_sql = ecommerce_init_sql
            challenge.save()
            self.stdout.write(f'Updated challenge: {challenge.title}')
        
        # For challenges without specific schemas, use the employee schema as default
        challenges_without_schema = Challenge.objects.filter(
            database_schema__isnull=True
        ) | Challenge.objects.filter(
            database_schema={}
        )
        
        for challenge in challenges_without_schema:
            if not challenge.database_schema:
                challenge.database_schema = employee_schema
                challenge.initialization_sql = employee_init_sql
                challenge.save()
                self.stdout.write(f'Set default schema for challenge: {challenge.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up challenge databases!')
        )
