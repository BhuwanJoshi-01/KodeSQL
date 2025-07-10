from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from django.contrib.auth import get_user_model
import json
import re
import sqlparse
from .models import Challenge, UserChallengeSubscription, ChallengeSubscriptionPlan

User = get_user_model()


class SQLValidationError(Exception):
    """Custom exception for SQL validation errors"""
    pass


def validate_sql_syntax(sql_text, statement_type="SQL"):
    """
    Enhanced SQL syntax validation using sqlparse library.
    Returns (is_valid, error_message)
    """
    if not sql_text or not sql_text.strip():
        return True, ""  # Empty SQL is allowed for optional fields

    try:
        # Parse the SQL
        parsed = sqlparse.parse(sql_text)

        if not parsed:
            return False, f"{statement_type} appears to be empty or invalid"

        # Check for basic syntax issues
        for statement in parsed:
            if not statement.tokens:
                continue

            # Convert to string and check for common issues
            sql_str = str(statement).strip()

            # Check for missing semicolon at the end (if multiple statements)
            if len(parsed) > 1 and not sql_str.endswith(';'):
                return False, f"{statement_type} statements should end with semicolon when multiple statements are present"

            # Check for obvious syntax errors (unmatched parentheses)
            if sql_str.count('(') != sql_str.count(')'):
                return False, f"{statement_type} has unmatched parentheses"

            # Enhanced validation for CREATE TABLE statements
            if statement_type == "Schema SQL" and sql_str.upper().startswith('CREATE TABLE'):
                schema_validation = _validate_schema_requirements(sql_str)
                if not schema_validation['valid']:
                    return False, schema_validation['error']

        return True, ""

    except Exception as e:
        return False, f"{statement_type} syntax error: {str(e)}"


def _validate_schema_requirements(create_table_sql):
    """
    Validate schema requirements like proper data types, etc.
    Primary key is optional - if needed, it can be added manually.
    Returns dict with 'valid' boolean and 'error' message.
    """
    try:
        sql_upper = create_table_sql.upper()

        # Primary key is now optional - removed mandatory check
        # Users can add PRIMARY KEY if needed for their specific challenge

        # Check for proper column definitions
        paren_start = create_table_sql.find('(')
        paren_end = create_table_sql.rfind(')')

        if paren_start == -1 or paren_end == -1:
            return {
                'valid': False,
                'error': "CREATE TABLE statement has malformed column definitions"
            }

        columns_section = create_table_sql[paren_start + 1:paren_end]

        # Check if we have at least one column
        column_definitions = _split_column_definitions(columns_section)
        actual_columns = [definition for definition in column_definitions
                         if definition.strip() and not definition.strip().upper().startswith(('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK', 'CONSTRAINT', 'KEY ', 'INDEX '))]

        if len(actual_columns) == 0:
            return {
                'valid': False,
                'error': "CREATE TABLE statement must define at least one column"
            }

        # Check for proper data types
        for col_def in actual_columns:
            if not _has_valid_data_type(col_def):
                return {
                    'valid': False,
                    'error': f"Column definition '{col_def.strip()}' appears to be missing a valid data type"
                }

        return {'valid': True, 'error': ''}

    except Exception as e:
        return {'valid': False, 'error': f"Error validating schema requirements: {str(e)}"}


def _has_valid_data_type(column_definition):
    """Check if column definition has a valid data type"""
    # Common SQL data types
    data_types = [
        'INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT',
        'VARCHAR', 'CHAR', 'TEXT', 'LONGTEXT', 'MEDIUMTEXT',
        'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL',
        'DATE', 'TIME', 'DATETIME', 'TIMESTAMP', 'YEAR',
        'BOOLEAN', 'BOOL', 'BIT',
        'BLOB', 'LONGBLOB', 'MEDIUMBLOB', 'TINYBLOB',
        'JSON', 'ENUM', 'SET'
    ]

    col_upper = column_definition.upper()
    return any(data_type in col_upper for data_type in data_types)


def extract_table_info_from_schema(schema_sql):
    """
    Extract table information from CREATE TABLE statements.
    Returns dict with table_name -> {columns: [...], constraints: [...]}
    """
    if not schema_sql or not schema_sql.strip():
        return {}

    tables_info = {}

    try:
        parsed = sqlparse.parse(schema_sql)

        for statement in parsed:
            sql_str = str(statement).strip().upper()

            if sql_str.startswith('CREATE TABLE'):
                # Extract table name and column info
                table_info = _parse_create_table_statement(str(statement))
                if table_info:
                    tables_info[table_info['name']] = table_info

    except Exception as e:
        raise SQLValidationError(f"Error parsing schema: {str(e)}")

    return tables_info


def _parse_create_table_statement(create_statement):
    """Parse a single CREATE TABLE statement to extract detailed table info"""
    try:
        # Extract table name
        table_match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\(',
                               create_statement, re.IGNORECASE)
        if not table_match:
            return None

        table_name = table_match.group(1)

        # Extract column definitions
        paren_start = create_statement.find('(')
        paren_end = create_statement.rfind(')')

        if paren_start == -1 or paren_end == -1:
            return None

        columns_section = create_statement[paren_start + 1:paren_end]

        # Enhanced parsing for columns and constraints
        columns = []
        constraints = []
        has_primary_key = False
        not_null_columns = []

        # Split by comma but handle nested parentheses
        column_definitions = _split_column_definitions(columns_section)

        for definition in column_definitions:
            definition = definition.strip()
            if not definition:
                continue

            definition_upper = definition.upper()

            # Check for table-level constraints
            if definition_upper.startswith(('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK', 'CONSTRAINT')):
                constraints.append(definition)
                if 'PRIMARY KEY' in definition_upper:
                    has_primary_key = True
            elif not definition_upper.startswith(('KEY ', 'INDEX ')):
                # Parse column definition
                column_info = _parse_column_definition(definition)
                if column_info:
                    columns.append(column_info)
                    if column_info.get('is_primary_key'):
                        has_primary_key = True
                    if column_info.get('not_null'):
                        not_null_columns.append(column_info['name'])

        return {
            'name': table_name,
            'columns': columns,
            'constraints': constraints,
            'has_primary_key': has_primary_key,
            'not_null_columns': not_null_columns,
            'column_names': [col['name'] if isinstance(col, dict) else col for col in columns]
        }

    except Exception:
        return None


