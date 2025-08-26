"""Unit tests for explicit clustering columns validation."""

import pytest

from tests.utils.discovery import ColumnInfo, TableInfo
from tests.validators.clustering import ClusteringValidator


@pytest.fixture
def clustering_validator():
    """Fixture providing a ClusteringValidator instance."""
    return ClusteringValidator()


class TestExplicitClusteringColumns:
    """Test suite for explicit clustering columns detection."""

    def test_table_with_single_clustering_column(self, clustering_validator):
        """Test table with single clustering column."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Test table with single clustering column",
            columns=[
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                ColumnInfo(name="category", type_text="STRING", comment="Category column"),
            ],
            properties={"clusteringColumns": [["category"]]},
        )

        assert clustering_validator.has_clustering_columns(table) is True
        assert clustering_validator.get_clustering_columns(table) == ["category"]
        assert clustering_validator.count_clustering_columns(table) == 1

    def test_table_with_multiple_clustering_columns(self, clustering_validator):
        """Test table with multiple clustering columns."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Test table with multiple clustering columns",
            columns=[
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                ColumnInfo(name="category", type_text="STRING", comment="Category"),
                ColumnInfo(name="region", type_text="STRING", comment="Region"),
            ],
            properties={"clusteringColumns": [["category"], ["region"]]},
        )

        assert clustering_validator.has_clustering_columns(table) is True
        assert clustering_validator.get_clustering_columns(table) == ["category", "region"]
        assert clustering_validator.count_clustering_columns(table) == 2

    def test_table_without_clustering_columns(self, clustering_validator):
        """Test table without clustering columns."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Test table without clustering",
            columns=[
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                ColumnInfo(name="name", type_text="STRING", comment="Name"),
            ],
            properties={},  # No clustering properties
        )

        assert clustering_validator.has_clustering_columns(table) is False
        assert clustering_validator.get_clustering_columns(table) == []
        assert clustering_validator.count_clustering_columns(table) == 0

    def test_table_with_no_properties(self, clustering_validator):
        """Test table with no properties at all."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Test table with no properties",
            columns=[
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
            ],
            properties=None,  # No properties
        )

        assert clustering_validator.has_clustering_columns(table) is False
        assert clustering_validator.get_clustering_columns(table) == []
        assert clustering_validator.count_clustering_columns(table) == 0

    def test_table_with_empty_clustering_columns(self, clustering_validator):
        """Test table with empty clustering columns list."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Test table with empty clustering",
            columns=[
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
            ],
            properties={"clusteringColumns": []},  # Empty clustering list
        )

        assert clustering_validator.has_clustering_columns(table) is False
        assert clustering_validator.get_clustering_columns(table) == []
        assert clustering_validator.count_clustering_columns(table) == 0

    def test_clustering_column_limits_validation(self, clustering_validator):
        """Test validation of clustering column limits."""
        # Table within limits (2 columns, max is 4)
        table_within_limits = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Table within clustering limits",
            columns=[
                ColumnInfo(name="col1", type_text="STRING", comment="Column 1"),
                ColumnInfo(name="col2", type_text="STRING", comment="Column 2"),
            ],
            properties={"clusteringColumns": [["col1"], ["col2"]]},
        )

        assert clustering_validator.validates_clustering_column_limits(table_within_limits) is True

        # Table at limits (4 columns, max is 4)
        table_at_limits = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Table at clustering limits",
            columns=[
                ColumnInfo(name="col1", type_text="STRING", comment="Column 1"),
                ColumnInfo(name="col2", type_text="STRING", comment="Column 2"),
                ColumnInfo(name="col3", type_text="STRING", comment="Column 3"),
                ColumnInfo(name="col4", type_text="STRING", comment="Column 4"),
            ],
            properties={"clusteringColumns": [["col1"], ["col2"], ["col3"], ["col4"]]},
        )

        assert clustering_validator.validates_clustering_column_limits(table_at_limits) is True

        # Table exceeding limits (5 columns, max is 4)
        table_exceeding_limits = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Table exceeding clustering limits",
            columns=[
                ColumnInfo(name="col1", type_text="STRING", comment="Column 1"),
                ColumnInfo(name="col2", type_text="STRING", comment="Column 2"),
                ColumnInfo(name="col3", type_text="STRING", comment="Column 3"),
                ColumnInfo(name="col4", type_text="STRING", comment="Column 4"),
                ColumnInfo(name="col5", type_text="STRING", comment="Column 5"),
            ],
            properties={"clusteringColumns": [["col1"], ["col2"], ["col3"], ["col4"], ["col5"]]},
        )

        assert clustering_validator.validates_clustering_column_limits(table_exceeding_limits) is False

    def test_table_without_clustering_passes_limits(self, clustering_validator):
        """Test that table without clustering passes column limits validation."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Table without clustering",
            columns=[
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
            ],
            properties={},  # No clustering
        )

        assert clustering_validator.validates_clustering_column_limits(table) is True

    def test_configuration_integration(self, clustering_validator):
        """Test that validator loads configuration correctly."""
        # Test that configuration values are loaded
        assert clustering_validator.clustering_property_name == "clusteringColumns"
        assert clustering_validator.max_clustering_columns == 4
        assert clustering_validator.allow_empty_clustering is True
        assert clustering_validator.require_explicit_clustering is False

    def test_complex_clustering_data_structure(self, clustering_validator):
        """Test handling of complex nested clustering data structures."""
        # Test realistic clustering data from Databricks
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Table with complex clustering structure",
            columns=[
                ColumnInfo(name="partition_date", type_text="DATE", comment="Partition date"),
                ColumnInfo(name="customer_id", type_text="BIGINT", comment="Customer ID"),
                ColumnInfo(name="product_category", type_text="STRING", comment="Product category"),
            ],
            properties={
                "clusteringColumns": [["partition_date"], ["customer_id"], ["product_category"]],
                "delta.feature.clustering": "supported",  # Additional clustering properties
            },
        )

        assert clustering_validator.has_clustering_columns(table) is True
        assert clustering_validator.get_clustering_columns(table) == [
            "partition_date",
            "customer_id",
            "product_category",
        ]
        assert clustering_validator.count_clustering_columns(table) == 3
        assert clustering_validator.validates_clustering_column_limits(table) is True

    def test_edge_case_malformed_clustering_data(self, clustering_validator):
        """Test handling of malformed clustering data."""
        # Test with malformed nested structure
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="Table with malformed clustering data",
            columns=[
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
            ],
            properties={
                "clusteringColumns": [[], ["valid_column"], []],  # Mixed empty and valid
            },
        )

        # Should handle malformed data gracefully
        assert clustering_validator.has_clustering_columns(table) is True
        assert clustering_validator.get_clustering_columns(table) == ["valid_column"]
        assert clustering_validator.count_clustering_columns(table) == 1
