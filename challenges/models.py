from django.db import models
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone
from datetime import timedelta
import json


class ChallengeTable(models.Model):
    """
    Individual table definition for a challenge.
    Supports multi-table challenges with isolated schemas per challenge.
    """
    challenge = models.ForeignKey('Challenge', on_delete=models.CASCADE, related_name='tables')
    table_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Original table name (auto-extracted from schema SQL and auto-prefixed with challenge ID for isolation)"
    )
    schema_sql = models.TextField(
        help_text="CREATE TABLE statement for this table"
    )
    run_dataset_sql = models.TextField(
        help_text="INSERT statements for test/trial data (users see this during testing)"
    )
    submit_dataset_sql = models.TextField(
        help_text="INSERT statements for validation data (hidden test cases for final submission)"
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order in admin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'table_name']
        unique_together = ['challenge', 'table_name']

    def __str__(self):
        return f"{self.challenge.title} - {self.table_name}"

    def get_unique_table_name(self):
        """Get the unique table name for this challenge table"""
        return f"{self.table_name}_q{self.challenge.id}"

    def get_processed_schema_sql(self):
        """
        Get schema SQL with unique table name and flag_id column added.
        Enhanced to handle various CREATE TABLE syntax variations and both MySQL/PostgreSQL.
        """
        import re

        if not self.schema_sql:
            return ""

        unique_name = self.get_unique_table_name()
        processed_schema = self.schema_sql.strip()

        # Enhanced table name replacement to handle various syntax patterns
        table_name_escaped = re.escape(self.table_name)

        # Pattern to match CREATE TABLE with optional IF NOT EXISTS and various quote styles
        patterns = [
            rf'\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`{table_name_escaped}`',
            rf'\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?"{table_name_escaped}"',
            rf'\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?\[{table_name_escaped}\]',
            rf'\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{table_name_escaped}\b'
        ]

        replacement = f'CREATE TABLE {unique_name}'

        # Try each pattern until one matches
        for pattern in patterns:
            if re.search(pattern, processed_schema, re.IGNORECASE):
                processed_schema = re.sub(pattern, replacement, processed_schema, flags=re.IGNORECASE)
                break

        # Enhanced flag_id column addition with better SQL parsing
        if 'flag_id' not in processed_schema.lower():
            processed_schema = self._add_flag_id_column(processed_schema)

        return processed_schema

    def _add_flag_id_column(self, schema_sql):
        """
        Add flag_id column to CREATE TABLE statement with proper syntax handling.
        Supports both MySQL and PostgreSQL syntax.
        Enhanced to handle various CREATE TABLE formats more reliably.
        """
        import re

        # Check if flag_id already exists (case insensitive)
        if 'flag_id' in schema_sql.lower():
            return schema_sql

        # Use line-by-line approach for better reliability
        return self._add_flag_id_column_fallback(schema_sql)

    def _add_flag_id_column_fallback(self, schema_sql):
        """
        Fallback method for adding flag_id column using line-by-line approach.
        Enhanced to handle various CREATE TABLE formats more reliably.
        """
        lines = schema_sql.split('\n')
        processed_lines = []

        # Find the last line that contains a closing parenthesis
        closing_paren_line_idx = -1
        for i in range(len(lines) - 1, -1, -1):
            if ')' in lines[i]:
                closing_paren_line_idx = i
                break

        if closing_paren_line_idx == -1:
            # No closing parenthesis found, return original
            return schema_sql

        # Process each line
        for i, line in enumerate(lines):
            if i == closing_paren_line_idx:
                # This is the line with the closing parenthesis
                closing_paren_pos = line.rfind(')')

                if closing_paren_pos >= 0:
                    # Get content before and after the closing parenthesis
                    before_paren = line[:closing_paren_pos]
                    after_paren = line[closing_paren_pos:]

                    # Check if we need a comma by looking at the previous line
                    needs_comma = True
                    if i > 0:
                        prev_line = lines[i-1].strip()
                        if not prev_line or prev_line.endswith(','):
                            needs_comma = False

                    # Also check if the current line has content before the closing paren
                    current_content = before_paren.strip()
                    if current_content and not current_content.endswith(','):
                        needs_comma = True
                    elif not current_content and i > 0:
                        # No content on current line, check previous line
                        prev_line = lines[i-1].strip()
                        if prev_line and not prev_line.endswith(','):
                            needs_comma = True
                        else:
                            needs_comma = False

                    comma = ',' if needs_comma else ''

                    # Add flag_id column
                    flag_id_column = self._get_flag_id_column_definition(comma)

                    # Reconstruct the line
                    new_line = before_paren + flag_id_column + after_paren
                    processed_lines.append(new_line)
                else:
                    processed_lines.append(line)
            else:
                processed_lines.append(line)

        return '\n'.join(processed_lines)

    def _get_flag_id_column_definition(self, comma):
        """
        Get database-specific flag_id column definition.
        Handles syntax differences between MySQL and PostgreSQL.
        """
        # For now, use standard SQL syntax that works with both MySQL and PostgreSQL
        # Both support INT NOT NULL DEFAULT 0 syntax
        if comma:
            return f"{comma}\n    flag_id INT NOT NULL DEFAULT 0"
        else:
            return f"\n    flag_id INT NOT NULL DEFAULT 0"

    def get_processed_dataset_sql(self, flag_id):
        """
        Get dataset SQL with unique table name and automated flag_id assignment.
        Implements the automated INSERT + UPDATE pattern as requested:
        1. Execute INSERT statements as-is
        2. Automatically UPDATE all inserted records to set flag_id = 1 (test) or 2 (submit)
        """
        import re

        dataset_sql = self.run_dataset_sql if flag_id == 1 else self.submit_dataset_sql
        if not dataset_sql:
            return ""

        unique_name = self.get_unique_table_name()
        processed_sql = dataset_sql.strip()

        # Replace table name with unique name in INSERT statements
        table_name_escaped = re.escape(self.table_name)
        patterns = [
            rf'\bINSERT\s+(?:INTO\s+)?`{table_name_escaped}`',
            rf'\bINSERT\s+(?:INTO\s+)?"{table_name_escaped}"',
            rf'\bINSERT\s+(?:INTO\s+)?\[{table_name_escaped}\]',
            rf'\bINSERT\s+(?:INTO\s+)?{table_name_escaped}\b'
        ]

        replacement = f'INSERT INTO {unique_name}'

        # Try each pattern until one matches
        for pattern in patterns:
            if re.search(pattern, processed_sql, re.IGNORECASE):
                processed_sql = re.sub(pattern, replacement, processed_sql, flags=re.IGNORECASE)
                break

        # Note: We don't modify INSERT statements - we rely on the DEFAULT value for flag_id
        # and then use UPDATE to set the correct flag_id value

        # Implement automated INSERT + UPDATE pattern
        # Step 1: Execute INSERT statements as-is (they will use flag_id DEFAULT 0)
        # Step 2: Add UPDATE statement to set flag_id to the appropriate value

        # Ensure the SQL ends with semicolon for proper statement separation
        if not processed_sql.rstrip().endswith(';'):
            processed_sql = processed_sql.rstrip() + ';'

        # Add automated UPDATE statement to set flag_id for all records with flag_id = 0
        update_statement = f"\nUPDATE {unique_name} SET flag_id = {flag_id} WHERE flag_id = 0;"

        processed_sql = processed_sql + update_statement

        return processed_sql

    def _fix_insert_statements_for_flag_id(self, sql, unique_table_name):
        """
        Fix INSERT statements to include flag_id column and value.
        This handles MySQL compatibility where column count must match value count.
        """
        import re

        # Check if this is INSERT INTO table (columns) VALUES
        column_spec_pattern = rf'INSERT\s+INTO\s+{re.escape(unique_table_name)}\s*\(([^)]+)\)\s+VALUES'
        column_match = re.search(column_spec_pattern, sql, re.IGNORECASE)

        if column_match:
            # This INSERT statement specifies columns - add flag_id to the column list
            columns = column_match.group(1).strip()

            # Check if flag_id is already in the column list
            if 'flag_id' not in columns.lower():
                # Add flag_id to the column list
                new_columns = f"{columns}, flag_id"

                # Replace the column specification
                new_sql = re.sub(
                    rf'INSERT\s+INTO\s+{re.escape(unique_table_name)}\s*\([^)]+\)\s+VALUES',
                    f'INSERT INTO {unique_table_name} ({new_columns}) VALUES',
                    sql,
                    flags=re.IGNORECASE,
                    count=1  # Only replace the first occurrence
                )

                # Add flag_id = 0 to each VALUES tuple
                def add_flag_id_value(match):
                    values = match.group(1).strip()
                    return f'({values}, 0)'

                # Find and update all value tuples
                new_sql = re.sub(r'\(([^)]+)\)', add_flag_id_value, new_sql)

                return new_sql
        else:
            # This is INSERT INTO table VALUES without column specification
            # Add flag_id = 0 to each VALUES tuple
            lines = sql.split('\n')
            fixed_lines = []

            for line in lines:
                # Check if this line contains value tuples
                if re.search(r'\([^)]+\)', line):
                    # Find all value tuples and add flag_id = 0
                    def add_flag_id(match):
                        values = match.group(1).strip()
                        # Add flag_id = 0 as the last value
                        return f'({values}, 0)'

                    fixed_line = re.sub(r'\(([^)]+)\)', add_flag_id, line)
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)

            return '\n'.join(fixed_lines)

        return sql