def _split_column_definitions(columns_section):
    """Split column definitions by comma, handling nested parentheses"""
    definitions = []
    current_def = ""
    paren_count = 0

    for char in columns_section:
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
        elif char == ',' and paren_count == 0:
            definitions.append(current_def.strip())
            current_def = ""
            continue

        current_def += char

    if current_def.strip():
        definitions.append(current_def.strip())

    return definitions


def _parse_column_definition(definition):
    """Parse a single column definition to extract detailed info"""
    try:
        parts = definition.split()
        if not parts:
            return None

        column_name = parts[0].strip('`"')
        definition_upper = definition.upper()

        # Extract column properties
        column_info = {
            'name': column_name,
            'is_primary_key': 'PRIMARY KEY' in definition_upper,
            'not_null': 'NOT NULL' in definition_upper,
            'auto_increment': 'AUTO_INCREMENT' in definition_upper or 'AUTOINCREMENT' in definition_upper,
            'has_default': 'DEFAULT' in definition_upper,
            'data_type': _extract_data_type(definition)
        }

        return column_info

    except Exception:
        return {'name': parts[0].strip('`"') if parts else 'unknown'}


def _extract_data_type(definition):
    """Extract data type from column definition"""
    # Simple data type extraction
    type_match = re.search(r'\b(INT|INTEGER|VARCHAR|CHAR|TEXT|DECIMAL|FLOAT|DOUBLE|DATE|DATETIME|TIMESTAMP|BOOLEAN|BOOL)\b',
                          definition.upper())
    return type_match.group(1) if type_match else 'UNKNOWN'


def validate_insert_statements_against_schema(insert_sql, tables_info):
    """
    Enhanced validation of INSERT statements against table schema.
    Returns (is_valid, error_message)
    """
    if not insert_sql or not insert_sql.strip():
        return True, ""  # Empty INSERT SQL is allowed

    if not tables_info:
        return False, "No table schema found to validate against"

    try:
        parsed = sqlparse.parse(insert_sql)

        for statement in parsed:
            sql_str = str(statement).strip()
            sql_upper = sql_str.upper()

            if sql_upper.startswith('INSERT'):
                # Extract table name from INSERT statement
                table_match = re.search(r'INSERT\s+INTO\s+`?(\w+)`?', sql_str, re.IGNORECASE)
                if table_match:
                    table_name = table_match.group(1)

                    # Check if table exists in schema
                    if table_name not in tables_info:
                        return False, f"Table '{table_name}' in INSERT statement not found in schema"

                    # Enhanced validation - comprehensive checks
                    validation_result = _validate_insert_statement_details(sql_str, table_name, tables_info[table_name])
                    if not validation_result['valid']:
                        return False, validation_result['error']

        return True, ""

    except Exception as e:
        return False, f"Error validating INSERT statements: {str(e)}"


def _validate_insert_statement_details(insert_statement, table_name, table_info):
    """
    Enhanced detailed validation of a single INSERT statement.
    Returns dict with 'valid' boolean and 'error' message.
    """
    try:
        sql_upper = insert_statement.upper()

        # Check for column list in INSERT
        columns_match = re.search(r'INSERT\s+INTO\s+`?\w+`?\s*\(([^)]+)\)',
                                insert_statement, re.IGNORECASE)

        if columns_match:
            # INSERT with explicit column list
            insert_columns = [col.strip().strip('`').strip('"') for col in columns_match.group(1).split(',')]
            schema_column_names = table_info.get('column_names', [])
            not_null_columns = table_info.get('not_null_columns', [])

            # Check if all INSERT columns exist in schema
            for col in insert_columns:
                if col.upper() not in [sc.upper() for sc in schema_column_names]:
                    return {
                        'valid': False,
                        'error': f"Column '{col}' in INSERT statement not found in table '{table_name}' schema"
                    }

            # Check for missing NOT NULL columns (excluding auto-increment primary keys and flag_id)
            missing_not_null = []
            for col_info in table_info.get('columns', []):
                if isinstance(col_info, dict):
                    col_name = col_info['name']
                    is_not_null = col_info.get('not_null', False)
                    is_auto_increment = col_info.get('auto_increment', False)

                    # Skip flag_id column as it's automatically handled by the system
                    if col_name.lower() == 'flag_id':
                        continue

                    if is_not_null and not is_auto_increment:
                        # Check if this NOT NULL column is included in INSERT
                        if col_name.upper() not in [ic.upper() for ic in insert_columns]:
                            missing_not_null.append(col_name)

            if missing_not_null:
                return {
                    'valid': False,
                    'error': f"INSERT statement missing required NOT NULL columns: {', '.join(missing_not_null)}"
                }

            # Additional check: warn about missing non-auto-increment columns (best practice)
            all_non_auto_columns = []
            for col_info in table_info.get('columns', []):
                if isinstance(col_info, dict):
                    col_name = col_info['name']
                    # Skip flag_id column as it's automatically handled by the system
                    if col_name.lower() == 'flag_id':
                        continue
                    if not col_info.get('auto_increment', False):
                        all_non_auto_columns.append(col_name)

            missing_columns = []
            for col_name in all_non_auto_columns:
                if col_name.upper() not in [ic.upper() for ic in insert_columns]:
                    missing_columns.append(col_name)

            # For data integrity, suggest including all columns (especially for challenge datasets)
            if missing_columns:
                return {
                    'valid': False,
                    'error': f"INSERT statement missing columns: {', '.join(missing_columns)}. For challenge datasets, it's recommended to include all table columns for data completeness."
                }



            # Validate VALUES section structure
            values_validation = _validate_values_section(insert_statement, table_name, len(insert_columns))
            if not values_validation['valid']:
                return values_validation

            # Validate data content against column constraints
            data_validation = _validate_insert_data_content(insert_statement, table_name, table_info, insert_columns)
            if not data_validation['valid']:
                return data_validation

        else:
            # INSERT without explicit column list - should include all non-auto-increment columns
            schema_column_names = table_info.get('column_names', [])
            required_columns = []

            for col_info in table_info.get('columns', []):
                if isinstance(col_info, dict):
                    col_name = col_info['name']
                    # Skip flag_id column as it's automatically handled by the system
                    if col_name.lower() == 'flag_id':
                        continue
                    if not col_info.get('auto_increment', False):
                        required_columns.append(col_name)
                else:
                    # Skip flag_id for simple column definitions too
                    if str(col_info).lower() != 'flag_id':
                        required_columns.append(col_info)

            # Validate VALUES section for implicit column list
            values_validation = _validate_values_section(insert_statement, table_name, len(required_columns))
            if not values_validation['valid']:
                return values_validation

        return {'valid': True, 'error': ''}

    except Exception as e:
        return {'valid': False, 'error': f"Error validating INSERT statement details: {str(e)}"}


