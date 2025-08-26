"""Unit tests for column documentation coverage validation.

Tests the 'Column documentation must meet coverage threshold' scenario.
"""

import pytest

from tests.utils.discovery import ColumnInfo, TableInfo
from tests.validators.documentation import DocumentationValidator


@pytest.fixture
def validator():
    """Fixture providing a DocumentationValidator instance."""
    return DocumentationValidator()


class TestColumnCoverageThreshold:
    """Test column documentation coverage threshold validation."""

    def test_zero_columns_returns_100_percent(self, validator):
        """Test that tables with 0 columns return 100% coverage (vacuously true)."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[],
        )

        percentage = validator.calculate_column_documentation_percentage(table)
        assert percentage == 100.0

        # Should meet any threshold
        assert validator.meets_column_documentation_threshold(table, 80.0) is True
        assert validator.meets_column_documentation_threshold(table, 100.0) is True

    def test_single_column_scenarios(self, validator):
        """Test edge cases with single columns."""
        # Single documented column
        table_documented = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="id", type_text="INT", comment="Primary key"),
            ],
        )

        assert validator.calculate_column_documentation_percentage(table_documented) == 100.0
        assert validator.meets_column_documentation_threshold(table_documented, 80.0) is True

        # Single undocumented column
        table_undocumented = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="id", type_text="INT", comment=None),
            ],
        )

        assert validator.calculate_column_documentation_percentage(table_undocumented) == 0.0
        assert validator.meets_column_documentation_threshold(table_undocumented, 80.0) is False

    def test_percentage_calculations(self, validator):
        """Test various documentation percentage calculations."""
        # 0% documented (0 of 4)
        table_0_percent = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="col1", type_text="INT", comment=None),
                ColumnInfo(name="col2", type_text="STRING", comment=None),
                ColumnInfo(name="col3", type_text="FLOAT", comment=None),
                ColumnInfo(name="col4", type_text="BOOLEAN", comment=None),
            ],
        )

        assert validator.calculate_column_documentation_percentage(table_0_percent) == 0.0

        # 50% documented (2 of 4)
        table_50_percent = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="col1", type_text="INT", comment="First column"),
                ColumnInfo(name="col2", type_text="STRING", comment=None),
                ColumnInfo(name="col3", type_text="FLOAT", comment="Third column"),
                ColumnInfo(name="col4", type_text="BOOLEAN", comment=None),
            ],
        )

        assert validator.calculate_column_documentation_percentage(table_50_percent) == 50.0

        # 75% documented (3 of 4)
        table_75_percent = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="col1", type_text="INT", comment="First column"),
                ColumnInfo(name="col2", type_text="STRING", comment="Second column"),
                ColumnInfo(name="col3", type_text="FLOAT", comment="Third column"),
                ColumnInfo(name="col4", type_text="BOOLEAN", comment=None),
            ],
        )

        assert validator.calculate_column_documentation_percentage(table_75_percent) == 75.0

        # 100% documented (4 of 4)
        table_100_percent = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="col1", type_text="INT", comment="First column"),
                ColumnInfo(name="col2", type_text="STRING", comment="Second column"),
                ColumnInfo(name="col3", type_text="FLOAT", comment="Third column"),
                ColumnInfo(name="col4", type_text="BOOLEAN", comment="Fourth column"),
            ],
        )

        assert validator.calculate_column_documentation_percentage(table_100_percent) == 100.0

    def test_boundary_conditions_80_percent_threshold(self, validator):
        """Test boundary conditions around 80% threshold."""
        # 79% (just below threshold) - 79 documented out of 100
        columns_79_percent = []
        for i in range(79):
            columns_79_percent.append(ColumnInfo(name=f"col{i}", type_text="STRING", comment=f"Column {i}"))
        for i in range(79, 100):
            columns_79_percent.append(ColumnInfo(name=f"col{i}", type_text="STRING", comment=None))

        table_79_percent = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=columns_79_percent,
        )

        assert validator.calculate_column_documentation_percentage(table_79_percent) == 79.0
        assert validator.meets_column_documentation_threshold(table_79_percent, 80.0) is False

        # 80% (exactly at threshold) - 4 documented out of 5
        table_80_percent = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="col1", type_text="INT", comment="Column 1"),
                ColumnInfo(name="col2", type_text="STRING", comment="Column 2"),
                ColumnInfo(name="col3", type_text="FLOAT", comment="Column 3"),
                ColumnInfo(name="col4", type_text="BOOLEAN", comment="Column 4"),
                ColumnInfo(name="col5", type_text="DATE", comment=None),
            ],
        )

        assert validator.calculate_column_documentation_percentage(table_80_percent) == 80.0
        assert validator.meets_column_documentation_threshold(table_80_percent, 80.0) is True

        # 81% (just above threshold) - 81 documented out of 100
        columns_81_percent = []
        for i in range(81):
            columns_81_percent.append(ColumnInfo(name=f"col{i}", type_text="STRING", comment=f"Column {i}"))
        for i in range(81, 100):
            columns_81_percent.append(ColumnInfo(name=f"col{i}", type_text="STRING", comment=None))

        table_81_percent = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=columns_81_percent,
        )

        assert validator.calculate_column_documentation_percentage(table_81_percent) == 81.0
        assert validator.meets_column_documentation_threshold(table_81_percent, 80.0) is True

    def test_whitespace_and_empty_comments_treated_as_undocumented(self, validator):
        """Test that empty and whitespace-only comments are treated as undocumented."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="col1", type_text="INT", comment="Valid comment"),
                ColumnInfo(name="col2", type_text="STRING", comment=""),  # Empty string
                ColumnInfo(name="col3", type_text="FLOAT", comment="   "),  # Whitespace only
                ColumnInfo(name="col4", type_text="BOOLEAN", comment=None),  # None
                ColumnInfo(name="col5", type_text="DATE", comment="\t\n  "),  # Tabs and newlines
            ],
        )

        # Only col1 should count as documented
        assert validator.calculate_column_documentation_percentage(table) == 20.0  # 1 of 5
        assert validator.meets_column_documentation_threshold(table, 80.0) is False

        undocumented = validator.get_undocumented_columns(table)
        assert set(undocumented) == {"col2", "col3", "col4", "col5"}

    def test_default_threshold_from_config(self, validator):
        """Test that default threshold is loaded from configuration."""
        # Create a table with 79% documentation
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="col1", type_text="STRING", comment="Column 1"),
                ColumnInfo(name="col2", type_text="STRING", comment="Column 2"),
                ColumnInfo(name="col3", type_text="STRING", comment="Column 3"),
                ColumnInfo(name="col4", type_text="STRING", comment="Column 4"),
                ColumnInfo(name="col5", type_text="STRING", comment=None),  # Undocumented
            ],
        )

        # 4 of 5 = 80% - should pass default threshold
        assert validator.calculate_column_documentation_percentage(table) == 80.0

        # Test with default threshold (should use config value of 80%)
        assert validator.meets_column_documentation_threshold(table) is True

    def test_custom_threshold_overrides_config(self, validator):
        """Test that custom threshold parameter overrides config value."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="col1", type_text="STRING", comment="Column 1"),
                ColumnInfo(name="col2", type_text="STRING", comment=None),
            ],
        )

        # 50% documentation
        assert validator.calculate_column_documentation_percentage(table) == 50.0

        # Should fail high threshold
        assert validator.meets_column_documentation_threshold(table, 80.0) is False
        # Should pass low threshold
        assert validator.meets_column_documentation_threshold(table, 40.0) is True

    def test_get_undocumented_columns(self, validator):
        """Test getting list of undocumented columns."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[
                ColumnInfo(name="documented_col", type_text="INT", comment="Has documentation"),
                ColumnInfo(name="undocumented_col1", type_text="STRING", comment=None),
                ColumnInfo(name="undocumented_col2", type_text="FLOAT", comment=""),
                ColumnInfo(name="undocumented_col3", type_text="BOOLEAN", comment="   "),
            ],
        )

        undocumented = validator.get_undocumented_columns(table)
        assert set(undocumented) == {"undocumented_col1", "undocumented_col2", "undocumented_col3"}

    def test_no_columns_returns_empty_undocumented_list(self, validator):
        """Test that tables with no columns return empty undocumented list."""
        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            columns=[],
        )

        undocumented = validator.get_undocumented_columns(table)
        assert undocumented == []
