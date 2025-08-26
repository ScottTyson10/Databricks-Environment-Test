"""Integration tests for "Cluster by auto flag detection" scenario.

Layer 2 tests that create real Databricks tables with automatic clustering, discover them,
and validate auto-clustering detection. Uses pytest patterns with real Databricks SDK integration.
"""

import os

import pytest
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

from tests.fixtures.clustering.cluster_by_auto_specs import TABLE_SPECS_CLUSTER_BY_AUTO
from tests.fixtures.table_factory import create_test_tables_for_cluster_by_auto_scenario
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
def cluster_by_auto_test_tables(databricks_client):
    """Class-scoped test tables for cluster-by-auto - create for each test class, cleanup after."""
    with create_test_tables_for_cluster_by_auto_scenario(databricks_client) as created_tables:
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
class TestClusterByAutoIntegration:
    """Integration tests for cluster-by-auto detection.

    Tests the "Tables can use clusterByAuto flag for automatic clustering" scenario end-to-end.
    Uses dedicated test tables designed specifically for automatic clustering validation.
    """

    def _get_table_by_fixture_key(self, fixture_dict, key, discovered_tables):
        """Helper to get a table by fixture key from discovered tables."""
        table_name = fixture_dict[key]
        for table in discovered_tables:
            if table.full_name == table_name:
                return table
        return None

    def test_end_to_end_cluster_by_auto_detection_validation(
        self, cluster_by_auto_test_tables, clustering_validator, integration_discovery
    ):
        """Test complete end-to-end flow: create → discover → validate cluster-by-auto detection."""
        # Verify we created the expected tables
        expected_count = len(TABLE_SPECS_CLUSTER_BY_AUTO)
        assert (
            len(cluster_by_auto_test_tables) == expected_count
        ), f"Expected {expected_count} tables, created {len(cluster_by_auto_test_tables)}"

        # Discover the tables we just created
        discovered_tables = integration_discovery.discover_tables()

        # Filter to only our auto clustering test tables
        discovered_auto_cluster_tables = [
            table for table in discovered_tables if table.table.startswith("auto_cluster_test_")
        ]

        # Should have discovered all our test tables
        assert (
            len(discovered_auto_cluster_tables) == expected_count
        ), f"Expected {expected_count} tables, found {len(discovered_auto_cluster_tables)}"

        # Validate each discovered table for auto clustering detection
        auto_clustering_results = {}
        for table in discovered_auto_cluster_tables:
            has_auto_clustering = clustering_validator.has_auto_clustering(table)
            auto_clustering_status = clustering_validator.get_auto_clustering_status(table)
            auto_clustering_results[table.table] = {
                "has_auto_clustering": has_auto_clustering,
                "status": auto_clustering_status,
            }

        # Check results match expectations from our specs
        expected_results = {}
        for spec in TABLE_SPECS_CLUSTER_BY_AUTO.values():
            expected_results[spec.name] = {
                "has_auto_clustering": spec.expected_has_auto_clustering,
                "status": "enabled" if spec.expected_has_auto_clustering else "disabled",
            }

        assert (
            auto_clustering_results == expected_results
        ), f"Auto clustering detection results mismatch: {auto_clustering_results}"

    def test_basic_enabled_auto_clustering_detection(
        self, cluster_by_auto_test_tables, clustering_validator, integration_discovery
    ):
        """Test detection of basic automatic clustering with real Databricks table."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our basic enabled auto clustering test table
        enabled_table = None
        for table in discovered_tables:
            if table.table == "auto_cluster_test_basic_enabled":
                enabled_table = table
                break

        assert enabled_table is not None, "Should find basic enabled auto clustering test table"
        assert clustering_validator.has_auto_clustering(enabled_table) is True, "Should detect auto clustering"
        assert clustering_validator.get_auto_clustering_status(enabled_table) == "enabled", "Status should be enabled"
        assert (
            clustering_validator.has_any_clustering_approach(enabled_table) is True
        ), "Should detect clustering approach"

    def test_basic_disabled_auto_clustering_detection(
        self, cluster_by_auto_test_tables, clustering_validator, integration_discovery
    ):
        """Test correct handling of tables without automatic clustering."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our basic disabled auto clustering test table
        disabled_table = None
        for table in discovered_tables:
            if table.table == "auto_cluster_test_basic_disabled":
                disabled_table = table
                break

        assert disabled_table is not None, "Should find basic disabled auto clustering test table"
        assert clustering_validator.has_auto_clustering(disabled_table) is False, "Should not detect auto clustering"
        assert (
            clustering_validator.get_auto_clustering_status(disabled_table) == "disabled"
        ), "Status should be disabled"
        assert (
            clustering_validator.has_any_clustering_approach(disabled_table) is False
        ), "Should not detect clustering approach"

    def test_single_column_auto_clustering(
        self, cluster_by_auto_test_tables, clustering_validator, integration_discovery
    ):
        """Test auto clustering detection with single column table."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our single column auto clustering test table
        single_col_table = None
        for table in discovered_tables:
            if table.table == "auto_cluster_test_single_column":
                single_col_table = table
                break

        assert single_col_table is not None, "Should find single column auto clustering test table"
        assert clustering_validator.has_auto_clustering(single_col_table) is True, "Should detect auto clustering"
        assert (
            clustering_validator.get_auto_clustering_status(single_col_table) == "enabled"
        ), "Status should be enabled"

    def test_multi_column_auto_clustering(
        self, cluster_by_auto_test_tables, clustering_validator, integration_discovery
    ):
        """Test auto clustering detection with multi-column realistic table."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our multi column auto clustering test table
        multi_col_table = None
        for table in discovered_tables:
            if table.table == "auto_cluster_test_multi_column":
                multi_col_table = table
                break

        assert multi_col_table is not None, "Should find multi column auto clustering test table"
        assert clustering_validator.has_auto_clustering(multi_col_table) is True, "Should detect auto clustering"
        assert clustering_validator.get_auto_clustering_status(multi_col_table) == "enabled", "Status should be enabled"

    def test_realistic_sales_auto_clustering(
        self, cluster_by_auto_test_tables, clustering_validator, integration_discovery
    ):
        """Test auto clustering detection with realistic sales table structure."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our realistic sales auto clustering test table
        sales_table = None
        for table in discovered_tables:
            if table.table == "auto_cluster_test_realistic_sales":
                sales_table = table
                break

        assert sales_table is not None, "Should find realistic sales auto clustering test table"
        assert clustering_validator.has_auto_clustering(sales_table) is True, "Should detect auto clustering"
        assert clustering_validator.get_auto_clustering_status(sales_table) == "enabled", "Status should be enabled"

    def test_empty_table_cost_effective_testing(
        self, cluster_by_auto_test_tables, clustering_validator, integration_discovery
    ):
        """Test cost-effective auto clustering detection using empty tables."""
        discovered_tables = integration_discovery.discover_tables()

        # Find both empty tables (with and without auto clustering)
        empty_auto_table = None
        empty_baseline_table = None
        for table in discovered_tables:
            if table.table == "auto_cluster_test_empty_table":
                empty_auto_table = table
            elif table.table == "auto_cluster_test_empty_baseline":
                empty_baseline_table = table

        assert empty_auto_table is not None, "Should find empty auto clustering test table"
        assert empty_baseline_table is not None, "Should find empty baseline test table"

        # Auto clustering table should be detected
        assert clustering_validator.has_auto_clustering(empty_auto_table) is True, "Should detect auto clustering"
        assert (
            clustering_validator.get_auto_clustering_status(empty_auto_table) == "enabled"
        ), "Status should be enabled"

        # Baseline table should not be detected
        assert (
            clustering_validator.has_auto_clustering(empty_baseline_table) is False
        ), "Should not detect auto clustering in baseline"
        assert (
            clustering_validator.get_auto_clustering_status(empty_baseline_table) == "disabled"
        ), "Baseline status should be disabled"

    def test_property_inspection_cluster_by_auto(
        self, cluster_by_auto_test_tables, clustering_validator, integration_discovery
    ):
        """Test inspection of actual table properties for clusterByAuto detection."""
        discovered_tables = integration_discovery.discover_tables()

        # Find an auto clustering enabled table
        enabled_table = None
        for table in discovered_tables:
            if table.table == "auto_cluster_test_basic_enabled":
                enabled_table = table
                break

        assert enabled_table is not None, "Should find auto clustering enabled test table"
        assert enabled_table.properties is not None, "Table should have properties"

        # Inspect actual properties (based on our feasibility test findings)
        properties = enabled_table.properties
        assert "clusterByAuto" in properties, "Should have clusterByAuto property"
        assert properties["clusterByAuto"] == "true", "clusterByAuto should be 'true'"

        # Verify our validator correctly interprets these properties
        assert clustering_validator.has_auto_clustering(enabled_table) is True

    @pytest.mark.parametrize(
        "fixture_key,expected_has_auto_clustering",
        [
            ("auto_clustering_enabled", True),
            ("auto_clustering_disabled", False),
            ("single_column_auto", True),
            ("multi_column_auto", True),
            ("realistic_sales_auto", True),
            ("empty_table_auto", True),
            ("empty_table_no_clustering", False),
        ],
    )
    def test_individual_auto_clustering_detection_parametrized(
        self,
        cluster_by_auto_test_tables,
        clustering_validator,
        integration_discovery,
        fixture_key,
        expected_has_auto_clustering,
    ):
        """Test auto clustering detection of individual tables using parametrize."""
        # Use the fixture to get the specific table
        target_table = self._get_table_by_fixture_key(
            cluster_by_auto_test_tables, fixture_key, integration_discovery.discover_tables()
        )

        assert target_table is not None, f"Could not find test table for fixture key: {fixture_key}"

        # Validate auto clustering detection
        has_auto_clustering = clustering_validator.has_auto_clustering(target_table)
        assert (
            has_auto_clustering is expected_has_auto_clustering
        ), f"Table {target_table.full_name} auto clustering detection mismatch. Expected {expected_has_auto_clustering}, got {has_auto_clustering}"

    def test_clustering_configuration_integration(self, clustering_validator):
        """Test that clustering validator respects auto clustering configuration in integration environment."""
        # Test auto clustering configuration values
        assert (
            clustering_validator.cluster_by_auto_property == "clusterByAuto"
        ), "Default clusterByAuto property should be clusterByAuto"
        assert clustering_validator.cluster_by_auto_value == "true", "Default clusterByAuto value should be 'true'"
        assert clustering_validator.require_cluster_by_auto is False, "Should not require auto clustering by default"

    def test_discovery_finds_all_cluster_by_auto_test_tables(self, cluster_by_auto_test_tables, integration_discovery):
        """Test that discovery engine finds all our cluster-by-auto test tables."""
        # Verify tables were created
        expected_count = len(TABLE_SPECS_CLUSTER_BY_AUTO)
        assert len(cluster_by_auto_test_tables) == expected_count, "Should have created all test tables"

        discovered_tables = integration_discovery.discover_tables()

        # Should find all auto clustering test tables in pytest_test_data schema
        auto_cluster_test_tables = [
            table for table in discovered_tables if table.table.startswith("auto_cluster_test_")
        ]

        assert (
            len(auto_cluster_test_tables) == expected_count
        ), f"Discovery should find all {expected_count} auto clustering test tables, found {len(auto_cluster_test_tables)}"

        # Verify all expected table names are present
        found_table_names = {table.table for table in auto_cluster_test_tables}
        expected_table_names = {spec.name for spec in TABLE_SPECS_CLUSTER_BY_AUTO.values()}

        assert (
            found_table_names == expected_table_names
        ), f"Table name mismatch. Expected: {expected_table_names}, Found: {found_table_names}"

    def test_has_any_clustering_approach_integration(
        self, cluster_by_auto_test_tables, clustering_validator, integration_discovery
    ):
        """Test has_any_clustering_approach method with real auto clustering tables."""
        discovered_tables = integration_discovery.discover_tables()

        # Find both enabled and disabled tables
        enabled_table = None
        disabled_table = None
        for table in discovered_tables:
            if table.table == "auto_cluster_test_basic_enabled":
                enabled_table = table
            elif table.table == "auto_cluster_test_basic_disabled":
                disabled_table = table

        assert enabled_table is not None, "Should find enabled auto clustering table"
        assert disabled_table is not None, "Should find disabled auto clustering table"

        # Enabled table should have clustering approach
        assert (
            clustering_validator.has_any_clustering_approach(enabled_table) is True
        ), "Enabled table should have clustering approach"

        # Disabled table should not have clustering approach
        assert (
            clustering_validator.has_any_clustering_approach(disabled_table) is False
        ), "Disabled table should not have clustering approach"
