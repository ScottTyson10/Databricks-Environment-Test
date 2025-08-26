"""Unit tests for table comment validation.

Tests table comment existence and length validation scenarios.
"""

import pytest

from tests.utils.discovery import TableInfo
from tests.validators.documentation import DocumentationValidator


@pytest.fixture
def validator():
    """Fixture providing a DocumentationValidator instance."""
    return DocumentationValidator()


@pytest.fixture
def base_table():
    """Fixture providing a base TableInfo for test variations."""
    return TableInfo(catalog="test_catalog", schema="test_schema", table="test_table")


class TestTableCommentValidation:
    """Test suite for the 'Tables must have a comment' scenario.

    Validates DocumentationValidator.has_comment() method using pytest patterns.
    """

    @pytest.mark.parametrize(
        "comment,expected",
        [
            ("Valid table comment", True),
            ("Short comment", True),
            ("Multi-line comment\nwith details", True),
            (None, False),
            ("", False),
            ("   ", False),
            ("\n\t  \n", False),
            (" ", False),
        ],
    )
    def test_has_comment_with_various_inputs(self, validator, base_table, comment, expected):
        """Test has_comment with various comment values using parametrize."""
        table = base_table._replace(comment=comment)
        result = validator.has_comment(table)
        assert result is expected

    def test_has_comment_with_valid_comment(self, validator, base_table):
        """Test has_comment with a clearly valid comment - should PASS."""
        table = base_table._replace(comment="This table stores customer purchase history and demographics")
        assert validator.has_comment(table) is True

    def test_has_comment_with_none_comment(self, validator, base_table):
        """Test has_comment with None comment - should FAIL.

        Based on SDK research: Databricks returns None for missing comments.
        """
        table = base_table._replace(comment=None)
        assert validator.has_comment(table) is False

    def test_has_comment_with_empty_string(self, validator, base_table):
        """Test has_comment with empty string comment - should FAIL."""
        table = base_table._replace(comment="")
        assert validator.has_comment(table) is False

    @pytest.mark.parametrize(
        "whitespace_comment",
        [
            "   ",
            "\n",
            "\t",
            "  \n\t  ",
            "\r\n  \t",
        ],
    )
    def test_has_comment_with_whitespace_only(self, validator, base_table, whitespace_comment):
        """Test has_comment with various whitespace-only comments - should FAIL."""
        table = base_table._replace(comment=whitespace_comment)
        assert validator.has_comment(table) is False

    def test_tableinfo_has_comment_method(self, base_table):
        """Test the TableInfo's own has_comment method for consistency."""
        table_with_comment = base_table._replace(comment="Valid comment")
        table_without_comment = base_table._replace(comment=None)
        table_empty_comment = base_table._replace(comment="")

        assert table_with_comment.has_comment() is True
        assert table_without_comment.has_comment() is False
        assert table_empty_comment.has_comment() is False

    def test_validator_initialization(self):
        """Test that validator initializes cleanly without config."""
        validator = DocumentationValidator()
        assert validator is not None

    def test_validator_with_multiple_tables(self, validator):
        """Test validator handles multiple table validations correctly."""
        tables = [
            TableInfo("cat1", "schema1", "table1", "Good comment"),
            TableInfo("cat1", "schema1", "table2", None),
            TableInfo("cat1", "schema1", "table3", ""),
            TableInfo("cat1", "schema1", "table4", "Another good comment"),
        ]

        results = [validator.has_comment(table) for table in tables]
        expected = [True, False, False, True]

        assert results == expected


