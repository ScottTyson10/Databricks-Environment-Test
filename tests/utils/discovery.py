"""Discovery engine data structures for Databricks tables."""

from __future__ import annotations

from typing import Any, NamedTuple


class ColumnInfo(NamedTuple):
    """Immutable column information based on Databricks SDK structure.

    Based on databricks.sdk.service.catalog.ColumnInfo research:
    - comment is either str or None (never empty string)
    - name is the column name
    - type_text is the data type as a string
    """

    name: str
    type_text: str
    comment: str | None = None


class TableInfo(NamedTuple):
    """Immutable table information based on Databricks SDK structure.

    Based on databricks.sdk.service.catalog.TableInfo research:
    - comment is either str or None (never empty string)
    - columns is a tuple of column dictionaries
    - full_name is the qualified table name (catalog.schema.table)
    - properties contains table properties including clustering info
    """

    catalog: str
    schema: str
    table: str
    comment: str | None = None
    columns: tuple[ColumnInfo, ...] = ()
    properties: dict[str, Any] | None = None

    @property
    def full_name(self) -> str:
        """Fully qualified table name."""
        return f"{self.catalog}.{self.schema}.{self.table}"

    @property
    def is_test_table(self) -> bool:
        """Check if this is a test table."""
        return self.schema == "pytest_test_data"

    def has_comment(self) -> bool:
        """Check if table has a non-empty comment.

        Based on SDK research: comments are either str or None.
        We treat None and empty/whitespace strings as "no comment".
        """
        return bool(self.comment and self.comment.strip())
