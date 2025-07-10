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

            # Use the correct settings variables that match our .env configuration
            conn = psycopg2.connect(
                host=getattr(settings, 'POSTGRESQL_HOST', 'localhost'),
                port=getattr(settings, 'POSTGRESQL_PORT', 5432),
                database=config.get('database', getattr(settings, 'POSTGRESQL_DB', 'sqlplayground_queries_pg')),
                user=getattr(settings, 'POSTGRESQL_USER', 'postgres'),
                password=getattr(settings, 'POSTGRESQL_PASSWORD', ''),
                cursor_factory=RealDictCursor
            )
            return conn
        except ImportError:
            raise ImportError("psycopg2 is required for PostgreSQL support. Install with: pip install psycopg2-binary")
    
    def _get_mysql_connection(self, config):
        """Get MySQL connection."""
        try:
            import mysql.connector

            # Use the correct settings variables that match our .env configuration
            conn = mysql.connector.connect(
                host=getattr(settings, 'MYSQL_HOST', 'localhost'),
                port=getattr(settings, 'MYSQL_PORT', 3306),
                database=config.get('database', getattr(settings, 'MYSQL_DB', 'sqlplayground_queries_mysql')),
                user=getattr(settings, 'MYSQL_USER', 'root'),
                password=getattr(settings, 'MYSQL_PASSWORD', ''),
                autocommit=True
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


def execute_sql_query_enhanced(engine, db_config_or_path, query):
    """
    Enhanced SQL query execution that handles complex queries, CTEs, multiple statements,
    and multiple result sets for both MySQL and PostgreSQL.

    This function is designed to work like professional SQL clients, supporting:
    - Common Table Expressions (CTEs)
    - Multiple SELECT statements
    - Complex subqueries and window functions
    - Mixed statement types (SELECT, INSERT, UPDATE, etc.)
    """
    from editor.views import remove_sql_comments
    import re

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

        # Use appropriate cursor type for each engine
        if engine == 'postgresql':
            import psycopg2.extras
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        elif engine == 'mysql':
            cursor = conn.cursor(dictionary=True, buffered=True)
        else:  # sqlite
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

        # Split query into individual statements
        statements = _split_sql_statements(clean_query)

        all_results = []
        total_changes = 0
        last_insert_id = None

        for i, statement in enumerate(statements):
            statement = statement.strip()
            if not statement:
                continue

            try:
                # Execute the statement
                cursor.execute(statement)

                # Determine if this is a SELECT statement or returns results
                is_select = _is_select_statement(statement)

                if is_select:
                    # Handle SELECT statements and other statements that return results
                    rows = cursor.fetchall()

                    if rows:
                        # Get column information
                        if engine == 'postgresql':
                            columns = list(rows[0].keys()) if rows else []
                            results = [dict(row) for row in rows]
                        elif engine == 'mysql':
                            columns = [desc[0] for desc in cursor.description] if cursor.description else []
                            results = rows  # Already dictionaries with dictionary=True cursor
                        else:  # sqlite
                            columns = [desc[0] for desc in cursor.description] if cursor.description else []
                            results = [dict(row) for row in rows]

                        # Filter out flag_id column from display if present
                        filtered_columns = [col for col in columns if col != 'flag_id']
                        filtered_results = []
                        for row in results:
                            if isinstance(row, dict):
                                filtered_row = {k: v for k, v in row.items() if k != 'flag_id'}
                            else:
                                # Handle tuple/list rows
                                filtered_row = {col: row[j] for j, col in enumerate(columns) if col != 'flag_id'}
                            filtered_results.append(filtered_row)

                        all_results.append({
                            'statement_index': i,
                            'statement': statement,
                            'type': 'SELECT',
                            'results': filtered_results,
                            'columns': filtered_columns,
                            'row_count': len(filtered_results)
                        })
                    else:
                        # Empty result set
                        all_results.append({
                            'statement_index': i,
                            'statement': statement,
                            'type': 'SELECT',
                            'results': [],
                            'columns': [],
                            'row_count': 0
                        })
                else:
                    # Handle INSERT, UPDATE, DELETE, etc.
                    if engine != 'postgresql':  # PostgreSQL auto-commits in autocommit mode
                        conn.commit()

                    changes = cursor.rowcount if hasattr(cursor, 'rowcount') else 0
                    total_changes += changes

                    # Get last insert ID for INSERT statements
                    if hasattr(cursor, 'lastrowid') and cursor.lastrowid:
                        last_insert_id = cursor.lastrowid

                    all_results.append({
                        'statement_index': i,
                        'statement': statement,
                        'type': 'MODIFICATION',
                        'changes': changes,
                        'message': f'Query executed successfully. {changes} row(s) affected.'
                    })

                # For MySQL, consume any remaining results to avoid "Unread result found" error
                if engine == 'mysql':
                    try:
                        while cursor.nextset():
                            pass
                    except:
                        pass

            except Exception as stmt_error:
                # If one statement fails, return error for that specific statement
                conn.close()
                return {
                    'success': False,
                    'error': f'Error in statement {i + 1}: {str(stmt_error)}',
                    'statement': statement,
                    'engine': engine
                }

        conn.close()

        # Prepare the response based on results
        if len(all_results) == 1:
            # Single statement - return simplified format
            result = all_results[0]
            if result['type'] == 'SELECT':
                return {
                    'success': True,
                    'results': result['results'],
                    'columns': result['columns'],
                    'row_count': result['row_count'],
                    'engine': engine
                }
            else:
                return {
                    'success': True,
                    'changes': result['changes'],
                    'last_id': last_insert_id,
                    'message': result['message'],
                    'engine': engine
                }
        else:
            # Multiple statements - return comprehensive format
            select_results = [r for r in all_results if r['type'] == 'SELECT']
            modification_results = [r for r in all_results if r['type'] == 'MODIFICATION']

            response = {
                'success': True,
                'multiple_statements': True,
                'total_statements': len(statements),
                'engine': engine
            }

            if select_results:
                # If there are SELECT results, prioritize the last one for main display
                last_select = select_results[-1]
                response.update({
                    'results': last_select['results'],
                    'columns': last_select['columns'],
                    'row_count': last_select['row_count']
                })
                response['all_select_results'] = select_results

            if modification_results:
                response.update({
                    'total_changes': total_changes,
                    'last_id': last_insert_id,
                    'modification_results': modification_results
                })

            if not select_results and modification_results:
                response['message'] = f'All statements executed successfully. {total_changes} total row(s) affected.'

            return response

    except Exception as e:
        try:
            conn.close()
        except:
            pass
        return {
            'success': False,
            'error': f'{engine.title()} Error: {str(e)}',
            'engine': engine
        }


def execute_sql_query_multi_engine(engine, db_config_or_path, query):
    """
    Legacy SQL query execution function - now uses enhanced execution.
    Maintained for backward compatibility.
    """
    return execute_sql_query_enhanced(engine, db_config_or_path, query)


def _split_sql_statements(query):
    """
    Split SQL query into individual statements, handling complex cases like:
    - Semicolons within string literals
    - CTEs and complex subqueries
    - Multiple statements
    """
    import re

    # Remove comments first
    from editor.views import remove_sql_comments
    clean_query = remove_sql_comments(query)

    # Simple approach: split by semicolon, but be smart about it
    # This handles most cases including CTEs
    statements = []
    current_statement = ""
    in_string = False
    string_char = None

    i = 0
    while i < len(clean_query):
        char = clean_query[i]

        # Handle string literals
        if char in ("'", '"') and not in_string:
            in_string = True
            string_char = char
            current_statement += char
        elif char == string_char and in_string:
            # Check if it's escaped
            if i > 0 and clean_query[i-1] == '\\':
                current_statement += char
            else:
                in_string = False
                string_char = None
                current_statement += char
        elif char == ';' and not in_string:
            # End of statement
            if current_statement.strip():
                statements.append(current_statement.strip())
            current_statement = ""
        else:
            current_statement += char

        i += 1

    # Add the last statement if it doesn't end with semicolon
    if current_statement.strip():
        statements.append(current_statement.strip())

    return statements


def _is_select_statement(statement):
    """
    Determine if a SQL statement returns results (SELECT, WITH, SHOW, DESCRIBE, etc.)
    """
    statement_upper = statement.upper().strip()

    # Statements that return results
    result_returning_keywords = [
        'SELECT', 'WITH', 'SHOW', 'DESCRIBE', 'DESC', 'EXPLAIN',
        'PRAGMA', 'CALL'  # Some stored procedures return results
    ]

    for keyword in result_returning_keywords:
        if statement_upper.startswith(keyword):
            return True

    return False


def execute_query_on_schema(schema_file_path, query, engine='mysql'):
    """
    Execute a query on a schema file for challenge validation.
    Creates a temporary database, loads the schema, executes the query, and returns results.
    """
    import tempfile
    import os
    import uuid
    from editor.views import remove_sql_comments

    # Clean the query
    clean_query = remove_sql_comments(query).strip()

    if not clean_query:
        return {
            'success': False,
            'error': 'Query is empty or contains only comments'
        }

    # Generate unique database name
    db_name = f"challenge_temp_{uuid.uuid4().hex[:8]}"

    try:
        # Read schema file
        with open(schema_file_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        if engine.lower() == 'mysql':
            return _execute_mysql_schema_query(db_name, schema_sql, clean_query)
        elif engine.lower() == 'postgresql':
            return _execute_postgresql_schema_query(db_name, schema_sql, clean_query)
        else:
            return {
                'success': False,
                'error': f'Unsupported engine: {engine}'
            }

    except Exception as e:
        return {
            'success': False,
            'error': f'Error executing query on schema: {str(e)}'
        }


def _execute_mysql_schema_query(db_name, schema_sql, query):
    """Execute query on MySQL with schema"""
    import mysql.connector
    from django.conf import settings

    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(
            host=getattr(settings, 'MYSQL_HOST', 'localhost'),
            user=getattr(settings, 'MYSQL_USER', 'root'),
            password=getattr(settings, 'MYSQL_PASSWORD', ''),
            port=getattr(settings, 'MYSQL_PORT', 3306)
        )
        cursor = conn.cursor(dictionary=True)

        # Create temporary database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
        cursor.execute(f"USE `{db_name}`")

        # Execute schema SQL
        for statement in schema_sql.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)

        # Execute user query
        cursor.execute(query)

        if query.upper().strip().startswith('SELECT'):
            results = cursor.fetchall()
            return {
                'success': True,
                'results': results,
                'row_count': len(results)
            }
        else:
            conn.commit()
            return {
                'success': True,
                'results': [],
                'changes': cursor.rowcount
            }

    except Exception as e:
        return {
            'success': False,
            'error': f'MySQL Error: {str(e)}'
        }
    finally:
        try:
            # Clean up temporary database
            cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
            cursor.close()
            conn.close()
        except:
            pass


def _execute_postgresql_schema_query(db_name, schema_sql, query):
    """Execute query on PostgreSQL with schema (converted from MySQL)"""
    import psycopg2
    import psycopg2.extras
    from django.conf import settings

    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=getattr(settings, 'POSTGRESQL_HOST', 'localhost'),
            user=getattr(settings, 'POSTGRESQL_USER', 'postgres'),
            password=getattr(settings, 'POSTGRESQL_PASSWORD', ''),
            port=getattr(settings, 'POSTGRESQL_PORT', 5432),
            database=getattr(settings, 'POSTGRESQL_DB', 'postgres')
        )
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Create temporary database
        cursor.execute(f"CREATE DATABASE {db_name}")
        cursor.close()
        conn.close()

        # Connect to the new database
        conn = psycopg2.connect(
            host=getattr(settings, 'POSTGRESQL_HOST', 'localhost'),
            user=getattr(settings, 'POSTGRESQL_USER', 'postgres'),
            password=getattr(settings, 'POSTGRESQL_PASSWORD', ''),
            port=getattr(settings, 'POSTGRESQL_PORT', 5432),
            database=db_name
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Convert MySQL schema to PostgreSQL compatible
        pg_schema = convert_mysql_to_postgresql(schema_sql)

        # Execute schema SQL
        for statement in pg_schema.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)

        # Execute user query
        cursor.execute(query)

        if query.upper().strip().startswith('SELECT'):
            results = cursor.fetchall()
            # Convert to list of dicts
            results = [dict(row) for row in results]
            return {
                'success': True,
                'results': results,
                'row_count': len(results)
            }
        else:
            conn.commit()
            return {
                'success': True,
                'results': [],
                'changes': cursor.rowcount
            }

    except Exception as e:
        return {
            'success': False,
            'error': f'PostgreSQL Error: {str(e)}'
        }
    finally:
        try:
            cursor.close()
            conn.close()
            # Clean up temporary database
            admin_conn = psycopg2.connect(
                host=getattr(settings, 'POSTGRESQL_HOST', 'localhost'),
                user=getattr(settings, 'POSTGRESQL_USER', 'postgres'),
                password=getattr(settings, 'POSTGRESQL_PASSWORD', ''),
                port=getattr(settings, 'POSTGRESQL_PORT', 5432),
                database=getattr(settings, 'POSTGRESQL_DB', 'postgres')
            )
            admin_conn.autocommit = True
            admin_cursor = admin_conn.cursor()
            admin_cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            admin_cursor.close()
            admin_conn.close()
        except:
            pass


