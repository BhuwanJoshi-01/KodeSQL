"""
Database Router for SQL Playground

This router directs database operations to the appropriate database:
- Primary PostgreSQL: All Django models (users, challenges, progress, etc.)
- Query PostgreSQL: SQL challenge execution for PostgreSQL engine
- Query MySQL: SQL challenge execution for MySQL engine
"""


class DatabaseRouter:
    """
    A router to control all database operations on models for different
    databases in the SQL Playground application.
    """

    def db_for_read(self, model, **hints):
        """Suggest the database to read from."""
        # All Django models use the default (primary) database
        return 'default'

    def db_for_write(self, model, **hints):
        """Suggest the database to write to."""
        # All Django models use the default (primary) database
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same app."""
        # Allow relations between objects in the default database
        db_set = {'default'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain apps' models get created on the right database."""
        # Only allow migrations on the default (primary) database
        # Query databases (query_postgres, query_mysql) are managed separately
        # for SQL challenge execution and don't need Django migrations
        if db == 'default':
            return True
        elif db in ['query_postgres', 'query_mysql']:
            # Don't run Django migrations on query execution databases
            return False
        return None


class QueryExecutionRouter:
    """
    Utility class for managing query execution database connections.
    This is used by the challenge execution system to connect to the
    appropriate database for running user SQL queries.
    """

    @staticmethod
    def get_database_config(engine):
        """
        Get database configuration for the specified engine.
        
        Args:
            engine (str): Database engine ('mysql' or 'postgresql')
            
        Returns:
            dict: Database configuration dictionary
        """
        from django.conf import settings
        
        if engine.lower() == 'mysql':
            return {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': settings.MYSQL_DB,
                'HOST': settings.MYSQL_HOST,
                'PORT': settings.MYSQL_PORT,
                'USER': settings.MYSQL_USER,
                'PASSWORD': settings.MYSQL_PASSWORD,
                'OPTIONS': {
                    'charset': 'utf8mb4',
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                },
            }
        elif engine.lower() == 'postgresql':
            return {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': settings.POSTGRESQL_DB,
                'HOST': settings.POSTGRESQL_HOST,
                'PORT': settings.POSTGRESQL_PORT,
                'USER': settings.POSTGRESQL_USER,
                'PASSWORD': settings.POSTGRESQL_PASSWORD,
                'OPTIONS': {},
            }
        else:
            raise ValueError(f"Unsupported database engine: {engine}")

    @staticmethod
    def get_connection_params(engine):
        """
        Get connection parameters for direct database connections.
        Used by challenge execution utilities that need raw database connections.
        
        Args:
            engine (str): Database engine ('mysql' or 'postgresql')
            
        Returns:
            dict: Connection parameters for the database driver
        """
        from django.conf import settings
        
        if engine.lower() == 'mysql':
            return {
                'host': settings.MYSQL_HOST,
                'port': settings.MYSQL_PORT,
                'user': settings.MYSQL_USER,
                'password': settings.MYSQL_PASSWORD,
                'database': settings.MYSQL_DB,
                'charset': 'utf8mb4',
            }
        elif engine.lower() == 'postgresql':
            return {
                'host': settings.POSTGRESQL_HOST,
                'port': settings.POSTGRESQL_PORT,
                'user': settings.POSTGRESQL_USER,
                'password': settings.POSTGRESQL_PASSWORD,
                'database': settings.POSTGRESQL_DB,
            }
        else:
            raise ValueError(f"Unsupported database engine: {engine}")
