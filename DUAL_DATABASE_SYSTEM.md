# Dual-Database SQL Challenge System

## Overview

The SQL Challenge system now supports dual-database execution with PostgreSQL and MySQL engines. Users can select their preferred database engine in the challenge editor and execute SQL queries against isolated datasets.

## System Architecture

### Database Configuration

1. **Primary PostgreSQL Database** (`default`)
   - Stores Django models (users, challenges, progress, subscriptions)
   - Host: localhost:5432
   - Database: postgres
   - User: postgres
   - Password: forgex99

2. **Query PostgreSQL Database** (`query_postgres`)
   - Executes SQL challenges for PostgreSQL engine
   - Host: localhost:5432
   - Database: sqlplayground_queries_pg
   - User: postgres
   - Password: forgex99

3. **Query MySQL Database** (`query_mysql`) - Optional
   - Executes SQL challenges for MySQL engine
   - Host: localhost:3306
   - Database: sqlplayground_queries_mysql
   - User: root
   - Password: forgex99

### Dual-Dataset System

Each challenge includes:

- **Schema SQL**: CREATE TABLE statements defining the database structure
- **Run Dataset**: Test data (flag_id=1) - visible to users during testing
- **Submit Dataset**: Validation data (flag_id=2) - used for final submission validation
- **Reference Query**: The correct SQL solution

## Features

### ✅ Implemented Features

1. **Database Engine Selection**
   - Users can choose between PostgreSQL and MySQL in the challenge editor
   - Engine selector dropdown in the challenge solve interface

2. **Automatic SQL Conversion**
   - MySQL syntax automatically converted to PostgreSQL when needed
   - Handles AUTO_INCREMENT → SERIAL, data type conversions, etc.

3. **Isolated Challenge Execution**
   - Each challenge runs in a temporary database
   - Automatic cleanup after query execution
   - No interference between different users or challenges

4. **Dual-Dataset Validation**
   - Test mode: Users can run queries against test dataset
   - Submit mode: Final validation against hidden submit dataset
   - Automatic flag_id filtering ensures proper dataset separation

5. **Comprehensive Challenge Library**
   - 20 SQL challenges covering various difficulty levels
   - 6 free challenges, 14 premium challenges
   - Topics: Basic SELECT, filtering, aggregation, joins, subqueries, etc.

### 🔧 Technical Implementation

1. **Challenge Model Enhancements**
   - `schema_sql`: Database schema definition
   - `run_dataset_sql`: Test data with flag_id=1
   - `submit_dataset_sql`: Validation data with flag_id=2
   - `supported_engines`: List of supported database engines

2. **Query Processing Pipeline**
   - Schema processing: Adds unique table names and flag_id columns
   - Dataset processing: Adds flag_id values to INSERT statements
   - Query processing: Adds flag_id filters and updates table names
   - SQL conversion: Converts MySQL syntax to PostgreSQL when needed

3. **Database Execution**
   - Temporary database creation for each query
   - Schema and dataset setup
   - Query execution with proper error handling
   - Automatic cleanup

## Usage

### For Users

1. **Access Challenges**
   - Navigate to the challenges page
   - Select a challenge to solve
   - Free challenges are accessible to all authenticated users
   - Premium challenges require an active subscription

2. **Solve Challenges**
   - Choose database engine (PostgreSQL/MySQL) from dropdown
   - Write SQL query in the Monaco editor
   - Click "Run Code" to test against test dataset
   - Click "Submit Solution" for final validation

3. **View Results**
   - Query results displayed in tabular format
   - Execution time and row count shown
   - Error messages for debugging

### For Administrators

1. **Create Challenges**
   - Use Django admin interface
   - Fill in schema_sql, run_dataset_sql, submit_dataset_sql
   - Set supported engines (PostgreSQL, MySQL)
   - Define reference query for validation

2. **Manage Challenges**
   - Edit existing challenges
   - Set difficulty levels and subscription requirements
   - Monitor challenge completion statistics

## Database Schema Example

```sql
-- Schema SQL
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL
);

-- Run Dataset SQL (Test Data)
INSERT INTO employees (name, department, salary, hire_date) VALUES
('John Doe', 'Engineering', 75000.00, '2022-01-15'),
('Jane Smith', 'Marketing', 65000.00, '2022-02-20'),
('Bob Johnson', 'Engineering', 80000.00, '2021-12-10'),
('Alice Brown', 'HR', 60000.00, '2022-03-05');

-- Submit Dataset SQL (Validation Data)
INSERT INTO employees (name, department, salary, hire_date) VALUES
('Mike Wilson', 'Engineering', 78000.00, '2022-01-20'),
('Sarah Davis', 'Marketing', 67000.00, '2022-02-25'),
('Tom Anderson', 'Engineering', 82000.00, '2021-11-15'),
('Lisa Garcia', 'HR', 62000.00, '2022-03-10'),
('David Miller', 'Sales', 72000.00, '2022-01-30');

-- Reference Query
SELECT * FROM employees WHERE salary > 70000;
```

## Configuration

### Environment Variables (.env)

```bash
# Primary Database (PostgreSQL)
PRIMARY_DB_ENGINE=django.db.backends.postgresql
PRIMARY_DB_NAME=postgres
PRIMARY_DB_HOST=localhost
PRIMARY_DB_PORT=5432
PRIMARY_DB_USER=postgres
PRIMARY_DB_PASSWORD=forgex99

# Query Execution Databases
QUERY_POSTGRES_DB_NAME=sqlplayground_queries_pg
QUERY_POSTGRES_HOST=localhost
QUERY_POSTGRES_PORT=5432
QUERY_POSTGRES_USER=postgres
QUERY_POSTGRES_PASSWORD=forgex99

QUERY_MYSQL_DB_NAME=sqlplayground_queries_mysql
QUERY_MYSQL_HOST=localhost
QUERY_MYSQL_PORT=3306
QUERY_MYSQL_USER=root
QUERY_MYSQL_PASSWORD=forgex99
```

## Testing

Run the comprehensive test suite:

```bash
python test_dual_database_system.py
```

This tests:
- Database connections
- Challenge data integrity
- SQL execution on different engines
- Dual-dataset functionality
- Challenge editor compatibility

## Current Status

✅ **PostgreSQL**: Fully implemented and tested
⚠️ **MySQL**: Configured but requires MySQL server installation

## Next Steps

1. **MySQL Setup**: Install and configure MySQL server for complete dual-database support
2. **Performance Optimization**: Implement connection pooling and query caching
3. **Advanced Features**: Add support for stored procedures, views, and complex schemas
4. **Monitoring**: Add logging and metrics for query execution performance

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify database servers are running
   - Check connection credentials in .env file
   - Ensure databases exist

2. **SQL Syntax Errors**
   - Check MySQL to PostgreSQL conversion
   - Verify schema SQL is valid
   - Ensure flag_id column is properly added

3. **Challenge Not Loading**
   - Verify challenge has complete dual-dataset structure
   - Check supported_engines field
   - Ensure user has proper access permissions
