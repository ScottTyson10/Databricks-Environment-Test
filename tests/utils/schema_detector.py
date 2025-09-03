"""Schema detection utilities for Databricks tables.

Provides reliable, performant schema detection with proper error handling and fallback strategies.
Research-based implementation prioritizing native SDK methods over SQL approaches.

See: research/clustering/small_tables_auto_exemption/DATABRICKS_SDK_SCHEMA_DETECTION_RESEARCH.md
"""

from __future__ import annotations

import logging

from databricks.sdk import WorkspaceClient

logger = logging.getLogger(__name__)


class SchemaDetectionError(Exception):
    """Raised when schema cannot be determined using any available method."""

    pass


class SchemaDetector:
    """Reliable schema detection for Databricks tables using native SDK.

    Research-proven implementation using client.tables.get() which provides:
    - Superior performance vs SQL methods
    - No clustering metadata pollution
    - No warehouse_id dependency
    - Type-safe enum responses
    """

    def __init__(self, client: WorkspaceClient):
        """Initialize schema detector.

        Args:
            client: Databricks workspace client
        """
        self.client = client

    def get_table_schema(self, table_name: str) -> list[tuple[str, str]]:
        """Get table schema using native Databricks SDK.

        Args:
            table_name: Full table name (catalog.schema.table)

        Returns:
            List of (column_name, column_type) tuples

        Raises:
            SchemaDetectionError: If schema cannot be determined
        """
        logger.debug(f"Getting schema for {table_name} using native SDK")

        try:
            table_info = self.client.tables.get(table_name)
            if not table_info.columns:
                raise SchemaDetectionError(f"Table {table_name} has no columns metadata")

            # Convert ColumnTypeName enums to strings, handling None values
            columns = []
            for col in table_info.columns:
                col_name = col.name or "unknown"
                col_type = col.type_name.value if col.type_name else "unknown"
                columns.append((col_name, col_type))
            logger.debug(f"Retrieved schema for {table_name}: {len(columns)} columns")
            return columns

        except Exception as e:
            raise SchemaDetectionError(f"Could not determine schema for {table_name}: {e}") from e
