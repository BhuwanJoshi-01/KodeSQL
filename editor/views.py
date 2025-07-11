from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import sqlite3
import os
import time
import re
import csv
import io

from .models import QueryHistory, SavedQuery
from users.models import UserDatabase


def sql_editor(request):
    """
    SQL Editor page.
    """
    context = {
        'page_title': 'SQL Editor',
    }
    return render(request, 'core/home.html', context)


@login_required
@require_http_methods(["POST"])
def execute_query(request):
    """
    Execute SQL query API endpoint.
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()

        if not query:
            return JsonResponse({
                'success': False,
                'error': 'Query is required'
            })

        # Security check - prevent dangerous operations
        if is_dangerous_query(query):
            return JsonResponse({
                'success': False,
                'error': 'This query contains commands that are not allowed in the playground'
            })

        # Get or create user database
        user_db, created = UserDatabase.objects.get_or_create(user=request.user)
        db_path = user_db.full_path

        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database with sample data if it's new
        if created or not os.path.exists(db_path):
            initialize_user_database(db_path)

        # Execute query
        start_time = time.time()
        result = execute_sql_query(db_path, query)
        execution_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds

        # Save to query history
        QueryHistory.objects.create(
            user=request.user,
            query=query,
            execution_time_ms=execution_time,
            success=result['success'],
            error_message=result.get('error', '')
        )

        # Update database last accessed time
        user_db.save()  # This will update last_accessed due to auto_now=True

        return JsonResponse(result)

    except Exception as e:
        # Save failed query to history
        QueryHistory.objects.create(
            user=request.user,
            query=query if 'query' in locals() else '',
            success=False,
            error_message=str(e)
        )

        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })


@login_required
@require_http_methods(["GET"])
def query_history(request):
    """
    Get user's query history.
    """
    try:
        history = QueryHistory.objects.filter(user=request.user).order_by('-executed_at')[:50]

        history_data = []
        for item in history:
            history_data.append({
                'id': item.id,
                'query': item.query,
                'executed_at': item.executed_at.isoformat(),
                'execution_time_ms': item.execution_time_ms,
                'success': item.success,
                'error_message': item.error_message
            })

        return JsonResponse({
            'success': True,
            'history': history_data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["GET"])
def saved_queries(request):
    """
    Get user's saved queries.
    """
    try:
        queries = SavedQuery.objects.filter(user=request.user).order_by('-created_at')

        queries_data = []
        for query in queries:
            queries_data.append({
                'id': query.id,
                'title': query.title,
                'query': query.query,
                'description': query.description,
                'is_favorite': query.is_favorite,
                'created_at': query.created_at.isoformat(),
                'updated_at': query.updated_at.isoformat()
            })

        return JsonResponse({
            'success': True,
            'queries': queries_data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["POST"])
def save_query(request):
    """
    Save a SQL query.
    """
    try:
        data = json.loads(request.body)

        title = data.get('title', '').strip()
        query = data.get('query', '').strip()
        description = data.get('description', '').strip()
        is_favorite = data.get('is_favorite', False)

        if not title or not query:
            return JsonResponse({
                'success': False,
                'error': 'Title and query are required'
            })

        # Check if title already exists for this user
        if SavedQuery.objects.filter(user=request.user, title=title).exists():
            return JsonResponse({
                'success': False,
                'error': 'A query with this title already exists'
            })

        saved_query = SavedQuery.objects.create(
            user=request.user,
            title=title,
            query=query,
            description=description,
            is_favorite=is_favorite
        )

        return JsonResponse({
            'success': True,
            'query': {
                'id': saved_query.id,
                'title': saved_query.title,
                'query': saved_query.query,
                'description': saved_query.description,
                'is_favorite': saved_query.is_favorite,
                'created_at': saved_query.created_at.isoformat()
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["DELETE"])
def delete_saved_query(request, query_id):
    """
    Delete a saved query.
    """
    try:
        saved_query = get_object_or_404(SavedQuery, id=query_id, user=request.user)
        saved_query.delete()

        return JsonResponse({
            'success': True,
            'message': 'Query deleted successfully'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# Helper Functions

def remove_sql_comments(query):
    """
    Remove SQL comments from query.
    Handles both single-line (--) and multi-line (/* */) comments.
    """
    # Remove single-line comments (-- comment)
    query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)

    # Remove multi-line comments (/* comment */)
    query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)

    return query


def is_dangerous_query(query):
    """
    Check if query contains dangerous SQL commands.
    """
    dangerous_commands = [
        'DROP', 'TRUNCATE', 'DELETE', 'ALTER', 'MODIFY',
        'RENAME', 'REMOVE', 'GRANT', 'REVOKE', 'CREATE USER',
        'DROP USER', 'ATTACH', 'DETACH', 'PRAGMA'
    ]

    # Convert to uppercase and remove comments
    clean_query = remove_sql_comments(query).upper()

    # Check for dangerous commands
    for cmd in dangerous_commands:
        if re.search(r'\b' + cmd + r'\b', clean_query):
            return True

    return False


def execute_sql_query_enhanced(db_path, query):
    """
    Enhanced SQL query execution for SQLite that handles complex queries, CTEs,
    multiple statements, and multiple result sets.
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()

        # Clean the query - remove comments and whitespace
        clean_query = remove_sql_comments(query).strip()

        # Check if query is empty after cleaning
        if not clean_query:
            conn.close()
            return {
                'success': False,
                'error': 'Query is empty or contains only comments'
            }

        # Split query into individual statements
        statements = _split_sql_statements_sqlite(clean_query)

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
                is_select = _is_select_statement_sqlite(statement)

                if is_select:
                    # Handle SELECT statements and other statements that return results
                    rows = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []

                    # Convert rows to list of dictionaries
                    results = []
                    for row in rows:
                        results.append(dict(row))

                    all_results.append({
                        'statement_index': i,
                        'statement': statement,
                        'type': 'SELECT',
                        'results': results,
                        'columns': columns,
                        'row_count': len(results)
                    })
                else:
                    # Handle INSERT, UPDATE, DELETE, etc.
                    conn.commit()
                    changes = cursor.rowcount
                    total_changes += changes

                    # Get last insert ID for INSERT statements
                    if cursor.lastrowid:
                        last_insert_id = cursor.lastrowid

                    all_results.append({
                        'statement_index': i,
                        'statement': statement,
                        'type': 'MODIFICATION',
                        'changes': changes,
                        'message': f'Query executed successfully. {changes} row(s) affected.'
                    })

            except Exception as stmt_error:
                # If one statement fails, return error for that specific statement
                conn.close()
                return {
                    'success': False,
                    'error': f'Error in statement {i + 1}: {str(stmt_error)}',
                    'statement': statement
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
                    'row_count': result['row_count']
                }
            else:
                return {
                    'success': True,
                    'changes': result['changes'],
                    'last_id': last_insert_id,
                    'message': result['message']
                }
        else:
            # Multiple statements - return comprehensive format
            select_results = [r for r in all_results if r['type'] == 'SELECT']
            modification_results = [r for r in all_results if r['type'] == 'MODIFICATION']

            response = {
                'success': True,
                'multiple_statements': True,
                'total_statements': len(statements)
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
            'error': f'SQLite Error: {str(e)}'
        }