def _validate_values_section(insert_statement, table_name, expected_column_count):
    """Enhanced validation of the VALUES section of an INSERT statement"""
    try:
        values_match = re.search(r'VALUES\s*(.+)', insert_statement, re.IGNORECASE | re.DOTALL)
        if not values_match:
            return {
                'valid': False,
                'error': f"INSERT statement for table '{table_name}' missing VALUES clause"
            }

        values_section = values_match.group(1).strip()

        if not values_section.startswith('('):
            return {
                'valid': False,
                'error': f"INSERT statement for table '{table_name}' has malformed VALUES clause"
            }

        # Count value groups and validate structure
        value_groups = _count_value_groups(values_section)

        if value_groups == 0:
            return {
                'valid': False,
                'error': f"INSERT statement for table '{table_name}' appears to have no value groups"
            }

        # Enhanced validation of value count and content per group
        value_group_matches = re.findall(r'\(([^)]+)\)', values_section)

        for i, group_content in enumerate(value_group_matches):
            group_values = [v.strip() for v in group_content.split(',')]

            # Check value count
            if len(group_values) != expected_column_count:
                return {
                    'valid': False,
                    'error': f"INSERT statement for table '{table_name}' row {i+1} has {len(group_values)} values but expected {expected_column_count} columns"
                }

            # Check for missing values (empty strings, just commas)
            for j, value in enumerate(group_values):
                if not value.strip():
                    return {
                        'valid': False,
                        'error': f"INSERT statement for table '{table_name}' row {i+1} column {j+1} is missing a value"
                    }

        return {'valid': True, 'error': ''}

    except Exception as e:
        return {'valid': False, 'error': f"Error validating VALUES section: {str(e)}"}


def _count_value_groups(values_section):
    """Count the number of value groups in VALUES clause"""
    count = 0
    paren_depth = 0
    i = 0

    while i < len(values_section):
        char = values_section[i]
        if char == '(':
            if paren_depth == 0:
                count += 1
            paren_depth += 1
        elif char == ')':
            paren_depth -= 1
        elif char == "'" or char == '"':
            # Skip quoted strings
            quote_char = char
            i += 1
            while i < len(values_section) and values_section[i] != quote_char:
                if values_section[i] == '\\':
                    i += 1  # Skip escaped character
                i += 1
        i += 1

    return count


def _validate_insert_data_content(insert_statement, table_name, table_info, insert_columns):
    """
    Validate the actual data content in INSERT statement against column constraints.
    Checks for NULL values in NOT NULL columns, missing values, etc.
    """
    try:
        # Extract column information
        columns_info = {col['name'].upper(): col for col in table_info.get('columns', []) if isinstance(col, dict)}

        # Extract VALUES section
        values_match = re.search(r'VALUES\s*(.+)', insert_statement, re.IGNORECASE | re.DOTALL)
        if not values_match:
            return {'valid': True, 'error': ''}  # Already validated in previous step

        values_section = values_match.group(1).strip()
        value_group_matches = re.findall(r'\(([^)]+)\)', values_section)

        for row_idx, group_content in enumerate(value_group_matches):
            group_values = [v.strip() for v in group_content.split(',')]

            # Validate each value against its column constraints
            for col_idx, value in enumerate(group_values):
                if col_idx >= len(insert_columns):
                    continue  # Skip if more values than columns (already caught earlier)

                column_name = insert_columns[col_idx].upper()
                column_info = columns_info.get(column_name, {})

                # Check for NULL values in NOT NULL columns
                if _is_null_value(value) and column_info.get('not_null', False):
                    return {
                        'valid': False,
                        'error': f"INSERT statement for table '{table_name}' row {row_idx + 1}: NULL value not allowed in NOT NULL column '{insert_columns[col_idx]}'"
                    }

                # Check for empty/missing values in required columns
                if _is_empty_value(value) and column_info.get('not_null', False):
                    return {
                        'valid': False,
                        'error': f"INSERT statement for table '{table_name}' row {row_idx + 1}: Empty value not allowed in NOT NULL column '{insert_columns[col_idx]}'"
                    }

                # Basic data type validation
                data_type_validation = _validate_data_type_compatibility(value, column_info.get('data_type', ''), insert_columns[col_idx])
                if not data_type_validation['valid']:
                    return {
                        'valid': False,
                        'error': f"INSERT statement for table '{table_name}' row {row_idx + 1}: {data_type_validation['error']}"
                    }

                # Additional data validation checks
                additional_checks = _validate_additional_data_constraints(value, column_info, insert_columns[col_idx], row_idx + 1)
                if not additional_checks['valid']:
                    return {
                        'valid': False,
                        'error': f"INSERT statement for table '{table_name}' {additional_checks['error']}"
                    }

        return {'valid': True, 'error': ''}

    except Exception as e:
        return {'valid': False, 'error': f"Error validating INSERT data content: {str(e)}"}


