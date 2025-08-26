"""Integration tests for "Column documentation must meet 80% threshold" scenario.

Layer 2 tests that create real Databricks tables, discover them, and validate column coverage.
Uses pytest patterns with real Databricks SDK integration.
"""

import os

import pytest
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

from tests.fixtures.documentation.column_coverage_specs import TABLE_SPECS_COLUMN_COVERAGE_THRESHOLD
from tests.fixtures.table_factory import create_test_tables_for_column_coverage_threshold_scenario
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
def column_coverage_threshold_test_tables(databricks_client):
    """Class-scoped test tables for column coverage threshold - create for each test class, cleanup after."""
    with create_test_tables_for_column_coverage_threshold_scenario(databricks_client) as created_tables:
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
class TestColumnCoverageThresholdIntegration:
    """Integration tests for column coverage threshold validation.

    Tests the "Column documentation must meet 80% threshold" scenario end-to-end.
    Uses dedicated test tables designed specifically for coverage threshold validation.
    """

    def _get_table_by_fixture_key(self, fixture_dict, key, discovered_tables):
        """Helper to get a table by fixture key from discovered tables."""
        table_name = fixture_dict[key]
        for table in discovered_tables:
            if table.full_name == table_name:
                return table
        return None

    def test_end_to_end_column_coverage_threshold_validation(
        self, column_coverage_threshold_test_tables, validator, integration_discovery
    ):
        """Test complete end-to-end flow: create → discover → validate column coverage threshold."""
        # Verify we created the expected tables
        expected_count = len(TABLE_SPECS_COLUMN_COVERAGE_THRESHOLD)
        assert (
            len(column_coverage_threshold_test_tables) == expected_count
        ), f"Expected {expected_count} tables, created {len(column_coverage_threshold_test_tables)}"

        # Discover the tables we just created
        discovered_tables = integration_discovery.discover_tables()

        # Filter to only our column coverage test tables
        discovered_coverage_tables = [table for table in discovered_tables if table.table.startswith("coverage_test_")]

        # Should have discovered all our test tables
        assert (
            len(discovered_coverage_tables) == expected_count
        ), f"Expected {expected_count} tables, found {len(discovered_coverage_tables)}"

        # Validate each discovered table for column coverage threshold
        coverage_results = {}
        for table in discovered_coverage_tables:
            validation_result = validator.meets_column_documentation_threshold(table, 80.0)
            coverage_results[table.table] = validation_result

        # Check results match expectations from our specs
        expected_results = {}
        for spec in TABLE_SPECS_COLUMN_COVERAGE_THRESHOLD.values():
            expected_results[spec.name] = spec.expected_pass

        assert coverage_results == expected_results, f"Column coverage validation results mismatch: {coverage_results}"

    def test_percentage_calculations_integration(
        self, column_coverage_threshold_test_tables, validator, integration_discovery
    ):
        """Test percentage calculations with real Databricks tables."""
        discovered_tables = integration_discovery.discover_tables()

        # Test specific percentage scenarios
        test_cases = [
            ("zero_columns", 100.0),  # Vacuously true
            ("single_documented", 100.0),  # 1/1 = 100%
            ("single_undocumented", 0.0),  # 0/1 = 0%
            ("zero_percent", 0.0),  # 0/4 = 0%
            ("fifty_percent", 50.0),  # 2/4 = 50%
            ("eighty_percent", 80.0),  # 4/5 = 80%
            ("hundred_percent", 100.0),  # 4/4 = 100%
        ]

        for fixture_key, expected_percentage in test_cases:
            table = self._get_table_by_fixture_key(
                column_coverage_threshold_test_tables, fixture_key, discovered_tables
            )
            assert table is not None, f"Should find test table for fixture key: {fixture_key}"

            actual_percentage = validator.calculate_column_documentation_percentage(table)
            assert (
                actual_percentage == expected_percentage
            ), f"Table {table.full_name}: expected {expected_percentage}%, got {actual_percentage}%"

    def test_boundary_conditions_integration(
        self, column_coverage_threshold_test_tables, validator, integration_discovery
    ):
        """Test boundary conditions around 80% threshold with real Databricks tables."""
        discovered_tables = integration_discovery.discover_tables()

        # Test just below threshold
        seventy_nine_table = self._get_table_by_fixture_key(
            column_coverage_threshold_test_tables, "seventy_nine_percent", discovered_tables
        )
        assert seventy_nine_table is not None, "Should find 79% test table"

        percentage_79 = validator.calculate_column_documentation_percentage(seventy_nine_table)
        assert 79.0 <= percentage_79 < 80.0, f"Expected ~79%, got {percentage_79}%"
        assert validator.meets_column_documentation_threshold(seventy_nine_table, 80.0) is False

        # Test exactly at threshold
        eighty_table = self._get_table_by_fixture_key(
            column_coverage_threshold_test_tables, "eighty_percent", discovered_tables
        )
        assert eighty_table is not None, "Should find 80% test table"

        percentage_80 = validator.calculate_column_documentation_percentage(eighty_table)
        assert percentage_80 == 80.0, f"Expected exactly 80%, got {percentage_80}%"
        assert validator.meets_column_documentation_threshold(eighty_table, 80.0) is True

        # Test just above threshold
        eighty_one_table = self._get_table_by_fixture_key(
            column_coverage_threshold_test_tables, "eighty_one_percent", discovered_tables
        )
        assert eighty_one_table is not None, "Should find 81% test table"

        percentage_81 = validator.calculate_column_documentation_percentage(eighty_one_table)
        assert percentage_81 > 80.0, f"Expected >80%, got {percentage_81}%"
        assert validator.meets_column_documentation_threshold(eighty_one_table, 80.0) is True

    def test_whitespace_handling_integration(
        self, column_coverage_threshold_test_tables, validator, integration_discovery
    ):
        """Test that whitespace comments are properly handled in integration environment."""
        discovered_tables = integration_discovery.discover_tables()

        whitespace_table = self._get_table_by_fixture_key(
            column_coverage_threshold_test_tables, "whitespace_comments", discovered_tables
        )
        assert whitespace_table is not None, "Should find whitespace test table"

        # Should count only 1 of 5 columns as documented (good_col)
        percentage = validator.calculate_column_documentation_percentage(whitespace_table)
        assert percentage == 20.0, f"Expected 20% (1/5), got {percentage}%"
        assert validator.meets_column_documentation_threshold(whitespace_table, 80.0) is False

        undocumented = validator.get_undocumented_columns(whitespace_table)
        assert len(undocumented) == 4, f"Expected 4 undocumented columns, got {len(undocumented)}"

    def test_default_threshold_from_config_integration(
        self, column_coverage_threshold_test_tables, validator, integration_discovery
    ):
        """Test that default threshold is loaded from configuration in integration environment."""
        discovered_tables = integration_discovery.discover_tables()

        # Test with a table that should pass default 80% threshold
        eighty_table = self._get_table_by_fixture_key(
            column_coverage_threshold_test_tables, "eighty_percent", discovered_tables
        )
        assert eighty_table is not None, "Should find 80% test table"

        # Test with default threshold (should use config value of 80%)
        assert validator.meets_column_documentation_threshold(eighty_table) is True

        # Test with a table that should fail default threshold
        fifty_table = self._get_table_by_fixture_key(
            column_coverage_threshold_test_tables, "fifty_percent", discovered_tables
        )
        assert fifty_table is not None, "Should find 50% test table"

        assert validator.meets_column_documentation_threshold(fifty_table) is False

    def test_get_undocumented_columns_integration(
        self, column_coverage_threshold_test_tables, validator, integration_discovery
    ):
        """Test getting list of undocumented columns with real Databricks tables."""
        discovered_tables = integration_discovery.discover_tables()

        # Test table with mix of documented and undocumented columns
        fifty_table = self._get_table_by_fixture_key(
            column_coverage_threshold_test_tables, "fifty_percent", discovered_tables
        )
        assert fifty_table is not None, "Should find 50% test table"

        undocumented = validator.get_undocumented_columns(fifty_table)
        # From the spec: col1 and col3 are documented, col2 and col4 are not
        expected_undocumented = {"col2", "col4"}
        assert set(undocumented) == expected_undocumented, f"Expected {expected_undocumented}, got {set(undocumented)}"

    @pytest.mark.parametrize(
        "fixture_key,expected_pass",
        [
            ("zero_columns", True),
            ("single_documented", True),
            ("single_undocumented", False),
            ("zero_percent", False),
            ("fifty_percent", False),
            ("seventy_nine_percent", False),
            ("eighty_percent", True),
            ("eighty_one_percent", True),
            ("hundred_percent", True),
            ("whitespace_comments", False),
        ],
    )
    def test_individual_coverage_threshold_validation_parametrized(
        self, column_coverage_threshold_test_tables, validator, integration_discovery, fixture_key, expected_pass
    ):
        """Test validation of individual coverage threshold tables using parametrize."""
        # Use the fixture to get the specific table
        target_table = self._get_table_by_fixture_key(
            column_coverage_threshold_test_tables, fixture_key, integration_discovery.discover_tables()
        )

        assert target_table is not None, f"Could not find test table for fixture key: {fixture_key}"

        # Validate the table
        result = validator.meets_column_documentation_threshold(target_table, 80.0)
        actual_percentage = validator.calculate_column_documentation_percentage(target_table)

        assert (
            result is expected_pass
        ), f"Table {target_table.full_name} coverage validation mismatch. Expected {expected_pass}, got {result}. Actual coverage: {actual_percentage}%"

    def test_discovery_finds_all_coverage_threshold_test_tables(
        self, column_coverage_threshold_test_tables, integration_discovery
    ):
        """Test that discovery engine finds all our coverage threshold test tables."""
        # Verify tables were created
        expected_count = len(TABLE_SPECS_COLUMN_COVERAGE_THRESHOLD)
        assert len(column_coverage_threshold_test_tables) == expected_count, "Should have created all test tables"

        discovered_tables = integration_discovery.discover_tables()

        # Should find all coverage test tables in pytest_test_data schema
        coverage_test_tables = [table for table in discovered_tables if table.table.startswith("coverage_test_")]

        assert (
            len(coverage_test_tables) == expected_count
        ), f"Discovery should find all {expected_count} coverage test tables, found {len(coverage_test_tables)}"

        # Verify all expected table names are present
        found_table_names = {table.table for table in coverage_test_tables}
        expected_table_names = {spec.name for spec in TABLE_SPECS_COLUMN_COVERAGE_THRESHOLD.values()}

        assert (
            found_table_names == expected_table_names
        ), f"Table name mismatch. Expected: {expected_table_names}, Found: {found_table_names}"
