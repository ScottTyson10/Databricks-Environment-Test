"""Test table specifications for explicit clustering columns validation.

Defines test tables designed for Layer 2 integration testing of explicit clustering columns.
Each table represents a specific test case for clustering column detection and validation.
"""

from __future__ import annotations

from tests.fixtures.table_factory import TestTableSpecWithClustering

# Test table specifications for explicit clustering columns scenario
# Each spec represents a specific clustering validation test case
TABLE_SPECS_EXPLICIT_CLUSTERING: dict[str, TestTableSpecWithClustering] = {
    # Tables WITH clustering columns - should pass clustering detection
    "single_clustering_column": TestTableSpecWithClustering(
        name="clustering_test_single_column",
        comment="Test table with single clustering column",
        expected_pass=True,
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("category", "STRING", "Category column for clustering"),
            ("value", "DOUBLE", "Numeric value column"),
        ],
        clustering_columns=["category"],  # Single clustering column
    ),
    "multiple_clustering_columns": TestTableSpecWithClustering(
        name="clustering_test_multiple_columns",
        comment="Test table with multiple clustering columns",
        expected_pass=True,
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("region", "STRING", "Geographic region for clustering"),
            ("category", "STRING", "Product category for clustering"),
            ("date_partition", "DATE", "Date partition for clustering"),
            ("value", "DOUBLE", "Numeric value column"),
        ],
        clustering_columns=["region", "category", "date_partition"],  # Multiple clustering columns
    ),
    "at_max_clustering_limit": TestTableSpecWithClustering(
        name="clustering_test_at_max_limit",
        comment="Test table at maximum clustering column limit (4 columns)",
        expected_pass=True,
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("cluster_col1", "STRING", "First clustering column"),
            ("cluster_col2", "STRING", "Second clustering column"),
            ("cluster_col3", "STRING", "Third clustering column"),
            ("cluster_col4", "STRING", "Fourth clustering column"),
            ("non_cluster_col", "DOUBLE", "Non-clustered column"),
        ],
        clustering_columns=["cluster_col1", "cluster_col2", "cluster_col3", "cluster_col4"],  # At limit (4)
    ),
    # Tables WITHOUT clustering columns - should still be detected correctly
    "no_clustering_columns": TestTableSpecWithClustering(
        name="clustering_test_no_clustering",
        comment="Test table without any clustering columns",
        expected_pass=False,  # No clustering columns = fails clustering detection
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("name", "STRING", "Name column"),
            ("created_at", "TIMESTAMP", "Creation timestamp"),
        ],
        clustering_columns=[],  # No clustering columns
    ),
    # Note: Tables exceeding clustering limits (5+ columns) cannot be created in Databricks
    # These limits are enforced at table creation time, so we test this scenario in unit tests only
    # Edge cases for robust testing
    "mixed_data_types_clustering": TestTableSpecWithClustering(
        name="clustering_test_mixed_types",
        comment="Test table with different data types in clustering columns",
        expected_pass=True,
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("date_cluster", "DATE", "Date clustering column"),
            ("string_cluster", "STRING", "String clustering column"),
            ("int_cluster", "INTEGER", "Integer clustering column"),
            ("other_data", "ARRAY<STRING>", "Non-clustered array column"),
        ],
        clustering_columns=["date_cluster", "string_cluster", "int_cluster"],  # Mixed types
    ),
    "realistic_sales_table": TestTableSpecWithClustering(
        name="clustering_test_realistic_sales",
        comment="Realistic sales table with clustering for performance testing",
        expected_pass=True,
        columns=[
            ("sale_id", "BIGINT", "Unique sale identifier"),
            ("customer_id", "BIGINT", "Customer identifier for clustering"),
            ("product_category", "STRING", "Product category for clustering"),
            ("sale_date", "DATE", "Sale date"),
            ("amount", "DECIMAL(10,2)", "Sale amount"),
            ("quantity", "INTEGER", "Quantity sold"),
            ("discount_applied", "BOOLEAN", "Whether discount was applied"),
        ],
        clustering_columns=["customer_id", "product_category"],  # Realistic clustering
    ),
}
