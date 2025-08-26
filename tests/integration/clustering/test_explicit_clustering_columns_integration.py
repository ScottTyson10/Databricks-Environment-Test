"""Integration tests for "Explicit clustering columns detection" scenario.

Layer 2 tests that create real Databricks tables with clustering, discover them, and validate clustering detection.
Uses pytest patterns with real Databricks SDK integration.
"""

import os

import pytest
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

from tests.fixtures.clustering.explicit_clustering_specs import TABLE_SPECS_EXPLICIT_CLUSTERING
from tests.fixtures.table_factory import create_test_tables_for_explicit_clustering_columns_scenario
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
def explicit_clustering_test_tables(databricks_client):
    """Class-scoped test tables for explicit clustering - create for each test class, cleanup after."""
    with create_test_tables_for_explicit_clustering_columns_scenario(databricks_client) as created_tables:
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
class TestExplicitClusteringColumnsIntegration:
    """Integration tests for explicit clustering columns detection.

    Tests the "Explicit clustering columns detection" scenario end-to-end.
    Uses dedicated test tables designed specifically for clustering validation.
    """

    def _get_table_by_fixture_key(self, fixture_dict, key, discovered_tables):
        """Helper to get a table by fixture key from discovered tables."""
        table_name = fixture_dict[key]
        for table in discovered_tables:
            if table.full_name == table_name:
                return table
        return None

    def test_end_to_end_clustering_detection_validation(
        self, explicit_clustering_test_tables, clustering_validator, integration_discovery
    ):
        """Test complete end-to-end flow: create → discover → validate clustering detection."""
        # Verify we created the expected tables
        expected_count = len(TABLE_SPECS_EXPLICIT_CLUSTERING)
        assert (
            len(explicit_clustering_test_tables) == expected_count
        ), f"Expected {expected_count} tables, created {len(explicit_clustering_test_tables)}"

        # Discover the tables we just created
        discovered_tables = integration_discovery.discover_tables()

        # Filter to only our clustering test tables
        discovered_clustering_tables = [
            table for table in discovered_tables if table.table.startswith("clustering_test_")
        ]

        # Should have discovered all our test tables
        assert (
            len(discovered_clustering_tables) == expected_count
        ), f"Expected {expected_count} tables, found {len(discovered_clustering_tables)}"

        # Validate each discovered table for clustering detection
        clustering_results = {}
        for table in discovered_clustering_tables:
            has_clustering = clustering_validator.has_clustering_columns(table)
            clustering_results[table.table] = has_clustering

        # Check results match expectations from our specs
        expected_results = {}
        for spec in TABLE_SPECS_EXPLICIT_CLUSTERING.values():
            # Tables with clustering columns should be detected (expected_pass = has clustering)
            expected_results[spec.name] = len(spec.clustering_columns) > 0

        assert clustering_results == expected_results, f"Clustering detection results mismatch: {clustering_results}"

    def test_single_clustering_column_detection(
        self, explicit_clustering_test_tables, clustering_validator, integration_discovery
    ):
        """Test detection of single clustering column with real Databricks table."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our single clustering column test table
        single_cluster_table = None
        for table in discovered_tables:
            if table.table == "clustering_test_single_column":
                single_cluster_table = table
                break

        assert single_cluster_table is not None, "Should find single clustering column test table"
        assert clustering_validator.has_clustering_columns(single_cluster_table) is True, "Should detect clustering"

        clustering_columns = clustering_validator.get_clustering_columns(single_cluster_table)
        assert clustering_columns == ["category"], f"Expected ['category'], got {clustering_columns}"
        assert (
            clustering_validator.count_clustering_columns(single_cluster_table) == 1
        ), "Should count 1 clustering column"

    def test_multiple_clustering_columns_detection(
        self, explicit_clustering_test_tables, clustering_validator, integration_discovery
    ):
        """Test detection of multiple clustering columns with real Databricks table."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our multiple clustering columns test table
        multiple_cluster_table = None
        for table in discovered_tables:
            if table.table == "clustering_test_multiple_columns":
                multiple_cluster_table = table
                break

        assert multiple_cluster_table is not None, "Should find multiple clustering columns test table"
        assert clustering_validator.has_clustering_columns(multiple_cluster_table) is True, "Should detect clustering"

        clustering_columns = clustering_validator.get_clustering_columns(multiple_cluster_table)
        expected_columns = ["region", "category", "date_partition"]
        assert clustering_columns == expected_columns, f"Expected {expected_columns}, got {clustering_columns}"
        assert (
            clustering_validator.count_clustering_columns(multiple_cluster_table) == 3
        ), "Should count 3 clustering columns"

    def test_no_clustering_columns_detection(
        self, explicit_clustering_test_tables, clustering_validator, integration_discovery
    ):
        """Test correct handling of tables without clustering columns."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our no clustering test table
        no_cluster_table = None
        for table in discovered_tables:
            if table.table == "clustering_test_no_clustering":
                no_cluster_table = table
                break

        assert no_cluster_table is not None, "Should find no clustering test table"
        assert clustering_validator.has_clustering_columns(no_cluster_table) is False, "Should not detect clustering"

        clustering_columns = clustering_validator.get_clustering_columns(no_cluster_table)
        assert clustering_columns == [], f"Expected empty list, got {clustering_columns}"
        assert clustering_validator.count_clustering_columns(no_cluster_table) == 0, "Should count 0 clustering columns"

    def test_clustering_column_limits_validation(
        self, explicit_clustering_test_tables, clustering_validator, integration_discovery
    ):
        """Test validation of clustering column limits with real Databricks tables."""
        discovered_tables = integration_discovery.discover_tables()

        # Test table at limit (4 columns) - should pass
        at_limit_table = None
        for table in discovered_tables:
            if table.table == "clustering_test_at_max_limit":
                at_limit_table = table
                break

        assert at_limit_table is not None, "Should find at-limit test table"
        assert (
            clustering_validator.validates_clustering_column_limits(at_limit_table) is True
        ), "Should pass limits validation"
        assert clustering_validator.count_clustering_columns(at_limit_table) == 4, "Should have 4 clustering columns"

    # Note: Tables exceeding clustering limits cannot be created in Databricks
    # Databricks enforces the 4-column limit at table creation time
    # This scenario is tested in unit tests with mock data instead

    def test_mixed_data_types_clustering(
        self, explicit_clustering_test_tables, clustering_validator, integration_discovery
    ):
        """Test clustering columns with mixed data types."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our mixed data types test table
        mixed_types_table = None
        for table in discovered_tables:
            if table.table == "clustering_test_mixed_types":
                mixed_types_table = table
                break

        assert mixed_types_table is not None, "Should find mixed data types test table"
        assert clustering_validator.has_clustering_columns(mixed_types_table) is True, "Should detect clustering"

        clustering_columns = clustering_validator.get_clustering_columns(mixed_types_table)
        expected_columns = ["date_cluster", "string_cluster", "int_cluster"]
        assert clustering_columns == expected_columns, f"Expected {expected_columns}, got {clustering_columns}"

    def test_realistic_table_clustering(
        self, explicit_clustering_test_tables, clustering_validator, integration_discovery
    ):
        """Test clustering detection with realistic table structure."""
        discovered_tables = integration_discovery.discover_tables()

        # Find our realistic sales test table
        sales_table = None
        for table in discovered_tables:
            if table.table == "clustering_test_realistic_sales":
                sales_table = table
                break

        assert sales_table is not None, "Should find realistic sales test table"
        assert clustering_validator.has_clustering_columns(sales_table) is True, "Should detect clustering"

        clustering_columns = clustering_validator.get_clustering_columns(sales_table)
        expected_columns = ["customer_id", "product_category"]
        assert clustering_columns == expected_columns, f"Expected {expected_columns}, got {clustering_columns}"

    @pytest.mark.parametrize(
        "fixture_key,expected_has_clustering",
        [
            ("single_clustering_column", True),
            ("multiple_clustering_columns", True),
            ("at_max_clustering_limit", True),
            ("no_clustering_columns", False),
            # Note: exceeds_clustering_limit removed - Databricks prevents creation of tables with >4 clustering columns
            ("mixed_data_types_clustering", True),
            ("realistic_sales_table", True),
        ],
    )
    def test_individual_clustering_detection_parametrized(
        self,
        explicit_clustering_test_tables,
        clustering_validator,
        integration_discovery,
        fixture_key,
        expected_has_clustering,
    ):
        """Test clustering detection of individual tables using parametrize."""
        # Use the fixture to get the specific table
        target_table = self._get_table_by_fixture_key(
            explicit_clustering_test_tables, fixture_key, integration_discovery.discover_tables()
        )

        assert target_table is not None, f"Could not find test table for fixture key: {fixture_key}"

        # Validate clustering detection
        has_clustering = clustering_validator.has_clustering_columns(target_table)
        assert (
            has_clustering is expected_has_clustering
        ), f"Table {target_table.full_name} clustering detection mismatch. Expected {expected_has_clustering}, got {has_clustering}"

    def test_clustering_configuration_integration(self, clustering_validator):
        """Test that clustering validator respects configuration in integration environment."""
        # Test default validator configuration
        assert (
            clustering_validator.clustering_property_name == "clusteringColumns"
        ), "Default clustering property should be clusteringColumns"
        assert clustering_validator.max_clustering_columns == 4, "Default max clustering columns should be 4"
        assert clustering_validator.allow_empty_clustering is True, "Should allow empty clustering by default"

    def test_discovery_finds_all_clustering_test_tables(self, explicit_clustering_test_tables, integration_discovery):
        """Test that discovery engine finds all our clustering test tables."""
        # Verify tables were created
        expected_count = len(TABLE_SPECS_EXPLICIT_CLUSTERING)
        assert len(explicit_clustering_test_tables) == expected_count, "Should have created all test tables"

        discovered_tables = integration_discovery.discover_tables()

        # Should find all clustering test tables in pytest_test_data schema
        clustering_test_tables = [table for table in discovered_tables if table.table.startswith("clustering_test_")]

        assert (
            len(clustering_test_tables) == expected_count
        ), f"Discovery should find all {expected_count} clustering test tables, found {len(clustering_test_tables)}"

        # Verify all expected table names are present
        found_table_names = {table.table for table in clustering_test_tables}
        expected_table_names = {spec.name for spec in TABLE_SPECS_EXPLICIT_CLUSTERING.values()}

        assert (
            found_table_names == expected_table_names
        ), f"Table name mismatch. Expected: {expected_table_names}, Found: {found_table_names}"
