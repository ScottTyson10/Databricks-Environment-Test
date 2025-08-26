"""Integration tests for "Delta auto-optimization" scenario.

Layer 2 tests that create real Databricks tables with delta auto-optimization properties,
discover them, and validate delta auto-optimization detection. Uses pytest patterns with 
real Databricks SDK integration.
"""

import os

import pytest
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

from tests.fixtures.clustering.delta_auto_optimization_specs import TABLE_SPECS_DELTA_AUTO_OPTIMIZATION
from tests.fixtures.table_factory import create_test_tables_for_delta_auto_optimization_scenario
from tests.utils.discovery_engine import create_integration_discovery
from tests.validators.clustering import ClusteringValidator

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
def delta_auto_optimization_test_tables(databricks_client):
    """Class-scoped test tables for delta auto-optimization - create for each test class, cleanup after."""
    with create_test_tables_for_delta_auto_optimization_scenario(databricks_client) as created_tables:
        yield created_tables


@pytest.fixture(scope="class")
def clustering_validator():
    """Clustering validator fixture - reused across all tests in a class."""
    return ClusteringValidator()


@pytest.fixture(scope="class")
def integration_discovery(databricks_client):
    """Discovery engine configured for integration testing - reused across all tests in a class."""
    return create_integration_discovery(databricks_client)


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("CREATE_TEST_TABLES") != "true", reason="Integration tests require CREATE_TEST_TABLES=true"
)
class TestDeltaAutoOptimizationIntegration:
    """Integration tests for delta auto-optimization detection.

    Tests the "Tables can use delta auto-optimization for clustering" scenario end-to-end.
    Uses dedicated test tables designed specifically for delta auto-optimization validation.
    """

    def _get_table_by_fixture_key(self, fixture_dict, key, discovered_tables):
        """Helper to get a table by fixture key from discovered tables."""
        table_name = fixture_dict[key]
        for table in discovered_tables:
            if table.full_name == table_name:
                return table
        return None

    def test_end_to_end_delta_auto_optimization_detection_validation(
        self, delta_auto_optimization_test_tables, clustering_validator, integration_discovery
    ):
        """Test complete end-to-end flow: create → discover → validate delta auto-optimization detection."""
        # Verify we created the expected tables
        expected_count = len(TABLE_SPECS_DELTA_AUTO_OPTIMIZATION)
        assert (
            len(delta_auto_optimization_test_tables) == expected_count
        ), f"Expected {expected_count} tables, created {len(delta_auto_optimization_test_tables)}"

        # Discover the tables we just created
        discovered_tables = integration_discovery.discover_tables()

        # Filter to only our delta auto-optimization test tables
        discovered_delta_opt_tables = [
            table for table in discovered_tables if table.table.startswith("delta_opt_test_")
        ]

        # Should have discovered all our test tables
        assert (
            len(discovered_delta_opt_tables) == expected_count
        ), f"Expected {expected_count} tables, found {len(discovered_delta_opt_tables)}"

        # Validate each discovered table for delta auto-optimization detection
        delta_optimization_results = {}
        for table in discovered_delta_opt_tables:
            has_optimize_write = clustering_validator.has_optimize_write(table)
            has_auto_compact = clustering_validator.has_auto_compact(table)
            has_delta_optimization = clustering_validator.has_delta_auto_optimization(table)
            delta_optimization_results[table.table] = {
                "has_optimize_write": has_optimize_write,
                "has_auto_compact": has_auto_compact,
                "has_delta_auto_optimization": has_delta_optimization,
            }

        # Check results match expectations from our specs
        expected_results = {}
        for spec in TABLE_SPECS_DELTA_AUTO_OPTIMIZATION.values():
            expected_results[spec.name] = {
                "has_optimize_write": spec.optimize_write_enabled,
                "has_auto_compact": spec.auto_compact_enabled,
                "has_delta_auto_optimization": spec.expected_has_delta_auto_optimization,
            }

        assert (
            delta_optimization_results == expected_results
        ), f"Delta auto-optimization detection results mismatch: {delta_optimization_results}"

    def test_both_flags_enabled_detection(
        self, delta_auto_optimization_test_tables, clustering_validator, integration_discovery
    ):
        """Test detection of table with both optimizeWrite and autoCompact enabled."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our both flags enabled test table
        both_flags_table = None
        for table in discovered_tables:
            if table.table == "delta_opt_test_both_enabled":
                both_flags_table = table
                break

        assert both_flags_table is not None, "Should find both flags enabled test table"
        assert clustering_validator.has_optimize_write(both_flags_table) is True, "Should detect optimizeWrite"
        assert clustering_validator.has_auto_compact(both_flags_table) is True, "Should detect autoCompact"
        assert (
            clustering_validator.has_delta_auto_optimization(both_flags_table) is True
        ), "Should detect delta auto-optimization"
        assert (
            clustering_validator.has_any_clustering_approach(both_flags_table) is True
        ), "Should detect clustering approach"

    def test_optimize_write_only_detection(
        self, delta_auto_optimization_test_tables, clustering_validator, integration_discovery
    ):
        """Test correct handling of table with only optimizeWrite enabled."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our optimize write only test table
        optimize_only_table = None
        for table in discovered_tables:
            if table.table == "delta_opt_test_optimize_only":
                optimize_only_table = table
                break

        assert optimize_only_table is not None, "Should find optimize write only test table"
        assert clustering_validator.has_optimize_write(optimize_only_table) is True, "Should detect optimizeWrite"
        assert clustering_validator.has_auto_compact(optimize_only_table) is False, "Should not detect autoCompact"
        assert (
            clustering_validator.has_delta_auto_optimization(optimize_only_table) is False
        ), "Should not detect delta auto-optimization (requires both flags)"
        assert (
            clustering_validator.has_any_clustering_approach(optimize_only_table) is False
        ), "Should not detect clustering approach"

    def test_auto_compact_only_detection(
        self, delta_auto_optimization_test_tables, clustering_validator, integration_discovery
    ):
        """Test correct handling of table with only autoCompact enabled."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our auto compact only test table
        compact_only_table = None
        for table in discovered_tables:
            if table.table == "delta_opt_test_compact_only":
                compact_only_table = table
                break

        assert compact_only_table is not None, "Should find auto compact only test table"
        assert clustering_validator.has_optimize_write(compact_only_table) is False, "Should not detect optimizeWrite"
        assert clustering_validator.has_auto_compact(compact_only_table) is True, "Should detect autoCompact"
        assert (
            clustering_validator.has_delta_auto_optimization(compact_only_table) is False
        ), "Should not detect delta auto-optimization (requires both flags)"
        assert (
            clustering_validator.has_any_clustering_approach(compact_only_table) is False
        ), "Should not detect clustering approach"

    def test_neither_flag_enabled_detection(
        self, delta_auto_optimization_test_tables, clustering_validator, integration_discovery
    ):
        """Test correct handling of table with neither optimization flag enabled."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our neither flag enabled test table
        neither_table = None
        for table in discovered_tables:
            if table.table == "delta_opt_test_neither_enabled":
                neither_table = table
                break

        assert neither_table is not None, "Should find neither flag enabled test table"
        assert clustering_validator.has_optimize_write(neither_table) is False, "Should not detect optimizeWrite"
        assert clustering_validator.has_auto_compact(neither_table) is False, "Should not detect autoCompact"
        assert (
            clustering_validator.has_delta_auto_optimization(neither_table) is False
        ), "Should not detect delta auto-optimization"
        assert (
            clustering_validator.has_any_clustering_approach(neither_table) is False
        ), "Should not detect clustering approach"

    def test_single_column_delta_optimization(
        self, delta_auto_optimization_test_tables, clustering_validator, integration_discovery
    ):
        """Test delta auto-optimization detection with single column table."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our single column test table
        single_col_table = None
        for table in discovered_tables:
            if table.table == "delta_opt_test_single_column":
                single_col_table = table
                break

        assert single_col_table is not None, "Should find single column delta optimization test table"
        assert clustering_validator.has_optimize_write(single_col_table) is True, "Should detect optimizeWrite"
        assert clustering_validator.has_auto_compact(single_col_table) is True, "Should detect autoCompact"
        assert (
            clustering_validator.has_delta_auto_optimization(single_col_table) is True
        ), "Should detect delta auto-optimization"

    def test_realistic_sales_delta_optimization(
        self, delta_auto_optimization_test_tables, clustering_validator, integration_discovery
    ):
        """Test delta auto-optimization detection with realistic sales table structure."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our realistic sales test table
        sales_table = None
        for table in discovered_tables:
            if table.table == "delta_opt_test_sales_optimized":
                sales_table = table
                break

        assert sales_table is not None, "Should find realistic sales delta optimization test table"
        assert clustering_validator.has_optimize_write(sales_table) is True, "Should detect optimizeWrite"
        assert clustering_validator.has_auto_compact(sales_table) is True, "Should detect autoCompact"
        assert (
            clustering_validator.has_delta_auto_optimization(sales_table) is True
        ), "Should detect delta auto-optimization"

    def test_empty_table_cost_effective_testing(
        self, delta_auto_optimization_test_tables, clustering_validator, integration_discovery
    ):
        """Test cost-effective delta auto-optimization detection using empty tables."""
        discovered_tables = integration_discovery.discover_tables()

        # Find both empty tables (with and without delta optimization)
        empty_optimized_table = None
        empty_baseline_table = None
        for table in discovered_tables:
            if table.table == "delta_opt_test_empty_optimized":
                empty_optimized_table = table
            elif table.table == "delta_opt_test_empty_baseline":
                empty_baseline_table = table

        assert empty_optimized_table is not None, "Should find empty optimized test table"
        assert empty_baseline_table is not None, "Should find empty baseline test table"

        # Optimized table should be detected
        assert clustering_validator.has_optimize_write(empty_optimized_table) is True, "Should detect optimizeWrite"
        assert clustering_validator.has_auto_compact(empty_optimized_table) is True, "Should detect autoCompact"
        assert (
            clustering_validator.has_delta_auto_optimization(empty_optimized_table) is True
        ), "Should detect delta auto-optimization"

        # Baseline table should not be detected
        assert (
            clustering_validator.has_optimize_write(empty_baseline_table) is False
        ), "Should not detect optimizeWrite in baseline"
        assert (
            clustering_validator.has_auto_compact(empty_baseline_table) is False
        ), "Should not detect autoCompact in baseline"
        assert (
            clustering_validator.has_delta_auto_optimization(empty_baseline_table) is False
        ), "Should not detect delta auto-optimization in baseline"

    def test_property_inspection_delta_auto_optimization(
        self, delta_auto_optimization_test_tables, clustering_validator, integration_discovery
    ):
        """Test inspection of actual table properties for delta auto-optimization detection."""
        discovered_tables = integration_discovery.discover_tables()

        # Find a delta auto-optimization enabled table
        enabled_table = None
        for table in discovered_tables:
            if table.table == "delta_opt_test_both_enabled":
                enabled_table = table
                break

        assert enabled_table is not None, "Should find delta auto-optimization enabled test table"
        assert enabled_table.properties is not None, "Table should have properties"

        # Inspect actual properties (based on our feasibility test findings)
        properties = enabled_table.properties
        assert "delta.autoOptimize.optimizeWrite" in properties, "Should have optimizeWrite property"
        assert properties["delta.autoOptimize.optimizeWrite"] == "true", "optimizeWrite should be 'true'"
        assert "delta.autoOptimize.autoCompact" in properties, "Should have autoCompact property"
        assert properties["delta.autoOptimize.autoCompact"] == "true", "autoCompact should be 'true'"

        # Verify our validator correctly interprets these properties
        assert clustering_validator.has_delta_auto_optimization(enabled_table) is True

    @pytest.mark.parametrize(
        "fixture_key,expected_has_optimize_write,expected_has_auto_compact,expected_has_delta_optimization",
        [
            ("both_flags_enabled", True, True, True),
            ("optimize_write_only", True, False, False),
            ("auto_compact_only", False, True, False),
            ("neither_flag_enabled", False, False, False),
            ("single_column_both_flags", True, True, True),
            ("realistic_sales_optimized", True, True, True),
            ("empty_table_optimized", True, True, True),
            ("empty_table_baseline", False, False, False),
        ],
    )
    def test_individual_delta_optimization_detection_parametrized(
        self,
        delta_auto_optimization_test_tables,
        clustering_validator,
        integration_discovery,
        fixture_key,
        expected_has_optimize_write,
        expected_has_auto_compact,
        expected_has_delta_optimization,
    ):
        """Test delta auto-optimization detection of individual tables using parametrize."""
        # Use the fixture to get the specific table
        target_table = self._get_table_by_fixture_key(
            delta_auto_optimization_test_tables, fixture_key, integration_discovery.discover_tables()
        )

        assert target_table is not None, f"Could not find test table for fixture key: {fixture_key}"

        # Validate delta auto-optimization detection
        has_optimize_write = clustering_validator.has_optimize_write(target_table)
        has_auto_compact = clustering_validator.has_auto_compact(target_table)
        has_delta_optimization = clustering_validator.has_delta_auto_optimization(target_table)

        assert (
            has_optimize_write is expected_has_optimize_write
        ), f"Table {target_table.full_name} optimizeWrite detection mismatch. Expected {expected_has_optimize_write}, got {has_optimize_write}"
        assert (
            has_auto_compact is expected_has_auto_compact
        ), f"Table {target_table.full_name} autoCompact detection mismatch. Expected {expected_has_auto_compact}, got {has_auto_compact}"
        assert (
            has_delta_optimization is expected_has_delta_optimization
        ), f"Table {target_table.full_name} delta auto-optimization detection mismatch. Expected {expected_has_delta_optimization}, got {has_delta_optimization}"

    def test_clustering_configuration_integration(self, clustering_validator):
        """Test that clustering validator respects delta auto-optimization configuration in integration environment."""
        # Test delta auto-optimization configuration values
        assert (
            clustering_validator.optimize_write_property == "delta.autoOptimize.optimizeWrite"
        ), "Default optimizeWrite property should be delta.autoOptimize.optimizeWrite"
        assert clustering_validator.optimize_write_value == "true", "Default optimizeWrite value should be 'true'"
        assert (
            clustering_validator.auto_compact_property == "delta.autoOptimize.autoCompact"
        ), "Default autoCompact property should be delta.autoOptimize.autoCompact"
        assert clustering_validator.auto_compact_value == "true", "Default autoCompact value should be 'true'"
        assert clustering_validator.require_both_delta_flags is True, "Should require both flags by default"

    def test_discovery_finds_all_delta_optimization_test_tables(
        self, delta_auto_optimization_test_tables, integration_discovery
    ):
        """Test that discovery engine finds all our delta auto-optimization test tables."""
        # Verify tables were created
        expected_count = len(TABLE_SPECS_DELTA_AUTO_OPTIMIZATION)
        assert len(delta_auto_optimization_test_tables) == expected_count, "Should have created all test tables"

        discovered_tables = integration_discovery.discover_tables()

        # Should find all delta optimization test tables in pytest_test_data schema
        delta_opt_test_tables = [
            table for table in discovered_tables if table.table.startswith("delta_opt_test_")
        ]

        assert (
            len(delta_opt_test_tables) == expected_count
        ), f"Discovery should find all {expected_count} delta optimization test tables, found {len(delta_opt_test_tables)}"

        # Verify all expected table names are present
        found_table_names = {table.table for table in delta_opt_test_tables}
        expected_table_names = {spec.name for spec in TABLE_SPECS_DELTA_AUTO_OPTIMIZATION.values()}

        assert (
            found_table_names == expected_table_names
        ), f"Table name mismatch. Expected: {expected_table_names}, Found: {found_table_names}"

    def test_get_delta_auto_optimization_status_integration(
        self, delta_auto_optimization_test_tables, clustering_validator, integration_discovery
    ):
        """Test get_delta_auto_optimization_status method with real delta optimization tables."""
        discovered_tables = integration_discovery.discover_tables()

        # Find both enabled and partially enabled tables
        both_flags_table = None
        optimize_only_table = None
        for table in discovered_tables:
            if table.table == "delta_opt_test_both_enabled":
                both_flags_table = table
            elif table.table == "delta_opt_test_optimize_only":
                optimize_only_table = table

        assert both_flags_table is not None, "Should find both flags enabled table"
        assert optimize_only_table is not None, "Should find optimize only table"

        # Test comprehensive status for both flags enabled
        status_both = clustering_validator.get_delta_auto_optimization_status(both_flags_table)
        expected_status_both = {
            "has_optimize_write": True,
            "has_auto_compact": True,
            "has_delta_auto_optimization": True,
            "optimize_write_property": "delta.autoOptimize.optimizeWrite",
            "auto_compact_property": "delta.autoOptimize.autoCompact",
            "require_both_flags": True,
        }
        assert status_both == expected_status_both, "Both flags status should match expected"

        # Test comprehensive status for optimize only
        status_optimize_only = clustering_validator.get_delta_auto_optimization_status(optimize_only_table)
        expected_status_optimize_only = {
            "has_optimize_write": True,
            "has_auto_compact": False,
            "has_delta_auto_optimization": False,
            "optimize_write_property": "delta.autoOptimize.optimizeWrite",
            "auto_compact_property": "delta.autoOptimize.autoCompact",
            "require_both_flags": True,
        }
        assert status_optimize_only == expected_status_optimize_only, "Optimize only status should match expected"