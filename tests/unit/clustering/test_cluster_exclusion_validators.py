"""Unit tests for cluster exclusion validation."""

import pytest

from tests.utils.discovery import ColumnInfo, TableInfo
from tests.validators.clustering import ClusteringValidator


@pytest.fixture
def clustering_validator():
    """Fixture providing a ClusteringValidator instance."""
    return ClusteringValidator()


class TestClusterExclusionDetection:
    """Test suite for cluster exclusion flag detection."""

    def test_table_with_cluster_exclusion_enabled(self, clustering_validator):
        """Test table with cluster_exclusion='true'."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="excluded_table",
            comment="Test table with cluster exclusion enabled",
            columns=(
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                ColumnInfo(name="data", type_text="STRING", comment="Data column"),
            ),
            properties={"cluster_exclusion": "true"},
        )

        assert clustering_validator.has_cluster_exclusion(table) is True
        assert clustering_validator.get_cluster_exclusion_status(table) == "excluded"
        assert clustering_validator.is_exempt_from_clustering_requirements(table) is True
        assert clustering_validator.should_enforce_clustering_requirements(table) is False

    def test_table_with_cluster_exclusion_disabled(self, clustering_validator):
        """Test table with cluster_exclusion='false'."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="not_excluded_table",
            comment="Test table with cluster exclusion disabled",
            columns=(
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                ColumnInfo(name="data", type_text="STRING", comment="Data column"),
            ),
            properties={"cluster_exclusion": "false"},
        )

        assert clustering_validator.has_cluster_exclusion(table) is False
        assert clustering_validator.get_cluster_exclusion_status(table) == "not_excluded"
        assert clustering_validator.is_exempt_from_clustering_requirements(table) is False
        assert clustering_validator.should_enforce_clustering_requirements(table) is True

    def test_table_without_cluster_exclusion_property(self, clustering_validator):
        """Test table without cluster_exclusion property."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="regular_table",
            comment="Test table without cluster exclusion property",
            columns=(
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                ColumnInfo(name="data", type_text="STRING", comment="Data column"),
            ),
            properties={"some_other_property": "value"},
        )

        assert clustering_validator.has_cluster_exclusion(table) is False
        assert clustering_validator.get_cluster_exclusion_status(table) == "not_excluded"
        assert clustering_validator.is_exempt_from_clustering_requirements(table) is False
        assert clustering_validator.should_enforce_clustering_requirements(table) is True

    def test_table_with_no_properties(self, clustering_validator):
        """Test table with no properties at all."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="no_properties_table",
            comment="Test table with no properties",
            columns=(
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                ColumnInfo(name="data", type_text="STRING", comment="Data column"),
            ),
            properties=None,
        )

        assert clustering_validator.has_cluster_exclusion(table) is False
        assert clustering_validator.get_cluster_exclusion_status(table) == "unknown"
        assert clustering_validator.is_exempt_from_clustering_requirements(table) is False
        assert clustering_validator.should_enforce_clustering_requirements(table) is True

    def test_table_with_empty_properties(self, clustering_validator):
        """Test table with empty properties dictionary."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="empty_properties_table",
            comment="Test table with empty properties",
            columns=(
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                ColumnInfo(name="data", type_text="STRING", comment="Data column"),
            ),
            properties={},
        )

        assert clustering_validator.has_cluster_exclusion(table) is False
        assert clustering_validator.get_cluster_exclusion_status(table) == "not_excluded"
        assert clustering_validator.is_exempt_from_clustering_requirements(table) is False
        assert clustering_validator.should_enforce_clustering_requirements(table) is True


class TestClusterExclusionEdgeCases:
    """Test edge cases for cluster exclusion detection."""

    def test_cluster_exclusion_case_insensitive(self, clustering_validator):
        """Test that cluster_exclusion value is case insensitive."""
        test_cases = [
            {"cluster_exclusion": "TRUE"},
            {"cluster_exclusion": "True"},
            {"cluster_exclusion": "tRuE"},
        ]

        for properties in test_cases:
            table = TableInfo(
                catalog="test_catalog",
                schema="test_schema",
                table="case_test_table",
                comment="Test table for case insensitive cluster exclusion",
                columns=(ColumnInfo(name="id", type_text="INT", comment="Primary key"),),
                properties=properties,
            )

            assert clustering_validator.has_cluster_exclusion(table) is True
            assert clustering_validator.get_cluster_exclusion_status(table) == "excluded"

    def test_cluster_exclusion_non_string_values(self, clustering_validator):
        """Test cluster_exclusion with non-string values."""
        test_cases = [
            {"cluster_exclusion": True},  # Boolean true
            {"cluster_exclusion": 1},  # Integer 1
            {"cluster_exclusion": "yes"},  # Non-standard string
            {"cluster_exclusion": ""},  # Empty string
        ]

        for properties in test_cases:
            table = TableInfo(
                catalog="test_catalog",
                schema="test_schema",
                table="non_string_test_table",
                comment="Test table for non-string cluster exclusion values",
                columns=(ColumnInfo(name="id", type_text="INT", comment="Primary key"),),
                properties=properties,
            )

            # Only string "true" (case insensitive) should be considered as exclusion
            expected_excluded = str(properties["cluster_exclusion"]).lower() == "true"
            assert clustering_validator.has_cluster_exclusion(table) is expected_excluded

    def test_cluster_exclusion_with_other_clustering_approaches(self, clustering_validator):
        """Test cluster exclusion combined with other clustering approaches."""
        # Table with both cluster_exclusion and explicit clustering
        table_with_explicit = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="mixed_table",
            comment="Test table with both exclusion and explicit clustering",
            columns=(
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                ColumnInfo(name="category", type_text="STRING", comment="Category column"),
            ),
            properties={
                "cluster_exclusion": "true",
                "clusteringColumns": '[["category"]]',
            },
        )

        assert clustering_validator.has_cluster_exclusion(table_with_explicit) is True
        assert clustering_validator.has_clustering_columns(table_with_explicit) is True
        assert clustering_validator.is_exempt_from_clustering_requirements(table_with_explicit) is True

        # Table with both cluster_exclusion and auto-clustering
        table_with_auto = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="mixed_auto_table",
            comment="Test table with both exclusion and auto clustering",
            columns=(
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                ColumnInfo(name="category", type_text="STRING", comment="Category column"),
            ),
            properties={
                "cluster_exclusion": "true",
                "clusterByAuto": "true",
            },
        )

        assert clustering_validator.has_cluster_exclusion(table_with_auto) is True
        assert clustering_validator.has_auto_clustering(table_with_auto) is True
        assert clustering_validator.is_exempt_from_clustering_requirements(table_with_auto) is True


class TestClusterExclusionConfiguration:
    """Test cluster exclusion configuration handling."""

    def test_honor_exclusion_flag_disabled(self, clustering_validator):
        """Test behavior when honor_exclusion_flag is disabled."""
        # Create a validator with modified configuration
        # Note: This is a unit test, so we directly modify the instance
        clustering_validator.honor_exclusion_flag = False

        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="excluded_table",
            comment="Test table with cluster exclusion",
            columns=(ColumnInfo(name="id", type_text="INT", comment="Primary key"),),
            properties={"cluster_exclusion": "true"},
        )

        # When honor_exclusion_flag is False, exclusion should be ignored
        assert clustering_validator.has_cluster_exclusion(table) is False
        assert clustering_validator.get_cluster_exclusion_status(table) == "disabled"
        assert clustering_validator.is_exempt_from_clustering_requirements(table) is False

    def test_custom_exclusion_property_name(self, clustering_validator):
        """Test custom exclusion property name."""
        # Modify the property name for this test
        clustering_validator.exclusion_property_name = "custom_exclusion_flag"

        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="custom_table",
            comment="Test table with custom exclusion property",
            columns=(ColumnInfo(name="id", type_text="INT", comment="Primary key"),),
            properties={"custom_exclusion_flag": "true"},
        )

        assert clustering_validator.has_cluster_exclusion(table) is True
        assert clustering_validator.get_cluster_exclusion_status(table) == "excluded"

        # Original property name should not work
        table_with_standard_property = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="standard_table",
            comment="Test table with standard exclusion property",
            columns=(ColumnInfo(name="id", type_text="INT", comment="Primary key"),),
            properties={"cluster_exclusion": "true"},
        )

        assert clustering_validator.has_cluster_exclusion(table_with_standard_property) is False