def _is_null_value(value):
    """Check if a value represents NULL"""
    value_upper = value.strip().upper()
    return value_upper == 'NULL'


def _is_empty_value(value):
    """Check if a value is empty, just whitespace, or empty quotes"""
    value_clean = value.strip()
    # Check for empty string, whitespace, or empty quotes
    return (not value_clean or
            value_clean == "''" or
            value_clean == '""' or
            value_clean == "'''" or
            value_clean == '"""')


def _validate_data_type_compatibility(value, data_type, column_name):
    """
    Enhanced validation of data type compatibility.
    Strictly validates that values match their expected data types.
    """
    try:
        if _is_null_value(value):
            return {'valid': True, 'error': ''}  # NULL handling is done separately

        value_stripped = value.strip()
        data_type_upper = data_type.upper()

        # Numeric types validation - strict checking
        if data_type_upper in ['INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT']:
            # Remove quotes if present (shouldn't be there for numbers)
            if value_stripped.startswith("'") and value_stripped.endswith("'"):
                return {
                    'valid': False,
                    'error': f"Integer value '{value}' in column '{column_name}' should not be quoted"
                }

            try:
                int(value_stripped)
            except ValueError:
                return {
                    'valid': False,
                    'error': f"Value '{value}' in column '{column_name}' is not a valid integer (expected: 123, got text)"
                }

        elif data_type_upper in ['DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE']:
            # Check if value is quoted (shouldn't be for numbers)
            if value_stripped.startswith("'") and value_stripped.endswith("'"):
                quoted_content = value_stripped[1:-1]  # Remove quotes

                # Check if quoted content is actually a text number
                quoted_lower = quoted_content.lower()
                text_number_words = ['thousand', 'million', 'billion', 'hundred', 'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']

                if any(word in quoted_lower for word in text_number_words):
                    return {
                        'valid': False,
                        'error': f"Value '{value}' in column '{column_name}' contains text numbers but should be numeric (e.g., use 80000.00 instead of 'eighty thousand')"
                    }

                # Try to parse the quoted content as number
                try:
                    float(quoted_content)
                    return {
                        'valid': False,
                        'error': f"Numeric value '{value}' in column '{column_name}' should not be quoted (use {quoted_content} instead of '{quoted_content}')"
                    }
                except ValueError:
                    return {
                        'valid': False,
                        'error': f"Value '{value}' in column '{column_name}' contains text but should be a number"
                    }

            # Try to parse unquoted value
            try:
                float(value_stripped)
            except ValueError:
                return {
                    'valid': False,
                    'error': f"Value '{value}' in column '{column_name}' is not a valid number (expected format: 123.45)"
                }

        # String types - check for proper quoting and validate content
        elif data_type_upper in ['VARCHAR', 'CHAR', 'TEXT']:
            if not _is_null_value(value):
                if not (value_stripped.startswith("'") and value_stripped.endswith("'")):
                    return {
                        'valid': False,
                        'error': f"String value '{value}' in column '{column_name}' should be quoted with single quotes"
                    }

                # Check string content for potential data type mismatches
                string_content = value_stripped[1:-1]  # Remove quotes

                # Check if string looks like a number but is in a string column
                try:
                    float(string_content)
                    # If it's a pure number in a string field, warn about potential type mismatch
                    if string_content.replace('.', '').replace('-', '').isdigit():
                        return {
                            'valid': False,
                            'error': f"Value '{value}' in column '{column_name}' appears to be a number but is in a text column. Consider using proper data types."
                        }
                except ValueError:
                    pass  # Good, it's actually text

        # Date/Time types
        elif data_type_upper in ['DATE', 'DATETIME', 'TIMESTAMP']:
            if not (value_stripped.startswith("'") and value_stripped.endswith("'")):
                return {
                    'valid': False,
                    'error': f"Date value '{value}' in column '{column_name}' should be quoted with single quotes"
                }

        # Boolean types
        elif data_type_upper in ['BOOLEAN', 'BOOL']:
            bool_values = ['TRUE', 'FALSE', '1', '0']
            if value_stripped.upper() not in bool_values:
                return {
                    'valid': False,
                    'error': f"Value '{value}' in column '{column_name}' is not a valid boolean (use TRUE, FALSE, 1, or 0)"
                }

        return {'valid': True, 'error': ''}

    except Exception as e:
        return {'valid': False, 'error': f"Error validating data type for column '{column_name}': {str(e)}"}


def validate_data_types_compatibility(insert_sql, tables_info):
    """
    Advanced validation to check data type compatibility.
    This is a simplified version - in production, you'd want more sophisticated type checking.
    Returns (is_valid, error_message)
    """
    if not insert_sql or not tables_info:
        return True, ""

    try:
        # Look for obvious data type mismatches
        sql_upper = insert_sql.upper()

        # Check for common issues like string values in numeric columns
        # This is a basic implementation - extend as needed

        # Look for potential NULL constraint violations
        if 'NULL' in sql_upper:
            # Check if NULLs are being inserted into NOT NULL columns
            # This would require more sophisticated parsing to be fully accurate
            pass

        # Check for potential foreign key issues
        # This would require understanding relationships between tables

        return True, ""

    except Exception as e:
        return False, f"Error validating data type compatibility: {str(e)}"


