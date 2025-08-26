"""Table specifications for delta auto-optimization integration testing.

Defines test table specifications for delta auto-optimization detection scenarios.
Each spec includes table structure and expected validation outcomes.
"""

from dataclasses import dataclass


@dataclass
class DeltaAutoOptimizationTableSpec:
    """Specification for a table used in delta auto-optimization integration testing.

    Attributes:
        name: Table name (will be prefixed in tests)
        columns: List of (column_name, column_type, column_comment) tuples
        optimize_write_enabled: Whether optimizeWrite should be enabled
        auto_compact_enabled: Whether autoCompact should be enabled
        expected_has_delta_auto_optimization: Expected result from has_delta_auto_optimization()
        description: Human-readable description of the test scenario
    """

    name: str
    columns: list[tuple[str, str, str]]
    optimize_write_enabled: bool
    auto_compact_enabled: bool
    expected_has_delta_auto_optimization: bool
    description: str


# Test table specifications for delta auto-optimization detection scenarios
TABLE_SPECS_DELTA_AUTO_OPTIMIZATION: dict[str, DeltaAutoOptimizationTableSpec] = {
    # Both flags enabled - should be detected
    "both_flags_enabled": DeltaAutoOptimizationTableSpec(
        name="delta_opt_test_both_enabled",
        columns=[
            ("transaction_id", "BIGINT", "Transaction identifier"),
            ("customer_id", "BIGINT", "Customer identifier"),
            ("amount", "DECIMAL(10,2)", "Transaction amount"),
        ],
        optimize_write_enabled=True,
        auto_compact_enabled=True,
        expected_has_delta_auto_optimization=True,
        description="Table with both optimizeWrite and autoCompact enabled",
    ),
    # Only optimizeWrite enabled - should not be detected (requires both by default)
    "optimize_write_only": DeltaAutoOptimizationTableSpec(
        name="delta_opt_test_optimize_only",
        columns=[
            ("order_id", "STRING", "Order identifier"),
            ("product_id", "STRING", "Product identifier"),
            ("quantity", "INT", "Order quantity"),
        ],
        optimize_write_enabled=True,
        auto_compact_enabled=False,
        expected_has_delta_auto_optimization=False,
        description="Table with only optimizeWrite enabled",
    ),
    # Only autoCompact enabled - should not be detected (requires both by default)
    "auto_compact_only": DeltaAutoOptimizationTableSpec(
        name="delta_opt_test_compact_only",
        columns=[
            ("user_id", "BIGINT", "User identifier"),
            ("event_type", "STRING", "Event type"),
            ("timestamp", "TIMESTAMP", "Event timestamp"),
        ],
        optimize_write_enabled=False,
        auto_compact_enabled=True,
        expected_has_delta_auto_optimization=False,
        description="Table with only autoCompact enabled",
    ),
    # Neither flag enabled - should not be detected
    "neither_flag_enabled": DeltaAutoOptimizationTableSpec(
        name="delta_opt_test_neither_enabled",
        columns=[
            ("record_id", "STRING", "Record identifier"),
            ("data_value", "STRING", "Data value"),
            ("created_at", "TIMESTAMP", "Creation timestamp"),
        ],
        optimize_write_enabled=False,
        auto_compact_enabled=False,
        expected_has_delta_auto_optimization=False,
        description="Table with neither optimization flag enabled",
    ),
    # Single column with both flags - minimal viable table
    "single_column_both_flags": DeltaAutoOptimizationTableSpec(
        name="delta_opt_test_single_column",
        columns=[
            ("id", "BIGINT", "Unique identifier"),
        ],
        optimize_write_enabled=True,
        auto_compact_enabled=True,
        expected_has_delta_auto_optimization=True,
        description="Single column table with both optimization flags",
    ),
    # Realistic sales table with full optimization
    "realistic_sales_optimized": DeltaAutoOptimizationTableSpec(
        name="delta_opt_test_sales_optimized",
        columns=[
            ("sale_id", "BIGINT", "Sale identifier"),
            ("customer_id", "BIGINT", "Customer who made purchase"),
            ("product_category", "STRING", "Product category"),
            ("sale_date", "DATE", "Sale date"),
            ("amount", "DECIMAL(12,2)", "Sale amount"),
            ("payment_method", "STRING", "Payment method"),
            ("store_id", "STRING", "Store identifier"),
        ],
        optimize_write_enabled=True,
        auto_compact_enabled=True,
        expected_has_delta_auto_optimization=True,
        description="Realistic sales table with full delta auto-optimization",
    ),
    # Cost-effective empty table with both flags
    "empty_table_optimized": DeltaAutoOptimizationTableSpec(
        name="delta_opt_test_empty_optimized",
        columns=[
            ("test_col1", "STRING", "Test column 1"),
            ("test_col2", "INT", "Test column 2"),
        ],
        optimize_write_enabled=True,
        auto_compact_enabled=True,
        expected_has_delta_auto_optimization=True,
        description="Empty table with both optimization flags - cost-effective testing",
    ),
    # Cost-effective empty table without optimization (baseline)
    "empty_table_baseline": DeltaAutoOptimizationTableSpec(
        name="delta_opt_test_empty_baseline",
        columns=[
            ("test_col1", "STRING", "Test column 1"),
            ("test_col2", "INT", "Test column 2"),
        ],
        optimize_write_enabled=False,
        auto_compact_enabled=False,
        expected_has_delta_auto_optimization=False,
        description="Empty baseline table without optimization flags for comparison",
    ),
}


def get_delta_auto_optimization_table_count() -> int:
    """Get total number of delta auto-optimization test tables."""
    return len(TABLE_SPECS_DELTA_AUTO_OPTIMIZATION)


def get_delta_auto_optimization_enabled_specs() -> list[DeltaAutoOptimizationTableSpec]:
    """Get all table specs with delta auto-optimization enabled."""
    return [spec for spec in TABLE_SPECS_DELTA_AUTO_OPTIMIZATION.values() if spec.expected_has_delta_auto_optimization]


def get_delta_auto_optimization_disabled_specs() -> list[DeltaAutoOptimizationTableSpec]:
    """Get all table specs with delta auto-optimization disabled."""
    return [spec for spec in TABLE_SPECS_DELTA_AUTO_OPTIMIZATION.values() if not spec.expected_has_delta_auto_optimization]


def get_delta_auto_optimization_spec_by_name(name: str) -> DeltaAutoOptimizationTableSpec | None:
    """Get a specific table spec by key name."""
    return TABLE_SPECS_DELTA_AUTO_OPTIMIZATION.get(name)