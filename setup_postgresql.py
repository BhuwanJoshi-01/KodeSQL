#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script for SQL Playground
This script creates the required PostgreSQL databases and users.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database_and_user():
    """Create PostgreSQL databases and users for the SQL Playground application."""
    
    # Database configuration from .env
    admin_user = 'postgres'
    admin_password = input("Enter PostgreSQL admin (postgres) password: ")
    host = os.getenv('PRIMARY_DB_HOST', 'localhost')
    port = int(os.getenv('PRIMARY_DB_PORT', '5432'))
    
    # Database names and users from .env
    main_db_name = os.getenv('PRIMARY_DB_NAME', 'postgres')
    query_db_name = os.getenv('QUERY_POSTGRES_DB_NAME', 'sqlplayground_queries_pg')
    
    db_user = os.getenv('PRIMARY_DB_USER', 'postgres')
    db_password = os.getenv('PRIMARY_DB_PASSWORD', 'forgex99')
    
    try:
        # Connect to PostgreSQL server as admin
        print(f"Connecting to PostgreSQL server at {host}:{port}...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=admin_user,
            password=admin_password,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create user if it doesn't exist (only if not using postgres user)
        if db_user != 'postgres':
            print(f"Creating user '{db_user}'...")
            try:
                cursor.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_password}';")
                print(f"User '{db_user}' created successfully.")
            except psycopg2.errors.DuplicateObject:
                print(f"User '{db_user}' already exists.")
                # Update password
                cursor.execute(f"ALTER USER {db_user} WITH PASSWORD '{db_password}';")
                print(f"Password updated for user '{db_user}'.")
        
        # Create main database if it doesn't exist
        if main_db_name != 'postgres':
            print(f"Creating main database '{main_db_name}'...")
            try:
                cursor.execute(f"CREATE DATABASE {main_db_name} OWNER {db_user};")
                print(f"Database '{main_db_name}' created successfully.")
            except psycopg2.errors.DuplicateDatabase:
                print(f"Database '{main_db_name}' already exists.")
        
        # Create query execution database
        print(f"Creating query database '{query_db_name}'...")
        try:
            cursor.execute(f"CREATE DATABASE {query_db_name} OWNER {db_user};")
            print(f"Database '{query_db_name}' created successfully.")
        except psycopg2.errors.DuplicateDatabase:
            print(f"Database '{query_db_name}' already exists.")
        
        # Grant privileges
        if db_user != 'postgres':
            print(f"Granting privileges to user '{db_user}'...")
            if main_db_name != 'postgres':
                cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {main_db_name} TO {db_user};")
            cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {query_db_name} TO {db_user};")
            print("Privileges granted successfully.")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*50)
        print("PostgreSQL setup completed successfully!")
        print("="*50)
        print(f"Main database: {main_db_name}")
        print(f"Query database: {query_db_name}")
        print(f"User: {db_user}")
        print(f"Host: {host}")
        print(f"Port: {port}")
        print("\nYou can now run your Django application.")
        
    except psycopg2.Error as e:
        print(f"Error setting up PostgreSQL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def test_connection():
    """Test the database connection with the configured settings."""
    
    host = os.getenv('PRIMARY_DB_HOST', 'localhost')
    port = int(os.getenv('PRIMARY_DB_PORT', '5432'))
    main_db_name = os.getenv('PRIMARY_DB_NAME', 'postgres')
    query_db_name = os.getenv('QUERY_POSTGRES_DB_NAME', 'sqlplayground_queries_pg')
    db_user = os.getenv('PRIMARY_DB_USER', 'postgres')
    db_password = os.getenv('PRIMARY_DB_PASSWORD', 'forgex99')
    
    print("\nTesting database connections...")
    
    # Test main database connection
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=main_db_name,
            user=db_user,
            password=db_password
        )
        conn.close()
        print(f"✓ Main database connection successful: {main_db_name}")
    except psycopg2.Error as e:
        print(f"✗ Main database connection failed: {e}")
        return False
    
    # Test query database connection
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=query_db_name,
            user=db_user,
            password=db_password
        )
        conn.close()
        print(f"✓ Query database connection successful: {query_db_name}")
    except psycopg2.Error as e:
        print(f"✗ Query database connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("PostgreSQL Database Setup for SQL Playground")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode - only test connections
        if test_connection():
            print("\nAll database connections are working!")
        else:
            print("\nSome database connections failed. Please check your configuration.")
            sys.exit(1)
    else:
        # Setup mode - create databases and users
        create_database_and_user()
        
        # Test the connections after setup
        if test_connection():
            print("\nSetup verification successful!")
        else:
            print("\nSetup completed but connection test failed. Please check your configuration.")