class ChallengeForm(forms.ModelForm):
    """
    Form for creating and editing challenges.
    """
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='clean'),
        help_text="Description of the challenge"
    )

    question = forms.CharField(
        widget=CKEditor5Widget(config_name='clean'),
        help_text="The challenge question with examples and context"
    )

    hint = forms.CharField(
        widget=CKEditor5Widget(config_name='clean'),
        required=False,
        help_text="Optional hint to help users solve the challenge"
    )

    # Tags as multiple choice field
    tags = forms.MultipleChoiceField(
        choices=Challenge.TAG_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'tag-checkbox-group'
        }),
        required=False,
        help_text="Select relevant tags that describe the SQL concepts used in this challenge"
    )
    
    # Enhanced dual-dataset solution fields
    schema_sql = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control sql-editor',
            'rows': 8,
            'placeholder': 'CREATE TABLE employees (\n    id INT AUTO_INCREMENT PRIMARY KEY,\n    name VARCHAR(100),\n    department VARCHAR(50),\n    salary DECIMAL(10,2)\n);'
        }),
        help_text="SQL schema definition (CREATE TABLE statements). Table names will be auto-prefixed with challenge ID."
    )

    run_dataset_sql = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control sql-editor',
            'rows': 6,
            'placeholder': 'INSERT INTO employees (name, department, salary) VALUES\n(\'Alice\', \'Engineering\', 75000),\n(\'Bob\', \'Marketing\', 65000);'
        }),
        help_text="INSERT statements for test/trial data. Users will see this data when testing their queries."
    )

    submit_dataset_sql = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control sql-editor',
            'rows': 6,
            'placeholder': 'INSERT INTO employees (name, department, salary) VALUES\n(\'Charlie\', \'Engineering\', 80000),\n(\'Diana\', \'HR\', 55000),\n(\'Eve\', NULL, NULL);'
        }),
        help_text="INSERT statements for validation data. This data includes edge cases and is used for final submission validation."
    )

    reference_query = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control sql-editor',
            'rows': 4,
            'placeholder': 'SELECT * FROM employees WHERE salary > 50000;'
        }),
        help_text="Write the correct SQL query that solves this challenge"
    )



    # Multi-engine support fields
    supported_engines = forms.MultipleChoiceField(
        choices=Challenge.DATABASE_ENGINE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        help_text="Select which database engines this challenge supports",
        label="Supported Database Engines"
    )

    # Simplified database schema fields - only show custom fields when needed
    custom_database_schema_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'json-editor',
            'rows': 8,
            'placeholder': '{\n  "tables": {\n    "users": {\n      "columns": [\n        {"name": "id", "type": "INTEGER PRIMARY KEY"},\n        {"name": "name", "type": "TEXT"}\n      ]\n    }\n  }\n}'
        }),
        required=False,
        help_text="Custom database schema information as JSON (only for custom schema type)",
        label="Custom Database Schema (JSON)"
    )
    
    class Meta:
        model = Challenge
        fields = [
            'title', 'description', 'difficulty', 'question', 'hint',
            'schema_sql', 'run_dataset_sql', 'submit_dataset_sql', 'reference_query',
            'subscription_type', 'company', 'tags', 'xp',
            'supported_engines', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter challenge title'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control'
            }),
            'expected_query': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'SELECT * FROM users WHERE age > 18;'
            }),
            'sample_data': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.csv,.sql,.json'
            }),
            'subscription_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Google, Amazon, Microsoft'
            }),
            'xp': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '10',
                'min': '1',
                'max': '1000'
            }),

            'database_schema_type': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'toggleCustomSchemaFields(this.value)'
            }),
            'custom_initialization_sql': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'CREATE TABLE users (\n    id INTEGER PRIMARY KEY,\n    name TEXT,\n    email TEXT\n);'
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'expected_query': 'The correct SQL solution for this challenge',
            'sample_data': 'Upload CSV or SQL file with sample data for testing',
            'subscription_type': 'Whether this challenge is free or requires a paid subscription',
            'company': 'Company associated with this challenge (optional)',
            'xp': 'Experience points awarded for completing this challenge (1-1000)',

            'database_schema': 'JSON schema describing the database structure',
            'initialization_sql': 'SQL commands to set up the challenge database',
            'order': 'Challenge order (lower numbers appear first)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate supported_engines field
        if self.instance and self.instance.pk:
            self.fields['supported_engines'].initial = self.instance.get_supported_engines()
        else:
            # Set default supported engines for new challenges (hosting service provides MySQL and PostgreSQL)
            self.fields['supported_engines'].initial = ['mysql', 'postgresql']



    def clean_schema_sql(self):
        """
        Validate schema SQL syntax and structure.
        """
        schema_sql = self.cleaned_data.get('schema_sql', '')

        if schema_sql:
            # Validate SQL syntax
            is_valid, error_msg = validate_sql_syntax(schema_sql, "Schema SQL")
            if not is_valid:
                raise forms.ValidationError(error_msg)

            # Check if it contains CREATE TABLE statements
            if 'CREATE TABLE' not in schema_sql.upper():
                raise forms.ValidationError("Schema SQL must contain at least one CREATE TABLE statement")

        return schema_sql

    def clean_run_dataset_sql(self):
        """
        Validate run dataset SQL syntax.
        """
        run_dataset_sql = self.cleaned_data.get('run_dataset_sql', '')

        if run_dataset_sql:
            # Validate SQL syntax
            is_valid, error_msg = validate_sql_syntax(run_dataset_sql, "Run Dataset SQL")
            if not is_valid:
                raise forms.ValidationError(error_msg)

        return run_dataset_sql

    def clean_submit_dataset_sql(self):
        """
        Validate submit dataset SQL syntax.
        """
        submit_dataset_sql = self.cleaned_data.get('submit_dataset_sql', '')

        if submit_dataset_sql:
            # Validate SQL syntax
            is_valid, error_msg = validate_sql_syntax(submit_dataset_sql, "Submit Dataset SQL")
            if not is_valid:
                raise forms.ValidationError(error_msg)

        return submit_dataset_sql

    def clean_reference_query(self):
        """
        Validate reference query SQL syntax.
        """
        reference_query = self.cleaned_data.get('reference_query', '')

        if reference_query:
            # Validate SQL syntax
            is_valid, error_msg = validate_sql_syntax(reference_query, "Solution Query")
            if not is_valid:
                raise forms.ValidationError(error_msg)

        return reference_query

    def clean_tags(self):
        """
        Return the selected tags as a list.
        """
        tags = self.cleaned_data.get('tags', [])
        return tags if isinstance(tags, list) else []

    def clean(self):
        """
        Perform cross-field validation to ensure schema and data consistency.
        """
        cleaned_data = super().clean()
        schema_sql = cleaned_data.get('schema_sql')
        run_dataset_sql = cleaned_data.get('run_dataset_sql')
        submit_dataset_sql = cleaned_data.get('submit_dataset_sql')
        reference_query = cleaned_data.get('reference_query')

        # Only perform comprehensive validation if we have schema SQL
        if schema_sql:
            try:
                # Extract table information from schema
                tables_info = extract_table_info_from_schema(schema_sql)

                if not tables_info:
                    raise forms.ValidationError("Could not parse table information from schema SQL")

                # Validate run dataset SQL against schema
                if run_dataset_sql:
                    is_valid, error_msg = validate_insert_statements_against_schema(run_dataset_sql, tables_info)
                    if not is_valid:
                        raise forms.ValidationError(f"Run Dataset SQL validation failed: {error_msg}")

                # Validate submit dataset SQL against schema
                if submit_dataset_sql:
                    is_valid, error_msg = validate_insert_statements_against_schema(submit_dataset_sql, tables_info)
                    if not is_valid:
                        raise forms.ValidationError(f"Submit Dataset SQL validation failed: {error_msg}")

                # Comprehensive challenge validation
                if schema_sql and submit_dataset_sql and reference_query:
                    # Test complete challenge setup
                    validation_result = self._test_complete_challenge_setup(schema_sql, submit_dataset_sql, reference_query)
                    if not validation_result['success']:
                        raise forms.ValidationError(f"Challenge setup test failed: {validation_result['error']}")

                    # Validate challenge completeness
                    completeness_check = _validate_challenge_completeness(schema_sql, run_dataset_sql, submit_dataset_sql, reference_query)
                    if not completeness_check['valid']:
                        raise forms.ValidationError(f"Challenge completeness check failed: {completeness_check['error']}")

                    # Validate foreign key consistency
                    fk_check = _validate_foreign_key_consistency(tables_info)
                    if not fk_check['valid']:
                        raise forms.ValidationError(f"Foreign key validation failed: {fk_check['error']}")

                    # Validate dataset consistency
                    if run_dataset_sql:
                        consistency_check = _validate_data_consistency_across_datasets(run_dataset_sql, submit_dataset_sql, tables_info)
                        if not consistency_check['valid']:
                            raise forms.ValidationError(f"Dataset consistency check failed: {consistency_check['error']}")

            except SQLValidationError as e:
                raise forms.ValidationError(str(e))
            except Exception as e:
                raise forms.ValidationError(f"Validation error: {str(e)}")

        return cleaned_data

    def _test_complete_challenge_setup(self, schema_sql, dataset_sql, reference_query):
        """
        Test the complete challenge setup by creating a temporary database and executing the reference query.
        Returns dict with success status and error message if any.
        """
        try:
            from .utils import execute_dual_dataset_query
            from .models import Challenge
            import uuid

            # Create a temporary challenge object for testing (don't save to DB)
            temp_challenge = Challenge(
                id=999999,  # Temporary ID
                title="Validation Test",
                schema_sql=schema_sql,
                submit_dataset_sql=dataset_sql,
                reference_query=reference_query
            )

            # Test the reference query execution
            result = execute_dual_dataset_query(
                challenge=temp_challenge,
                query=reference_query,
                flag_id=2,  # Submit dataset
                engine='mysql'
            )

            if result['success']:
                return {'success': True, 'message': 'Challenge setup validated successfully'}
            else:
                return {'success': False, 'error': result.get('error', 'Unknown error during validation')}

        except Exception as e:
            return {'success': False, 'error': f'Validation test failed: {str(e)}'}

    def save(self, commit=True):
        """
        Save the challenge with data from the custom fields.
        """
        challenge = super().save(commit=False)





        # Set supported_engines from the multi-select field
        challenge.supported_engines = self.cleaned_data.get('supported_engines', ['sqlite', 'postgresql', 'mysql'])

        # Set tags from the cleaned field
        challenge.tags = self.cleaned_data.get('tags', [])

        if commit:
            challenge.save()

            # Execute reference query if all required fields are provided
            if challenge.schema_sql and challenge.submit_dataset_sql and challenge.reference_query:
                success, message = challenge.execute_reference_query()
                if not success:
                    self.add_error(None, f"Reference query execution failed: {message}")

        return challenge


