"""Unit tests for comprehensive documentation validation.

Tests the comprehensive validator that combines multiple individual checks.
"""

import pytest

from tests.utils.discovery import ColumnInfo, TableInfo
from tests.validators.comprehensive import ComprehensiveDocumentationValidator


@pytest.fixture
def comprehensive_validator():
    """Fixture providing a ComprehensiveDocumentationValidator instance."""
    return ComprehensiveDocumentationValidator()


class TestComprehensiveDocumentationValidator:
    """Test suite for comprehensive documentation validation."""

    def test_all_checks_pass_scenario(self, comprehensive_validator):
        """Test table that passes all documentation checks."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="This is a comprehensive documentation example for testing",
            columns=[
                ColumnInfo(name="user_id", type_text="INT", comment="Unique user identifier"),
                ColumnInfo(name="email", type_text="STRING", comment="User email address"),
                ColumnInfo(name="name", type_text="STRING", comment="Full user name"),
                ColumnInfo(name="created_at", type_text="TIMESTAMP", comment="Record creation timestamp"),
                ColumnInfo(name="data_field", type_text="STRING", comment="Additional data field"),
            ],
        )

        result = comprehensive_validator.evaluate_table_compliance(table)

        assert result.overall_compliant is True
        assert result.failure_reasons == []
        assert result.individual_results["table_has_comment"] is True
        assert result.individual_results["table_comment_length"] is True
        assert result.individual_results["no_placeholder_comments"] is True
        assert result.individual_results["critical_columns_documented"] is True

    def test_multiple_failures_scenario(self, comprehensive_validator):
        """Test table that fails multiple documentation checks."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            comment="TODO",  # Placeholder comment, too short
            columns=[
                ColumnInfo(name="user_id", type_text="INT", comment=None),  # Critical, undocumented
                ColumnInfo(name="data", type_text="STRING", comment="Regular field"),  # Not critical
            ],
        )

        result = comprehensive_validator.evaluate_table_compliance(table)

        assert result.overall_compliant is False
        assert len(result.failure_reasons) >= 3  # Should fail multiple checks

        # Check individual results
        assert result.individual_results["table_has_comment"] is True  # Has content
        assert result.individual_results["table_comment_length"] is False  # Too short
        assert result.individual_results["no_placeholder_comments"] is False  # Is placeholder
        assert result.individual_results["critical_columns_documented"] is False  # user_id undocumented

    def test_configuration_integration(self, comprehensive_validator):
        """Test that comprehensive validator uses configuration correctly."""
        # Should load 5 required checks from config
        assert len(comprehensive_validator._required_checks) == 5
        assert "table_has_comment" in comprehensive_validator._required_checks
        assert "column_coverage >= 80" in comprehensive_validator._required_checks

    def test_evaluate_multiple_tables(self, comprehensive_validator):
        """Test evaluating multiple tables with summary statistics."""
        tables = [
            # Compliant table
            TableInfo(
                catalog="cat",
                schema="schema",
                table="good_table",
                comment="Good table with comprehensive documentation",
                columns=[
                    ColumnInfo(name="id", type_text="INT", comment="Primary key"),
                    ColumnInfo(name="name", type_text="STRING", comment="Entity name"),
                    ColumnInfo(name="created_at", type_text="TIMESTAMP", comment="Creation time"),
                ],
            ),
            # Non-compliant table
            TableInfo(
                catalog="cat",
                schema="schema",
                table="bad_table",
                comment=None,  # No comment
                columns=[
                    ColumnInfo(name="user_id", type_text="INT", comment=None),  # Critical, undocumented
                ],
            ),
        ]

        results, summary = comprehensive_validator.evaluate_tables(tables)

        assert len(results) == 2
        assert summary["total_tables"] == 2
        assert summary["comprehensive_compliant"] == 1
        assert summary["comprehensive_compliance_rate"] == 50.0

        # Check individual results breakdown
        assert results[0].overall_compliant is True
        assert results[1].overall_compliant is False