class Challenge(models.Model):
    """
    SQL challenges for users to solve.
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('extreme', 'Extreme Hard'),
    ]

    SUBSCRIPTION_TYPE_CHOICES = [
        ('free', 'Free'),
        ('paid', 'Paid'),
    ]

    DATABASE_ENGINE_CHOICES = [
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
    ]

    DATABASE_SCHEMA_CHOICES = [
        ('employees', 'Employee Database'),
        ('ecommerce', 'E-commerce Database (Orders & Returns)'),
        ('students', 'Student Database (Students, Courses, Enrollments)'),
        ('custom', 'Custom Schema'),
    ]

    # Predefined tag choices with descriptions
    TAG_CHOICES = [
        ('joins', 'Joins - Combining data from multiple tables using INNER, LEFT, RIGHT, FULL OUTER joins'),
        ('aggregation', 'Aggregation - Using functions like COUNT, SUM, AVG, MIN, MAX with GROUP BY'),
        ('subqueries', 'Subqueries - Nested queries and correlated subqueries'),
        ('window-functions', 'Window Functions - Advanced analytics using ROW_NUMBER, RANK, LAG, LEAD, etc.'),
        ('advanced-sql', 'Advanced SQL - Complex queries combining multiple concepts'),
        ('analytics', 'Analytics - Business intelligence and data analysis queries'),
        ('filtering', 'Filtering - Using WHERE clauses with various conditions'),
        ('sorting', 'Sorting - Using ORDER BY with different criteria'),
        ('string-functions', 'String Functions - Text manipulation using CONCAT, SUBSTRING, UPPER, LOWER, etc.'),
        ('date-functions', 'Date Functions - Working with dates and time calculations'),
        ('case-statements', 'Case Statements - Conditional logic using CASE WHEN'),
        ('performance', 'Performance - Query optimization and indexing concepts'),
    ]

    title = models.CharField(max_length=255)
    description = CKEditor5Field(config_name='tutorial')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    question = CKEditor5Field(config_name='tutorial')
    hint = CKEditor5Field(config_name='tutorial', blank=True)
    # Enhanced dual-dataset solution system
    schema_sql = models.TextField(
        blank=True,
        help_text="SQL schema definition (CREATE TABLE statements) - will be auto-prefixed with challenge ID"
    )
    run_dataset_sql = models.TextField(
        blank=True,
        help_text="INSERT statements for test/trial data (users see this during testing)"
    )
    submit_dataset_sql = models.TextField(
        blank=True,
        help_text="INSERT statements for validation data (hidden test cases for final submission)"
    )
    reference_query = models.TextField(
        blank=True,
        help_text="The correct SQL query that solves this challenge (admin/superuser writes this)"
    )
    expected_result_json = models.JSONField(
        default=list,
        blank=True,
        help_text="Auto-generated JSON result from executing the reference query on submit dataset"
    )

    # Legacy schema field (kept for backward compatibility)
    mysql_schema_file = models.FileField(
        upload_to='challenges/schemas/',
        blank=True,
        null=True,
        help_text="Upload MySQL schema file (.sql) containing table structures and data (legacy)"
    )

    # Legacy fields (kept for backward compatibility)
    expected_query = models.TextField(blank=True)
    expected_result = models.JSONField(default=list)  # Store expected result as JSON
    sample_data = models.FileField(upload_to='challenges/sample_data/', blank=True, null=True,
                                   help_text="Upload CSV or SQL file with sample data (legacy)")

    # Simplified database schema selection
    database_schema_type = models.CharField(
        max_length=20,
        choices=DATABASE_SCHEMA_CHOICES,
        default='employees',
        help_text="Select a predefined database schema for this challenge"
    )

    # Custom schema fields (only used when database_schema_type='custom')
    custom_initialization_sql = models.TextField(
        blank=True,
        help_text="Custom SQL commands (only used for custom schema type)"
    )
    custom_database_schema = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom database schema information (only used for custom schema type)"
    )

    # Multi-database engine support (simplified)
    supported_engines = models.JSONField(
        default=list,
        blank=True,
        help_text="List of supported database engines for this challenge"
    )

    # Subscription and categorization fields
    subscription_type = models.CharField(max_length=10, choices=SUBSCRIPTION_TYPE_CHOICES, default='free')
    company = models.CharField(max_length=100, blank=True, help_text="Company associated with this challenge")
    tags = models.JSONField(default=list, help_text="List of tags for categorization (e.g., ['joins', 'aggregation'])")

    # Gamification
    xp = models.PositiveIntegerField(default=10, help_text="Experience points awarded for completing this challenge")

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'difficulty', 'created_at']

    def __str__(self):
        return f"{self.title} ({self.difficulty})"

    def save(self, *args, **kwargs):
        """Auto-generate order and expected results if not set"""
        # Auto-generate order if not set
        if not self.order:
            # Get the highest order value and add 1
            max_order = Challenge.objects.aggregate(
                max_order=models.Max('order')
            )['max_order']
            self.order = (max_order or 0) + 1

        # Save first to ensure we have an ID
        super().save(*args, **kwargs)

        # Auto-generate expected results for dual-dataset challenges
        self._generate_expected_results_if_needed()

    def _generate_expected_results_if_needed(self):
        """
        Automatically generate expected results by executing the reference query
        against the submit dataset (flag_id=2). This happens when:
        1. Challenge has schema_sql, submit_dataset_sql, and reference_query
        2. Expected_result is empty or None
        3. Challenge is being saved by a superuser (in admin context)
        """
        # Only generate if we have all required fields for dual-dataset system
        if not (self.schema_sql and self.submit_dataset_sql and self.reference_query):
            return

        # Only generate if expected_result is empty or None
        if self.expected_result and len(self.expected_result) > 0:
            return

        try:
            # Execute reference query against submit dataset to generate expected results
            success, message = self.execute_reference_query()
            if success:
                print(f"✅ Auto-generated expected results for challenge: {self.title}")
            else:
                print(f"⚠️ Failed to auto-generate expected results for {self.title}: {message}")
        except Exception as e:
            print(f"❌ Error auto-generating expected results for {self.title}: {str(e)}")

    def get_unique_table_names(self):
        """
        Generate unique table names for this challenge to avoid conflicts.
        Returns a mapping of original table names to unique names.
        Supports both legacy single-table and new multi-table systems.
        """
        import re
        unique_mapping = {}

        # Check if using new multi-table system
        if self.tables.exists():
            for table in self.tables.all():
                unique_mapping[table.table_name] = table.get_unique_table_name()
            return unique_mapping

        # Legacy single-table system
        if not self.schema_sql:
            return {}

        # Extract table names from CREATE TABLE statements
        table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?'
        table_names = re.findall(table_pattern, self.schema_sql, re.IGNORECASE)

        # Create unique names using challenge ID
        for table_name in table_names:
            unique_mapping[table_name] = f"{table_name}_q{self.id}"

        return unique_mapping

    def get_all_schema_sql(self):
        """
        Get combined schema SQL for all tables in this challenge.
        Supports both legacy single-table and new multi-table systems.
        """
        # Check if using new multi-table system
        if self.tables.exists():
            schema_parts = []
            for table in self.tables.all().order_by('order', 'table_name'):
                processed_schema = table.get_processed_schema_sql()
                if processed_schema:
                    schema_parts.append(processed_schema)
            return ';\n'.join(schema_parts) + ';' if schema_parts else ""

        # Legacy single-table system
        return self.get_processed_schema_sql()

    def get_all_dataset_sql(self, flag_id):
        """
        Get combined dataset SQL for all tables in this challenge.
        Supports both legacy single-table and new multi-table systems.
        """
        # Check if using new multi-table system
        if self.tables.exists():
            dataset_parts = []
            for table in self.tables.all().order_by('order', 'table_name'):
                processed_dataset = table.get_processed_dataset_sql(flag_id)
                if processed_dataset:
                    dataset_parts.append(processed_dataset)
            return ';\n'.join(dataset_parts) + ';' if dataset_parts else ""

        # Legacy single-table system
        if flag_id == 1:
            return self.process_dataset_sql(self.run_dataset_sql, flag_id)
        else:
            return self.process_dataset_sql(self.submit_dataset_sql, flag_id)

    def has_multi_table_setup(self):
        """Check if this challenge uses the new multi-table system"""
        return self.tables.exists()

    def validate_flag_id_columns(self):
        """
        Validate that all tables in this challenge have flag_id columns.
        Returns (is_valid, error_message) tuple.
        """
        schema_sql = self.get_all_schema_sql()
        if not schema_sql:
            return False, "No schema SQL found"

        if 'flag_id' not in schema_sql.lower():
            return False, "Schema SQL is missing flag_id columns. Please recreate the challenge or manually add 'flag_id INT NOT NULL DEFAULT 0' to all CREATE TABLE statements."

        return True, ""

    def get_table_count(self):
        """Get the number of tables in this challenge"""
        if self.has_multi_table_setup():
            return self.tables.count()
        elif self.schema_sql:
            import re
            table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?'
            table_names = re.findall(table_pattern, self.schema_sql, re.IGNORECASE)
            return len(table_names)
        return 0

    def process_dataset_sql(self, dataset_sql, flag_id, table_mapping=None):
        """
        Process INSERT statements to add flag_id and update table names.
        """
        import re

        if not dataset_sql:
            return ""

        if table_mapping is None:
            table_mapping = self.get_unique_table_names()

        processed_sql = dataset_sql

        # Replace table names with unique names
        for original_name, unique_name in table_mapping.items():
            # Replace in INSERT statements
            pattern = r'\bINSERT\s+(?:INTO\s+)?`?' + re.escape(original_name) + r'`?'
            replacement = f'INSERT INTO {unique_name}'
            processed_sql = re.sub(pattern, replacement, processed_sql, flags=re.IGNORECASE)

        # Add flag_id to INSERT statements (handle multi-row inserts)
        # Pattern to match: INSERT INTO table (columns) VALUES (...), (...), ...;
        insert_pattern = r'INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*(.*?)(?=;|$)'

        def add_flag_id_to_multirow(match):
            table_name = match.group(1)
            columns = match.group(2).strip()
            values_section = match.group(3).strip()

            # Check if flag_id is already in the column list
            if 'flag_id' in columns.lower():
                # flag_id already exists, just return the original with updated table name
                return f"INSERT INTO {table_name} ({columns}) VALUES\n{values_section}"

            # Add flag_id to columns
            new_columns = f"{columns}, flag_id"

            # Process each row in the VALUES section
            # Split by '), (' to get individual rows
            rows = []
            current_row = ""
            paren_count = 0

            for char in values_section:
                current_row += char
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                    if paren_count == 0:
                        # End of a row
                        row_content = current_row.strip()
                        if row_content.startswith('(') and row_content.endswith(')'):
                            # Remove outer parentheses and add flag_id
                            inner_content = row_content[1:-1]
                            new_row = f"({inner_content}, {flag_id})"
                            rows.append(new_row)
                        current_row = ""
                elif char == ',' and paren_count == 0:
                    # Skip comma between rows
                    current_row = ""

            new_values = ',\n'.join(rows)
            return f"INSERT INTO {table_name} ({new_columns}) VALUES\n{new_values}"

        processed_sql = re.sub(insert_pattern, add_flag_id_to_multirow, processed_sql, flags=re.IGNORECASE | re.DOTALL)

        return processed_sql

    def get_processed_schema_sql(self):
        """
        Get schema SQL with unique table names and flag_id column added.
        Supports both legacy single-table and multi-table systems.
        """
        import re

        # Check if this is a multi-table setup
        if self.has_multi_table_setup():
            # Multi-table system: combine all table schemas
            all_schemas = []
            for table in self.tables.all():
                processed_schema = table.get_processed_schema_sql()
                if processed_schema:
                    all_schemas.append(processed_schema)
            return '\n\n'.join(all_schemas)

        # Legacy single-table system
        if not self.schema_sql:
            return ""

        table_mapping = self.get_unique_table_names()
        processed_schema = self.schema_sql

        # Replace table names with unique names
        for original_name, unique_name in table_mapping.items():
            # Replace in CREATE TABLE statements
            pattern = r'\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?' + re.escape(original_name) + r'`?'
            replacement = f'CREATE TABLE {unique_name}'
            processed_schema = re.sub(pattern, replacement, processed_schema, flags=re.IGNORECASE)

        # Add flag_id column to each CREATE TABLE statement (only if not already present)
        def add_flag_id_column(match):
            table_definition = match.group(0)
            # Check if flag_id column already exists
            if 'flag_id' in table_definition.lower():
                return table_definition  # Already has flag_id, don't add it again

            # Add flag_id column before the closing parenthesis
            if table_definition.rstrip().endswith(')'):
                return table_definition.rstrip()[:-1] + ', flag_id INT DEFAULT 1)'
            return table_definition

        # Find CREATE TABLE statements and add flag_id column if needed
        # Updated pattern to handle table names with underscores and multiline statements
        table_pattern = r'CREATE\s+TABLE\s+[\w_]+\s*\([^)]+\)'
        processed_schema = re.sub(table_pattern, add_flag_id_column, processed_schema, flags=re.IGNORECASE | re.DOTALL)

        return processed_schema

    def execute_reference_query(self):
        """
        Execute the reference query on the submit dataset and store the result.
        Supports both legacy single-table and new multi-table systems.
        """
        if not self.reference_query:
            return False, "Reference query is required"

        # Check if we have the required data for execution
        if self.has_multi_table_setup():
            # Multi-table system: check if all tables have submit datasets
            if not all(table.submit_dataset_sql for table in self.tables.all()):
                return False, "All tables must have submit dataset SQL defined"
        else:
            # Legacy system: check if submit dataset exists
            if not self.schema_sql or not self.submit_dataset_sql:
                return False, "Schema SQL and submit dataset are required for legacy challenges"

        try:
            from .utils import execute_dual_dataset_query, normalize_json_result, ensure_consistent_column_order
            result = execute_dual_dataset_query(
                challenge=self,
                query=self.reference_query,
                flag_id=2,  # Submit dataset
                engine='mysql'
            )

            if result['success']:
                # Ensure consistent column ordering before normalization
                raw_results = result['results']
                columns = result.get('columns', [])

                # Apply consistent column ordering
                ordered_results = ensure_consistent_column_order(raw_results, columns)

                # Normalize the result to handle Decimal and other non-JSON serializable types
                # Use exact order preservation for expected results
                from .utils import normalize_json_result_with_exact_order
                normalized_result = normalize_json_result_with_exact_order(ordered_results)
                self.expected_result = normalized_result
                self.save(update_fields=['expected_result'])
                return True, "Reference query executed successfully on submit dataset with consistent column and row ordering"
            else:
                return False, f"Reference query failed: {result['error']}"

        except Exception as e:
            return False, f"Error executing reference query: {str(e)}"

    def validate_user_query(self, user_query, engine='mysql', is_test_mode=False):
        """
        Execute user query on the appropriate dataset and compare with expected result.

        Args:
            user_query: The SQL query to validate
            engine: Database engine to use ('mysql' or 'postgresql')
            is_test_mode: If True, use run dataset (flag_id=1), else use submit dataset (flag_id=2)

        Returns:
            Tuple of (is_correct, message)
        """
        # Check if using dual-dataset system (legacy or multi-table)
        if (self.schema_sql and self.submit_dataset_sql) or self.has_multi_table_setup():
            return self._validate_dual_dataset_query(user_query, engine, is_test_mode)
        else:
            return False, "Challenge not properly configured with schema and expected result"

    def _validate_dual_dataset_query(self, user_query, engine, is_test_mode):
        """Validate query using the new dual-dataset system"""
        try:
            from .utils import execute_dual_dataset_query, normalize_json_result

            flag_id = 1 if is_test_mode else 2

            # Execute user query on selected dataset
            result = execute_dual_dataset_query(
                challenge=self,
                query=user_query,
                flag_id=flag_id,
                engine=engine
            )

            if not result['success']:
                return False, f"Query execution failed: {result['error']}"

            if is_test_mode:
                # For test mode, just return success (no validation against expected result)
                return True, f"Query executed successfully on test dataset. Returned {result.get('row_count', 0)} rows."
            else:
                # For submit mode, compare with expected result using consistent column ordering
                from .utils import ensure_consistent_column_order

                # Apply consistent column ordering to user results
                raw_user_results = result['results']
                columns = result.get('columns', [])
                ordered_user_results = ensure_consistent_column_order(raw_user_results, columns)

                # Normalize both results for comparison with EXACT ORDER MATCHING
                from .utils import normalize_json_result_with_exact_order

                user_result = normalize_json_result_with_exact_order(ordered_user_results)
                expected_result = normalize_json_result_with_exact_order(self.expected_result)

                if user_result == expected_result:
                    return True, "Query result matches expected output"
                else:
                    # Provide more detailed error message for debugging
                    user_count = len(user_result) if isinstance(user_result, list) else 1
                    expected_count = len(expected_result) if isinstance(expected_result, list) else 1

                    if user_count != expected_count:
                        return False, f"Query result does not match expected output. Expected {expected_count} rows, got {user_count} rows."
                    else:
                        # Check if it's a row order issue
                        # Try comparing with sorted results to see if content matches but order is wrong
                        user_result_sorted = normalize_json_result(ordered_user_results, preserve_order=False)
                        expected_result_sorted = normalize_json_result(self.expected_result, preserve_order=False)

                        if user_result_sorted == expected_result_sorted:
                            return False, f"Query result has correct data but wrong row order. Check your ORDER BY clause."
                        else:
                            return False, f"Query result does not match expected output. Expected {expected_count} rows with different values or order."

        except Exception as e:
            return False, f"Error validating query: {str(e)}"



    def get_database_schema_config(self):
        """Get the database schema configuration from settings"""
        from django.conf import settings

        if self.database_schema_type == 'custom':
            return {
                'name': 'Custom Schema',
                'description': 'Custom database schema',
                'initialization_sql': {
                    'sqlite': self.custom_initialization_sql,
                    'postgresql': self.custom_initialization_sql,
                    'mysql': self.custom_initialization_sql,
                },
                'schema': self.custom_database_schema
            }

        return settings.CHALLENGE_DATABASE_SCHEMAS.get(
            self.database_schema_type,
            settings.CHALLENGE_DATABASE_SCHEMAS['employees']
        )

    def get_initialization_sql(self, engine='mysql'):
        """Get initialization SQL for the specified database engine"""
        schema_config = self.get_database_schema_config()
        return schema_config['initialization_sql'].get(engine, '')

    def get_database_schema(self):
        """Get the database schema information"""
        schema_config = self.get_database_schema_config()
        return schema_config.get('schema', {})



    def get_supported_engines(self):
        """Get list of supported database engines"""
        if isinstance(self.supported_engines, list) and self.supported_engines:
            # Filter out SQLite if it exists in the list
            return [engine for engine in self.supported_engines if engine != 'sqlite']
        return ['mysql', 'postgresql']

    @property
    def expected_result_json(self):
        """Return expected result as formatted JSON string."""
        return json.dumps(self.expected_result, indent=2)

    def user_has_access(self, user):
        """Check if user has access to this challenge"""
        # All challenges require authentication
        if not user or not user.is_authenticated:
            return False

        # Free challenges are accessible to authenticated users
        if self.subscription_type == 'free':
            return True

        # Paid challenges require active subscription
        # Check if user has active challenge subscription
        active_subscription = UserChallengeSubscription.objects.filter(
            user=user,
            status='active'
        ).first()

        return active_subscription and active_subscription.is_active

    @property
    def is_premium(self):
        """Check if this is a premium challenge"""
        return self.subscription_type == 'paid'

    def get_supported_engines(self):
        """Get list of supported database engines for this challenge"""
        if self.supported_engines:
            # Filter out SQLite if it exists in the list
            return [engine for engine in self.supported_engines if engine != 'sqlite']
        # Default to MySQL and PostgreSQL (hosting service engines)
        return ['mysql', 'postgresql']

    def supports_engine(self, engine):
        """Check if challenge supports a specific database engine"""
        return engine in self.get_supported_engines()

    def get_challenge_database_path(self, user, engine='sqlite'):
        """Get the path to the challenge-specific database for a user"""
        from django.conf import settings
        import os

        # Create challenge-specific database path
        db_dir = os.path.join(settings.MEDIA_ROOT, 'challenge_databases', str(user.id))
        os.makedirs(db_dir, exist_ok=True)

        # Different file extensions for different engines
        if engine == 'sqlite':
            return os.path.join(db_dir, f'challenge_{self.id}.db')
        else:
            # For PostgreSQL and MySQL, we'll use a different naming convention
            return os.path.join(db_dir, f'challenge_{self.id}_{engine}.db')

    def initialize_challenge_database(self, user, engine='mysql'):
        """Initialize the challenge database with sample data for specified engine"""
        from .utils import DatabaseEngineManager

        # Use the new database engine manager with simplified schema system
        db_manager = DatabaseEngineManager(engine)
        return db_manager.initialize_challenge_database(self, user)

    def _load_sample_data(self, cursor, file_path):
        """Load sample data from CSV or SQL file"""
        import csv
        import os

        if not os.path.exists(file_path):
            return

        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.sql':
            # Execute SQL file
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                for statement in statements:
                    cursor.execute(statement)

        elif file_extension == '.csv':
            # Load CSV data (requires table name to be specified in database_schema)
            if 'tables' in self.database_schema:
                for table_name, table_info in self.database_schema['tables'].items():
                    if table_info.get('data_file') == os.path.basename(file_path):
                        self._load_csv_to_table(cursor, file_path, table_name, table_info)

    def _load_csv_to_table(self, cursor, csv_path, table_name, table_info):
        """Load CSV data into a specific table"""
        import csv

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Get column names and types from table_info
            columns = table_info.get('columns', [])
            if not columns:
                # Infer from CSV headers
                columns = list(reader.fieldnames)

            # Create table if it doesn't exist
            if columns:
                column_defs = []
                for col in columns:
                    if isinstance(col, dict):
                        col_name = col['name']
                        col_type = col.get('type', 'TEXT')
                        column_defs.append(f"{col_name} {col_type}")
                    else:
                        column_defs.append(f"{col} TEXT")

                create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
                cursor.execute(create_sql)

                # Insert data
                for row in reader:
                    placeholders = ', '.join(['?' for _ in row])
                    insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                    cursor.execute(insert_sql, list(row.values()))


class UserChallengeProgress(models.Model):
    """
    Track user progress on challenges.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='challenge_progress')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='user_progress')
    is_completed = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    best_query = models.TextField(blank=True)
    xp_earned = models.PositiveIntegerField(default=0, help_text="XP earned from completing this challenge")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'challenge']

    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"{self.user.email} - {self.challenge.title} ({status})"


