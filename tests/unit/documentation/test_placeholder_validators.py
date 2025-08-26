"""Unit tests for placeholder text detection in table comments.

Tests the 'Table comments must not be placeholder text' scenario.
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


class TestPlaceholderTextValidation:
    """Test placeholder text detection in table comments."""

    def test_standard_placeholder_patterns(self, validator, base_table):
        """Test detection of standard placeholder patterns."""
        placeholder_comments = [
            "TODO",
            "FIXME",
            "TBD",
            "XXX",
            "HACK",
            "PLACEHOLDER",
            "TEMP",
            "NOTE",
            "BUG",
            "NA",
            "N/A",
        ]

        for comment in placeholder_comments:
            table = base_table._replace(comment=comment)
            assert validator.has_placeholder_comment(table) is True, f"Should detect '{comment}' as placeholder"

    def test_case_insensitive_detection(self, validator, base_table):
        """Test that placeholder detection is case-insensitive."""
        test_cases = [
            ("todo", True),
            ("TODO", True),
            ("Todo", True),
            ("tOdO", True),
            ("fixme", True),
            ("FIXME", True),
            ("FixMe", True),
            ("tbd", True),
            ("TBD", True),
            ("Tbd", True),
        ]

        for comment, expected in test_cases:
            table = base_table._replace(comment=comment)
            result = validator.has_placeholder_comment(table)
            assert result is expected, f"Comment '{comment}' should be detected as placeholder: {expected}"

    def test_obvious_placeholder_detection(self, validator, base_table):
        """Test that obvious placeholder patterns are detected."""
        obvious_placeholder_comments = [
            "TODO: Add proper documentation",  # TODO at start
            "FIXME: Update this comment",  # FIXME at start
            "NOTE: Review this code",  # NOTE at start
            "XXX: needs review",  # XXX at start
            "HACK: temporary solution",  # HACK at start
            "BUG: fix this issue",  # BUG at start
            "TBD",  # TBD standalone
            "TEMP",  # TEMP standalone
        ]

        for comment in obvious_placeholder_comments:
            table = base_table._replace(comment=comment)
            assert validator.has_placeholder_comment(table) is True, f"Should detect placeholder in '{comment}'"

    def test_valid_comments_not_flagged(self, validator, base_table):
        """Test that valid documentation comments are not flagged as placeholders."""
        test_cases = [
            ("User authentication table", False),
            ("Contains customer data and preferences", False),
            ("Product catalog with pricing information", False),
            ("Stores user session information", False),
            ("Financial transaction records", False),  # No longer flagged - "n/a" requires word boundary
            ("Employee directory and contact details", False),
            ("Inventory tracking for warehouse operations", False),
            ("Order processing and fulfillment data", False),
        ]

        for comment, expected in test_cases:
            table = base_table._replace(comment=comment)
            result = validator.has_placeholder_comment(table)
            assert result is expected, f"Comment '{comment}' expected: {expected}, got: {result}"

    def test_edge_cases(self, validator, base_table):
        """Test edge cases for placeholder detection."""
        edge_cases = [
            # Empty and None comments should not be flagged as placeholders
            (None, False),
            ("", False),
            ("   ", False),  # Whitespace only
            # Words that contain placeholder patterns but are valid
            ("Notification settings", False),  # Contains "not" but not "note"
            ("Fixed rate calculations", False),  # Contains "fix" but not "fixme"
            ("Temporary employee records", False),  # "temp" requires word boundary - not flagged
            # Whitespace around placeholders
            ("  TODO  ", True),
            ("\tFIXME\n", True),
            (" TBD ", True),
        ]

        for comment, expected in edge_cases:
            table = base_table._replace(comment=comment)
            result = validator.has_placeholder_comment(table)
            assert result is expected, f"Comment '{comment}' placeholder detection expected: {expected}, got: {result}"

    def test_contextual_words_not_flagged(self, validator, base_table):
        """Test that placeholder words in legitimate context are not flagged."""
        contextual_comments = [
            "User table stores customer data",  # No placeholder words
            "Product data with pricing logic",  # No placeholder words
            "Customer info and privacy fields",  # No placeholder words
            "Order processing business rules",  # No placeholder words
            "Please note that this dataset...",  # "note" in context - should not flag
            "Bug tracking system for issues",  # "bug" in context - should not flag
            "Temperature readings from sensors",  # "temp" in context - should not flag
        ]

        # These should NOT be flagged as they're legitimate documentation
        for comment in contextual_comments:
            table = base_table._replace(comment=comment)
            assert validator.has_placeholder_comment(table) is False, f"Should NOT flag legitimate content '{comment}'"

    def test_boundary_patterns(self, validator, base_table):
        """Test boundary cases for pattern matching."""
        boundary_cases = [
            # Exact matches should be flagged
            ("TODO", True),
            ("FIXME", True),
            ("TBD", True),
            ("XXX", True),
            # Start-of-comment patterns should be flagged
            ("TODO: description", True),
            ("FIXME: fix this", True),
            ("NOTE: important", True),
            # Similar words should NOT be flagged
            ("TOD", False),  # Not quite "TODO"
            ("TODOS", False),  # Plural, not exact match
            ("NODE", False),  # Similar to "NOTE" but different
            ("FIXED", False),  # Past tense, not "FIXME"
            ("NOTED", False),  # Past tense, not "NOTE"
            # Words in context should NOT be flagged
            ("This TODO item", False),  # TODO not at start
            ("Bug tracking", False),  # "bug" in context
            ("Temperature data", False),  # "temp" in context
        ]

        for comment, expected in boundary_cases:
            table = base_table._replace(comment=comment)
            result = validator.has_placeholder_comment(table)
            assert result is expected, f"Comment '{comment}' expected: {expected}, got: {result}"

    def test_placeholder_vs_other_validations_independence(self, validator, base_table):
        """Test that placeholder validation is independent of other validations."""
        # A placeholder comment might still pass other validations
        long_placeholder = base_table._replace(comment="TODO: Add detailed documentation here")
        assert validator.has_comment(long_placeholder) is True  # Has content
        assert validator.has_minimum_length(long_placeholder) is True  # Long enough
        assert validator.has_placeholder_comment(long_placeholder) is True  # But is placeholder

        # A short valid comment
        short_valid = base_table._replace(comment="User data")
        assert validator.has_comment(short_valid) is True  # Has content
        assert validator.has_minimum_length(short_valid) is False  # Too short
        assert validator.has_placeholder_comment(short_valid) is False  # Not placeholder

        # None comment fails all
        none_comment = base_table._replace(comment=None)
        assert validator.has_comment(none_comment) is False
        assert validator.has_minimum_length(none_comment) is False
        assert validator.has_placeholder_comment(none_comment) is False

    def test_improved_precision_no_false_positives(self, validator, base_table):
        """Test that the improved logic avoids false positives from legitimate documentation."""
        # These comments should NOT be flagged despite containing placeholder-like words
        legitimate_documentation = [
            ("Product catalog with pricing information", False),  # Contains "n/a" in "information"
            ("Financial transaction records", False),  # Contains "n/a" in "transaction"
            ("Temporary employee records", False),  # Contains "temp" in "temporary"
            ("Customer data and preferences", False),  # Contains "n/a" in "and"
            ("Notification system settings", False),  # Contains "not" but not "note"
            ("Fixed-rate mortgage calculations", False),  # Contains "fix" but not "fixme"
            ("Bug tracking system details", False),  # Contains "bug" in context - should NOT be flagged
            ("System temperatures and readings", False),  # Contains "temp" in "temperatures"
            (
                "Please note that this dataset represents...",
                False,
            ),  # Contains "note" in context - should NOT be flagged
            ("The hackathon event planning", False),  # Contains "hack" in context - should NOT be flagged
        ]

        for comment, expected in legitimate_documentation:
            table = base_table._replace(comment=comment)
            result = validator.has_placeholder_comment(table)
            assert result is expected, f"Comment '{comment}' precision test failed: expected {expected}, got {result}"

    def test_start_of_comment_patterns(self, validator, base_table):
        """Test that placeholder patterns at start of comments are detected."""
        start_pattern_cases = [
            # Should be flagged (obvious placeholder usage)
            ("TODO: Add documentation", True),
            ("FIXME: Update logic", True),
            ("NOTE: Review implementation", True),
            ("XXX: Needs attention", True),
            ("HACK: Temporary workaround", True),
            ("BUG: Fix this issue", True),
            # Should NOT be flagged (not at start)
            ("Status: TBD", False),  # TBD not at start
            ("This TODO item", False),  # TODO not at start
            ("Review FIXME later", False),  # FIXME not at start
        ]

        for comment, expected in start_pattern_cases:
            table = base_table._replace(comment=comment)
            result = validator.has_placeholder_comment(table)
            assert result is expected, f"Start pattern test for '{comment}' failed: expected {expected}, got {result}"