def convert_mysql_to_postgresql(mysql_sql):
    """
    Convert MySQL SQL to PostgreSQL compatible SQL.
    This is a basic converter for common cases.
    """
    import re

    # Convert MySQL specific syntax to PostgreSQL
    pg_sql = mysql_sql

    # Convert INT AUTO_INCREMENT PRIMARY KEY to SERIAL PRIMARY KEY
    pg_sql = re.sub(r'\bINT\s+AUTO_INCREMENT\s+PRIMARY\s+KEY\b', 'SERIAL PRIMARY KEY', pg_sql, flags=re.IGNORECASE)

    # Convert standalone AUTO_INCREMENT to SERIAL (fallback)
    pg_sql = re.sub(r'\bAUTO_INCREMENT\b', 'SERIAL', pg_sql, flags=re.IGNORECASE)

    # Convert MySQL data types to PostgreSQL equivalents
    type_mappings = {
        r'\bTINYINT\b': 'SMALLINT',
        r'\bMEDIUMINT\b': 'INTEGER',
        r'\bBIGINT\b': 'BIGINT',
        r'\bVARCHAR\((\d+)\)': r'VARCHAR(\1)',
        r'\bTEXT\b': 'TEXT',
        r'\bDATETIME\b': 'TIMESTAMP',
        r'\bTIMESTAMP\b': 'TIMESTAMP',
        r'\bDOUBLE\b': 'DOUBLE PRECISION',
        r'\bFLOAT\b': 'REAL',
        r'\bDECIMAL\((\d+),(\d+)\)': r'DECIMAL(\1,\2)',
    }

    for mysql_type, pg_type in type_mappings.items():
        pg_sql = re.sub(mysql_type, pg_type, pg_sql, flags=re.IGNORECASE)

    # Remove MySQL specific options
    pg_sql = re.sub(r'\bENGINE\s*=\s*\w+', '', pg_sql, flags=re.IGNORECASE)
    pg_sql = re.sub(r'\bCHARSET\s*=\s*\w+', '', pg_sql, flags=re.IGNORECASE)
    pg_sql = re.sub(r'\bCOLLATE\s*=\s*\w+', '', pg_sql, flags=re.IGNORECASE)

    # Convert backticks to double quotes for identifiers
    pg_sql = re.sub(r'`([^`]+)`', r'"\1"', pg_sql)

    return pg_sql


