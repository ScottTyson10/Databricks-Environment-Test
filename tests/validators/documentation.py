"""Documentation validators for table and column comments."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tests.utils.config_loader import get_config_loader

if TYPE_CHECKING:
    from tests.utils.discovery import TableInfo


class DocumentationValidator:
    """Validator for documentation compliance of Databricks tables.

    Supports multiple documentation scenarios.
    """

    def __init__(self) -> None:
        """Initialize validator with configuration from YAML file."""
        self._config_loader = get_config_loader()

        # Load configuration values from YAML
        self.minimum_comment_length = int(self._config_loader.get_validation_threshold("minimum_comment_length", 10))
        self.required_column_coverage_percent = float(
            self._config_loader.get_validation_threshold("required_column_coverage_percent", 80)
        )
        self.critical_column_patterns = self._config_loader.get_critical_column_patterns()
        self.placeholder_patterns = self._config_loader.get_placeholder_patterns()
        self.placeholder_config = self._config_loader.get_placeholder_detection_config()
        self.comment_validation_config = self._config_loader.get_comment_validation_config()

    def has_comment(self, table: TableInfo) -> bool:
        """Check if table has a meaningful comment.

        Based on SDK research:
        - Comments are either str or None (never empty string from SDK)
        - We treat None and whitespace-only strings as "no comment"

        Args:
            table: TableInfo object with table metadata

        Returns:
            True if table has a non-empty comment, False otherwise
        """
        if table.comment is None:
            return False

        # Check for whitespace-only strings
        return bool(table.comment.strip())

    def has_minimum_length(self, table: TableInfo) -> bool:
        """Check if table comment meets minimum length requirement.

        Args:
            table: TableInfo object with table metadata

        Returns:
            True if table comment is at least minimum_comment_length characters, False otherwise
        """
        if table.comment is None:
            return False

        # Count characters in the comment (Unicode-aware)
        comment_length = len(table.comment)
        return comment_length >= self.minimum_comment_length

    def has_placeholder_comment(self, table: TableInfo) -> bool:
        """Check if table comment appears to be placeholder text.

        Focuses on obvious placeholder patterns - standalone placeholder words
        or common placeholder phrases like "TODO:", not legitimate documentation
        that happens to contain placeholder words in context.

        Args:
            table: TableInfo object with table metadata

        Returns:
            True if table comment appears to be placeholder text, False otherwise
        """
        if table.comment is None or table.comment.strip() == "":
            # Empty or None comments are not considered placeholders
            # (they are handled by has_comment() validator)
            return False

        comment = table.comment.strip()
        comment_lower = comment.lower()

        # Use placeholder patterns from configuration
        import re

        exact_patterns = self.placeholder_patterns
        case_sensitive = self.placeholder_config.get("case_sensitive", False)

        # Determine comment to check based on case sensitivity
        check_comment = comment if case_sensitive else comment_lower

        for pattern in exact_patterns:
            check_pattern = pattern if case_sensitive else pattern.lower()
            # Check for exact match
            if check_comment == check_pattern:
                return True

        # Check for common placeholder phrases (obvious placeholder usage)
        placeholder_phrases = [rf"^\s*{pattern}\s*:" for pattern in exact_patterns] + [  # "PATTERN:" at start
            rf"^\s*{pattern}\s*$" for pattern in exact_patterns  # "PATTERN" as complete comment
        ]

        return any(re.search(phrase_pattern, check_comment) for phrase_pattern in placeholder_phrases)

    def _is_column_critical(self, column_name_lower: str, patterns_with_boundaries: list[dict]) -> bool:
        """Check if a column name matches any critical pattern using appropriate matching strategy.

        Args:
            column_name_lower: Column name in lowercase
            patterns_with_boundaries: List of pattern dicts with 'pattern' and 'word_boundary' fields

        Returns:
            True if column matches any critical pattern, False otherwise
        """
        for pattern_info in patterns_with_boundaries:
            pattern = pattern_info["pattern"].lower()
            use_word_boundary = pattern_info.get("word_boundary", False)

            if use_word_boundary:
                # Use word boundary matching - pattern must be a complete word or word part
                # Handle both underscore_case and camelCase patterns
                # Match: user_id, customer_id, id, UserId, customerId (but not humidity_relative_id)
                escaped_pattern = re.escape(pattern)
                word_patterns = [
                    rf"^{escaped_pattern}$",  # Exact match: "id"
                    rf"^{escaped_pattern}_",  # Start with underscore: "id_something"
                    rf"_{escaped_pattern}_",  # Middle with underscore: "user_id_field"
                    rf"_{escaped_pattern}$",  # End with underscore: "user_id"
                    rf"{escaped_pattern}$",  # End of camelCase: "userId", "customerId"
                    rf"^{escaped_pattern}(?=[A-Z])",  # Start of camelCase: "idField" -> "id" + "Field"
                ]
                if any(re.search(wp, column_name_lower) for wp in word_patterns):
                    return True
            else:
                # Use substring matching - pattern can appear anywhere
                # Match patterns like: email_address, user_email, email
                if pattern in column_name_lower:
                    return True

        return False

    def get_undocumented_critical_columns(self, table: TableInfo) -> list[str]:
        """Get list of critical columns that lack documentation.

        Critical columns are identified by patterns in their names (case-insensitive):
        - Identity: id, key, uuid
        - PII: email, name, phone, address, ssn, dob, birth
        - Financial: account, credit, card, bank, salary, payment
        - Security: password, token, secret
        - Audit: created, modified, updated, deleted, user

        Args:
            table: TableInfo object with table metadata including columns

        Returns:
            List of column names that are critical but lack documentation
        """
        if not table.columns:
            return []

        # Get critical patterns with word boundary settings from configuration
        critical_patterns_with_boundaries = get_config_loader().get_critical_column_patterns_with_boundaries()

        undocumented_critical = []

        for col in table.columns:
            col_name_lower = col.name.lower()

            # Check if column is critical using appropriate matching strategy
            is_critical = self._is_column_critical(col_name_lower, critical_patterns_with_boundaries)

            if is_critical:
                # Check if column has documentation
                has_documentation = bool(col.comment and col.comment.strip())

                if not has_documentation:
                    undocumented_critical.append(col.name)

        return undocumented_critical

    def has_all_critical_columns_documented(self, table: TableInfo) -> bool:
        """Check if all critical columns in the table have documentation.

        Args:
            table: TableInfo object with table metadata including columns

        Returns:
            True if all critical columns are documented, False otherwise
        """
        return len(self.get_undocumented_critical_columns(table)) == 0

    def calculate_column_documentation_percentage(self, table: TableInfo) -> float:
        """Calculate percentage of columns with documentation.

        A column is considered documented if:
        - comment is not None
        - comment.strip() is not empty

        Args:
            table: TableInfo object with table metadata including columns

        Returns:
            Percentage (0.0-100.0) of documented columns.
            Returns 100.0 for tables with 0 columns (vacuously true).
        """
        if not table.columns:
            return 100.0  # No columns = vacuously true = 100% compliant

        documented_count = sum(1 for col in table.columns if col.comment and col.comment.strip())

        return (documented_count / len(table.columns)) * 100.0

    def meets_column_documentation_threshold(self, table: TableInfo, threshold: float | None = None) -> bool:
        """Check if table meets column documentation coverage threshold.

        Args:
            table: TableInfo object with table metadata including columns
            threshold: Percentage threshold (0-100). If None, uses config value.

        Returns:
            True if table meets or exceeds the documentation threshold, False otherwise
        """
        if threshold is None:
            threshold = float(self._config_loader.get_validation_threshold("required_column_coverage_percent", 80))

        actual_percentage = self.calculate_column_documentation_percentage(table)
        return actual_percentage >= threshold

    def get_undocumented_columns(self, table: TableInfo) -> list[str]:
        """Get list of columns that lack documentation.

        Args:
            table: TableInfo object with table metadata including columns

        Returns:
            List of column names that lack documentation
        """
        if not table.columns:
            return []

        undocumented = []
        for col in table.columns:
            has_documentation = bool(col.comment and col.comment.strip())
            if not has_documentation:
                undocumented.append(col.name)

        return undocumented
