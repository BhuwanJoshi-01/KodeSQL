"""
Management command to create sample tutorials and lessons.
"""

from django.core.management.base import BaseCommand
from tutorials.models import Tutorial, Lesson


class Command(BaseCommand):
    help = 'Create sample tutorials and lessons'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample tutorials...')
        
        # Tutorial 1: SQL Basics
        tutorial1, created = Tutorial.objects.get_or_create(
            title="SQL Basics",
            defaults={
                'description': "Learn the fundamentals of SQL including SELECT statements, filtering, and basic operations.",
                'difficulty': 'beginner',
                'icon': 'school',
                'order': 1
            }
        )
        
        if created:
            # Lesson 1.1: Introduction to SQL
            Lesson.objects.create(
                tutorial=tutorial1,
                title="Introduction to SQL",
                content="""
Welcome to SQL! SQL (Structured Query Language) is a programming language designed for managing and manipulating relational databases.

In this lesson, you'll learn:
- What SQL is and why it's important
- Basic database concepts
- How to write your first SQL query

SQL is used to:
- Retrieve data from databases
- Insert new data
- Update existing data
- Delete data
- Create and modify database structures

Let's start with the most basic SQL command: SELECT.
                """,
                example_query="SELECT 'Hello, SQL!' as greeting;",
                expected_output="greeting\nHello, SQL!",
                order=1
            )
            
            # Lesson 1.2: SELECT Statement
            Lesson.objects.create(
                tutorial=tutorial1,
                title="The SELECT Statement",
                content="""
The SELECT statement is used to retrieve data from a database. It's the most commonly used SQL command.

Basic syntax:
```sql
SELECT column1, column2, ...
FROM table_name;
```

To select all columns, use the asterisk (*):
```sql
SELECT * FROM table_name;
```

Let's practice with our sample database!
                """,
                example_query="SELECT * FROM employees LIMIT 5;",
                expected_output="id | name | department | salary\n1 | John Doe | Engineering | 75000\n...",
                order=2
            )
            
            # Lesson 1.3: WHERE Clause
            Lesson.objects.create(
                tutorial=tutorial1,
                title="Filtering with WHERE",
                content="""
The WHERE clause is used to filter records based on specific conditions.

Syntax:
```sql
SELECT column1, column2, ...
FROM table_name
WHERE condition;
```

Common operators:
- = (equal)
- != or <> (not equal)
- > (greater than)
- < (less than)
- >= (greater than or equal)
- <= (less than or equal)
- LIKE (pattern matching)
- IN (match any value in a list)
                """,
                example_query="SELECT name, salary FROM employees WHERE salary > 50000;",
                expected_output="name | salary\nJohn Doe | 75000\n...",
                order=3
            )
        
        # Tutorial 2: Intermediate SQL
        tutorial2, created = Tutorial.objects.get_or_create(
            title="Intermediate SQL",
            defaults={
                'description': "Dive deeper into SQL with JOINs, GROUP BY, and aggregate functions.",
                'difficulty': 'intermediate',
                'icon': 'trending_up',
                'order': 2
            }
        )
        
        if created:
            # Lesson 2.1: JOINs
            Lesson.objects.create(
                tutorial=tutorial2,
                title="Understanding JOINs",
                content="""
JOINs are used to combine rows from two or more tables based on a related column.

Types of JOINs:
- INNER JOIN: Returns records that have matching values in both tables
- LEFT JOIN: Returns all records from the left table, and matched records from the right table
- RIGHT JOIN: Returns all records from the right table, and matched records from the left table
- FULL OUTER JOIN: Returns all records when there is a match in either left or right table

Let's start with INNER JOIN:
                """,
                example_query="""SELECT e.name, d.department_name 
FROM employees e 
INNER JOIN departments d ON e.department_id = d.id;""",
                expected_output="name | department_name\nJohn Doe | Engineering\n...",
                order=1
            )
            
            # Lesson 2.2: GROUP BY
            Lesson.objects.create(
                tutorial=tutorial2,
                title="Grouping Data with GROUP BY",
                content="""
The GROUP BY statement groups rows that have the same values into summary rows.
It's often used with aggregate functions like COUNT(), MAX(), MIN(), SUM(), AVG().

Syntax:
```sql
SELECT column_name(s)
FROM table_name
WHERE condition
GROUP BY column_name(s)
ORDER BY column_name(s);
```

Common aggregate functions:
- COUNT(): Returns the number of rows
- SUM(): Returns the sum of a numeric column
- AVG(): Returns the average value of a numeric column
- MAX(): Returns the maximum value
- MIN(): Returns the minimum value
                """,
                example_query="SELECT department, COUNT(*) as employee_count FROM employees GROUP BY department;",
                expected_output="department | employee_count\nEngineering | 5\nMarketing | 3\n...",
                order=2
            )
        
        # Tutorial 3: Advanced SQL
        tutorial3, created = Tutorial.objects.get_or_create(
            title="Advanced SQL",
            defaults={
                'description': "Master advanced SQL concepts including subqueries, window functions, and complex queries.",
                'difficulty': 'advanced',
                'icon': 'psychology',
                'order': 3
            }
        )
        
        if created:
            # Lesson 3.1: Subqueries
            Lesson.objects.create(
                tutorial=tutorial3,
                title="Subqueries and Nested Queries",
                content="""
A subquery is a query nested inside another query. Subqueries can be used in SELECT, FROM, WHERE, and HAVING clauses.

Types of subqueries:
- Scalar subquery: Returns a single value
- Row subquery: Returns a single row
- Table subquery: Returns multiple rows and columns

Subqueries can be:
- Correlated: References columns from the outer query
- Non-correlated: Independent of the outer query

Let's explore some examples:
                """,
                example_query="""SELECT name, salary 
FROM employees 
WHERE salary > (SELECT AVG(salary) FROM employees);""",
                expected_output="name | salary\nJohn Doe | 75000\n...",
                order=1
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample tutorials and lessons!')
        )
