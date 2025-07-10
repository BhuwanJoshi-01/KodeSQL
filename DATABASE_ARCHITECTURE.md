# SQL Playground Database Architecture

## Overview

The SQL Playground application uses a multi-database architecture designed for scalability, security, and optimal performance. This document outlines the complete database configuration and architecture.

## Database Architecture

### 🗄️ Primary Database (PostgreSQL)
**Purpose**: Stores all Django models and website data
- **Database**: `sqlplayground_main`
- **Engine**: PostgreSQL
- **Contains**: Users, challenges, progress, subscriptions, courses, tutorials, etc.
- **Usage**: All Django ORM operations

### 🐘 Query PostgreSQL Database
**Purpose**: SQL challenge execution for PostgreSQL engine
- **Database**: `sqlplayground_queries_pg`
- **Engine**: PostgreSQL
- **Contains**: Temporary tables and data for PostgreSQL challenge execution
- **Usage**: User SQL query execution when PostgreSQL engine is selected

### 🐬 Query MySQL Database
**Purpose**: SQL challenge execution for MySQL engine
- **Database**: `sqlplayground_queries_mysql`
- **Engine**: MySQL
- **Contains**: Temporary tables and data for MySQL challenge execution
- **Usage**: User SQL query execution when MySQL engine is selected

## Environment Variables

### Primary Database Configuration
```env
# Primary PostgreSQL Database (Website Data)
PRIMARY_DB_ENGINE=django.db.backends.postgresql
PRIMARY_DB_NAME=sqlplayground_main
PRIMARY_DB_HOST=localhost
PRIMARY_DB_PORT=5432
PRIMARY_DB_USER=postgres
PRIMARY_DB_PASSWORD=your_primary_db_password
```

### Query Execution Databases
```env
# Secondary PostgreSQL Database (Query Execution)
QUERY_POSTGRES_DB_NAME=sqlplayground_queries_pg
QUERY_POSTGRES_HOST=localhost
QUERY_POSTGRES_PORT=5432
QUERY_POSTGRES_USER=postgres
QUERY_POSTGRES_PASSWORD=your_query_postgres_password

# MySQL Database (Query Execution)
QUERY_MYSQL_DB_NAME=sqlplayground_queries_mysql
QUERY_MYSQL_HOST=localhost
QUERY_MYSQL_PORT=3306
QUERY_MYSQL_USER=root
QUERY_MYSQL_PASSWORD=your_query_mysql_password
```

## Database Router

The application uses a custom database router (`sqlplayground.routers.DatabaseRouter`) that:

- **Routes all Django models** to the primary PostgreSQL database
- **Prevents migrations** on query execution databases
- **Manages relationships** between objects in the same database
- **Provides utilities** for query execution database connections

## Key Features

### ✅ SQLite Completely Removed
- No SQLite references in database configuration
- All SQLite-specific code removed from challenge execution
- Clean PostgreSQL and MySQL-only architecture

### ✅ Hosting Service Ready
- Optimized for hosting services that provide PostgreSQL and MySQL
- No file-based database dependencies
- Scalable multi-database architecture

### ✅ Security & Isolation
- Website data isolated from query execution
- Temporary databases for challenge execution
- Proper connection management and cleanup

### ✅ Performance Optimized
- Connection pooling enabled
- Health checks configured
- Separate databases prevent query execution from affecting website performance

## Database Connections

### Django ORM Connections
```python
# Automatic routing via DatabaseRouter
from challenges.models import Challenge
challenge = Challenge.objects.get(id=1)  # Uses primary PostgreSQL
```

### Query Execution Connections
```python
# Via QueryExecutionRouter utility
from sqlplayground.routers import QueryExecutionRouter

# Get MySQL connection config
mysql_config = QueryExecutionRouter.get_database_config('mysql')

# Get PostgreSQL connection params
pg_params = QueryExecutionRouter.get_connection_params('postgresql')
```

## Deployment Instructions

### 1. Database Setup
Create the following databases on your hosting service:
- `sqlplayground_main` (PostgreSQL)
- `sqlplayground_queries_pg` (PostgreSQL)
- `sqlplayground_queries_mysql` (MySQL)

### 2. Environment Configuration
Update your `.env` file with the actual database credentials from your hosting service.

### 3. Run Migrations
```bash
python manage.py migrate
```
This will create all Django tables in the primary PostgreSQL database.

### 4. Verify Configuration
The system will automatically handle:
- Database routing
- Query execution database connections
- Temporary table management for challenges

## Benefits

### 🚀 Scalability
- Separate databases for different purposes
- Query execution doesn't impact website performance
- Easy to scale individual database components

### 🔒 Security
- Website data isolated from user query execution
- Temporary databases prevent data persistence issues
- Proper connection management

## Important Configuration Notes

### PostgreSQL vs MySQL Options
- **PostgreSQL**: Does NOT use `charset` option (causes connection errors)
- **MySQL**: Uses `charset: utf8mb4` option for proper Unicode support
- **Connection Options**: Properly configured for each database engine

### 🛠️ Maintainability
- Clean separation of concerns
- Well-documented database router
- Environment-based configuration

### 🌐 Hosting Service Compatibility
- Works with any hosting service providing PostgreSQL and MySQL
- No SQLite dependencies
- Standard database connection patterns

## Migration from Previous Architecture

The new architecture automatically handles:
- ✅ Removal of all SQLite references
- ✅ Migration to PostgreSQL primary database
- ✅ Setup of separate query execution databases
- ✅ Database routing configuration
- ✅ Updated challenge execution system

No manual data migration is required for challenges as they now use the new dual-dataset system with direct SQL definitions.

## Support

For any database configuration issues:
1. Verify environment variables are correctly set
2. Ensure all three databases exist on your hosting service
3. Check database user permissions
4. Review Django logs for connection errors

The architecture is designed to be robust and hosting-service agnostic, working with any provider that offers PostgreSQL and MySQL databases.
