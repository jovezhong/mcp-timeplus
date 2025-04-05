import unittest

from dotenv import load_dotenv

from mcp_timeplus import create_timeplus_client, list_databases, list_tables, run_sql

load_dotenv()


class TestTimeplusTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the environment before tests."""
        cls.client = create_timeplus_client()

        # Prepare test database and table
        cls.test_db = "default"
        cls.test_table = "test_table"
        cls.client.command(f"CREATE DATABASE IF NOT EXISTS {cls.test_db}")

        # Drop table if exists to ensure clean state
        cls.client.command(f"DROP STREAM IF EXISTS {cls.test_db}.{cls.test_table}")

        # Create table with comments
        cls.client.command(f"""
            CREATE STREAM IF NOT EXISTS {cls.test_db}.{cls.test_table} (
                id uint32,
                name string
            )
            COMMENT 'Test table for unit testing'
        """)
        cls.client.command(f"""
            INSERT INTO {cls.test_db}.{cls.test_table} (id, name) VALUES (1, 'Alice'), (2, 'Bob')
        """)

    @classmethod
    def tearDownClass(cls):
        """Clean up the environment after tests."""
        cls.client.command(f"DROP DATABASE IF EXISTS {cls.test_db}")

    def test_list_databases(self):
        """Test listing databases."""
        result = list_databases()
        self.assertIn(self.test_db, result)

    def test_list_tables_without_like(self):
        """Test listing tables without a 'LIKE' filter."""
        result = list_tables(self.test_db)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], self.test_table)

    def test_list_tables_with_like(self):
        """Test listing tables with a 'LIKE' filter."""
        result = list_tables(self.test_db, like=f"{self.test_table}%")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], self.test_table)

    def test_run_select_query_success(self):
        """Test running a SELECT query successfully."""
        query = f"SELECT * FROM {self.test_db}.{self.test_table}"
        result = run_sql(query)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[0]["name"], "Alice")

    def test_run_select_query_failure(self):
        """Test running a SELECT query with an error."""
        query = f"SELECT * FROM {self.test_db}.non_existent_table"
        result = run_sql(query)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "error")
        self.assertIn("Query failed", result["message"])


    def test_table_and_column_comments(self):
        """Test that table and column comments are correctly retrieved."""
        result = list_tables(self.test_db)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

        table_info = result[0]
        # Verify table comment
        self.assertEqual(table_info["comment"], "Test table for unit testing")

        # Get columns by name for easier testing
        columns = {col["name"]: col for col in table_info["columns"]}

        # Verify column comments
        self.assertEqual(columns["id"]["comment"], "Primary identifier")
        self.assertEqual(columns["name"]["comment"], "User name field")


if __name__ == "__main__":
    unittest.main()
