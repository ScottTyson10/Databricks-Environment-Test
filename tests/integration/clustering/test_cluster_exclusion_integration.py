"""Integration tests for "Tables can be exempted from clustering with cluster_exclusion flag" scenario.

Layer 2 tests that create real Databricks tables with cluster_exclusion property,
discover them, and validate exclusion detection. Uses pytest patterns with
real Databricks SDK integration.
"""

import pytest
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

from tests.fixtures.clustering.cluster_exclusion_specs import TABLE_SPECS_CLUSTER_EXCLUSION
from tests.fixtures.table_factory import create_test_tables_for_cluster_exclusion_scenario
from tests.utils.discovery_engine import create_integration_discovery
from tests.validators.clustering import ClusteringValidator


@pytest.fixture(scope="session")
def databricks_client():
    """Session-scoped Databricks client fixture."""
    load_dotenv()
    return WorkspaceClient()


@pytest.fixture(scope="session")
def cluster_exclusion_test_tables(databricks_client):
    """Session-scoped fixture creating test tables for cluster exclusion scenarios.

    Creates all tables defined in TABLE_SPECS_CLUSTER_EXCLUSION with proper cleanup.
    Tables are created once per test session and shared across all tests.
    """
    with create_test_tables_for_cluster_exclusion_scenario(databricks_client) as tables:
        yield tables


@pytest.fixture(scope="function")
def integration_discovery(databricks_client):
    """Function-scoped discovery engine for integration tests."""
    return create_integration_discovery(databricks_client, test_catalog="workspace", test_schema="pytest_test_data")


@pytest.fixture(scope="function")
def clustering_validator():
    """Function-scoped clustering validator."""
    return ClusteringValidator()


