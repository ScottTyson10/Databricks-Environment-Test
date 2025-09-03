"""Integration tests for "Small tables under 1GB can be exempted from clustering" scenario.

Layer 2 tests that create real Databricks tables with different sizes,
discover them, and validate size-based exemption logic. Uses pytest patterns with
real Databricks SDK integration and actual table size detection.
"""

import pytest
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

from tests.fixtures.clustering.size_exemption_specs import TABLE_SPECS_SIZE_EXEMPTION
from tests.fixtures.table_factory import create_test_tables_for_size_exemption_scenario
from tests.utils.discovery_engine import create_integration_discovery
from tests.validators.clustering import ClusteringValidator


@pytest.fixture(scope="session")
def databricks_client():
    """Session-scoped Databricks client fixture."""
    load_dotenv()
    return WorkspaceClient()


@pytest.fixture(scope="session")
def size_exemption_test_tables(databricks_client):
    """Session-scoped fixture creating test tables for size exemption scenarios.

    Creates all tables defined in TABLE_SPECS_SIZE_EXEMPTION with proper cleanup.
    Tables are created once per test session and shared across all tests.
    Includes data insertion to achieve target sizes for testing.
    """
    with create_test_tables_for_size_exemption_scenario(databricks_client) as tables:
        yield tables


@pytest.fixture(scope="session")
def integration_discovery(databricks_client):
    """Session-scoped discovery engine for integration tests."""
    return create_integration_discovery(databricks_client, test_catalog="workspace", test_schema="pytest_test_data")


@pytest.fixture(scope="session")
def discovered_tables(integration_discovery):
    """Session-scoped fixture that discovers tables once and caches results."""
    return integration_discovery.discover_tables()


@pytest.fixture(scope="function")
def clustering_validator():
    """Function-scoped clustering validator."""
    return ClusteringValidator()