def ensure_consistent_column_order(results, reference_columns=None):
    """
    Ensure consistent column ordering in query results.
    This function is used during challenge creation to maintain column order consistency.

    Args:
        results: List of dictionaries representing query results
        reference_columns: Optional list of column names in desired order

    Returns:
        List of dictionaries with consistent column ordering
    """
    if not results or not isinstance(results, list):
        return results

    # If no reference columns provided, use the order from the first result
    if not reference_columns and results:
        first_result = results[0]
        if isinstance(first_result, dict):
            reference_columns = list(first_result.keys())

    if not reference_columns:
        return results

    # Reorder all results to match the reference column order
    ordered_results = []
    for result in results:
        if isinstance(result, dict):
            ordered_result = {}
            # First, add columns in the reference order
            for col in reference_columns:
                if col in result:
                    ordered_result[col] = result[col]
            # Then add any additional columns not in reference
            for col, value in result.items():
                if col not in ordered_result:
                    ordered_result[col] = value
            ordered_results.append(ordered_result)
        else:
            ordered_results.append(result)

    return ordered_results


def normalize_json_result(result, preserve_order=False):
    """
    Normalize JSON result for comparison between MySQL and PostgreSQL.
    Handles different data types and ensures consistent formatting across engines.

    Args:
        result: The result to normalize
        preserve_order: If True, preserves the original row order (for exact order matching)
    """
    import json
    import decimal
    from datetime import datetime, date

    def normalize_value(value):
        """Normalize individual values for cross-database consistency"""
        if value is None:
            return None
        elif isinstance(value, bool):
            # Ensure boolean consistency (MySQL might return 1/0, PostgreSQL true/false)
            return bool(value)
        elif isinstance(value, int):
            return int(value)
        elif isinstance(value, float):
            # Round to avoid floating point precision differences
            return round(float(value), 10)
        elif isinstance(value, decimal.Decimal):
            # Convert Decimal to float for consistency
            return round(float(value), 10)
        elif isinstance(value, (datetime, date)):
            # Ensure consistent date/datetime formatting
            return value.isoformat()
        elif isinstance(value, str):
            # Strip whitespace and ensure consistent string formatting
            return value.strip()
        elif isinstance(value, bytes):
            # Handle binary data
            return value.decode('utf-8', errors='ignore')
        else:
            # Convert any other type to string
            return str(value)

    if isinstance(result, list):
        normalized = []
        for row in result:
            if isinstance(row, dict):
                normalized_row = {}
                # Preserve original key order instead of sorting
                for key in row.keys():
                    # Skip flag_id column from comparison
                    if key.lower() != 'flag_id':
                        normalized_row[key] = normalize_value(row[key])
                normalized.append(normalized_row)
            else:
                normalized.append(normalize_value(row))

        # Only sort if preserve_order is False (for backward compatibility)
        if not preserve_order:
            # Sort rows by their string representation for consistent ordering
            # This handles cases where different engines might return rows in different orders
            try:
                normalized.sort(key=lambda x: json.dumps(x, sort_keys=True) if isinstance(x, dict) else str(x))
            except (TypeError, ValueError):
                # If sorting fails, keep original order
                pass

        return normalized
    else:
        return normalize_value(result)


