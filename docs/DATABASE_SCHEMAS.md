# Database Schema Configuration

## Overview

The SQL challenge system now uses a **simplified database configuration** approach where all database schemas are predefined in `settings.py` instead of being configured individually for each challenge.

## Benefits of the Simplified System

✅ **No Complex Configuration**: No more JSON editors or complex database setup per challenge  
✅ **Consistency**: All challenges using the same schema type have identical database structure  
✅ **Multi-Engine Support**: Each schema automatically works with SQLite, PostgreSQL, and MySQL  
✅ **Easy Maintenance**: Add new schemas in one place (settings.py) for all challenges  
✅ **Sample Data Included**: Each schema comes with realistic sample data  

## Available Database Schemas

### 1. Employee Database (`employees`)
- **Tables**: `employees`
- **Use Case**: Basic SQL queries, filtering, aggregation
- **Sample Data**: 5 employees with departments and salaries

### 2. E-commerce Database (`ecommerce`) 
- **Tables**: `orders`, `returns`
- **Use Case**: Business analytics, joins, date operations
- **Sample Data**: Customer orders and return records

### 3. Student Database (`students`)
- **Tables**: `students`, `courses`, `enrollments`
- **Use Case**: Academic queries, complex joins, grade analysis
- **Sample Data**: Students enrolled in various courses with grades

### 4. Custom Schema (`custom`)
- **Use Case**: Advanced challenges requiring unique database structures
- **Configuration**: Define custom SQL and schema in the challenge form

## How to Use

### For Admins Creating Challenges

1. Go to Django Admin → Challenges → Add Challenge
2. In the "Database Configuration" section, select a schema type from the dropdown
3. The database will automatically be set up with the predefined structure and sample data
4. For custom schemas, additional fields will appear to define your own SQL

### For Developers Adding New Schemas

1. Edit `sqlplayground/settings.py`
2. Add your schema to the `CHALLENGE_DATABASE_SCHEMAS` dictionary
3. Include schema definition and initialization SQL for all supported engines
4. Update `Challenge.DATABASE_SCHEMA_CHOICES` in `challenges/models.py`

## Configuration Location

All database schemas are configured in:
```
sqlplayground/settings.py
→ CHALLENGE_DATABASE_SCHEMAS
```

## Management Commands

- `python manage.py show_database_schemas` - View current schema configuration
- `python manage.py migrate_to_simplified_schemas` - Migrate existing challenges

## Migration from Old System

The old complex system with individual JSON configurations has been replaced. Existing challenges have been automatically migrated to use the appropriate predefined schemas based on their content.