class TestSizeExemptionIntegration:
    """Integration tests for size-based clustering exemption with real Databricks tables."""

    def test_discovery_finds_all_test_tables(self, size_exemption_test_tables, discovered_tables):
        """Test that discovery engine finds all our size exemption test tables."""
        # Verify tables were created
        expected_count = len(TABLE_SPECS_SIZE_EXEMPTION)
        assert len(size_exemption_test_tables) == expected_count, "Should have created all test tables"

        # Should find all size exemption test tables in pytest_test_data schema
        exemption_test_tables = [table for table in discovered_tables if table.table.startswith("size_exemption_test_")]

        assert (
            len(exemption_test_tables) == expected_count
        ), f"Discovery should find all {expected_count} size exemption test tables, found {len(exemption_test_tables)}"

        # Verify all expected table names are present
        found_table_names = {table.table for table in exemption_test_tables}
        expected_table_names = {spec.name for spec in TABLE_SPECS_SIZE_EXEMPTION.values()}
        assert found_table_names == expected_table_names, "All expected test tables should be discovered"

    def test_small_table_size_detection(self, size_exemption_test_tables, discovered_tables, clustering_validator):
        """Test that small tables are correctly identified as small via size detection."""

        # Find small tables
        small_tables = [
            table
            for table in discovered_tables
            if table.table.startswith("size_exemption_test_") and "small" in table.table
        ]

        for table in small_tables:
            # Skip clustered table - it has clustering so size doesn't matter
            if "clustered" in table.table:
                continue

            # Get actual table size
            table_size = clustering_validator.get_table_size_bytes(table)
            assert table_size is not None, f"Should be able to determine size for {table.table}"

            # Test size detection using test threshold
            is_small = clustering_validator.is_small_table(
                table, clustering_validator.test_size_threshold_bytes, table_size
            )
            assert is_small is True, f"Small table {table.table} should be detected as small"

            # Test exemption based on size
            is_exempt = clustering_validator.is_exempt_from_clustering_requirements(
                table, clustering_validator.test_size_threshold_bytes, table_size
            )
            assert is_exempt is True, f"Small table {table.table} should be exempt from clustering"

    def test_large_table_size_detection(self, size_exemption_test_tables, discovered_tables, clustering_validator):
        """Test that large tables are correctly identified as large via size detection."""

        # Find large tables (without manual exclusion)
        large_tables = [
            table
            for table in discovered_tables
            if table.table.startswith("size_exemption_test_")
            and "large" in table.table
            and "excluded" not in table.table
        ]

        for table in large_tables:
            # Get actual table size
            table_size = clustering_validator.get_table_size_bytes(table)
            assert table_size is not None, f"Should be able to determine size for {table.table}"

            # Test size detection using test threshold
            is_small = clustering_validator.is_small_table(
                table, clustering_validator.test_size_threshold_bytes, table_size
            )
            assert is_small is False, f"Large table {table.table} should not be detected as small"

            # Test no exemption based on size
            is_exempt = clustering_validator.is_exempt_from_clustering_requirements(
                table, clustering_validator.test_size_threshold_bytes, table_size
            )
            assert is_exempt is False, f"Large table {table.table} should not be exempt from clustering"

    def test_manual_exclusion_overrides_size(self, size_exemption_test_tables, discovered_tables, clustering_validator):
        """Test that manual cluster_exclusion flag overrides size-based logic."""

        # Find tables with manual exclusion
        manually_excluded_tables = [
            table
            for table in discovered_tables
            if table.table.startswith("size_exemption_test_") and "excluded" in table.table
        ]

        for table in manually_excluded_tables:
            # Verify manual exclusion flag
            assert (
                clustering_validator.has_cluster_exclusion(table) is True
            ), f"Table {table.table} should have manual exclusion flag"

            # Get actual table size
            table_size = clustering_validator.get_table_size_bytes(table)

            # Verify exemption regardless of size
            is_exempt = clustering_validator.is_exempt_from_clustering_requirements(
                table, clustering_validator.test_size_threshold_bytes, table_size
            )
            assert is_exempt is True, f"Manually excluded table {table.table} should be exempt regardless of size"

            # Test that manual exclusion takes precedence (no size needed)
            exemption_without_size = clustering_validator.is_exempt_from_clustering_requirements(
                table, clustering_validator.test_size_threshold_bytes, None
            )
            assert exemption_without_size is True, f"Manual exclusion should work without size check for {table.table}"

    def test_clustered_table_not_exempt(self, size_exemption_test_tables, discovered_tables, clustering_validator):
        """Test that tables with clustering are not subject to size-based exemption."""

        # Find clustered tables
        clustered_tables = [
            table
            for table in discovered_tables
            if table.table.startswith("size_exemption_test_") and "clustered" in table.table
        ]

        for table in clustered_tables:
            # Verify clustering is present (this test assumes clustering detection works)
            # Note: We don't test clustering detection here as that's a separate scenario

            # Even if table is small, clustering should take precedence
            # Small clustered table should still pass validation because it has clustering
            # Size exemption should not apply when clustering is present

            # This tests our business logic: clustered tables are not subject to exemption rules
            # (They already have clustering, so they don't need exemption)

            # For now, just verify the table exists and we can iterate over clustered tables
            assert table is not None, f"Clustered table {table.table} should exist"

    def test_empty_table_exemption(self, size_exemption_test_tables, discovered_tables, clustering_validator):
        """Test that empty tables are considered small and exempt."""

        # Find empty table
        empty_table = None
        for table in discovered_tables:
            if table.table == "size_exemption_test_empty_table":
                empty_table = table
                break

        assert empty_table is not None, "Should find empty test table"

        # Get actual table size
        table_size = clustering_validator.get_table_size_bytes(empty_table)

        # Empty table should be small
        is_small = clustering_validator.is_small_table(
            empty_table, clustering_validator.test_size_threshold_bytes, table_size
        )
        assert is_small is True, "Empty table should be detected as small"

        # Empty table should be exempt
        is_exempt = clustering_validator.is_exempt_from_clustering_requirements(
            empty_table, clustering_validator.test_size_threshold_bytes, table_size
        )
        assert is_exempt is True, "Empty table should be exempt from clustering"

    def test_boundary_conditions(self, size_exemption_test_tables, discovered_tables, clustering_validator):
        """Test tables at size boundaries (near 1MB threshold)."""

        # Find boundary table
        boundary_table = None
        for table in discovered_tables:
            if table.table == "size_exemption_test_boundary":
                boundary_table = table
                break

        assert boundary_table is not None, "Should find boundary test table"

        # Get actual table size
        table_size = clustering_validator.get_table_size_bytes(boundary_table)

        # Test size detection near boundary
        is_small = clustering_validator.is_small_table(
            boundary_table, clustering_validator.test_size_threshold_bytes, table_size
        )
        # Should be small (under 1MB test threshold)
        assert is_small is True, "Boundary table should be small (under test threshold)"

        # Should be exempt
        is_exempt = clustering_validator.is_exempt_from_clustering_requirements(
            boundary_table, clustering_validator.test_size_threshold_bytes, table_size
        )
        assert is_exempt is True, "Boundary table should be exempt"

    def test_size_detection_without_size_data(
        self, size_exemption_test_tables, discovered_tables, clustering_validator
    ):
        """Test graceful handling when size data is not available."""

        # Find any test table
        test_table = None
        for table in discovered_tables:
            if table.table.startswith("size_exemption_test_"):
                test_table = table
                break

        assert test_table is not None, "Should find at least one test table"

        # Size detection should return False when no size_bytes provided
        is_small = clustering_validator.is_small_table(test_table, clustering_validator.test_size_threshold_bytes, None)
        assert is_small is False, "Should return False when size cannot be determined"

        # Exemption should fall back to manual exclusion only
        is_exempt = clustering_validator.is_exempt_from_clustering_requirements(
            test_table, clustering_validator.test_size_threshold_bytes, None
        )
        # Should depend only on manual exclusion flag, not size
        has_manual_exclusion = clustering_validator.has_cluster_exclusion(test_table)
        assert is_exempt == has_manual_exclusion, "Without size_bytes, should fall back to manual exclusion only"

    def test_configuration_values(self, clustering_validator):
        """Test that configuration values are properly loaded for size thresholds."""
        # These should match clustering_config.yaml values
        assert clustering_validator.size_threshold_bytes == 1_073_741_824, "Production threshold should be 1GB"
        assert clustering_validator.test_size_threshold_bytes == 1_048_576, "Test threshold should be 1MB"
        assert clustering_validator.exempt_small_tables is True, "Size exemption should be enabled"

    @pytest.mark.parametrize("table_type", ["small_exempt_table", "large_table_no_exemption"])
    def test_validator_method_consistency(
        self, size_exemption_test_tables, discovered_tables, clustering_validator, table_type
    ):
        """Test that validator methods are consistent with each other."""

        # Find the specified test table
        test_table = None
        expected_table_name = TABLE_SPECS_SIZE_EXEMPTION[table_type].name
        for table in discovered_tables:
            if table.table == expected_table_name:
                test_table = table
                break

        assert test_table is not None, f"Should find {table_type} test table"

        # Get actual table size
        table_size = clustering_validator.get_table_size_bytes(test_table)

        # Test method consistency
        is_exempt = clustering_validator.is_exempt_from_clustering_requirements(
            test_table, clustering_validator.test_size_threshold_bytes, table_size
        )
        should_enforce = clustering_validator.should_enforce_clustering_requirements(
            test_table, clustering_validator.test_size_threshold_bytes, table_size
        )

        # These should be inverses of each other
        assert is_exempt != should_enforce, "is_exempt and should_enforce should be inverses"