# ============================================================================
# COMPREHENSIVE VALIDATION FUNCTIONS
# ============================================================================

def _validate_reference_query_content(query_sql):
    """
    Comprehensive validation for reference queries.
    """
    try:
        query_upper = query_sql.upper().strip()

        # Check if it's a SELECT query
        if not query_upper.startswith('SELECT'):
            return False, "Reference query should be a SELECT statement"

        # Check for dangerous operations
        dangerous_operations = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        for op in dangerous_operations:
            if f' {op} ' in f' {query_upper} ':
                return False, f"Reference query should not contain {op} operations"

        # Check for common issues
        if 'SELECT *' in query_upper and 'ORDER BY' not in query_upper:
            return False, "SELECT * queries should include ORDER BY for consistent results across different database engines"

        # Check for potential performance issues
        if query_upper.count('JOIN') > 5:
            return False, "Reference query has too many JOINs (>5) which may cause performance issues"

        # Check for missing WHERE clause in complex queries
        if ('JOIN' in query_upper or 'UNION' in query_upper) and 'WHERE' not in query_upper:
            return False, "Complex queries with JOINs should typically include WHERE clauses to avoid cartesian products"

        return True, ""

    except Exception as e:
        return False, f"Reference query validation error: {str(e)}"


def _validate_foreign_key_consistency(tables_info):
    """
    Validate foreign key relationships between tables.
    """
    try:
        # Extract all table names and their columns
        table_columns = {}
        for table_name, table_data in tables_info.items():
            table_columns[table_name] = [col['name'] for col in table_data.get('columns', [])]

        # Check foreign key references
        for table_name, table_data in tables_info.items():
            for constraint in table_data.get('constraints', []):
                if constraint.get('type') == 'FOREIGN KEY':
                    ref_table = constraint.get('referenced_table')
                    ref_column = constraint.get('referenced_column')

                    if ref_table not in table_columns:
                        return {
                            'valid': False,
                            'error': f"Foreign key in table '{table_name}' references non-existent table '{ref_table}'"
                        }

                    if ref_column not in table_columns[ref_table]:
                        return {
                            'valid': False,
                            'error': f"Foreign key in table '{table_name}' references non-existent column '{ref_column}' in table '{ref_table}'"
                        }

        return {'valid': True, 'error': ''}

    except Exception as e:
        return {'valid': False, 'error': f"Foreign key validation error: {str(e)}"}


