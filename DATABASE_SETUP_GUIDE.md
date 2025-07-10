# PostgreSQL Database Setup Guide for SQL Playground

## Issue Analysis
Based on your `.env` file, I can see the potential issues with your PostgreSQL setup:

1. **Database Names Mismatch**: Your `.env` file has:
   - `PRIMARY_DB_NAME=postgres` (using default postgres database)
   - `QUERY_POSTGRES_DB_NAME=sqlplayground_queries_pg`

2. **Password**: Your password is set to `forgex99`

## Solution: Create Required Databases

### Method 1: Using the provided SQL script

1. **Open Command Prompt** and navigate to your project directory:
   ```cmd
   cd "d:\Freelnacing\Project_NamasteSQL\Django_Version"
   ```

2. **Run the database setup script**:
   ```cmd
   psql -U postgres -f setup_databases.sql
   ```
   When prompted for password, enter: `forgex99`

### Method 2: Manual Database Creation

1. **Connect to PostgreSQL**:
   ```cmd
   psql -U postgres
   ```
   Password: `forgex99`

2. **Create the databases**:
   ```sql
   -- Create main database for Django models
   CREATE DATABASE sqlplayground_main;
   
   -- Create query execution database for PostgreSQL challenges
   CREATE DATABASE sqlplayground_queries_pg;
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE sqlplayground_main TO postgres;
   GRANT ALL PRIVILEGES ON DATABASE sqlplayground_queries_pg TO postgres;
   
   -- Exit
   \q
   ```

### Method 3: Using Django Management Commands

If the databases exist but Django can't connect, try:

1. **Check database connection**:
   ```cmd
   python manage.py check --database=default
   ```

2. **Run migrations**:
   ```cmd
   python manage.py migrate
   ```

3. **Create superuser**:
   ```cmd
   python manage.py createsuperuser
   ```

## Update .env File (Recommended)

I recommend updating your `.env` file to use the dedicated database:

```env
# Change this line:
PRIMARY_DB_NAME=postgres

# To this:
PRIMARY_DB_NAME=sqlplayground_main
```

## Troubleshooting

### If PostgreSQL service is not running:
1. **Windows**: Start PostgreSQL service from Services.msc
2. **Or via command line**:
   ```cmd
   net start postgresql-x64-17
   ```

### If you get "database does not exist" error:
1. The databases haven't been created yet
2. Run the setup script above
3. Make sure PostgreSQL is running

### If you get "authentication failed" error:
1. Check your password in the `.env` file
2. Make sure the postgres user exists
3. Try connecting manually: `psql -U postgres`

### If you get "connection refused" error:
1. PostgreSQL service is not running
2. Check if PostgreSQL is listening on port 5432
3. Check firewall settings

## Testing the Setup

After creating the databases, test the connection:

```cmd
# Test Django connection
python manage.py check

# Test database-specific connection
python manage.py check --database=default
python manage.py check --database=query_postgres

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver 8007
```

## MySQL Database (Optional)

If you also need MySQL for the project, you'll need to:

1. **Install MySQL** (if not already installed)
2. **Update the password** in `.env` file:
   ```env
   QUERY_MYSQL_PASSWORD=your_actual_mysql_password
   ```
3. **Create the MySQL database**:
   ```sql
   CREATE DATABASE sqlplayground_queries_mysql;
   ```

## Summary

The main issue is likely that the required databases don't exist. Run the provided SQL script or create them manually using the commands above. After that, your Django application should be able to connect to PostgreSQL successfully.
