"""Test table specifications for cluster exclusion validation.

Defines test tables designed for Layer 2 integration testing of cluster exclusion flag.
Each table represents a specific test case for cluster exclusion detection and validation.
"""

from __future__ import annotations

from tests.fixtures.table_factory import TestTableSpecWithProperties

# Test table specifications for cluster exclusion scenario
# Each spec represents a specific exclusion validation test case
TABLE_SPECS_CLUSTER_EXCLUSION: dict[str, TestTableSpecWithProperties] = {
    # Table WITH cluster_exclusion=true - should be exempt from clustering requirements
    "excluded_table": TestTableSpecWithProperties(
        name="cluster_exclusion_test_excluded",
        comment="Test table explicitly excluded from clustering requirements",
        expected_pass=True,  # Should pass validation as it's exempt
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("data", "STRING", "Data column"),
            ("value", "DOUBLE", "Numeric value column"),
            ("created_date", "DATE", "Record creation date"),
        ],
        properties={"cluster_exclusion": "true"},  # Explicit exclusion flag
    ),
    # Table WITHOUT cluster_exclusion - should not be exempt
    "not_excluded_table": TestTableSpecWithProperties(
        name="cluster_exclusion_test_not_excluded",
        comment="Test table without exclusion flag (subject to clustering requirements)",
        expected_pass=False,  # May fail clustering requirements if no clustering present
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("category", "STRING", "Category column"),
            ("amount", "DECIMAL(10,2)", "Transaction amount"),
        ],
        properties={},  # No exclusion flag
    ),
    # Table with cluster_exclusion=false - explicitly not excluded
    "explicitly_not_excluded": TestTableSpecWithProperties(
        name="cluster_exclusion_test_false_flag",
        comment="Test table with cluster_exclusion explicitly set to false",
        expected_pass=False,  # Subject to clustering requirements
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("user_id", "BIGINT", "User identifier"),
            ("status", "STRING", "Record status"),
        ],
        properties={"cluster_exclusion": "false"},  # Explicitly false
    ),
    # Table with exclusion AND clustering - exclusion should take precedence
    "excluded_with_clustering": TestTableSpecWithProperties(
        name="cluster_exclusion_test_mixed",
        comment="Test table with both exclusion flag and clustering columns",
        expected_pass=True,  # Should pass as exclusion takes precedence
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("region", "STRING", "Geographic region"),
            ("category", "STRING", "Product category"),
            ("value", "DOUBLE", "Numeric value"),
        ],
        properties={
            "cluster_exclusion": "true",
            # Note: Clustering columns would be set separately via CLUSTER BY clause
            # This tests that exclusion overrides clustering requirements
        },
    ),
    # Table with other properties but no exclusion
    "other_properties_only": TestTableSpecWithProperties(
        name="cluster_exclusion_test_other_props",
        comment="Test table with other properties but no exclusion flag",
        expected_pass=False,  # Subject to clustering requirements
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("data", "STRING", "Data column"),
        ],
        properties={
            "delta.minWriterVersion": "7",
            "delta.enableDeletionVectors": "true",
            # No cluster_exclusion property
        },
    ),
    # Table with case variation in exclusion flag value
    "excluded_case_variant": TestTableSpecWithProperties(
        name="cluster_exclusion_test_case_variant",
        comment="Test table with cluster_exclusion using different case",
        expected_pass=True,  # Should be case-insensitive
        columns=[
            ("id", "BIGINT", "Primary key column"),
            ("name", "STRING", "Name column"),
        ],
        properties={"cluster_exclusion": "TRUE"},  # Uppercase value
    ),
}
