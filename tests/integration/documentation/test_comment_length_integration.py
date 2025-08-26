"""Integration tests for "Table comments must be at least 10 characters" scenario.

Layer 2 tests that create real Databricks tables, discover them, and validate comment length.
Uses pytest patterns with real Databricks SDK integration.
"""

import os

import pytest
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

from tests.fixtures.documentation.table_comment_specs import TABLE_SPECS_COMMENT_LENGTH
from tests.fixtures.table_factory import create_test_tables_for_comment_length_scenario
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
def comment_length_test_tables(databricks_client):
    """Class-scoped test tables for comment length - create for each test class, cleanup after."""
    with create_test_tables_for_comment_length_scenario(databricks_client) as created_tables:
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
class TestCommentLengthIntegration:
    """Integration tests for comment length validation.

    Tests the "Table comments must be at least 10 characters" scenario end-to-end.
    Uses dedicated test tables designed specifically for length validation.
    """

    def _get_table_by_fixture_key(self, fixture_dict, key, discovered_tables):
        """Helper to get a table by fixture key from discovered tables."""
        table_name = fixture_dict[key]
        for table in discovered_tables:
            if table.full_name == table_name:
                return table
        return None

    def test_end_to_end_comment_length_validation(self, comment_length_test_tables, validator, integration_discovery):
        """Test complete end-to-end flow: create → discover → validate comment length."""
        # Verify we created the expected tables
        expected_count = len(TABLE_SPECS_COMMENT_LENGTH)
        assert (
            len(comment_length_test_tables) == expected_count
        ), f"Expected {expected_count} tables, created {len(comment_length_test_tables)}"

        # Discover the tables we just created
        discovered_tables = integration_discovery.discover_tables()

        # Filter to only our comment length test tables
        discovered_length_tables = [table for table in discovered_tables if table.table.startswith("length_test_")]

        # Should have discovered all our test tables
        assert (
            len(discovered_length_tables) == expected_count
        ), f"Expected {expected_count} tables, found {len(discovered_length_tables)}"

        # Validate each discovered table for comment length
        length_results = {}
        for table in discovered_length_tables:
            validation_result = validator.has_minimum_length(table)
            length_results[table.table] = validation_result

        # Check results match expectations from our specs
        expected_results = {}
        for spec in TABLE_SPECS_COMMENT_LENGTH.values():
            expected_results[spec.name] = spec.expected_pass

        assert length_results == expected_results, f"Length validation results mismatch: {length_results}"

    def test_comment_length_boundary_conditions(self, comment_length_test_tables, validator, integration_discovery):
        """Test boundary conditions (9 vs 10 vs 11 characters) with real Databricks tables."""
        discovered_tables = integration_discovery.discover_tables()

        # Test exactly 9 characters (should fail)
        table_9_chars = None
        for table in discovered_tables:
            if table.table == "length_test_exactly_9":
                table_9_chars = table
                break

        assert table_9_chars is not None, "Should find 9-character test table"
        assert len(table_9_chars.comment) == 9, f"Expected 9 chars, got {len(table_9_chars.comment)}"
        assert validator.has_minimum_length(table_9_chars) is False, "9-character comment should fail"

        # Test exactly 10 characters (should pass)
        table_10_chars = None
        for table in discovered_tables:
            if table.table == "length_test_exactly_10":
                table_10_chars = table
                break

        assert table_10_chars is not None, "Should find 10-character test table"
        assert len(table_10_chars.comment) == 10, f"Expected 10 chars, got {len(table_10_chars.comment)}"
        assert validator.has_minimum_length(table_10_chars) is True, "10-character comment should pass"

    def test_unicode_comment_length_integration(self, comment_length_test_tables, validator, integration_discovery):
        """Test Unicode character handling in comment length validation."""
        # Use the specific table from our fixture instead of discovery
        unicode_table_name = comment_length_test_tables["unicode_comment"]
        discovered_tables = integration_discovery.discover_tables()

        # Find our specific Unicode test table
        unicode_table = None
        for table in discovered_tables:
            if table.full_name == unicode_table_name:
                unicode_table = table
                break

        assert unicode_table is not None, f"Should find Unicode test table: {unicode_table_name}"
        assert "🚀" in unicode_table.comment, "Comment should contain Unicode characters"

        # Unicode characters should count as single characters
        comment_length = len(unicode_table.comment)
        assert comment_length >= 10, f"Unicode comment should be >= 10 chars, got {comment_length}"
        assert validator.has_minimum_length(unicode_table) is True, "Unicode comment should pass length validation"

    def test_whitespace_handling_integration(self, comment_length_test_tables, validator, integration_discovery):
        """Test that whitespace is counted toward length in integration environment."""
        # Use specific table from our fixture
        whitespace_table_name = comment_length_test_tables["whitespace_10_chars"]
        discovered_tables = integration_discovery.discover_tables()

        # Find our specific whitespace test table
        whitespace_table = None
        for table in discovered_tables:
            if table.full_name == whitespace_table_name:
                whitespace_table = table
                break

        assert whitespace_table is not None, f"Should find whitespace test table: {whitespace_table_name}"

        # "  test    " should be exactly 10 characters
        assert len(whitespace_table.comment) == 10, f"Expected 10 chars, got {len(whitespace_table.comment)}"
        assert validator.has_minimum_length(whitespace_table) is True, "10-char comment with spaces should pass"

    def test_none_and_empty_comments_integration(self, comment_length_test_tables, validator, integration_discovery):
        """Test None and empty comment handling in integration environment."""
        # Use specific tables from our fixture
        none_table_name = comment_length_test_tables["none_comment"]
        empty_table_name = comment_length_test_tables["empty_comment"]
        discovered_tables = integration_discovery.discover_tables()

        # Test None comment
        none_table = None
        for table in discovered_tables:
            if table.full_name == none_table_name:
                none_table = table
                break

        assert none_table is not None, f"Should find None comment test table: {none_table_name}"
        assert none_table.comment is None, "Comment should be None"
        assert validator.has_minimum_length(none_table) is False, "None comment should fail length validation"

        # Test empty comment
        empty_table = None
        for table in discovered_tables:
            if table.full_name == empty_table_name:
                empty_table = table
                break

        assert empty_table is not None, f"Should find empty comment test table: {empty_table_name}"
        # NOTE: Databricks converts empty string comments to None when stored
        assert empty_table.comment is None, "Comment should be None (Databricks converts empty strings to None)"
        assert validator.has_minimum_length(empty_table) is False, "Empty comment should fail length validation"

    @pytest.mark.parametrize(
        "fixture_key,expected_pass",
        [
            ("long_comment", True),
            ("exactly_10_chars", True),
            ("exactly_9_chars", False),
            ("short_comment", False),
            ("unicode_comment", True),
            ("whitespace_10_chars", True),
            ("none_comment", False),
            ("empty_comment", False),
        ],
    )
    def test_individual_length_validation_parametrized(
        self, comment_length_test_tables, validator, integration_discovery, fixture_key, expected_pass
    ):
        """Test validation of individual comment length tables using parametrize."""
        # Use the fixture to get the specific table
        target_table = self._get_table_by_fixture_key(
            comment_length_test_tables, fixture_key, integration_discovery.discover_tables()
        )

        assert target_table is not None, f"Could not find test table for fixture key: {fixture_key}"

        # Validate the table
        result = validator.has_minimum_length(target_table)
        assert (
            result is expected_pass
        ), f"Table {target_table.full_name} length validation mismatch. Expected {expected_pass}, got {result}. Comment: '{target_table.comment}'"

    def test_comment_length_configuration_integration(self, validator):
        """Test that comment length validation respects configuration in integration environment."""
        # Test default validator configuration
        assert validator.minimum_comment_length == 10, "Default configuration should be 10 characters"

        # Test that configuration is loaded properly
        # (Future: when config loading is implemented, test config file values)

    def test_discovery_finds_all_length_test_tables(self, comment_length_test_tables, integration_discovery):
        """Test that discovery engine finds all our comment length test tables."""
        # Verify tables were created
        expected_count = len(TABLE_SPECS_COMMENT_LENGTH)
        assert len(comment_length_test_tables) == expected_count, "Should have created all test tables"

        discovered_tables = integration_discovery.discover_tables()

        # Should find all length test tables in pytest_test_data schema
        length_test_tables = [table for table in discovered_tables if table.table.startswith("length_test_")]

        assert (
            len(length_test_tables) == expected_count
        ), f"Discovery should find all {expected_count} length test tables, found {len(length_test_tables)}"

        # Verify all expected table names are present
        found_table_names = {table.table for table in length_test_tables}
        expected_table_names = {spec.name for spec in TABLE_SPECS_COMMENT_LENGTH.values()}

        assert (
            found_table_names == expected_table_names
        ), f"Table name mismatch. Expected: {expected_table_names}, Found: {found_table_names}"