class XPTransaction(models.Model):
    """
    Track XP transactions for audit purposes and detailed history.
    """
    TRANSACTION_TYPE_CHOICES = [
        ('challenge_completion', 'Challenge Completion'),
        ('bonus', 'Bonus XP'),
        ('adjustment', 'Manual Adjustment'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='xp_transactions')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, null=True, blank=True, related_name='xp_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, default='challenge_completion')
    xp_amount = models.IntegerField(help_text="XP amount (can be negative for deductions)")
    description = models.CharField(max_length=255, help_text="Description of the XP transaction")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.xp_amount} XP ({self.transaction_type})"


class ChallengeSubscriptionPlan(models.Model):
    """Subscription plans for challenges"""
    DURATION_CHOICES = [
        ('1_month', '1 Month'),
        ('2_months', '2 Months'),
        ('3_months', '3 Months'),
        ('6_months', '6 Months'),
        ('9_months', '9 Months'),
        ('12_months', '12 Months'),
        ('24_months', '24 Months'),
        ('unlimited', 'Unlimited'),
    ]

    name = models.CharField(max_length=100)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    features = models.JSONField(default=list, help_text="List of features for this plan")
    is_active = models.BooleanField(default=True)
    is_recommended = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'price']

    def __str__(self):
        return f"{self.name} ({self.get_duration_display()})"

    @property
    def effective_price(self):
        """Return the effective price (discounted if available)"""
        return self.price

    @property
    def formatted_price(self):
        """Get formatted price with currency symbol"""
        from django.conf import settings
        currency = getattr(settings, 'RAZORPAY_CURRENCY', 'INR').upper()
        if currency == 'INR':
            return f"₹{self.price:.2f}"
        else:
            return f"${self.price:.2f}"

    @property
    def formatted_original_price(self):
        """Get formatted original price with currency symbol"""
        from django.conf import settings
        currency = getattr(settings, 'RAZORPAY_CURRENCY', 'INR').upper()
        if currency == 'INR':
            return f"₹{self.original_price:.2f}"
        else:
            return f"${self.original_price:.2f}"

    @property
    def has_discount(self):
        """Check if plan has a discount"""
        return self.original_price and self.original_price > self.price

    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.has_discount:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    def get_duration_days(self):
        """Get duration in days"""
        duration_map = {
            '1_month': 30,
            '2_months': 60,
            '3_months': 90,
            '6_months': 180,
            '9_months': 270,
            '12_months': 365,
            '24_months': 730,
            'unlimited': None,
        }
        return duration_map.get(self.duration)


