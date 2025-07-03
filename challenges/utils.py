"""
Database engine utilities for multi-database support in challenges.
"""

import os
import sqlite3
import json
import csv
from django.conf import settings


class DatabaseEngineManager:
    """
    Manages database operations across different database engines.
    """
    
    def __init__(self, engine='sqlite'):
        self.engine = engine
        self.supported_engines = ['sqlite', 'postgresql', 'mysql']
        
        if engine not in self.supported_engines:
            raise ValueError(f"Unsupported database engine: {engine}")
    
    def get_connection(self, db_path_or_config):
        """
        Get database connection based on engine type.
        """
        if self.engine == 'sqlite':
            return self._get_sqlite_connection(db_path_or_config)
        elif self.engine == 'postgresql':
            return self._get_postgresql_connection(db_path_or_config)
        elif self.engine == 'mysql':
            return self._get_mysql_connection(db_path_or_config)
        else:
            raise ValueError(f"Unsupported engine: {self.engine}")
    
    def _get_sqlite_connection(self, db_path):
        """Get SQLite connection."""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _get_postgresql_connection(self, config):
        """Get PostgreSQL connection."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            # Use environment variables or default test database
            conn = psycopg2.connect(
                host=getattr(settings, 'CHALLENGE_POSTGRES_HOST', 'localhost'),
                port=getattr(settings, 'CHALLENGE_POSTGRES_PORT', 5432),
                database=config.get('database', 'challenge_test'),
                user=getattr(settings, 'CHALLENGE_POSTGRES_USER', 'postgres'),
                password=getattr(settings, 'CHALLENGE_POSTGRES_PASSWORD', 'password'),
                cursor_factory=RealDictCursor
            )
            return conn
        except ImportError:
            raise ImportError("psycopg2 is required for PostgreSQL support. Install with: pip install psycopg2-binary")
    
    def _get_mysql_connection(self, config):
        """Get MySQL connection."""
        try:
            import mysql.connector
            from mysql.connector.cursor import MySQLCursorDict
            
            # Use environment variables or default test database
            conn = mysql.connector.connect(
                host=getattr(settings, 'CHALLENGE_MYSQL_HOST', 'localhost'),
                port=getattr(settings, 'CHALLENGE_MYSQL_PORT', 3306),
                database=config.get('database', 'challenge_test'),
                user=getattr(settings, 'CHALLENGE_MYSQL_USER', 'root'),
                password=getattr(settings, 'CHALLENGE_MYSQL_PASSWORD', 'password'),
                cursor_class=MySQLCursorDict
            )
            return conn
        except ImportError:
            raise ImportError("mysql-connector-python is required for MySQL support. Install with: pip install mysql-connector-python")
    
    def initialize_challenge_database(self, challenge, user):
        """
        Initialize challenge database for the specified engine.
        """
        try:
            if self.engine == 'sqlite':
                return self._initialize_sqlite_database(challenge, user)
            elif self.engine == 'postgresql':
                return self._initialize_postgresql_database(challenge, user)
            elif self.engine == 'mysql':
                return self._initialize_mysql_database(challenge, user)
        except Exception as e:
            print(f"Error initializing {self.engine} database: {e}")
            raise e
    
    def _initialize_sqlite_database(self, challenge, user):
        """Initialize SQLite database."""
        db_path = challenge.get_challenge_database_path(user, 'sqlite')
        
        # Remove existing database to start fresh
        if os.path.exists(db_path):
            os.remove(db_path)
        
        conn = self.get_connection(db_path)
        cursor = conn.cursor()
        
        try:
            # Execute initialization SQL
            init_sql = self._get_initialization_sql(challenge, 'sqlite')
            if init_sql:
                statements = [stmt.strip() for stmt in init_sql.split(';') if stmt.strip()]
                for statement in statements:
                    cursor.execute(statement)
            
            # Load sample data if provided
            if challenge.sample_data:
                self._load_sample_data(cursor, challenge.sample_data.path, 'sqlite')
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _initialize_postgresql_database(self, challenge, user):
        """Initialize PostgreSQL database."""
        # Create unique database name for this challenge and user
        db_name = f"challenge_{challenge.id}_user_{user.id}"
        
        # First connect to default database to create challenge database
        default_config = {'database': 'postgres'}
        admin_conn = self.get_connection(default_config)
        admin_conn.autocommit = True
        admin_cursor = admin_conn.cursor()
        
        try:
            # Drop database if exists and create new one
            admin_cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            admin_cursor.execute(f"CREATE DATABASE {db_name}")
        finally:
            admin_conn.close()
        
        # Connect to the new database and initialize
        config = {'database': db_name}
        conn = self.get_connection(config)
        cursor = conn.cursor()
        
        try:
            # Execute initialization SQL
            init_sql = self._get_initialization_sql(challenge, 'postgresql')
            if init_sql:
                statements = [stmt.strip() for stmt in init_sql.split(';') if stmt.strip()]
                for statement in statements:
                    cursor.execute(statement)
            
            # Load sample data if provided
            if challenge.sample_data:
                self._load_sample_data(cursor, challenge.sample_data.path, 'postgresql')
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _initialize_mysql_database(self, challenge, user):
        """Initialize MySQL database."""
        # Create unique database name for this challenge and user
        db_name = f"challenge_{challenge.id}_user_{user.id}"
        
        # First connect to default database to create challenge database
        default_config = {'database': 'mysql'}
        admin_conn = self.get_connection(default_config)
        admin_cursor = admin_conn.cursor()
        
        try:
            # Drop database if exists and create new one
            admin_cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            admin_cursor.execute(f"CREATE DATABASE {db_name}")
        finally:
            admin_conn.close()
        
        # Connect to the new database and initialize
        config = {'database': db_name}
        conn = self.get_connection(config)
        cursor = conn.cursor()
        
        try:
            # Execute initialization SQL
            init_sql = self._get_initialization_sql(challenge, 'mysql')
            if init_sql:
                statements = [stmt.strip() for stmt in init_sql.split(';') if stmt.strip()]
                for statement in statements:
                    cursor.execute(statement)
            
            # Load sample data if provided
            if challenge.sample_data:
                self._load_sample_data(cursor, challenge.sample_data.path, 'mysql')
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _get_initialization_sql(self, challenge, engine):
        """
        Get engine-specific initialization SQL using the simplified schema system.
        """
        # Get schema configuration from settings
        schema_config = challenge.get_database_schema_config()

        if not schema_config:
            return None

        # Get engine-specific SQL
        initialization_sql = schema_config.get('initialization_sql', {})

        if engine in initialization_sql:
            return initialization_sql[engine]

        # Fallback to SQLite SQL and adapt it
        sqlite_sql = initialization_sql.get('sqlite', '')
        if sqlite_sql:
            return self._adapt_sql_for_engine(sqlite_sql, engine)

        return None
    
    def _adapt_sql_for_engine(self, sql, engine):
        """
        Adapt SQL syntax for different database engines.
        """
        if engine == 'sqlite':
            return sql
        elif engine == 'postgresql':
            # Convert SQLite syntax to PostgreSQL
            sql = sql.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
            sql = sql.replace('DATETIME DEFAULT CURRENT_TIMESTAMP', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            sql = sql.replace('BOOLEAN DEFAULT 1', 'BOOLEAN DEFAULT TRUE')
            sql = sql.replace('BOOLEAN DEFAULT 0', 'BOOLEAN DEFAULT FALSE')
            return sql
        elif engine == 'mysql':
            # Convert SQLite syntax to MySQL
            sql = sql.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'INT AUTO_INCREMENT PRIMARY KEY')
            sql = sql.replace('DATETIME DEFAULT CURRENT_TIMESTAMP', 'DATETIME DEFAULT CURRENT_TIMESTAMP')
            sql = sql.replace('BOOLEAN DEFAULT 1', 'BOOLEAN DEFAULT TRUE')
            sql = sql.replace('BOOLEAN DEFAULT 0', 'BOOLEAN DEFAULT FALSE')
            return sql
        
        return sql
    
    def _load_sample_data(self, cursor, file_path, engine):
        """
        Load sample data from CSV or SQL file for specific engine.
        """
        if not os.path.exists(file_path):
            return
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.sql':
            # Execute SQL file
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
                adapted_sql = self._adapt_sql_for_engine(sql_content, engine)
                statements = [stmt.strip() for stmt in adapted_sql.split(';') if stmt.strip()]
                for statement in statements:
                    cursor.execute(statement)
        
        elif file_extension == '.csv':
            # Load CSV data (implementation would be similar to existing method)
            # This would need to be adapted for each engine's specific syntax
            pass


def execute_sql_query_multi_engine(engine, db_config_or_path, query):
    """
    Execute SQL query against specified database engine.
    """
    from editor.views import remove_sql_comments
    
    # Clean the query
    clean_query = remove_sql_comments(query).strip()
    
    if not clean_query:
        return {
            'success': False,
            'error': 'Query is empty or contains only comments'
        }
    
    db_manager = DatabaseEngineManager(engine)
    
    try:
        conn = db_manager.get_connection(db_config_or_path)
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute(clean_query)
        
        # Check if it's a SELECT query
        if clean_query.upper().startswith('SELECT'):
            rows = cursor.fetchall()
            
            # Handle different cursor types
            if engine == 'sqlite':
                columns = [description[0] for description in cursor.description] if cursor.description else []
                results = [dict(row) for row in rows]
            else:
                # PostgreSQL and MySQL with dict cursors
                columns = list(rows[0].keys()) if rows else []
                results = [dict(row) for row in rows]
            
            conn.close()
            
            return {
                'success': True,
                'results': results,
                'columns': columns,
                'row_count': len(results),
                'engine': engine
            }
        else:
            # For INSERT, UPDATE, DELETE, etc.
            conn.commit()
            changes = cursor.rowcount
            
            conn.close()
            
            return {
                'success': True,
                'changes': changes,
                'message': f'Query executed successfully on {engine}. {changes} row(s) affected.',
                'engine': engine
            }
    
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return {
            'success': False,
            'error': f'{engine.upper()} Error: {str(e)}',
            'engine': engine
        }
