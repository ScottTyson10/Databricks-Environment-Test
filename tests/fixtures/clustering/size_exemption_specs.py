"""Test table specifications for size-based clustering exemption validation.

Defines test tables designed for Layer 2 integration testing of automatic size-based exemption.
Each table represents a specific test case for size threshold detection and exemption logic.
"""

from __future__ import annotations

from tests.fixtures.table_factory import TestTableSpecWithClustering, TestTableSpecWithProperties

# Test table specifications for size-based exemption scenario
# Each spec represents a specific size exemption validation test case
TABLE_SPECS_SIZE_EXEMPTION: dict[str, TestTableSpecWithProperties | TestTableSpecWithClustering] = {
    # Small table (under 1MB test threshold) - should be exempt
    "small_exempt_table": TestTableSpecWithProperties(
        name="size_exemption_test_small_table",
        comment="Small test table that should be automatically exempt from clustering",
        expected_pass=True,  # Should pass validation as it's under test threshold (1MB)
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("data", "STRING", "Small data column"),
        ],
        properties={},  # No manual exclusion flag - relying on size-based exemption
        # Note: Will be kept small (under 1MB) by inserting minimal test data
    ),
    # Small table with manual exclusion - both exemptions should apply
    "small_table_with_manual_exclusion": TestTableSpecWithProperties(
        name="size_exemption_test_small_excluded",
        comment="Small table that is also manually excluded - double exemption test",
        expected_pass=True,  # Should pass due to both size and manual exemption
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("value", "DOUBLE", "Numeric value"),
        ],
        properties={"cluster_exclusion": "true"},  # Manual exclusion AND size exemption
    ),
    # Small table with clustering - clustering should take precedence over size exemption
    "small_table_with_clustering": TestTableSpecWithClustering(
        name="size_exemption_test_small_clustered",
        comment="Small table with clustering columns - clustering should override size exemption",
        expected_pass=True,  # Should pass because clustering is present (not subject to exemption)
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("category", "STRING", "Category for clustering"),
            ("data", "STRING", "Data column"),
        ],
        clustering_columns=["category"],  # Will be clustered, so size exemption doesn't apply
    ),
    # Large table (will be made over test threshold) - should NOT be exempt
    "large_table_no_exemption": TestTableSpecWithProperties(
        name="size_exemption_test_large_table",
        comment="Large table that should not be exempt from clustering requirements",
        expected_pass=False,  # Should fail validation as it's over test threshold and no clustering
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("large_data", "STRING", "Large data column for size testing"),
            ("category", "STRING", "Category column"),
            ("value", "DOUBLE", "Numeric value"),
            ("created_at", "TIMESTAMP", "Creation timestamp"),
        ],
        properties={},  # No exclusion flags
        # Note: Will have larger data inserted to exceed 1MB test threshold
    ),
    # Large table with manual exclusion - manual exclusion should override size
    "large_table_with_manual_exclusion": TestTableSpecWithProperties(
        name="size_exemption_test_large_excluded",
        comment="Large table with manual exclusion - manual flag should override size check",
        expected_pass=True,  # Should pass due to manual exclusion despite large size
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("large_data", "STRING", "Large data column"),
            ("metadata", "STRING", "Additional metadata column"),
        ],
        properties={"cluster_exclusion": "true"},  # Manual exclusion overrides size
    ),
    # Edge case: Empty table - should be considered small
    "empty_table": TestTableSpecWithProperties(
        name="size_exemption_test_empty_table",
        comment="Empty table to test zero/minimal size exemption logic",
        expected_pass=True,  # Should be exempt as empty table is under threshold
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("data", "STRING", "Data column"),
        ],
        properties={},
        # Note: No data will be inserted, testing zero-size case
    ),
    # Production threshold test table - sized close to 1GB boundary
    "threshold_boundary_table": TestTableSpecWithProperties(
        name="size_exemption_test_boundary",
        comment="Table for testing size boundary conditions near thresholds",
        expected_pass=True,  # Will be kept under test threshold (1MB)
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("data", "STRING", "Variable size data for boundary testing"),
            ("filler", "STRING", "Additional column for size control"),
        ],
        properties={},
        # Note: Used to test exact threshold boundaries in integration tests
    ),
}
