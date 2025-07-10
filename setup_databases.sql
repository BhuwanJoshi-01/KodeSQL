-- PostgreSQL Database Setup for SQL Playground
-- This script creates the necessary databases for the Django SQL Playground project

-- Connect to PostgreSQL as postgres user
-- Run this with: psql -U postgres -f setup_databases.sql

-- Create main database for Django models
CREATE DATABASE sqlplayground_main;

-- Create query execution database for PostgreSQL challenges
CREATE DATABASE sqlplayground_queries_pg;

-- Grant privileges to postgres user (adjust username if needed)
GRANT ALL PRIVILEGES ON DATABASE sqlplayground_main TO postgres;
GRANT ALL PRIVILEGES ON DATABASE sqlplayground_queries_pg TO postgres;

-- Connect to the main database and create any additional extensions if needed
\c sqlplayground_main;

-- Create any required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Connect to the query database and set it up
\c sqlplayground_queries_pg;

-- Create any required extensions for query execution
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\echo 'Database setup completed successfully!'
\echo 'Created databases:'
\echo '  - sqlplayground_main (for Django models)'
\echo '  - sqlplayground_queries_pg (for PostgreSQL query execution)'
