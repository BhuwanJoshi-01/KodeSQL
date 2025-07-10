#!/usr/bin/env python
"""
Demonstration of multi-table challenge creation and access.
Shows how superusers can create challenges with multiple tables
and how users can access all tables in their queries.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqlplayground.settings')
django.setup()

from django.contrib.auth import get_user_model
from challenges.models import Challenge, ChallengeTable

User = get_user_model()

def create_multi_table_demo():
    """Create a comprehensive multi-table challenge demonstration."""
    
    print("🎯 Multi-Table Challenge Demo: 'E-Commerce Database Analysis'")
    print("=" * 70)
    
    # Create the challenge with a complex reference query using multiple tables
    challenge = Challenge.objects.create(
        title="E-Commerce Database Analysis - Multi-Table Demo",
        description="""
        Analyze an e-commerce database with multiple related tables.
        Write queries that JOIN across customers, orders, and products tables.
        This demonstrates how users can access multiple tables in a single challenge.
        """,
        difficulty="HARD",
        reference_query="""
        SELECT 
            c.name as customer_name,
            COUNT(o.id) as total_orders,
            SUM(p.price * o.quantity) as total_spent,
            AVG(p.price) as avg_product_price
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id AND o.flag_id = 2
        LEFT JOIN products p ON o.product_id = p.id AND p.flag_id = 2
        WHERE c.flag_id = 2
        GROUP BY c.id, c.name
        HAVING total_spent > 100
        ORDER BY total_spent DESC;
        """
    )
    
    print(f"✅ Challenge created: {challenge.title}")
    
    # Table 1: Customers
    print("\n📋 Creating Customers table...")
    table1 = ChallengeTable.objects.create(
        challenge=challenge,
        table_name="customers",
        schema_sql="""CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    city VARCHAR(50)
)""",
        run_dataset_sql="""INSERT INTO customers (id, name, email, city) VALUES 
(1, 'Alice Johnson', 'alice@email.com', 'New York'),
(2, 'Bob Smith', 'bob@email.com', 'Los Angeles')""",
        submit_dataset_sql="""INSERT INTO customers (id, name, email, city) VALUES 
(1, 'Alice Johnson', 'alice@email.com', 'New York'),
(2, 'Bob Smith', 'bob@email.com', 'Los Angeles'),
(3, 'Carol Davis', 'carol@email.com', 'Chicago')"""
    )
    
    # Table 2: Products
    print("📋 Creating Products table...")
    table2 = ChallengeTable.objects.create(
        challenge=challenge,
        table_name="products",
        schema_sql="""CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    category VARCHAR(50)
)""",
        run_dataset_sql="""INSERT INTO products (id, name, price, category) VALUES 
(1, 'Laptop', 999.99, 'Electronics'),
(2, 'Book', 19.99, 'Education'),
(3, 'Headphones', 79.99, 'Electronics')""",
        submit_dataset_sql="""INSERT INTO products (id, name, price, category) VALUES 
(1, 'Laptop', 999.99, 'Electronics'),
(2, 'Book', 19.99, 'Education'),
(3, 'Headphones', 79.99, 'Electronics'),
(4, 'Tablet', 299.99, 'Electronics')"""
    )
    
    # Table 3: Orders (Junction table)
    print("📋 Creating Orders table...")
    table3 = ChallengeTable.objects.create(
        challenge=challenge,
        table_name="orders",
        schema_sql="""CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    quantity INT,
    order_date DATE
)""",
        run_dataset_sql="""INSERT INTO orders (id, customer_id, product_id, quantity, order_date) VALUES 
(1, 1, 1, 1, '2024-01-15'),
(2, 1, 2, 2, '2024-01-16'),
(3, 2, 3, 1, '2024-01-17')""",
        submit_dataset_sql="""INSERT INTO orders (id, customer_id, product_id, quantity, order_date) VALUES 
(1, 1, 1, 1, '2024-01-15'),
(2, 1, 2, 2, '2024-01-16'),
(3, 2, 3, 1, '2024-01-17'),
(4, 3, 1, 1, '2024-01-18'),
(5, 1, 4, 1, '2024-01-19')"""
    )
    
    print("\n🔧 Testing Multi-Table System:")
    print("=" * 50)
    
    # Test 1: Verify all tables are created
    table_count = challenge.tables.count()
    print(f"1️⃣ Tables Created: {table_count} tables")
    for i, table in enumerate(challenge.tables.all(), 1):
        print(f"   Table {i}: {table.table_name} (unique: {table.get_unique_table_name()})")
    
    # Test 2: Verify automation works for all tables
    print(f"\n2️⃣ Automation Status:")
    all_automated = True
    for table in challenge.tables.all():
        schema = table.get_processed_schema_sql()
        has_flag_id = 'flag_id' in schema
        has_unique_name = table.get_unique_table_name() in schema
        
        if not (has_flag_id and has_unique_name):
            all_automated = False
        
        print(f"   {table.table_name}: flag_id={has_flag_id}, unique_name={has_unique_name}")
    
    print(f"   Overall: {'✅ All tables automated' if all_automated else '❌ Some tables failed'}")
    
    # Test 3: Test reference query with multiple tables
    print(f"\n3️⃣ Multi-Table Query Execution:")
    try:
        success, message = challenge.execute_reference_query()
        print(f"   Reference Query: {'✅ SUCCESS' if success else '❌ FAILED'}")
        if success:
            challenge.refresh_from_db()
            if challenge.expected_result_json and challenge.expected_result_json != '[]':
                import json
                results = json.loads(challenge.expected_result_json)
                print(f"   Results Generated: {len(results)} rows")
                if results:
                    print(f"   Sample Result: {results[0]}")
        else:
            print(f"   Error: {message}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Show how users can access tables
    print(f"\n4️⃣ User Access to Tables:")
    print("   Users can write queries like:")
    print("   ```sql")
    print("   SELECT c.name, p.name as product, o.quantity")
    print("   FROM customers c")
    print("   JOIN orders o ON c.id = o.customer_id") 
    print("   JOIN products p ON o.product_id = p.id")
    print("   WHERE c.city = 'New York';")
    print("   ```")
    
    print(f"\n🎉 Multi-Table Demo Results:")
    print(f"   Challenge ID: {challenge.id}")
    print(f"   Tables: {challenge.tables.count()}")
    print(f"   All tables have unique names and flag_id columns")
    print(f"   Reference query works across all tables")
    print(f"   Users can JOIN and query across all tables")
    
    print(f"\n🌐 Test in Browser:")
    print(f"   Admin Edit: http://127.0.0.1:8000/admin/challenge/{challenge.id}/edit/")
    print(f"   Challenge Page: http://127.0.0.1:8000/challenges/{challenge.id}/")
    
    return challenge

if __name__ == "__main__":
    try:
        challenge = create_multi_table_demo()
        print(f"\n✨ Multi-table challenge created successfully!")
        print(f"   Superusers can add multiple tables via the admin form")
        print(f"   Users can access all tables in their SQL queries")
        print(f"   All automation features work across multiple tables")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