class TestCommentLengthValidation:
    """Test suite for the 'Table comments must be at least 10 characters' scenario.

    Validates DocumentationValidator.has_minimum_length() method with various edge cases.
    """

    @pytest.mark.parametrize(
        "comment,expected",
        [
            # Valid comments (10+ characters)
            ("This is a valid comment", True),
            ("Ten chars!", True),
            ("Longer comment with detailed description", True),
            ("🚀 Unicode comment", True),
            ("   Leading and trailing spaces   ", True),
            # Invalid comments (< 10 characters)
            ("Short", False),
            ("Nine char", False),
            ("A", False),
            ("", False),
            ("   ", False),
            (None, False),
            ("🚀", False),
            ("🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀", True),  # 10 Unicode characters
            ("\n\t Test \n", False),
            ("Tab\tSeparated\tComment", True),
        ],
    )
    def test_has_minimum_length_with_various_inputs(self, validator, base_table, comment, expected):
        """Test has_minimum_length with various inputs using parametrize."""
        table = base_table._replace(comment=comment)
        result = validator.has_minimum_length(table)
        assert result is expected

    def test_minimum_length_boundary_conditions(self, validator, base_table):
        """Test boundary conditions around the 10-character threshold."""
        # Exactly 9 characters - should fail
        table_9 = base_table._replace(comment="123456789")
        assert validator.has_minimum_length(table_9) is False
        assert len("123456789") == 9

        # Exactly 10 characters - should pass
        table_10 = base_table._replace(comment="1234567890")
        assert validator.has_minimum_length(table_10) is True
        assert len("1234567890") == 10

        # Exactly 11 characters - should pass
        table_11 = base_table._replace(comment="12345678901")
        assert validator.has_minimum_length(table_11) is True
        assert len("12345678901") == 11

    def test_minimum_length_with_unicode(self, validator, base_table):
        """Test minimum length calculation with Unicode characters."""
        # Unicode characters should count as 1 character each
        unicode_comment = "café naïve résumé"  # 17 characters including spaces
        table = base_table._replace(comment=unicode_comment)
        assert validator.has_minimum_length(table) is True
        assert len(unicode_comment) == 17

        # Short Unicode - should fail
        short_unicode = "café"  # 4 characters
        table_short = base_table._replace(comment=short_unicode)
        assert validator.has_minimum_length(table_short) is False
        assert len(short_unicode) == 4

    def test_minimum_length_none_handling(self, validator, base_table):
        """Test that None comments are handled correctly."""
        table = base_table._replace(comment=None)
        assert validator.has_minimum_length(table) is False

    def test_minimum_length_with_whitespace(self, validator, base_table):
        """Test that whitespace is counted toward length."""
        # Whitespace should count - this is 10 spaces
        whitespace_comment = "          "
        table = base_table._replace(comment=whitespace_comment)
        assert validator.has_minimum_length(table) is True
        assert len(whitespace_comment) == 10

        # Mixed whitespace and text - should pass
        mixed_comment = "  Test  \n  "  # 11 characters total
        table_mixed = base_table._replace(comment=mixed_comment)
        assert validator.has_minimum_length(table_mixed) is True
        assert len(mixed_comment) == 11

    def test_minimum_length_configuration(self, validator):
        """Test that validator loads the minimum length configuration."""
        # Should be 10 from config
        assert validator.minimum_comment_length == 10

    def test_minimum_length_with_multiple_tables(self, validator):
        """Test minimum length validation across multiple tables."""
        tables = [
            TableInfo("cat", "schema", "table1", "Valid comment that is long enough"),
            TableInfo("cat", "schema", "table2", "Short"),
            TableInfo("cat", "schema", "table3", None),
            TableInfo("cat", "schema", "table4", "Ten chars!"),
            TableInfo("cat", "schema", "table5", "Nine chr"),
        ]

        results = [validator.has_minimum_length(table) for table in tables]
        expected = [True, False, False, True, False]

        assert results == expected

    def test_length_vs_comment_validation_independence(self, validator, base_table):
        """Test that length validation and comment existence are independent checks."""
        # Long comment with valid content - both should pass
        good_table = base_table._replace(comment="This is a good long comment")
        assert validator.has_comment(good_table) is True
        assert validator.has_minimum_length(good_table) is True

        # Short comment with valid content - comment exists but length fails
        short_table = base_table._replace(comment="Short")
        assert validator.has_comment(short_table) is True
        assert validator.has_minimum_length(short_table) is False

        # None comment - both fail
        none_table = base_table._replace(comment=None)
        assert validator.has_comment(none_table) is False
        assert validator.has_minimum_length(none_table) is False
