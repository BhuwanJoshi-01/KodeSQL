#!/usr/bin/env python3
"""
Database Connection Test Script for KodeSQL on cPanel
This script tests database connections with different configurations
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_postgresql_connection():
    """Test PostgreSQL connection with different configurations."""
    print("🔍 Testing PostgreSQL Connection...")
    
    # Test configurations
    configs = [
        {
            'host': '127.0.0.1',
            'sslmode': 'prefer',
            'name': 'IPv4 with SSL prefer'
        },
        {
            'host': '127.0.0.1',
            'sslmode': 'disable',
            'name': 'IPv4 with SSL disabled'
        },
        {
            'host': 'localhost',
            'sslmode': 'disable',
            'name': 'localhost with SSL disabled'
        }
    ]
    
    for config in configs:
        print(f"\n📋 Testing: {config['name']}")
        try:
            import psycopg2
            
            conn_params = {
                'host': config['host'],
                'port': os.environ.get('PRIMARY_DB_PORT', '5432'),
                'database': os.environ.get('PRIMARY_DB_NAME', 'kodesqli_postgres'),
                'user': os.environ.get('PRIMARY_DB_USER', 'kodesqli_main_database'),
                'password': os.environ.get('PRIMARY_DB_PASSWORD', ''),
                'sslmode': config['sslmode'],
                'connect_timeout': 10
            }
            
            print(f"   Host: {conn_params['host']}")
            print(f"   Database: {conn_params['database']}")
            print(f"   User: {conn_params['user']}")
            print(f"   SSL Mode: {conn_params['sslmode']}")
            
            conn = psycopg2.connect(**conn_params)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            
            print(f"   ✅ SUCCESS: {version[0]}")
            return config  # Return successful config
            
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}")
    
    return None

def test_mysql_connection():
    """Test MySQL connection."""
    print("\n🔍 Testing MySQL Connection...")
    
    try:
        import pymysql
        
        conn_params = {
            'host': os.environ.get('QUERY_MYSQL_HOST', 'localhost'),
            'port': int(os.environ.get('QUERY_MYSQL_PORT', '3306')),
            'database': os.environ.get('QUERY_MYSQL_DB_NAME', 'kodesql_queries_mysql'),
            'user': os.environ.get('QUERY_MYSQL_USER', 'kodesql_mysql_user'),
            'password': os.environ.get('QUERY_MYSQL_PASSWORD', ''),
            'charset': 'utf8mb4'
        }
        
        print(f"   Host: {conn_params['host']}")
        print(f"   Database: {conn_params['database']}")
        print(f"   User: {conn_params['user']}")
        
        conn = pymysql.connect(**conn_params)
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        
        print(f"   ✅ SUCCESS: MySQL {version[0]}")
        return True
        
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        return False

def update_env_file(successful_config):
    """Update .env file with successful PostgreSQL configuration."""
    if not successful_config:
        return
    
    print(f"\n🔧 Updating .env file with successful configuration...")
    
    # Read current .env file
    with open('.env', 'r') as f:
        content = f.read()
    
    # Update host if needed
    if successful_config['host'] != os.environ.get('PRIMARY_DB_HOST'):
        content = content.replace(
            f"PRIMARY_DB_HOST={os.environ.get('PRIMARY_DB_HOST')}",
            f"PRIMARY_DB_HOST={successful_config['host']}"
        )
        content = content.replace(
            f"QUERY_POSTGRES_HOST={os.environ.get('QUERY_POSTGRES_HOST')}",
            f"QUERY_POSTGRES_HOST={successful_config['host']}"
        )
    
    # Write updated content
    with open('.env', 'w') as f:
        f.write(content)
    
    print(f"   ✅ Updated .env file with host: {successful_config['host']}")

def main():
    """Main test function."""
    print("🚀 KodeSQL Database Connection Test")
    print("=" * 50)
    
    # Test PostgreSQL
    successful_pg_config = test_postgresql_connection()
    
    # Test MySQL
    mysql_success = test_mysql_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Connection Test Summary")
    print("=" * 50)
    
    if successful_pg_config:
        print(f"✅ PostgreSQL: Working with {successful_pg_config['name']}")
        update_env_file(successful_pg_config)
    else:
        print("❌ PostgreSQL: All configurations failed")
        print("\n🔧 Troubleshooting Steps:")
        print("1. Verify database exists in cPanel → PostgreSQL Databases")
        print("2. Check user permissions (should have ALL PRIVILEGES)")
        print("3. Verify database name and credentials")
        print("4. Contact hosting provider about PostgreSQL configuration")
    
    if mysql_success:
        print("✅ MySQL: Working correctly")
    else:
        print("❌ MySQL: Connection failed")
        print("\n🔧 Troubleshooting Steps:")
        print("1. Verify database exists in cPanel → MySQL Databases")
        print("2. Check user permissions (should have ALL PRIVILEGES)")
        print("3. Verify database name and credentials")
    
    if successful_pg_config and mysql_success:
        print("\n🎉 All database connections working!")
        print("You can now run: python manage.py migrate")
    else:
        print("\n⚠️ Fix database issues before proceeding with migrations")

if __name__ == "__main__":
    main()
