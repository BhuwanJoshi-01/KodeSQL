@echo off
echo Setting up PostgreSQL databases for SQL Playground...
echo.
echo This script will create the following databases:
echo - sqlplayground_main (for Django models)
echo - sqlplayground_queries_pg (for PostgreSQL query execution)
echo.
echo You will be prompted for the PostgreSQL password.
echo According to your .env file, the password should be: forgex99
echo.
pause

echo Creating databases...
psql -U postgres -f setup_databases.sql

echo.
echo Database setup completed!
echo.
echo Next steps:
echo 1. Run migrations: python manage.py migrate
echo 2. Create superuser: python manage.py createsuperuser
echo 3. Start the server: python manage.py runserver 8007
echo.
pause