def _validate_data_consistency_across_datasets(run_dataset_sql, submit_dataset_sql, tables_info):
    """
    Validate that run and submit datasets have consistent structure and data types.
    """
    try:
        # Parse both datasets
        run_tables = _extract_insert_statements(run_dataset_sql)
        submit_tables = _extract_insert_statements(submit_dataset_sql)

        # Check that both datasets target the same tables
        run_table_names = set(run_tables.keys())
        submit_table_names = set(submit_tables.keys())

        if run_table_names != submit_table_names:
            missing_in_submit = run_table_names - submit_table_names
            missing_in_run = submit_table_names - run_table_names

            error_parts = []
            if missing_in_submit:
                error_parts.append(f"Submit dataset missing tables: {', '.join(missing_in_submit)}")
            if missing_in_run:
                error_parts.append(f"Run dataset missing tables: {', '.join(missing_in_run)}")

            return {
                'valid': False,
                'error': f"Dataset inconsistency: {'; '.join(error_parts)}"
            }

        # Check column consistency for each table
        for table_name in run_table_names:
            run_columns = run_tables[table_name].get('columns', [])
            submit_columns = submit_tables[table_name].get('columns', [])

            if run_columns != submit_columns:
                return {
                    'valid': False,
                    'error': f"Table '{table_name}' has different column structure between run and submit datasets"
                }

        return {'valid': True, 'error': ''}

    except Exception as e:
        return {'valid': False, 'error': f"Dataset consistency validation error: {str(e)}"}


def _validate_challenge_completeness(schema_sql, run_dataset_sql, submit_dataset_sql, reference_query):
    """
    Validate that all components of a challenge work together properly.
    """
    try:
        # Check that all required components are present
        if not all([schema_sql, submit_dataset_sql, reference_query]):
            missing = []
            if not schema_sql: missing.append("Schema SQL")
            if not submit_dataset_sql: missing.append("Submit Dataset SQL")
            if not reference_query: missing.append("Solution Query")

            return {
                'valid': False,
                'error': f"Challenge incomplete: missing {', '.join(missing)}"
            }

        # Extract table information from schema
        tables_info = extract_table_info_from_schema(schema_sql)

        # Validate that reference query uses tables from schema
        query_upper = reference_query.upper()
        schema_tables = list(tables_info.keys())

        tables_used_in_query = []
        for table_name in schema_tables:
            if table_name.upper() in query_upper:
                tables_used_in_query.append(table_name)

        if not tables_used_in_query:
            return {
                'valid': False,
                'error': "Reference query doesn't appear to use any tables from the schema"
            }

        # Check that datasets provide data for tables used in query
        submit_tables = _extract_insert_statements(submit_dataset_sql)
        for table_name in tables_used_in_query:
            if table_name not in submit_tables:
                return {
                    'valid': False,
                    'error': f"Submit dataset missing data for table '{table_name}' which is used in reference query"
                }

        return {'valid': True, 'error': ''}

    except Exception as e:
        return {'valid': False, 'error': f"Challenge completeness validation error: {str(e)}"}


def _extract_insert_statements(dataset_sql):
    """
    Extract table names and column information from INSERT statements.
    """
    tables = {}

    # Find all INSERT statements
    insert_pattern = r'INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)'
    matches = re.findall(insert_pattern, dataset_sql, re.IGNORECASE)

    for table_name, columns_str in matches:
        columns = [col.strip() for col in columns_str.split(',')]
        tables[table_name] = {'columns': columns}

    return tables


def _validate_additional_data_constraints(value, column_info, column_name, row_number):
    """
    Additional validation for data constraints beyond basic type checking.
    """
    try:
        if _is_null_value(value):
            return {'valid': True, 'error': ''}  # NULL handling is done elsewhere

        value_clean = value.strip().strip("'\"")
        data_type = column_info.get('data_type', '').upper()

        # Check for SQL keywords as data values
        sql_keywords = ['SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TABLE', 'DATABASE']
        if value_clean.upper() in sql_keywords:
            return {
                'valid': False,
                'error': f"row {row_number}: Value '{value_clean}' in column '{column_name}' is a SQL keyword and may cause issues"
            }

        # Check for potential XSS in string values
        if data_type in ['VARCHAR', 'CHAR', 'TEXT']:
            xss_patterns = ['<script', 'javascript:', 'onload=', 'onerror=', 'onclick=']
            value_lower = value_clean.lower()
            for pattern in xss_patterns:
                if pattern in value_lower:
                    return {
                        'valid': False,
                        'error': f"row {row_number}: Value in column '{column_name}' contains potentially dangerous content: {pattern}"
                    }

        # Check for extremely long values that might cause issues
        if len(value_clean) > 1000:
            return {
                'valid': False,
                'error': f"row {row_number}: Value in column '{column_name}' is extremely long ({len(value_clean)} characters) and may cause performance issues"
            }

        # Check for binary/control characters in text fields
        if data_type in ['VARCHAR', 'CHAR', 'TEXT']:
            if any(ord(char) < 32 and char not in ['\t', '\n', '\r'] for char in value_clean):
                return {
                    'valid': False,
                    'error': f"row {row_number}: Value in column '{column_name}' contains control characters that may cause display issues"
                }

        # Check for negative values in ID columns
        if 'id' in column_name.lower() and data_type in ['INT', 'INTEGER', 'BIGINT']:
            try:
                if int(value_clean) <= 0:
                    return {
                        'valid': False,
                        'error': f"row {row_number}: ID column '{column_name}' should have positive values (got {value_clean})"
                    }
            except ValueError:
                pass  # Already caught in type validation

        # Check for decimal precision issues
        if data_type in ['DECIMAL', 'NUMERIC']:
            try:
                float_val = float(value_clean)
                if '.' in value_clean:
                    decimal_places = len(value_clean.split('.')[1])
                    if decimal_places > 4:  # Reasonable limit for most use cases
                        return {
                            'valid': False,
                            'error': f"row {row_number}: Value in column '{column_name}' has too many decimal places ({decimal_places}). Consider rounding to 2-4 decimal places."
                        }
            except ValueError:
                pass  # Already caught in type validation

        # Check for suspicious email patterns (if column name suggests email)
        if 'email' in column_name.lower() and data_type in ['VARCHAR', 'CHAR', 'TEXT']:
            # If it doesn't contain @ but column is named email, it's likely invalid
            if '@' not in value_clean:
                return {
                    'valid': False,
                    'error': f"row {row_number}: Value '{value_clean}' in email column '{column_name}' appears to be an invalid email format (missing @)"
                }
            # If it contains @ but doesn't match email pattern, it's invalid
            elif '@' in value_clean and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value_clean):
                return {
                    'valid': False,
                    'error': f"row {row_number}: Value '{value_clean}' in email column '{column_name}' appears to be an invalid email format"
                }

        return {'valid': True, 'error': ''}

    except Exception as e:
        return {'valid': False, 'error': f"row {row_number}: Additional validation error for column '{column_name}': {str(e)}"}


