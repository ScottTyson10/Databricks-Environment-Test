"""Unit tests for critical column documentation validation.

Tests the 'Critical columns must be documented' scenario.
"""

import pytest

from tests.utils.discovery import ColumnInfo, TableInfo
from tests.validators.documentation import DocumentationValidator


@pytest.fixture
def validator():
    """Fixture providing a DocumentationValidator instance."""
    return DocumentationValidator()


class TestCriticalColumnDocumentation:
    """Test suite for the 'Critical columns must be documented' scenario.

    Validates DocumentationValidator methods for critical column documentation.
    """

    def test_no_columns_passes(self, validator):
        """Test that tables with no columns pass validation."""
        table = TableInfo(catalog="test_catalog", schema="test_schema", table="test_table", columns=[])
        assert validator.has_all_critical_columns_documented(table) is True
        assert validator.get_undocumented_critical_columns(table) == []

    def test_no_critical_columns_passes(self, validator):
        """Test that tables with no critical columns pass validation."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="regular_field", type_text="STRING", comment="Regular data"),
                ColumnInfo(name="data_value", type_text="INT", comment=None),
                ColumnInfo(name="notes", type_text="TEXT", comment="Some notes"),
            ],
        )
        assert validator.has_all_critical_columns_documented(table) is True
        assert validator.get_undocumented_critical_columns(table) == []

    def test_documented_critical_columns_pass(self, validator):
        """Test that documented critical columns pass validation."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="user_id", type_text="INT", comment="Unique user identifier"),
                ColumnInfo(name="email", type_text="STRING", comment="User email address"),
                ColumnInfo(name="created_at", type_text="TIMESTAMP", comment="Record creation time"),
            ],
        )
        assert validator.has_all_critical_columns_documented(table) is True
        assert validator.get_undocumented_critical_columns(table) == []

    def test_undocumented_critical_columns_fail(self, validator):
        """Test that undocumented critical columns are detected."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="user_id", type_text="INT", comment=None),
                ColumnInfo(name="email", type_text="STRING", comment=""),
                ColumnInfo(name="password_hash", type_text="STRING", comment="   "),
            ],
        )
        assert validator.has_all_critical_columns_documented(table) is False
        undocumented = validator.get_undocumented_critical_columns(table)
        assert set(undocumented) == {"user_id", "email", "password_hash"}

    def test_mixed_documentation_detects_violations(self, validator):
        """Test detection with mixed documented and undocumented critical columns."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="user_id", type_text="INT", comment="User ID"),
                ColumnInfo(name="email", type_text="STRING", comment=None),
                ColumnInfo(name="created_at", type_text="TIMESTAMP", comment="Creation time"),
                ColumnInfo(name="modified_by", type_text="STRING", comment=""),
                ColumnInfo(name="notes", type_text="TEXT", comment="User notes"),
            ],
        )
        assert validator.has_all_critical_columns_documented(table) is False
        undocumented = validator.get_undocumented_critical_columns(table)
        assert set(undocumented) == {"email", "modified_by"}

    @pytest.mark.parametrize(
        "column_name,is_critical",
        [
            # Identity patterns
            ("user_id", True),
            ("customer_key", True),
            ("uuid", True),
            ("record_uuid", True),
            # PII patterns
            ("email", True),
            ("user_email", True),
            ("phone", True),
            ("phone_number", True),
            ("address", True),
            ("home_address", True),
            ("ssn", True),
            ("dob", True),
            ("birth_date", True),
            ("customer_name", True),
            # Financial patterns
            ("account_number", True),
            ("credit_card", True),
            ("card_number", True),
            ("bank_account", True),
            ("salary", True),
            ("payment_amount", True),
            # Security patterns
            ("password", True),
            ("password_hash", True),
            ("api_token", True),
            ("secret_key", True),
            # Audit patterns
            ("created_at", True),
            ("modified_at", True),
            ("updated_by", True),
            ("deleted_flag", True),
            ("user_ref", True),
            # Non-critical columns
            ("data", False),
            ("value", False),
            ("description", False),
            ("status", False),
            ("type", False),
            ("category", False),
        ],
    )
    def test_critical_column_pattern_matching(self, validator, column_name, is_critical):
        """Test pattern matching for critical column identification."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name=column_name, type_text="STRING", comment=None),
            ],
        )

        undocumented = validator.get_undocumented_critical_columns(table)
        if is_critical:
            assert column_name in undocumented, f"'{column_name}' should be identified as critical"
        else:
            assert column_name not in undocumented, f"'{column_name}' should NOT be identified as critical"

    def test_case_insensitive_pattern_matching(self, validator):
        """Test that critical column patterns are matched case-insensitively."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="UserId", type_text="INT", comment=None),
                ColumnInfo(name="USER_EMAIL", type_text="STRING", comment=None),
                ColumnInfo(name="CustomerName", type_text="STRING", comment=None),
                ColumnInfo(name="CREATED_AT", type_text="TIMESTAMP", comment=None),
            ],
        )

        undocumented = validator.get_undocumented_critical_columns(table)
        # All should be detected despite different casing
        assert set(undocumented) == {"UserId", "USER_EMAIL", "CustomerName", "CREATED_AT"}

    def test_empty_and_whitespace_comments_treated_as_undocumented(self, validator):
        """Test that empty and whitespace-only comments are treated as undocumented."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="user_id", type_text="INT", comment=""),
                ColumnInfo(name="email", type_text="STRING", comment="   "),
                ColumnInfo(name="password", type_text="STRING", comment="\t\n"),
                ColumnInfo(name="created_at", type_text="TIMESTAMP", comment="Valid comment"),
            ],
        )

        undocumented = validator.get_undocumented_critical_columns(table)
        # Only created_at has valid documentation
        assert set(undocumented) == {"user_id", "email", "password"}

    def test_partial_pattern_matching(self, validator):
        """Test that patterns match when contained within column names."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                # These contain critical patterns and should be flagged
                ColumnInfo(name="internal_user_id", type_text="INT", comment=None),
                ColumnInfo(name="primary_email_address", type_text="STRING", comment=None),
                ColumnInfo(name="last_modified_timestamp", type_text="TIMESTAMP", comment=None),
                # These don't contain critical patterns
                ColumnInfo(name="description", type_text="TEXT", comment=None),
                ColumnInfo(name="status", type_text="STRING", comment=None),
            ],
        )

        undocumented = validator.get_undocumented_critical_columns(table)
        assert set(undocumented) == {"internal_user_id", "primary_email_address", "last_modified_timestamp"}
