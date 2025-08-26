"""Integration tests for "Tables must have a comment" scenario.

Layer 2 tests that create real Databricks tables, discover them, and validate.
Uses pytest patterns with real Databricks SDK integration.
"""

import os

import pytest
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

from tests.fixtures.documentation.table_comment_specs import TABLE_SPECS_HAS_COMMENT
from tests.fixtures.table_factory import create_test_tables_for_comment_scenario
from tests.utils.discovery_engine import create_integration_discovery
from tests.validators.documentation import DocumentationValidator

# Load environment variables
load_dotenv()


@pytest.fixture(scope="class")
def databricks_client():
    """Class-scoped Databricks client fixture."""
    return WorkspaceClient()


@pytest.fixture(scope="class")
@pytest.mark.skipif(
    os.getenv("CREATE_TEST_TABLES") != "true", reason="Integration tests require CREATE_TEST_TABLES=true"
)
def test_tables(databricks_client):
    """Class-scoped test tables - create for each test class, cleanup after."""
    with create_test_tables_for_comment_scenario(databricks_client) as created_tables:
        yield created_tables


@pytest.fixture(scope="class")
def validator():
    """Documentation validator fixture - reused across all tests in a class."""
    return DocumentationValidator()


@pytest.fixture(scope="class")
def integration_discovery(databricks_client):
    """Discovery engine configured for integration testing - reused across all tests in a class."""
    return create_integration_discovery(databricks_client)


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("CREATE_TEST_TABLES") != "true", reason="Integration tests require CREATE_TEST_TABLES=true"
)
class TestTableCommentIntegration:
    """Integration tests for table comment validation.

    Creates real test tables, discovers them, and validates end-to-end.
    """

    def _get_table_by_fixture_key(self, fixture_dict, key, discovered_tables):
        """Helper to get a table by fixture key from discovered tables."""
        table_name = fixture_dict[key]
        for table in discovered_tables:
            if table.full_name == table_name:
                return table
        return None

    def test_end_to_end_table_comment_validation(self, test_tables, validator, integration_discovery):
        """Test complete end-to-end flow: create → discover → validate."""
        # Verify we created the expected tables
        assert len(test_tables) == len(
            TABLE_SPECS_HAS_COMMENT
        ), f"Expected {len(TABLE_SPECS_HAS_COMMENT)} tables, created {len(test_tables)}"

        # Discover the tables we just created
        discovered_tables = integration_discovery.discover_tables()

        # Filter to only our test tables
        discovered_test_tables = [table for table in discovered_tables if table.table.startswith("test_table_")]

        # Should have discovered all our test tables
        assert len(discovered_test_tables) == len(
            TABLE_SPECS_HAS_COMMENT
        ), f"Expected {len(TABLE_SPECS_HAS_COMMENT)} tables, found {len(discovered_test_tables)}"

        # Validate each discovered table for comment existence
        comment_results = {}
        for table in discovered_test_tables:
            validation_result = validator.has_comment(table)
            comment_results[table.table] = validation_result

        # Check comment existence results match expectations
        expected_comment_results = {
            "test_table_with_comment": True,  # Has valid comment
            "test_table_without_comment": False,  # None comment
            "test_table_empty_comment": False,  # Empty string comment
            "test_table_whitespace_comment": False,  # Whitespace-only comment
        }

        assert comment_results == expected_comment_results, f"Comment validation results mismatch: {comment_results}"

    def test_table_discovery_finds_test_schema(self, test_tables, integration_discovery):
        """Test that discovery engine can find our test schema."""
        # Verify tables were created
        assert len(test_tables) > 0, "Should have created test tables"

        discovered_tables = integration_discovery.discover_tables()

        # Should find tables in pytest_test_data schema
        test_schema_tables = [table for table in discovered_tables if table.schema == "pytest_test_data"]

        assert len(test_schema_tables) > 0, "Discovery should find tables in pytest_test_data schema"

    @pytest.mark.parametrize(
        "spec_name,expected_pass",
        [
            ("with_comment", True),
            ("without_comment", False),
            ("empty_comment", False),
            ("whitespace_comment", False),
        ],
    )
    def test_individual_table_validation(self, test_tables, validator, integration_discovery, spec_name, expected_pass):
        """Test validation of individual test tables using parametrize."""
        # Use the fixture to get the specific table
        target_table = self._get_table_by_fixture_key(test_tables, spec_name, integration_discovery.discover_tables())

        assert target_table is not None, f"Could not find test table for fixture key: {spec_name}"

        # Validate the table
        result = validator.has_comment(target_table)
        assert (
            result is expected_pass
        ), f"Table {target_table.full_name} validation mismatch. Expected {expected_pass}, got {result}. Comment: '{target_table.comment}'"

    def test_discovery_configuration_limits(self, databricks_client):
        """Test that discovery respects configured limits (with room for expansion)."""
        # Create discovery with reasonable limits that allow our current tests plus future expansion
        from tests.utils.discovery_engine import DatabricksDiscovery, DiscoveryConfig

        config = DiscoveryConfig(
            target_catalogs=["workspace"],
            target_schemas=["pytest_test_data"],
            max_tables_per_schema=16,  # Room for expansion beyond our current 4 tables
            max_total_tables=16,
        )
        discovery_with_limits = DatabricksDiscovery(databricks_client, config)

        discovered_tables = discovery_with_limits.discover_tables()

        # Filter to only our test tables (ignore any leftover tables from other tests)
        our_test_tables = [table for table in discovered_tables if table.table.startswith("test_table_")]

        # Should find all our test tables (and respect limits for larger scenarios)
        assert (
            len(our_test_tables) == 4
        ), f"Should find all 4 test tables, found {len(our_test_tables)} test tables (total discovered: {len(discovered_tables)})"
        assert len(discovered_tables) <= 16, f"Should respect max_total_tables=16, found {len(discovered_tables)}"

    def test_table_comment_property_extraction(self, integration_discovery):
        """Test that table comments are properly extracted from Databricks."""
        discovered_tables = integration_discovery.discover_tables()

        # Find table with comment
        table_with_comment = None
        for table in discovered_tables:
            if table.table == "test_table_with_comment":
                table_with_comment = table
                break

        assert table_with_comment is not None
        assert table_with_comment.comment is not None
        assert "valid comment for testing" in table_with_comment.comment

        # Find table without comment
        table_without_comment = None
        for table in discovered_tables:
            if table.table == "test_table_without_comment":
                table_without_comment = table
                break

        assert table_without_comment is not None
        assert table_without_comment.comment is None