class ChallengeFilterForm(forms.Form):
    """
    Form for filtering challenges in the admin list view.
    """
    DIFFICULTY_CHOICES = [('', 'All Difficulties')] + Challenge.DIFFICULTY_CHOICES
    STATUS_CHOICES = [
        ('', 'All Status'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ]
    
    difficulty = forms.ChoiceField(
        choices=DIFFICULTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search challenges...'
        })
    )


class ChallengeSubscriptionPlanForm(forms.ModelForm):
    """
    Form for creating and editing challenge subscription plans.
    """
    features = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Enter features one per line:\n• Feature 1\n• Feature 2\n• Feature 3'
        }),
        required=False,
        help_text="Enter features one per line"
    )

    class Meta:
        model = ChallengeSubscriptionPlan
        fields = [
            'name', 'duration', 'price', 'original_price', 'description',
            'features', 'is_active', 'is_recommended', 'sort_order'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Premium Challenge Access'
            }),
            'duration': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'original_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe what this subscription plan includes...'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_recommended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
        }
        help_texts = {
            'original_price': 'Optional: Show crossed-out original price for discounts',
            'description': 'Brief description of what this plan includes',
            'is_recommended': 'Mark this plan as recommended (highlighted to users)',
            'sort_order': 'Lower numbers appear first in the list'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Convert features list to string for display
        if self.instance and self.instance.pk and self.instance.features:
            if isinstance(self.instance.features, list):
                # Handle case where features is a list containing a string representation of a list
                if len(self.instance.features) == 1 and isinstance(self.instance.features[0], str) and self.instance.features[0].startswith('['):
                    try:
                        import ast
                        actual_features = ast.literal_eval(self.instance.features[0])
                        if isinstance(actual_features, list):
                            self.fields['features'].initial = '\n'.join(actual_features)
                        else:
                            self.fields['features'].initial = '\n'.join(self.instance.features)
                    except (ValueError, SyntaxError):
                        self.fields['features'].initial = '\n'.join(self.instance.features)
                else:
                    self.fields['features'].initial = '\n'.join(self.instance.features)

    def clean_features(self):
        """Convert features string to list"""
        features_text = self.cleaned_data.get('features', '')
        if not features_text.strip():
            return []

        # Split by lines and clean up
        features = [line.strip() for line in features_text.split('\n') if line.strip()]

        # Remove bullet points if present
        cleaned_features = []
        for feature in features:
            # Remove common bullet point characters
            feature = feature.lstrip('•·*-').strip()
            if feature:
                cleaned_features.append(feature)

        return cleaned_features


class UserChallengeSubscriptionForm(forms.ModelForm):
    """
    Form for creating and editing user challenge subscriptions.
    """
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-placeholder': 'Select a user'
        }),
        help_text="Select the user for this subscription"
    )

    plan = forms.ModelChoiceField(
        queryset=ChallengeSubscriptionPlan.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text="Select the subscription plan"
    )

    class Meta:
        model = UserChallengeSubscription
        fields = [
            'user', 'plan', 'status', 'start_date', 'end_date',
            'amount_paid', 'payment_reference'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'payment_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Payment reference (optional)'
            }),
        }
        help_texts = {
            'end_date': 'Leave blank for unlimited plans',
            'amount_paid': 'Amount paid for this subscription',
            'payment_reference': 'Optional payment reference or transaction ID'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Order users by email for easier selection
        self.fields['user'].queryset = User.objects.all().order_by('email')

        # Order plans by sort_order and name
        self.fields['plan'].queryset = ChallengeSubscriptionPlan.objects.filter(
            is_active=True
        ).order_by('sort_order', 'name')


class SubscriptionFilterForm(forms.Form):
    """
    Form for filtering subscriptions in the admin list view.
    """
    STATUS_CHOICES = [('', 'All Status')] + UserChallengeSubscription.STATUS_CHOICES

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    plan = forms.ModelChoiceField(
        queryset=ChallengeSubscriptionPlan.objects.filter(is_active=True),
        required=False,
        empty_label="All Plans",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by user email, plan name...'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order plans by sort_order and name
        self.fields['plan'].queryset = ChallengeSubscriptionPlan.objects.filter(
            is_active=True
        ).order_by('sort_order', 'name')