class TestClusterExclusionIntegration:
    """Integration tests for cluster exclusion flag detection with real Databricks tables."""

    def test_discovery_finds_all_test_tables(self, cluster_exclusion_test_tables, integration_discovery):
        """Test that discovery engine finds all our cluster exclusion test tables."""
        # Verify tables were created
        expected_count = len(TABLE_SPECS_CLUSTER_EXCLUSION)
        assert len(cluster_exclusion_test_tables) == expected_count, "Should have created all test tables"

        discovered_tables = integration_discovery.discover_tables()

        # Should find all cluster exclusion test tables in pytest_test_data schema
        exclusion_test_tables = [
            table for table in discovered_tables if table.table.startswith("cluster_exclusion_test_")
        ]

        assert (
            len(exclusion_test_tables) == expected_count
        ), f"Discovery should find all {expected_count} cluster exclusion test tables, found {len(exclusion_test_tables)}"

        # Verify all expected table names are present
        found_table_names = {table.table for table in exclusion_test_tables}
        expected_table_names = {spec.name for spec in TABLE_SPECS_CLUSTER_EXCLUSION.values()}
        assert found_table_names == expected_table_names, "All expected test tables should be discovered"

    def test_excluded_table_detection(self, cluster_exclusion_test_tables, integration_discovery, clustering_validator):
        """Test detection of tables with cluster_exclusion=true property."""
        discovered_tables = integration_discovery.discover_tables()

        # Find the excluded table
        excluded_table = None
        for table in discovered_tables:
            if table.table == "cluster_exclusion_test_excluded":
                excluded_table = table
                break

        assert excluded_table is not None, "Should find the excluded test table"

        # Verify exclusion detection
        assert clustering_validator.has_cluster_exclusion(excluded_table) is True
        assert clustering_validator.get_cluster_exclusion_status(excluded_table) == "excluded"
        assert clustering_validator.is_exempt_from_clustering_requirements(excluded_table) is True
        assert clustering_validator.should_enforce_clustering_requirements(excluded_table) is False

        # Verify property exists and has correct value
        assert excluded_table.properties is not None
        assert "cluster_exclusion" in excluded_table.properties
        assert excluded_table.properties["cluster_exclusion"] == "true"

    def test_not_excluded_table_detection(
        self, cluster_exclusion_test_tables, integration_discovery, clustering_validator
    ):
        """Test detection of tables without cluster_exclusion property."""
        discovered_tables = integration_discovery.discover_tables()

        # Find the not excluded table
        not_excluded_table = None
        for table in discovered_tables:
            if table.table == "cluster_exclusion_test_not_excluded":
                not_excluded_table = table
                break

        assert not_excluded_table is not None, "Should find the not excluded test table"

        # Verify no exclusion detected
        assert clustering_validator.has_cluster_exclusion(not_excluded_table) is False
        assert clustering_validator.get_cluster_exclusion_status(not_excluded_table) == "not_excluded"
        assert clustering_validator.is_exempt_from_clustering_requirements(not_excluded_table) is False
        assert clustering_validator.should_enforce_clustering_requirements(not_excluded_table) is True

        # Property should not exist
        if not_excluded_table.properties:
            assert "cluster_exclusion" not in not_excluded_table.properties

    def test_explicitly_false_exclusion(
        self, cluster_exclusion_test_tables, integration_discovery, clustering_validator
    ):
        """Test detection of tables with cluster_exclusion=false."""
        discovered_tables = integration_discovery.discover_tables()

        # Find table with explicit false flag
        false_flag_table = None
        for table in discovered_tables:
            if table.table == "cluster_exclusion_test_false_flag":
                false_flag_table = table
                break

        assert false_flag_table is not None, "Should find the false flag test table"

        # Verify not excluded (false != true)
        assert clustering_validator.has_cluster_exclusion(false_flag_table) is False
        assert clustering_validator.get_cluster_exclusion_status(false_flag_table) == "not_excluded"
        assert clustering_validator.is_exempt_from_clustering_requirements(false_flag_table) is False
        assert clustering_validator.should_enforce_clustering_requirements(false_flag_table) is True

        # Property should exist but with value "false"
        assert false_flag_table.properties is not None
        assert "cluster_exclusion" in false_flag_table.properties
        assert false_flag_table.properties["cluster_exclusion"] == "false"

    def test_case_insensitive_exclusion(
        self, cluster_exclusion_test_tables, integration_discovery, clustering_validator
    ):
        """Test that cluster_exclusion detection is case-insensitive."""
        discovered_tables = integration_discovery.discover_tables()

        # Find table with uppercase TRUE value
        case_variant_table = None
        for table in discovered_tables:
            if table.table == "cluster_exclusion_test_case_variant":
                case_variant_table = table
                break

        assert case_variant_table is not None, "Should find the case variant test table"

        # Verify exclusion detected despite uppercase value
        assert clustering_validator.has_cluster_exclusion(case_variant_table) is True
        assert clustering_validator.get_cluster_exclusion_status(case_variant_table) == "excluded"
        assert clustering_validator.is_exempt_from_clustering_requirements(case_variant_table) is True

        # Property should have uppercase value
        assert case_variant_table.properties is not None
        assert "cluster_exclusion" in case_variant_table.properties
        assert case_variant_table.properties["cluster_exclusion"] == "TRUE"

    def test_exclusion_with_other_properties(
        self, cluster_exclusion_test_tables, integration_discovery, clustering_validator
    ):
        """Test that exclusion detection works when other properties are present."""
        discovered_tables = integration_discovery.discover_tables()

        # Find table with other properties
        other_props_table = None
        for table in discovered_tables:
            if table.table == "cluster_exclusion_test_other_props":
                other_props_table = table
                break

        assert other_props_table is not None, "Should find the other properties test table"

        # Verify no exclusion when property is absent
        assert clustering_validator.has_cluster_exclusion(other_props_table) is False
        assert clustering_validator.get_cluster_exclusion_status(other_props_table) == "not_excluded"

        # Verify other properties are present
        assert other_props_table.properties is not None
        assert len(other_props_table.properties) > 0
        assert "cluster_exclusion" not in other_props_table.properties

    def test_exclusion_precedence_over_clustering(
        self, cluster_exclusion_test_tables, integration_discovery, clustering_validator
    ):
        """Test that exclusion takes precedence even when clustering might be present."""
        discovered_tables = integration_discovery.discover_tables()

        # Find mixed table (exclusion + potentially has clustering)
        mixed_table = None
        for table in discovered_tables:
            if table.table == "cluster_exclusion_test_mixed":
                mixed_table = table
                break

        assert mixed_table is not None, "Should find the mixed test table"

        # Verify exclusion detected
        assert clustering_validator.has_cluster_exclusion(mixed_table) is True
        assert clustering_validator.is_exempt_from_clustering_requirements(mixed_table) is True

        # Even if table has clustering, it should still be exempt
        assert clustering_validator.should_enforce_clustering_requirements(mixed_table) is False

    def test_all_test_tables_validation(
        self, cluster_exclusion_test_tables, integration_discovery, clustering_validator
    ):
        """Test all cluster exclusion tables match their expected validation outcomes."""
        discovered_tables = integration_discovery.discover_tables()

        # Create lookup for discovered tables
        discovered_by_name = {table.table: table for table in discovered_tables}

        # Validate each test spec
        for _spec_name, spec in TABLE_SPECS_CLUSTER_EXCLUSION.items():
            table = discovered_by_name.get(spec.name)
            assert table is not None, f"Should find test table: {spec.name}"

            # Check if exclusion flag is present and true
            has_exclusion = False
            if spec.properties.get("cluster_exclusion"):
                has_exclusion = spec.properties["cluster_exclusion"].lower() == "true"

            # Verify exclusion detection matches expectation
            assert (
                clustering_validator.has_cluster_exclusion(table) == has_exclusion
            ), f"Table {spec.name}: exclusion detection should match spec"

            # Verify exemption status matches expected_pass
            # Note: expected_pass=True means table is exempt from clustering requirements
            if spec.expected_pass:
                assert clustering_validator.is_exempt_from_clustering_requirements(
                    table
                ), f"Table {spec.name}: should be exempt from clustering requirements"
            else:
                assert not clustering_validator.is_exempt_from_clustering_requirements(
                    table
                ), f"Table {spec.name}: should NOT be exempt from clustering requirements"