class UserChallengeSubscription(models.Model):
    """User subscriptions to challenges"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending Payment'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='challenge_subscriptions')
    plan = models.ForeignKey(ChallengeSubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions')

    # Subscription details
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)  # Null for unlimited plans
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Payment tracking
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=255, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)

    # Pending payment expiration
    pending_expires_at = models.DateTimeField(null=True, blank=True, help_text="When pending payment expires")

    # Notifications
    expiry_notification_sent = models.BooleanField(default=False)
    final_notification_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - Challenge Subscription ({self.plan.name})"

    @property
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status != 'active':
            return False

        if self.end_date is None:  # Unlimited plan
            return True

        return timezone.now() <= self.end_date

    @property
    def is_pending_expired(self):
        """Check if pending payment has expired"""
        if self.status != 'pending':
            return False

        if self.pending_expires_at is None:
            return False

        return timezone.now() > self.pending_expires_at

    @property
    def is_expiring_soon(self):
        """Check if subscription expires within 7 days"""
        if self.end_date is None:
            return False

        days_until_expiry = (self.end_date - timezone.now()).days
        return 0 <= days_until_expiry <= 7

    @property
    def days_remaining(self):
        """Get days remaining in subscription"""
        if self.end_date is None:
            return None

        days = (self.end_date - timezone.now()).days
        return max(0, days)

    @property
    def time_remaining(self):
        """Get human-readable time remaining"""
        if self.end_date is None:
            return "Unlimited"

        remaining = self.end_date - timezone.now()
        if remaining.days > 0:
            return f"{remaining.days} days"
        elif remaining.seconds > 3600:
            hours = remaining.seconds // 3600
            return f"{hours} hours"
        else:
            return "Expires soon"

    def activate(self):
        """Activate the subscription"""
        self.status = 'active'
        self.start_date = timezone.now()

        # Set end date based on plan duration
        if self.plan.duration != 'unlimited':
            duration_days = self.plan.get_duration_days()
            self.end_date = self.start_date + timedelta(days=duration_days)

        self.save()

    def expire(self):
        """Expire the subscription"""
        self.status = 'expired'
        self.save()

    def cancel_pending(self):
        """Cancel a pending subscription"""
        if self.status == 'pending':
            self.status = 'cancelled'
            self.save()

    def set_pending_expiration(self, minutes=30):
        """Set when pending payment expires"""
        self.pending_expires_at = timezone.now() + timedelta(minutes=minutes)
        self.save()

    @classmethod
    def cleanup_expired_pending(cls):
        """Clean up expired pending subscriptions"""
        expired_pending = cls.objects.filter(
            status='pending',
            pending_expires_at__lt=timezone.now()
        )
        count = expired_pending.count()
        expired_pending.update(status='expired')
        return count


# Signal to automatically ensure column ordering when challenge tables are created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=ChallengeTable)
def auto_apply_column_ordering_on_table_creation(sender, instance, created, **kwargs):
    """
    Automatically apply consistent column ordering when a challenge table is created.
    This ensures that challenges have proper column ordering from the start.
    """
    # Only process when a new table is created
    if not created:
        return

    challenge = instance.challenge

    # Only process if the challenge has a reference query
    if not challenge.reference_query:
        return

    # Skip if this is being called during the save process to avoid recursion
    if hasattr(challenge, '_applying_column_ordering'):
        return

    try:
        # Check if this challenge has all required data for execution
        has_data = False
        if challenge.has_multi_table_setup():
            # Multi-table system: check if all tables have submit datasets
            has_data = all(table.submit_dataset_sql for table in challenge.tables.all())
        else:
            # Legacy system: check if submit dataset exists
            has_data = bool(challenge.schema_sql and challenge.submit_dataset_sql)

        if not has_data:
            return  # Not ready yet, will be triggered when more tables are added

        # Set flag to prevent recursion
        challenge._applying_column_ordering = True

        # Generate expected results with proper column ordering
        success, message = challenge.execute_reference_query()

        if success:
            print(f"✅ Auto-applied consistent column ordering for challenge: {challenge.title}")
        else:
            print(f"⚠️ Failed to auto-apply column ordering for {challenge.title}: {message}")

        # Remove flag
        delattr(challenge, '_applying_column_ordering')

    except Exception as e:
        print(f"❌ Error auto-applying column ordering for {challenge.title}: {str(e)}")
        # Remove flag if it exists
        if hasattr(challenge, '_applying_column_ordering'):
            delattr(challenge, '_applying_column_ordering')