def normalize_json_result_with_exact_order(result):
    """
    Normalize JSON result while preserving exact row order.
    Use this for strict order validation where ORDER BY matters.
    """
    return normalize_json_result(result, preserve_order=True)


def execute_dual_dataset_query(challenge, query, flag_id, engine='mysql'):
    """
    Execute a query on a challenge's dual-dataset system.

    Args:
        challenge: Challenge instance with schema_sql, run_dataset_sql, submit_dataset_sql
        query: SQL query to execute
        flag_id: 1 for run dataset, 2 for submit dataset
        engine: Database engine ('mysql' or 'postgresql')

    Returns:
        Dict with success, results, error, etc.
    """
    import tempfile
    import os
    import uuid
    from editor.views import remove_sql_comments

    # Clean the query
    clean_query = remove_sql_comments(query).strip()

    if not clean_query:
        return {
            'success': False,
            'error': 'Query is empty or contains only comments'
        }

    # Generate unique database name
    db_name = f"challenge_{challenge.id}_temp_{uuid.uuid4().hex[:8]}"

    try:
        # Get processed schema and dataset SQL (supports both legacy and multi-table systems)
        schema_sql = challenge.get_all_schema_sql()
        dataset_sql = challenge.get_all_dataset_sql(flag_id)

        if not schema_sql or not dataset_sql:
            return {
                'success': False,
                'error': 'Schema SQL and dataset SQL are required'
            }

        # Process user query to use unique table names and add flag_id filter
        processed_query = _process_user_query(clean_query, challenge, flag_id)

        if engine.lower() == 'mysql':
            # Try MySQL first, fallback to PostgreSQL if MySQL is not available
            mysql_result = _execute_mysql_dual_dataset(db_name, schema_sql, dataset_sql, processed_query)

            # Check if MySQL connection failed
            if not mysql_result['success'] and ('2003' in mysql_result.get('error', '') or "Can't connect to MySQL server" in mysql_result.get('error', '')):
                print(f"MySQL not available, falling back to PostgreSQL: {mysql_result.get('error')}")
                # Fallback to PostgreSQL
                pg_result = _execute_postgresql_dual_dataset(db_name, schema_sql, dataset_sql, processed_query)
                # Add a note about the fallback
                if pg_result.get('success'):
                    pg_result['fallback_used'] = True
                    pg_result['original_engine'] = 'mysql'
                return pg_result
            else:
                return mysql_result
        elif engine.lower() == 'postgresql':
            return _execute_postgresql_dual_dataset(db_name, schema_sql, dataset_sql, processed_query)
        else:
            return {
                'success': False,
                'error': f'Unsupported engine: {engine}'
            }

    except Exception as e:
        return {
            'success': False,
            'error': f'Error executing dual-dataset query: {str(e)}'
        }


