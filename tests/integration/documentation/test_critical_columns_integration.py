"""Integration tests for "Critical columns must be documented" scenario.

Layer 2 tests that create real Databricks tables with critical columns, discover them, and validate documentation.
Uses pytest patterns with real Databricks SDK integration.
"""

import os

import pytest
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

from tests.fixtures.documentation.critical_columns_specs import TABLE_SPECS_CRITICAL_COLUMNS
from tests.fixtures.table_factory import create_test_tables_for_critical_columns_scenario
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
def critical_columns_test_tables(databricks_client):
    """Class-scoped test tables for critical columns - create for each test class, cleanup after."""
    with create_test_tables_for_critical_columns_scenario(databricks_client) as created_tables:
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
class TestCriticalColumnsIntegration:
    """Integration tests for critical column documentation validation.

    Tests the "Critical columns must be documented" scenario end-to-end.
    Uses dedicated test tables designed specifically for critical column validation.
    """

    def _get_table_by_fixture_key(self, fixture_dict, key, discovered_tables):
        """Helper to get a table by fixture key from discovered tables."""
        table_name = fixture_dict[key]
        for table in discovered_tables:
            if table.full_name == table_name:
                return table
        return None

    def test_end_to_end_critical_columns_validation(
        self, critical_columns_test_tables, validator, integration_discovery
    ):
        """Test complete end-to-end flow: create → discover → validate critical column documentation."""
        # Verify we created the expected tables
        expected_count = len(TABLE_SPECS_CRITICAL_COLUMNS)
        assert (
            len(critical_columns_test_tables) == expected_count
        ), f"Expected {expected_count} tables, created {len(critical_columns_test_tables)}"

        # Discover the tables we just created
        discovered_tables = integration_discovery.discover_tables()

        # Filter to only our critical column test tables
        discovered_critical_tables = [table for table in discovered_tables if table.table.startswith("critical_test_")]

        # Should have discovered all our test tables
        assert (
            len(discovered_critical_tables) == expected_count
        ), f"Expected {expected_count} tables, found {len(discovered_critical_tables)}"

        # Validate each discovered table for critical column documentation
        critical_column_results = {}
        for table in discovered_critical_tables:
            validation_result = validator.has_all_critical_columns_documented(table)
            critical_column_results[table.table] = validation_result

        # Check results match expectations from our specs
        expected_results = {}
        for spec in TABLE_SPECS_CRITICAL_COLUMNS.values():
            expected_results[spec.name] = spec.expected_pass

        assert (
            critical_column_results == expected_results
        ), f"Critical column validation results mismatch: {critical_column_results}"

    def test_get_undocumented_critical_columns_integration(
        self, critical_columns_test_tables, validator, integration_discovery
    ):
        """Test that get_undocumented_critical_columns returns correct undocumented columns."""
        discovered_tables = integration_discovery.discover_tables()

        # Test table with some undocumented critical columns
        some_undocumented_table = self._get_table_by_fixture_key(
            critical_columns_test_tables, "some_critical_undocumented", discovered_tables
        )
        assert some_undocumented_table is not None, "Should find some_critical_undocumented table"

        undocumented_columns = validator.get_undocumented_critical_columns(some_undocumented_table)
        expected_undocumented = ["user_id", "account_balance"]  # From our table spec
        assert set(undocumented_columns) == set(
            expected_undocumented
        ), f"Expected {expected_undocumented}, got {undocumented_columns}"

        # Test table with all documented critical columns
        all_documented_table = self._get_table_by_fixture_key(
            critical_columns_test_tables, "all_critical_documented", discovered_tables
        )
        assert all_documented_table is not None, "Should find all_critical_documented table"

        undocumented_columns = validator.get_undocumented_critical_columns(all_documented_table)
        assert (
            undocumented_columns == []
        ), f"All documented table should have no undocumented critical columns, got {undocumented_columns}"

    def test_no_critical_columns_table_passes(self, critical_columns_test_tables, validator, integration_discovery):
        """Test that tables with no critical columns pass validation."""
        discovered_tables = integration_discovery.discover_tables()

        no_critical_table = self._get_table_by_fixture_key(
            critical_columns_test_tables, "no_critical_columns", discovered_tables
        )
        assert no_critical_table is not None, "Should find no_critical_columns table"

        # Table with no critical columns should pass
        assert (
            validator.has_all_critical_columns_documented(no_critical_table) is True
        ), "Table with no critical columns should pass"

        # Should have no undocumented critical columns
        undocumented = validator.get_undocumented_critical_columns(no_critical_table)
        assert undocumented == [], "Table with no critical columns should have no undocumented critical columns"

    def test_mixed_critical_patterns_integration(self, critical_columns_test_tables, validator, integration_discovery):
        """Test that various critical column patterns are detected correctly."""
        discovered_tables = integration_discovery.discover_tables()

        mixed_patterns_table = self._get_table_by_fixture_key(
            critical_columns_test_tables, "mixed_critical_patterns", discovered_tables
        )
        assert mixed_patterns_table is not None, "Should find mixed_critical_patterns table"

        # Should fail because some critical columns are undocumented
        assert (
            validator.has_all_critical_columns_documented(mixed_patterns_table) is False
        ), "Mixed patterns table should fail"

        # Check specific undocumented columns
        undocumented = validator.get_undocumented_critical_columns(mixed_patterns_table)
        expected_undocumented = ["CustomerName", "security_token"]  # From our table spec
        assert set(undocumented) == set(expected_undocumented), f"Expected {expected_undocumented}, got {undocumented}"

    def test_whitespace_comments_integration(self, critical_columns_test_tables, validator, integration_discovery):
        """Test that whitespace-only comments are treated as undocumented."""
        discovered_tables = integration_discovery.discover_tables()

        whitespace_table = self._get_table_by_fixture_key(
            critical_columns_test_tables, "whitespace_comments", discovered_tables
        )
        assert whitespace_table is not None, "Should find whitespace_comments table"

        # Should fail because critical columns have whitespace/empty comments
        assert (
            validator.has_all_critical_columns_documented(whitespace_table) is False
        ), "Whitespace comments table should fail"

        # Check that whitespace/empty comments are detected as undocumented
        undocumented = validator.get_undocumented_critical_columns(whitespace_table)
        expected_undocumented = ["user_id", "payment_method"]  # Columns with whitespace/empty comments
        assert set(undocumented) == set(expected_undocumented), f"Expected {expected_undocumented}, got {undocumented}"

    def test_edge_case_patterns_integration(self, critical_columns_test_tables, validator, integration_discovery):
        """Test edge case critical column patterns like short 'id' and specific PII patterns."""
        discovered_tables = integration_discovery.discover_tables()

        edge_cases_table = self._get_table_by_fixture_key(
            critical_columns_test_tables, "edge_case_patterns", discovered_tables
        )
        assert edge_cases_table is not None, "Should find edge_case_patterns table"

        # Should fail because some critical columns are undocumented
        assert validator.has_all_critical_columns_documented(edge_cases_table) is False, "Edge cases table should fail"

        # Check specific undocumented columns
        undocumented = validator.get_undocumented_critical_columns(edge_cases_table)
        expected_undocumented = ["ssn", "credit_score"]  # PII and Financial patterns without documentation
        assert set(undocumented) == set(expected_undocumented), f"Expected {expected_undocumented}, got {undocumented}"

    @pytest.mark.parametrize(
        "fixture_key,expected_pass",
        [
            ("all_critical_documented", True),
            ("some_critical_undocumented", False),
            ("all_critical_undocumented", False),
            ("no_critical_columns", True),
            ("mixed_critical_patterns", False),
            ("whitespace_comments", False),
            ("edge_case_patterns", False),
        ],
    )
    def test_individual_critical_column_validation_parametrized(
        self, critical_columns_test_tables, validator, integration_discovery, fixture_key, expected_pass
    ):
        """Test validation of individual critical column tables using parametrize."""
        # Use the fixture to get the specific table
        target_table = self._get_table_by_fixture_key(
            critical_columns_test_tables, fixture_key, integration_discovery.discover_tables()
        )

        assert target_table is not None, f"Could not find test table for fixture key: {fixture_key}"

        # Validate the table
        result = validator.has_all_critical_columns_documented(target_table)
        assert (
            result is expected_pass
        ), f"Table {target_table.full_name} critical column validation mismatch. Expected {expected_pass}, got {result}"

        # Also test the detailed method for failure cases
        if not expected_pass:
            undocumented = validator.get_undocumented_critical_columns(target_table)
            assert (
                len(undocumented) > 0
            ), f"Failed table {target_table.full_name} should have undocumented critical columns"

    def test_critical_column_configuration_integration(self, validator):
        """Test that critical column validation respects configuration in integration environment."""
        # Test that validator has critical column patterns loaded
        assert hasattr(validator, "critical_column_patterns"), "Validator should have critical_column_patterns"
        assert len(validator.critical_column_patterns) > 0, "Should have at least one critical column pattern"

        # Check that common patterns are present
        patterns = [p.lower() for p in validator.critical_column_patterns]
        assert any("id" in pattern for pattern in patterns), "Should have ID patterns"
        assert any("email" in pattern for pattern in patterns), "Should have email patterns"

    def test_discovery_finds_all_critical_column_test_tables(self, critical_columns_test_tables, integration_discovery):
        """Test that discovery engine finds all our critical column test tables."""
        # Verify tables were created
        expected_count = len(TABLE_SPECS_CRITICAL_COLUMNS)
        assert len(critical_columns_test_tables) == expected_count, "Should have created all test tables"

        discovered_tables = integration_discovery.discover_tables()

        # Should find all critical test tables in pytest_test_data schema
        critical_test_tables = [table for table in discovered_tables if table.table.startswith("critical_test_")]

        assert (
            len(critical_test_tables) == expected_count
        ), f"Discovery should find all {expected_count} critical test tables, found {len(critical_test_tables)}"

        # Verify all expected table names are present
        found_table_names = {table.table for table in critical_test_tables}
        expected_table_names = {spec.name for spec in TABLE_SPECS_CRITICAL_COLUMNS.values()}

        assert (
            found_table_names == expected_table_names
        ), f"Table name mismatch. Expected: {expected_table_names}, Found: {found_table_names}"
