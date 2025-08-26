"""Unit tests for automatic clustering detection validation."""

import pytest

from tests.utils.discovery import ColumnInfo, TableInfo
from tests.validators.clustering import ClusteringValidator


@pytest.fixture
def clustering_validator():
    """Fixture providing a ClusteringValidator instance."""
    return ClusteringValidator()


class TestAutoClusteringDetection:
    """Test suite for automatic clustering detection using clusterByAuto flag."""

    def test_table_with_cluster_by_auto_enabled(self, clustering_validator):
        """Test table with clusterByAuto enabled."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Test table with automatic clustering",
            columns=(
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                ColumnInfo(name="category", type_text="STRING", comment="Category column"),
            ),
            properties={"clusterByAuto": "true"},
        )

        assert clustering_validator.has_auto_clustering(table) is True
        assert clustering_validator.get_auto_clustering_status(table) == "enabled"
        assert clustering_validator.has_any_clustering_approach(table) is True

    def test_table_with_cluster_by_auto_disabled(self, clustering_validator):
        """Test table with clusterByAuto explicitly disabled."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Test table with automatic clustering disabled",
            columns=(
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                ColumnInfo(name="category", type_text="STRING", comment="Category column"),
            ),
            properties={"clusterByAuto": "false"},
        )

        assert clustering_validator.has_auto_clustering(table) is False
        assert clustering_validator.get_auto_clustering_status(table) == "disabled"
        assert clustering_validator.has_any_clustering_approach(table) is False

    def test_table_without_cluster_by_auto_property(self, clustering_validator):
        """Test table without clusterByAuto property."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Test table without auto clustering property",
            columns=(
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                ColumnInfo(name="category", type_text="STRING", comment="Category column"),
            ),
            properties={},  # No clusterByAuto property
        )

        assert clustering_validator.has_auto_clustering(table) is False
        assert clustering_validator.get_auto_clustering_status(table) == "disabled"
        assert clustering_validator.has_any_clustering_approach(table) is False

    def test_table_with_no_properties(self, clustering_validator):
        """Test table with no properties at all."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Test table with no properties",
            columns=(ColumnInfo(name="id", type_text="INT", comment="Primary key"),),
            properties=None,  # No properties
        )

        assert clustering_validator.has_auto_clustering(table) is False
        assert clustering_validator.get_auto_clustering_status(table) == "unknown"
        assert clustering_validator.has_any_clustering_approach(table) is False

    def test_cluster_by_auto_case_insensitive(self, clustering_validator):
        """Test that clusterByAuto detection is case-insensitive."""
        test_cases = [
            ("True", True),
            ("TRUE", True),
            ("true", True),
            ("False", False),
            ("FALSE", False),
            ("false", False),
            ("yes", False),  # Only "true" should be accepted
            ("1", False),  # Only "true" should be accepted
        ]

        for property_value, expected_result in test_cases:
            table = TableInfo(
                catalog="test_catalog",
                schema="test_schema",
                table="test_table",
                comment=f"Test table with clusterByAuto={property_value}",
                columns=(ColumnInfo(name="id", type_text="INT", comment="Test column"),),
                properties={"clusterByAuto": property_value},
            )

            assert (
                clustering_validator.has_auto_clustering(table) is expected_result
            ), f"Failed for value: {property_value}"

    def test_combination_explicit_and_auto_clustering(self, clustering_validator):
        """Test table with both explicit clustering columns AND automatic clustering."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Test table with both explicit and automatic clustering",
            columns=(
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                ColumnInfo(name="category", type_text="STRING", comment="Category column"),
            ),
            properties={
                "clusteringColumns": [["category"]],  # Explicit clustering
                "clusterByAuto": "true",  # Auto clustering
            },
        )

        # Both detection methods should work
        assert clustering_validator.has_clustering_columns(table) is True
        assert clustering_validator.has_auto_clustering(table) is True
        assert clustering_validator.has_any_clustering_approach(table) is True
        assert clustering_validator.get_clustering_columns(table) == ["category"]
        assert clustering_validator.get_auto_clustering_status(table) == "enabled"

    def test_realistic_databricks_auto_clustering_properties(self, clustering_validator):
        """Test with realistic properties from Databricks auto clustering table."""
        # Based on feasibility test results
        table = TableInfo(
            catalog="workspace",
            schema="pytest_test_data",
            table="auto_cluster_table",
            comment="Realistic automatic clustering table",
            columns=(
                ColumnInfo(name="id", type_text="INT", comment="ID column"),
                ColumnInfo(name="category", type_text="STRING", comment="Category column"),
            ),
            properties={
                "delta.lastCommitTimestamp": "1756182043000",
                "clusteringColumns": "[]",  # Empty initially
                "delta.lastUpdateVersion": "0",
                "delta.feature.clustering": "supported",
                "delta.enableRowTracking": "true",
                "clusterByAuto": "true",  # Main detection property
                "delta.feature.invariants": "supported",
            },
        )

        assert clustering_validator.has_auto_clustering(table) is True
        assert clustering_validator.get_auto_clustering_status(table) == "enabled"
        assert clustering_validator.has_any_clustering_approach(table) is True
        # Explicit clustering columns are empty initially (system will populate later)
        assert clustering_validator.has_clustering_columns(table) is False  # Empty clustering columns initially

    def test_configuration_integration(self, clustering_validator):
        """Test that auto-clustering validator respects configuration."""
        # Test default configuration values
        assert clustering_validator.cluster_by_auto_property == "clusterByAuto"
        assert clustering_validator.cluster_by_auto_value == "true"
        assert clustering_validator.require_cluster_by_auto is False

    def test_edge_case_malformed_cluster_by_auto_data(self, clustering_validator):
        """Test handling of malformed clusterByAuto data."""
        test_cases = [
            (None, False),  # None value
            ("", False),  # Empty string
            ("   ", False),  # Whitespace only
            ("invalid", False),  # Invalid value
            (123, False),  # Non-string value (should still work via str conversion)
        ]

        for property_value, expected_result in test_cases:
            table = TableInfo(
                catalog="test_catalog",
                schema="test_schema",
                table="test_table",
                comment=f"Test malformed clusterByAuto value: {property_value}",
                columns=(ColumnInfo(name="id", type_text="INT", comment="Test column"),),
                properties={"clusterByAuto": property_value},
            )

            assert (
                clustering_validator.has_auto_clustering(table) is expected_result
            ), f"Failed for value: {repr(property_value)}"

    def test_auto_clustering_status_comprehensive(self, clustering_validator):
        """Test all possible auto clustering status scenarios."""
        test_cases = [
            (None, "unknown", "No properties at all"),
            ({}, "disabled", "Empty properties"),
            ({"clusterByAuto": "true"}, "enabled", "Auto clustering enabled"),
            ({"clusterByAuto": "false"}, "disabled", "Auto clustering disabled"),
            ({"clusterByAuto": "invalid"}, "disabled", "Invalid clusterByAuto value"),
            ({"other_prop": "value"}, "disabled", "clusterByAuto property missing"),
        ]

        for properties, expected_status, description in test_cases:
            table = TableInfo(
                catalog="test_catalog",
                schema="test_schema",
                table="test_table",
                comment=description,
                columns=(ColumnInfo(name="id", type_text="INT", comment="Test column"),),
                properties=properties,
            )

            assert (
                clustering_validator.get_auto_clustering_status(table) == expected_status
            ), f"Failed for: {description}"

    def test_has_any_clustering_approach_scenarios(self, clustering_validator):
        """Test comprehensive scenarios for has_any_clustering_approach method."""
        test_cases = [
            # (explicit_clustering, auto_clustering, expected_result, description)
            (None, None, False, "No clustering at all"),
            ([["col1"]], None, True, "Only explicit clustering"),
            (None, "true", True, "Only automatic clustering"),
            ([["col1"]], "true", True, "Both explicit and automatic clustering"),
            ([["col1"]], "false", True, "Explicit clustering, auto disabled"),
            ([], "true", True, "Empty explicit clustering, auto enabled"),
            ([], "false", False, "Empty explicit clustering, auto disabled"),
        ]

        for explicit, auto, expected, description in test_cases:
            properties = {}
            if explicit is not None:
                properties["clusteringColumns"] = explicit
            if auto is not None:
                properties["clusterByAuto"] = auto

            table = TableInfo(
                catalog="test_catalog",
                schema="test_schema",
                table="test_table",
                comment=description,
                columns=(ColumnInfo(name="col1", type_text="STRING", comment="Test column"),),
                properties=properties,
            )

            result = clustering_validator.has_any_clustering_approach(table)
            assert result is expected, f"Failed for: {description} - Expected {expected}, got {result}"