class TestClusterExclusionPropertiesExtraction:
    """Test property extraction and availability through discovery engine."""

    def test_properties_extracted_correctly(self, cluster_exclusion_test_tables, integration_discovery):
        """Test that table properties are correctly extracted by discovery engine."""
        discovered_tables = integration_discovery.discover_tables()

        # Check each test table
        for table in discovered_tables:
            if not table.table.startswith("cluster_exclusion_test_"):
                continue

            # All our test tables should have properties (even if empty dict)
            assert table.properties is not None, f"Table {table.table} should have properties dict"

            # Find corresponding spec
            spec = None
            for spec_entry in TABLE_SPECS_CLUSTER_EXCLUSION.values():
                if spec_entry.name == table.table:
                    spec = spec_entry
                    break

            if spec and spec.properties:
                # Verify expected properties are present
                for prop_key, prop_value in spec.properties.items():
                    assert prop_key in table.properties, f"Table {table.table}: expected property {prop_key} not found"
                    assert (
                        table.properties[prop_key] == prop_value
                    ), f"Table {table.table}: property {prop_key} value mismatch"

    def test_integration_with_config_loader(self, clustering_validator):
        """Test that configuration values are properly loaded for exclusion detection."""
        # Verify config is loaded correctly
        assert clustering_validator.honor_exclusion_flag is True
        assert clustering_validator.exclusion_property_name == "cluster_exclusion"

        # These should have reasonable defaults from config
        assert clustering_validator.size_threshold_bytes > 0
        assert clustering_validator.test_size_threshold_bytes > 0
        assert isinstance(clustering_validator.exempt_small_tables, bool)
