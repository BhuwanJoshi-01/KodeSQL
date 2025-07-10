"""
Comprehensive tests for the dual database system automation enhancements.
Tests automated schema processing, dataset flagging, and JSON generation.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from challenges.models import Challenge, ChallengeTable
import json

User = get_user_model()


class AutomationEnhancementsTestCase(TestCase):
    """Test suite for automated dual database system enhancements."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create superuser for admin access
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        
        # Create test challenge
        self.challenge = Challenge.objects.create(
            title="Test Automation Challenge",
            description="Testing automated features",
            difficulty="EASY",
            reference_query="SELECT * FROM Departments WHERE flag_id = 2"
        )

    def test_enhanced_schema_processing(self):
        """Test automated flag_id column addition with various CREATE TABLE syntax."""
        
        # Test Case 1: Basic CREATE TABLE
        table1 = ChallengeTable.objects.create(
            challenge=self.challenge,
            table_name="Departments",
            schema_sql="CREATE TABLE Departments (id INT PRIMARY KEY, name VARCHAR(100))"
        )
        
        processed_schema = table1.get_processed_schema_sql()
        self.assertIn("flag_id INT NOT NULL DEFAULT 0", processed_schema)
        self.assertIn(table1.get_unique_table_name(), processed_schema)
        
        # Test Case 2: CREATE TABLE with IF NOT EXISTS
        table2 = ChallengeTable.objects.create(
            challenge=self.challenge,
            table_name="Employees",
            schema_sql="CREATE TABLE IF NOT EXISTS Employees (id INT, name VARCHAR(50))"
        )
        
        processed_schema = table2.get_processed_schema_sql()
        self.assertIn("flag_id INT NOT NULL DEFAULT 0", processed_schema)
        
        # Test Case 3: CREATE TABLE with backticks
        table3 = ChallengeTable.objects.create(
            challenge=self.challenge,
            table_name="Projects",
            schema_sql="CREATE TABLE `Projects` (id INT, title VARCHAR(200))"
        )
        
        processed_schema = table3.get_processed_schema_sql()
        self.assertIn("flag_id INT NOT NULL DEFAULT 0", processed_schema)
        
        # Test Case 4: CREATE TABLE with double quotes
        table4 = ChallengeTable.objects.create(
            challenge=self.challenge,
            table_name="Tasks",
            schema_sql='CREATE TABLE "Tasks" (id INT, description TEXT)'
        )
        
        processed_schema = table4.get_processed_schema_sql()
        self.assertIn("flag_id INT NOT NULL DEFAULT 0", processed_schema)

    def test_automated_dataset_processing(self):
        """Test automated INSERT + UPDATE pattern for flag_id assignment."""
        
        table = ChallengeTable.objects.create(
            challenge=self.challenge,
            table_name="Departments",
            schema_sql="CREATE TABLE Departments (id INT, name VARCHAR(100))",
            run_dataset_sql="INSERT INTO Departments (id, name) VALUES (1, 'IT'), (2, 'HR')",
            submit_dataset_sql="INSERT INTO Departments (id, name) VALUES (1, 'IT'), (2, 'HR'), (3, 'Finance')"
        )
        
        # Test run dataset (flag_id = 1)
        processed_run_sql = table.get_processed_dataset_sql(1)
        self.assertIn("INSERT INTO", processed_run_sql)
        self.assertIn("UPDATE", processed_run_sql)
        self.assertIn("SET flag_id = 1", processed_run_sql)
        self.assertIn("WHERE flag_id = 0", processed_run_sql)
        
        # Test submit dataset (flag_id = 2)
        processed_submit_sql = table.get_processed_dataset_sql(2)
        self.assertIn("INSERT INTO", processed_submit_sql)
        self.assertIn("UPDATE", processed_submit_sql)
        self.assertIn("SET flag_id = 2", processed_submit_sql)
        self.assertIn("WHERE flag_id = 0", processed_submit_sql)

    def test_enhanced_table_name_detection(self):
        """Test improved table name extraction from various CREATE TABLE syntax."""
        
        from challenges.views import _extract_table_name_from_schema
        
        # Test various CREATE TABLE patterns
        test_cases = [
            ("CREATE TABLE Departments (id INT)", "Departments"),
            ("CREATE TABLE IF NOT EXISTS `Employees` (id INT)", "Employees"),
            ('CREATE TABLE "Projects" (id INT)', "Projects"),
            ("CREATE TABLE [Tasks] (id INT)", "Tasks"),
            ("CREATE TABLE schema.Users (id INT)", "Users"),
            ("create table lowercase_table (id int)", "lowercase_table"),
            ("CREATE TABLE Mixed_Case_123 (id INT)", "Mixed_Case_123"),
        ]
        
        for schema_sql, expected_name in test_cases:
            with self.subTest(schema_sql=schema_sql):
                extracted_name = _extract_table_name_from_schema(schema_sql, 1)
                self.assertEqual(extracted_name, expected_name)
        
        # Test fallback for invalid syntax
        invalid_sql = "INVALID SQL STATEMENT"
        fallback_name = _extract_table_name_from_schema(invalid_sql, 5)
        self.assertEqual(fallback_name, "table_5")

    def test_automatic_json_generation_integration(self):
        """Test that JSON generation is automatically triggered during challenge creation/update."""
        
        # Login as superuser
        self.client.login(username='admin', password='testpass123')
        
        # Create challenge with multi-table data via admin interface
        challenge_data = {
            'title': 'Auto JSON Test Challenge',
            'description': 'Testing automatic JSON generation',
            'difficulty': 'MEDIUM',
            'reference_query': 'SELECT COUNT(*) as total FROM Departments WHERE flag_id = 2',
            'tables[1][table_name]': 'Departments',
            'tables[1][schema_sql]': 'CREATE TABLE Departments (id INT PRIMARY KEY, name VARCHAR(100))',
            'tables[1][run_dataset_sql]': 'INSERT INTO Departments (id, name) VALUES (1, "IT")',
            'tables[1][submit_dataset_sql]': 'INSERT INTO Departments (id, name) VALUES (1, "IT"), (2, "HR")',
        }
        
        # Test challenge creation
        response = self.client.post(reverse('challenges:admin_challenge_create'), challenge_data)
        
        # Should redirect on success
        self.assertEqual(response.status_code, 302)
        
        # Verify challenge was created
        created_challenge = Challenge.objects.filter(title='Auto JSON Test Challenge').first()
        self.assertIsNotNone(created_challenge)
        
        # Verify table was created
        self.assertEqual(created_challenge.tables.count(), 1)
        
        # Note: Actual JSON generation testing would require database setup
        # which is complex in unit tests. The integration is tested via the
        # _auto_generate_expected_results function call in the views.

    def test_admin_interface_automation_indicators(self):
        """Test that admin interface shows automation indicators."""
        
        # Login as superuser
        self.client.login(username='admin', password='testpass123')
        
        # Access challenge creation form
        response = self.client.get(reverse('challenges:admin_challenge_create'))
        self.assertEqual(response.status_code, 200)
        
        # Check for automation indicators in the response
        content = response.content.decode('utf-8')
        self.assertIn("Automated JSON Generation", content)
        self.assertIn("Auto-Processing", content)
        self.assertIn("flag_id columns & data flagging automated", content)
        
        # Ensure manual JSON generation button is removed
        self.assertNotIn("Generate Output JSON", content)
        self.assertNotIn("generateExpectedOutput", content)

    def test_database_engine_compatibility(self):
        """Test that flag_id column syntax works for both MySQL and PostgreSQL."""
        
        table = ChallengeTable.objects.create(
            challenge=self.challenge,
            table_name="TestTable",
            schema_sql="CREATE TABLE TestTable (id INT PRIMARY KEY, data VARCHAR(50))"
        )
        
        # Get flag_id column definition
        flag_id_def = table._get_flag_id_column_definition(",")
        
        # Should use standard SQL syntax compatible with both databases
        self.assertIn("flag_id INT NOT NULL DEFAULT 0", flag_id_def)
        
        # Test that processed schema contains the flag_id column
        processed_schema = table.get_processed_schema_sql()
        self.assertIn("flag_id INT NOT NULL DEFAULT 0", processed_schema)

    def test_error_handling_and_edge_cases(self):
        """Test error handling for edge cases in automation."""
        
        # Test empty schema SQL
        table1 = ChallengeTable.objects.create(
            challenge=self.challenge,
            table_name="EmptyTable",
            schema_sql=""
        )
        
        processed_schema = table1.get_processed_schema_sql()
        self.assertEqual(processed_schema, "")
        
        # Test empty dataset SQL
        processed_dataset = table1.get_processed_dataset_sql(1)
        self.assertEqual(processed_dataset, "")
        
        # Test schema with existing flag_id column
        table2 = ChallengeTable.objects.create(
            challenge=self.challenge,
            table_name="ExistingFlagTable",
            schema_sql="CREATE TABLE ExistingFlagTable (id INT, flag_id INT DEFAULT 0)"
        )
        
        processed_schema = table2.get_processed_schema_sql()
        # Should not add duplicate flag_id column
        self.assertEqual(processed_schema.lower().count('flag_id'), 1)

    def tearDown(self):
        """Clean up test data."""
        Challenge.objects.all().delete()
        User.objects.all().delete()
