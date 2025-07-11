#!/usr/bin/env python3
"""
PostgreSQL Connection Fix Script for cPanel
This script tries different PostgreSQL connection methods to find what works
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection(config_name, host, port, sslmode, extra_options=None):
    """Test a specific PostgreSQL connection configuration."""
    print(f"\n🔍 Testing: {config_name}")
    
    try:
        import psycopg2
        
        conn_params = {
            'host': host,
            'port': port,
            'database': os.environ.get('PRIMARY_DB_NAME', 'kodesqli_postgres'),
            'user': os.environ.get('PRIMARY_DB_USER', 'kodesqli_main_database'),
            'password': os.environ.get('PRIMARY_DB_PASSWORD', ''),
            'sslmode': sslmode,
            'connect_timeout': 10
        }
        
        if extra_options:
            conn_params.update(extra_options)
        
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   SSL Mode: {sslmode}")
        print(f"   Database: {conn_params['database']}")
        print(f"   User: {conn_params['user']}")
        
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        
        print(f"   ✅ SUCCESS: Connected to PostgreSQL")
        print(f"   Version: {version[0][:50]}...")
        return conn_params
        
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        return None

def main():
    """Test different PostgreSQL connection configurations."""
    print("🚀 PostgreSQL Connection Troubleshooter")
    print("=" * 60)
    
    # Different configurations to try
    configs = [
        # Unix socket connections (often work best in cPanel)
        ("Unix Socket (default)", "/var/run/postgresql", "", "disable"),
        ("Unix Socket (tmp)", "/tmp", "", "disable"),
        ("Unix Socket (local)", "/var/lib/postgresql", "", "disable"),
        
        # TCP connections with SSL
        ("TCP with SSL required", "127.0.0.1", "5432", "require"),
        ("TCP with SSL prefer", "127.0.0.1", "5432", "prefer"),
        ("TCP with SSL allow", "127.0.0.1", "5432", "allow"),
        
        # TCP connections without SSL
        ("TCP without SSL (127.0.0.1)", "127.0.0.1", "5432", "disable"),
        ("TCP without SSL (localhost)", "localhost", "5432", "disable"),
        
        # Alternative ports (some cPanel setups use different ports)
        ("Alternative port 5433", "127.0.0.1", "5433", "disable"),
        ("Alternative port 5434", "127.0.0.1", "5434", "disable"),
    ]
    
    successful_config = None
    
    for config_name, host, port, sslmode in configs:
        result = test_connection(config_name, host, port, sslmode)
        if result:
            successful_config = result
            break
    
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    
    if successful_config:
        print("✅ Found working PostgreSQL configuration!")
        print(f"   Host: {successful_config['host']}")
        print(f"   Port: {successful_config['port']}")
        print(f"   SSL Mode: {successful_config['sslmode']}")
        
        # Update .env file
        print("\n🔧 Updating .env file...")
        update_env_file(successful_config)
        
        print("\n🎉 Configuration updated! Try running:")
        print("   python manage.py migrate")
        
    else:
        print("❌ No working PostgreSQL configuration found!")
        print("\n🔧 Troubleshooting Steps:")
        print("1. Check if PostgreSQL is installed and running")
        print("2. Verify database exists in cPanel → PostgreSQL Databases")
        print("3. Check user permissions (ALL PRIVILEGES required)")
        print("4. Contact hosting provider with this error:")
        print("   'FATAL: no pg_hba.conf entry for host'")
        print("5. Ask them to configure PostgreSQL access for your user")
        
        print("\n📞 Questions to ask your hosting provider:")
        print("- What host should I use to connect to PostgreSQL?")
        print("- What SSL mode is required?")
        print("- Can you add my user to pg_hba.conf?")
        print("- Is PostgreSQL available on this hosting plan?")

def update_env_file(config):
    """Update .env file with working configuration."""
    try:
        # Read current .env
        with open('.env', 'r') as f:
            content = f.read()
        
        # Update host
        content = content.replace(
            f"PRIMARY_DB_HOST={os.environ.get('PRIMARY_DB_HOST')}",
            f"PRIMARY_DB_HOST={config['host']}"
        )
        content = content.replace(
            f"QUERY_POSTGRES_HOST={os.environ.get('QUERY_POSTGRES_HOST')}",
            f"QUERY_POSTGRES_HOST={config['host']}"
        )
        
        # Update port if different
        if config['port'] and config['port'] != '5432':
            content = content.replace(
                f"PRIMARY_DB_PORT=5432",
                f"PRIMARY_DB_PORT={config['port']}"
            )
            content = content.replace(
                f"QUERY_POSTGRES_PORT=5432",
                f"QUERY_POSTGRES_PORT={config['port']}"
            )
        
        # Write updated content
        with open('.env', 'w') as f:
            f.write(content)
        
        print("   ✅ .env file updated successfully")
        
    except Exception as e:
        print(f"   ❌ Failed to update .env file: {e}")

if __name__ == "__main__":
    main()
