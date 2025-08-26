"""Table specifications for cluster-by-auto integration testing.

Defines test table specifications for automatic clustering detection scenarios.
Each spec includes table structure and expected validation outcomes.
"""

from dataclasses import dataclass


@dataclass
class ClusterByAutoTableSpec:
    """Specification for a table used in cluster-by-auto integration testing.

    Attributes:
        name: Table name (will be prefixed in tests)
        columns: List of (column_name, column_type, column_comment) tuples
        auto_clustering_enabled: Whether this table should have CLUSTER BY AUTO
        expected_has_auto_clustering: Expected result from has_auto_clustering()
        description: Human-readable description of the test scenario
    """

    name: str
    columns: list[tuple[str, str, str]]
    auto_clustering_enabled: bool
    expected_has_auto_clustering: bool
    description: str


# Test table specifications for cluster-by-auto detection scenarios
TABLE_SPECS_CLUSTER_BY_AUTO: dict[str, ClusterByAutoTableSpec] = {
    # Basic automatic clustering scenario
    "auto_clustering_enabled": ClusterByAutoTableSpec(
        name="auto_cluster_test_basic_enabled",
        columns=[
            ("id", "INT", "Primary key"),
            ("category", "STRING", "Category for clustering"),
            ("region", "STRING", "Region for clustering"),
        ],
        auto_clustering_enabled=True,
        expected_has_auto_clustering=True,
        description="Table with CLUSTER BY AUTO enabled - should be detected",
    ),
    # Baseline table without automatic clustering
    "auto_clustering_disabled": ClusterByAutoTableSpec(
        name="auto_cluster_test_basic_disabled",
        columns=[
            ("id", "INT", "Primary key"),
            ("category", "STRING", "Category column"),
            ("region", "STRING", "Region column"),
        ],
        auto_clustering_enabled=False,
        expected_has_auto_clustering=False,
        description="Table without automatic clustering - should not be detected",
    ),
    # Single column table with auto clustering
    "single_column_auto": ClusterByAutoTableSpec(
        name="auto_cluster_test_single_column",
        columns=[
            ("transaction_id", "BIGINT", "Transaction identifier"),
        ],
        auto_clustering_enabled=True,
        expected_has_auto_clustering=True,
        description="Single column table with automatic clustering",
    ),
    # Multi-column table with auto clustering
    "multi_column_auto": ClusterByAutoTableSpec(
        name="auto_cluster_test_multi_column",
        columns=[
            ("customer_id", "BIGINT", "Customer identifier"),
            ("product_id", "STRING", "Product identifier"),
            ("order_date", "DATE", "Order date"),
            ("amount", "DECIMAL(10,2)", "Order amount"),
            ("status", "STRING", "Order status"),
        ],
        auto_clustering_enabled=True,
        expected_has_auto_clustering=True,
        description="Multi-column realistic table with automatic clustering",
    ),
    # Realistic sales table with auto clustering
    "realistic_sales_auto": ClusterByAutoTableSpec(
        name="auto_cluster_test_realistic_sales",
        columns=[
            ("sale_id", "BIGINT", "Sale identifier"),
            ("customer_id", "BIGINT", "Customer who made purchase"),
            ("product_category", "STRING", "Product category"),
            ("sale_date", "TIMESTAMP", "When sale occurred"),
            ("amount", "DECIMAL(12,2)", "Sale amount"),
            ("payment_method", "STRING", "Payment method used"),
            ("store_location", "STRING", "Store location"),
        ],
        auto_clustering_enabled=True,
        expected_has_auto_clustering=True,
        description="Realistic sales table with automatic clustering for performance",
    ),
    # Empty table with auto clustering (cost-effective testing)
    "empty_table_auto": ClusterByAutoTableSpec(
        name="auto_cluster_test_empty_table",
        columns=[
            ("test_col1", "STRING", "Test column 1"),
            ("test_col2", "INT", "Test column 2"),
        ],
        auto_clustering_enabled=True,
        expected_has_auto_clustering=True,
        description="Empty table with auto clustering - cost-effective testing approach",
    ),
    # Comparison table without clustering (baseline for empty table)
    "empty_table_no_clustering": ClusterByAutoTableSpec(
        name="auto_cluster_test_empty_baseline",
        columns=[
            ("test_col1", "STRING", "Test column 1"),
            ("test_col2", "INT", "Test column 2"),
        ],
        auto_clustering_enabled=False,
        expected_has_auto_clustering=False,
        description="Empty baseline table without clustering for comparison",
    ),
}


def get_cluster_by_auto_table_count() -> int:
    """Get total number of cluster-by-auto test tables."""
    return len(TABLE_SPECS_CLUSTER_BY_AUTO)


def get_cluster_by_auto_enabled_specs() -> list[ClusterByAutoTableSpec]:
    """Get all table specs with auto clustering enabled."""
    return [spec for spec in TABLE_SPECS_CLUSTER_BY_AUTO.values() if spec.auto_clustering_enabled]


def get_cluster_by_auto_disabled_specs() -> list[ClusterByAutoTableSpec]:
    """Get all table specs with auto clustering disabled."""
    return [spec for spec in TABLE_SPECS_CLUSTER_BY_AUTO.values() if not spec.auto_clustering_enabled]


def get_cluster_by_auto_spec_by_name(name: str) -> ClusterByAutoTableSpec | None:
    """Get a specific table spec by key name."""
    return TABLE_SPECS_CLUSTER_BY_AUTO.get(name)