def execute_sql_query(db_path, query):
    """
    Legacy SQL query execution function - now uses enhanced execution.
    Maintained for backward compatibility.
    """
    return execute_sql_query_enhanced(db_path, query)


def _split_sql_statements_sqlite(query):
    """
    Split SQL query into individual statements for SQLite, handling complex cases.
    """
    # Remove comments first
    clean_query = remove_sql_comments(query)

    # Simple approach: split by semicolon, but be smart about it
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


def _is_select_statement_sqlite(statement):
    """
    Determine if a SQL statement returns results for SQLite.
    """
    statement_upper = statement.upper().strip()

    # Statements that return results in SQLite
    result_returning_keywords = [
        'SELECT', 'WITH', 'PRAGMA', 'EXPLAIN'
    ]

    for keyword in result_returning_keywords:
        if statement_upper.startswith(keyword):
            return True

    return False


def initialize_user_database(db_path):
    """
    Initialize user's database with sample tables and data.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create sample tables
        sample_schema = """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            age INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Products table
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price DECIMAL(10, 2),
            category TEXT,
            in_stock BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Orders table
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER DEFAULT 1,
            order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        );

        -- Insert sample data
        INSERT OR IGNORE INTO users (username, email, first_name, last_name, age) VALUES
        ('john_doe', 'john@example.com', 'John', 'Doe', 28),
        ('jane_smith', 'jane@example.com', 'Jane', 'Smith', 32),
        ('bob_wilson', 'bob@example.com', 'Bob', 'Wilson', 25),
        ('alice_brown', 'alice@example.com', 'Alice', 'Brown', 29),
        ('charlie_davis', 'charlie@example.com', 'Charlie', 'Davis', 35);

        INSERT OR IGNORE INTO products (name, price, category) VALUES
        ('Laptop', 999.99, 'Electronics'),
        ('Mouse', 29.99, 'Electronics'),
        ('Keyboard', 79.99, 'Electronics'),
        ('Monitor', 299.99, 'Electronics'),
        ('Desk Chair', 199.99, 'Furniture'),
        ('Coffee Mug', 12.99, 'Kitchen'),
        ('Notebook', 5.99, 'Office'),
        ('Pen Set', 15.99, 'Office');

        INSERT OR IGNORE INTO orders (user_id, product_id, quantity) VALUES
        (1, 1, 1),
        (1, 2, 2),
        (2, 3, 1),
        (2, 4, 1),
        (3, 5, 1),
        (4, 6, 3),
        (4, 7, 5),
        (5, 8, 2);
        """

        cursor.executescript(sample_schema)
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error initializing database: {e}")
        if 'conn' in locals():
            conn.close()


@login_required
@require_http_methods(["POST"])
def export_results(request, format):
    """
    Export query results in specified format (csv, json).
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()

        if not query:
            return JsonResponse({
                'success': False,
                'error': 'Query is required'
            })

        # Security check
        if is_dangerous_query(query):
            return JsonResponse({
                'success': False,
                'error': 'This query contains commands that are not allowed'
            })

        # Get user database
        user_db = UserDatabase.objects.get(user=request.user)
        db_path = user_db.full_path

        if not os.path.exists(db_path):
            return JsonResponse({
                'success': False,
                'error': 'Database not found'
            })

        # Execute query
        result = execute_sql_query(db_path, query)

        if not result['success']:
            return JsonResponse({
                'success': False,
                'error': result['error']
            })

        results = result.get('results', [])

        if not results:
            return JsonResponse({
                'success': False,
                'error': 'No data to export'
            })

        # Generate filename
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

        if format.lower() == 'csv':
            # Export as CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="query_results_{timestamp}.csv"'
            return response

        elif format.lower() == 'json':
            # Export as JSON
            json_data = json.dumps(results, indent=2, default=str)

            response = HttpResponse(json_data, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="query_results_{timestamp}.json"'
            return response

        else:
            return JsonResponse({
                'success': False,
                'error': 'Unsupported export format. Use csv or json.'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