def _process_user_query(query, challenge, flag_id):
    """
    Process user query to use unique table names and add flag_id filter.
    Only adds flag_id filter if the query references tables from the schema.
    """
    import re

    table_mapping = challenge.get_unique_table_names()
    processed_query = query
    tables_referenced = []
    table_aliases = {}  # Map unique_name -> alias

    # Replace table names with unique names and track which tables are referenced
    for original_name, unique_name in table_mapping.items():
        # Replace table names in FROM clauses (with optional alias)
        pattern = r'\bFROM\s+`?' + re.escape(original_name) + r'`?(\s+(\w+))?\b'
        def replace_from(match):
            alias = match.group(2) if match.group(2) else None
            if alias and alias.upper() not in ['WHERE', 'ORDER', 'GROUP', 'HAVING', 'LIMIT', 'SELECT', 'FROM', 'JOIN', 'ON', 'AND', 'OR']:
                table_aliases[unique_name] = alias
                return f'FROM {unique_name} {alias}'
            else:
                # If alias is a SQL keyword, preserve it after the table name
                if alias:
                    return f'FROM {unique_name} {alias}'
                else:
                    return f'FROM {unique_name}'

        if re.search(pattern, processed_query, flags=re.IGNORECASE):
            tables_referenced.append((original_name, unique_name))
        processed_query = re.sub(pattern, replace_from, processed_query, flags=re.IGNORECASE)

        # Replace table names in JOIN clauses (with optional alias)
        pattern = r'\bJOIN\s+`?' + re.escape(original_name) + r'`?(\s+(\w+))?\b'
        def replace_join(match):
            alias = match.group(2) if match.group(2) else None
            if alias and alias.upper() not in ['WHERE', 'ORDER', 'GROUP', 'HAVING', 'LIMIT', 'SELECT', 'FROM', 'JOIN', 'ON', 'AND', 'OR']:
                table_aliases[unique_name] = alias
                return f'JOIN {unique_name} {alias}'
            else:
                return f'JOIN {unique_name}'

        if re.search(pattern, processed_query, flags=re.IGNORECASE):
            if (original_name, unique_name) not in tables_referenced:
                tables_referenced.append((original_name, unique_name))
        processed_query = re.sub(pattern, replace_join, processed_query, flags=re.IGNORECASE)

    # Only add flag_id filter if the query references tables from the schema
    if not tables_referenced:
        # Query doesn't reference any schema tables (e.g., "SELECT 1 as test")
        # Return as-is without adding flag_id filter
        return processed_query

    # Check if the challenge schema actually has flag_id columns
    # This prevents errors when flag_id columns are missing
    schema_sql = challenge.get_all_schema_sql()
    if not schema_sql or 'flag_id' not in schema_sql.lower():
        # Schema doesn't have flag_id columns, return query without flag_id filter
        # This handles legacy challenges or improperly created challenges
        return processed_query

    # Check if this is a CTE query
    is_cte_query = bool(re.search(r'\bWITH\b', processed_query, re.IGNORECASE))

    if is_cte_query:
        # For CTE queries, add flag_id filters to each SELECT statement within the CTE
        # This is complex, so for now we'll add flag_id filters to individual SELECT statements
        def add_flag_id_to_select(match):
            select_statement = match.group(0)
            # Check if this SELECT references our tables
            table_referenced = False
            for original_name, unique_name in tables_referenced:
                if unique_name in select_statement:
                    table_referenced = True
                    break

            if table_referenced:
                # Add WHERE flag_id = {flag_id} to this SELECT
                if 'WHERE' in select_statement.upper():
                    # Add to existing WHERE
                    select_statement = re.sub(
                        r'\bWHERE\b',
                        f'WHERE {unique_name}.flag_id = {flag_id} AND',
                        select_statement,
                        flags=re.IGNORECASE
                    )
                else:
                    # Add new WHERE clause before FROM
                    # Find the FROM clause and add WHERE before any GROUP BY, ORDER BY, etc.
                    keywords = ['GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'UNION']
                    where_added = False
                    for keyword in keywords:
                        pattern = r'\b' + keyword.replace(' ', r'\s+') + r'\b'
                        if re.search(pattern, select_statement, re.IGNORECASE):
                            select_statement = re.sub(
                                pattern,
                                f'WHERE {unique_name}.flag_id = {flag_id} {keyword}',
                                select_statement,
                                flags=re.IGNORECASE
                            )
                            where_added = True
                            break

                    if not where_added:
                        # Add at the end of the SELECT statement
                        select_statement += f' WHERE {unique_name}.flag_id = {flag_id}'

            return select_statement

        # Apply flag_id filters to SELECT statements within the CTE
        # This regex matches SELECT statements that are not the main outer SELECT
        processed_query = re.sub(
            r'SELECT\s+[^)]+?FROM\s+\w+',
            add_flag_id_to_select,
            processed_query,
            flags=re.IGNORECASE | re.DOTALL
        )

        return processed_query

    # Add flag_id filter to WHERE clause
    # Check if this is a JOIN query by looking for JOIN keywords
    is_join_query = bool(re.search(r'\bJOIN\b', processed_query, re.IGNORECASE))

    if is_join_query:
        # For JOIN queries, we need to add flag_id conditions for each referenced table
        flag_id_conditions = []
        for original_name, unique_name in tables_referenced:
            # Use alias if available, otherwise use unique table name
            if unique_name in table_aliases:
                alias = table_aliases[unique_name]
                flag_id_conditions.append(f'{alias}.flag_id = {flag_id}')
            else:
                flag_id_conditions.append(f'{unique_name}.flag_id = {flag_id}')

        flag_id_clause = ' AND '.join(flag_id_conditions)
    else:
        # For simple queries with one table, use simple flag_id
        flag_id_clause = f'flag_id = {flag_id}'

    if 'WHERE' in processed_query.upper():
        # Add to existing WHERE clause
        processed_query = re.sub(
            r'\bWHERE\b',
            f'WHERE {flag_id_clause} AND',
            processed_query,
            flags=re.IGNORECASE
        )
    else:
        # Remove trailing semicolon if present
        has_semicolon = processed_query.rstrip().endswith(';')
        if has_semicolon:
            processed_query = processed_query.rstrip().rstrip(';')

        # Add WHERE clause before GROUP BY, HAVING, ORDER BY, LIMIT (in correct SQL order)
        # But avoid matching these keywords inside parentheses (like in window functions)
        keywords = ['GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT']
        where_added = False
        for keyword in keywords:
            # Use regex to properly match the keyword as a whole phrase
            # but not inside parentheses (to avoid window functions)
            pattern = r'\b' + keyword.replace(' ', r'\s+') + r'\b'

            # Find all matches and check if they're outside parentheses
            matches = list(re.finditer(pattern, processed_query, re.IGNORECASE))
            for match in matches:
                # Check if this match is inside parentheses by counting open/close parens before it
                text_before = processed_query[:match.start()]
                open_parens = text_before.count('(')
                close_parens = text_before.count(')')

                # If we're not inside parentheses (equal number of open/close), this is a valid match
                if open_parens == close_parens:
                    processed_query = re.sub(
                        pattern,
                        f'WHERE {flag_id_clause} {keyword}',
                        processed_query,
                        count=1,  # Only replace the first valid occurrence
                        flags=re.IGNORECASE
                    )
                    where_added = True
                    break

            if where_added:
                break

        if not where_added:
            # No special keywords found, add WHERE at the end
            processed_query += f' WHERE {flag_id_clause}'

        # Add semicolon back if it was there
        if has_semicolon:
            processed_query += ';'

    return processed_query


def _execute_mysql_dual_dataset(db_name, schema_sql, dataset_sql, query):
    """Execute dual-dataset query on MySQL using enhanced execution"""
    import mysql.connector
    from django.conf import settings

    try:
        # Connect to MySQL server using new configuration
        conn = mysql.connector.connect(
            host=getattr(settings, 'MYSQL_HOST', 'localhost'),
            user=getattr(settings, 'MYSQL_USER', 'root'),
            password=getattr(settings, 'MYSQL_PASSWORD', ''),
            port=getattr(settings, 'MYSQL_PORT', 3306)
        )
        cursor = conn.cursor(dictionary=True, buffered=True)

        # Create temporary database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
        cursor.execute(f"USE `{db_name}`")

        # Execute schema SQL using enhanced statement splitting
        schema_statements = _split_sql_statements(schema_sql)
        for statement in schema_statements:
            if statement.strip():
                cursor.execute(statement)
                # Consume any results to avoid "Unread result found" error
                try:
                    while cursor.nextset():
                        pass
                except:
                    pass

        # Execute dataset SQL using enhanced statement splitting
        dataset_statements = _split_sql_statements(dataset_sql)
        for statement in dataset_statements:
            if statement.strip():
                cursor.execute(statement)
                # Consume any results to avoid "Unread result found" error
                try:
                    while cursor.nextset():
                        pass
                except:
                    pass

        # Execute user query using enhanced logic
        statements = _split_sql_statements(query)
        all_results = []

        for i, statement in enumerate(statements):
            statement = statement.strip()
            if not statement:
                continue

            cursor.execute(statement)

            # Determine if this statement returns results
            is_select = _is_select_statement(statement)

            if is_select:
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                # Filter out flag_id column from display while preserving column order
                filtered_columns = [col for col in columns if col != 'flag_id']
                filtered_results = []
                for row in results:
                    if isinstance(row, dict):
                        # Preserve column order by iterating through filtered_columns
                        filtered_row = {}
                        for col in filtered_columns:
                            if col in row:
                                filtered_row[col] = row[col]
                    else:
                        # Handle tuple/list results
                        filtered_row = {}
                        for j, col in enumerate(columns):
                            if col != 'flag_id':
                                filtered_row[col] = row[j]
                    filtered_results.append(filtered_row)

                all_results.append({
                    'type': 'SELECT',
                    'results': filtered_results,
                    'columns': filtered_columns,
                    'row_count': len(filtered_results)
                })
            else:
                conn.commit()
                changes = cursor.rowcount
                all_results.append({
                    'type': 'MODIFICATION',
                    'changes': changes
                })

            # Consume any remaining results to avoid "Unread result found" error
            try:
                while cursor.nextset():
                    pass
            except:
                pass

        # Return results based on what was executed
        if len(all_results) == 1 and all_results[0]['type'] == 'SELECT':
            # Single SELECT statement
            result = all_results[0]
            return {
                'success': True,
                'results': result['results'],
                'columns': result['columns'],
                'row_count': result['row_count']
            }
        elif len(all_results) == 1 and all_results[0]['type'] == 'MODIFICATION':
            # Single modification statement
            result = all_results[0]
            return {
                'success': True,
                'results': [],
                'changes': result['changes']
            }
        else:
            # Multiple statements - return the last SELECT result if any
            select_results = [r for r in all_results if r['type'] == 'SELECT']
            if select_results:
                last_select = select_results[-1]
                return {
                    'success': True,
                    'results': last_select['results'],
                    'columns': last_select['columns'],
                    'row_count': last_select['row_count'],
                    'multiple_statements': True
                }
            else:
                total_changes = sum(r['changes'] for r in all_results if r['type'] == 'MODIFICATION')
                return {
                    'success': True,
                    'results': [],
                    'changes': total_changes,
                    'multiple_statements': True
                }

    except Exception as e:
        return {
            'success': False,
            'error': f'MySQL Error: {str(e)}'
        }
    finally:
        try:
            # Clean up temporary database
            cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
            cursor.close()
            conn.close()
        except:
            pass


def _execute_postgresql_dual_dataset(db_name, schema_sql, dataset_sql, query):
    """Execute dual-dataset query on PostgreSQL (converted from MySQL)"""
    import psycopg2
    import psycopg2.extras
    from django.conf import settings

    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=getattr(settings, 'POSTGRESQL_HOST', 'localhost'),
            user=getattr(settings, 'POSTGRESQL_USER', 'postgres'),
            password=getattr(settings, 'POSTGRESQL_PASSWORD', ''),
            port=getattr(settings, 'POSTGRESQL_PORT', 5432),
            database=getattr(settings, 'POSTGRESQL_DB', 'postgres')
        )
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Create temporary database
        cursor.execute(f"CREATE DATABASE {db_name}")
        cursor.close()
        conn.close()

        # Connect to the new database
        conn = psycopg2.connect(
            host=getattr(settings, 'POSTGRESQL_HOST', 'localhost'),
            user=getattr(settings, 'POSTGRESQL_USER', 'postgres'),
            password=getattr(settings, 'POSTGRESQL_PASSWORD', ''),
            port=getattr(settings, 'POSTGRESQL_PORT', 5432),
            database=db_name
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Convert MySQL schema to PostgreSQL compatible
        pg_schema = convert_mysql_to_postgresql(schema_sql)
        pg_dataset = convert_mysql_to_postgresql(dataset_sql)

        # Execute schema SQL using enhanced statement splitting
        schema_statements = _split_sql_statements(pg_schema)
        for statement in schema_statements:
            if statement.strip():
                cursor.execute(statement)

        # Execute dataset SQL using enhanced statement splitting
        dataset_statements = _split_sql_statements(pg_dataset)
        for statement in dataset_statements:
            if statement.strip():
                cursor.execute(statement)

        # Execute user query using enhanced logic
        statements = _split_sql_statements(query)
        all_results = []

        for i, statement in enumerate(statements):
            statement = statement.strip()
            if not statement:
                continue

            cursor.execute(statement)

            # Determine if this statement returns results
            is_select = _is_select_statement(statement)

            if is_select:
                results = cursor.fetchall()
                # Convert to list of dicts
                results = [dict(row) for row in results]

                # Extract column names from the first result if available
                columns = list(results[0].keys()) if results else []

                # Filter out flag_id column from display while preserving column order
                filtered_columns = [col for col in columns if col != 'flag_id']
                filtered_results = []
                for row in results:
                    # Preserve column order by iterating through filtered_columns
                    filtered_row = {}
                    for col in filtered_columns:
                        if col in row:
                            filtered_row[col] = row[col]
                    filtered_results.append(filtered_row)

                all_results.append({
                    'type': 'SELECT',
                    'results': filtered_results,
                    'columns': filtered_columns,
                    'row_count': len(filtered_results)
                })
            else:
                conn.commit()
                changes = cursor.rowcount
                all_results.append({
                    'type': 'MODIFICATION',
                    'changes': changes
                })

        # Return results based on what was executed
        if len(all_results) == 1 and all_results[0]['type'] == 'SELECT':
            # Single SELECT statement
            result = all_results[0]
            return {
                'success': True,
                'results': result['results'],
                'columns': result['columns'],
                'row_count': result['row_count']
            }
        elif len(all_results) == 1 and all_results[0]['type'] == 'MODIFICATION':
            # Single modification statement
            result = all_results[0]
            return {
                'success': True,
                'results': [],
                'changes': result['changes']
            }
        else:
            # Multiple statements - return the last SELECT result if any
            select_results = [r for r in all_results if r['type'] == 'SELECT']
            if select_results:
                last_select = select_results[-1]
                return {
                    'success': True,
                    'results': last_select['results'],
                    'columns': last_select['columns'],
                    'row_count': last_select['row_count'],
                    'multiple_statements': True
                }
            else:
                total_changes = sum(r['changes'] for r in all_results if r['type'] == 'MODIFICATION')
                return {
                    'success': True,
                    'results': [],
                    'changes': total_changes,
                    'multiple_statements': True
                }

    except Exception as e:
        return {
            'success': False,
            'error': f'PostgreSQL Error: {str(e)}'
        }
    finally:
        try:
            cursor.close()
            conn.close()
            # Clean up temporary database
            admin_conn = psycopg2.connect(
                host=getattr(settings, 'POSTGRESQL_HOST', 'localhost'),
                user=getattr(settings, 'POSTGRESQL_USER', 'postgres'),
                password=getattr(settings, 'POSTGRESQL_PASSWORD', ''),
                port=getattr(settings, 'POSTGRESQL_PORT', 5432),
                database=getattr(settings, 'POSTGRESQL_DB', 'postgres')
            )
            admin_conn.autocommit = True
            admin_cursor = admin_conn.cursor()
            admin_cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            admin_cursor.close()
            admin_conn.close()
        except:
            pass
