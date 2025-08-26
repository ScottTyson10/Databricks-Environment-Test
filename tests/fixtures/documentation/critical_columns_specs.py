"""Table specifications for critical columns scenarios.

Contains test table specs for:
- Critical columns must be documented
"""

from tests.fixtures.table_factory import TestTableSpecWithColumns

# Predefined test table specifications for "Critical columns must be documented" scenario
TABLE_SPECS_CRITICAL_COLUMNS = {
    "all_critical_documented": TestTableSpecWithColumns(
        name="critical_test_all_documented",
        comment="Table with all critical columns properly documented",
        expected_pass=True,
        columns=[
            ("user_id", "BIGINT", "Primary identifier for users"),
            ("customer_email", "STRING", "Customer email address for notifications"),
            ("account_balance", "DECIMAL(10,2)", "Current account balance"),
            ("created_at", "TIMESTAMP", "Record creation timestamp"),
        ],
    ),
    "some_critical_undocumented": TestTableSpecWithColumns(
        name="critical_test_some_undocumented",
        comment="Table with some critical columns missing documentation",
        expected_pass=False,
        columns=[
            ("user_id", "BIGINT", None),  # Critical column without documentation
            ("customer_email", "STRING", "Customer email address for notifications"),
            ("account_balance", "DECIMAL(10,2)", None),  # Critical column without documentation
            ("created_at", "TIMESTAMP", "Record creation timestamp"),
        ],
    ),
    "all_critical_undocumented": TestTableSpecWithColumns(
        name="critical_test_all_undocumented",
        comment="Table with all critical columns missing documentation",
        expected_pass=False,
        columns=[
            ("user_id", "BIGINT", None),
            ("customer_email", "STRING", None),
            ("account_balance", "DECIMAL(10,2)", None),
            ("password_hash", "STRING", None),
        ],
    ),
    "no_critical_columns": TestTableSpecWithColumns(
        name="critical_test_no_critical",
        comment="Table with no critical columns (should pass)",
        expected_pass=True,
        columns=[
            ("description", "STRING", "General description field"),
            ("category", "STRING", "Product category"),
            ("status", "STRING", None),  # Non-critical column can be undocumented
        ],
    ),
    "mixed_critical_patterns": TestTableSpecWithColumns(
        name="critical_test_mixed_patterns",
        comment="Table with various critical column patterns",
        expected_pass=False,
        columns=[
            ("USER_ID", "BIGINT", "User identifier"),  # Uppercase pattern documented
            ("CustomerName", "STRING", None),  # CamelCase critical pattern undocumented
            ("audit_log_id", "STRING", "Audit log reference"),  # Audit pattern documented
            ("security_token", "STRING", None),  # Security pattern undocumented
            ("normal_field", "STRING", None),  # Non-critical field can be undocumented
        ],
    ),
    "whitespace_comments": TestTableSpecWithColumns(
        name="critical_test_whitespace",
        comment="Table with critical columns having whitespace-only comments",
        expected_pass=False,
        columns=[
            ("user_id", "BIGINT", "   \n\t   "),  # Whitespace-only comment (should fail)
            ("email", "STRING", "Valid email comment"),
            ("payment_method", "STRING", ""),  # Empty comment (should fail)
        ],
    ),
    "edge_case_patterns": TestTableSpecWithColumns(
        name="critical_test_edge_cases",
        comment="Table with edge case critical column patterns",
        expected_pass=False,
        columns=[
            ("id", "BIGINT", "Primary key"),  # Short 'id' pattern documented
            ("ssn", "STRING", None),  # PII pattern undocumented
            ("api_key", "STRING", "API access key"),  # Security pattern documented
            ("credit_score", "INT", None),  # Financial pattern undocumented
        ],
    ),
}
