"""Schema detection utilities for Databricks tables.

Provides reliable, performant schema detection with proper error handling and fallback strategies.
Research-based implementation prioritizing native SDK methods over SQL approaches.

See: research/clustering/small_tables_auto_exemption/DATABRICKS_SDK_SCHEMA_DETECTION_RESEARCH.md
"""

from __future__ import annotations

import logging
from typing import Optional

from databricks.sdk import WorkspaceClient

logger = logging.getLogger(__name__)


class SchemaDetectionError(Exception):
    """Raised when schema cannot be determined using any available method."""
    pass


class SchemaDetector:
    """Reliable schema detection for Databricks tables.
    
    Uses research-based method priority:
    1. Native SDK (client.tables.get) - Primary method
    2. Information Schema - SQL fallback for edge cases  
    3. DESCRIBE TABLE - Last resort with intelligent parsing
    """
    
    def __init__(self, client: WorkspaceClient, warehouse_id: Optional[str] = None):
        """Initialize schema detector.
        
        Args:
            client: Databricks workspace client
            warehouse_id: Optional warehouse ID for SQL fallback methods
        """
        self.client = client
        self.warehouse_id = warehouse_id
    
    def get_table_schema(self, table_name: str) -> list[tuple[str, str]]:
        """Get table schema using most reliable method available.
        
        Args:
            table_name: Full table name (catalog.schema.table)
            
        Returns:
            List of (column_name, column_type) tuples
            
        Raises:
            SchemaDetectionError: If schema cannot be determined from any method
        """
        logger.debug(f"Detecting schema for {table_name}")
        
        # Method 1: Native SDK (Primary - fastest, most reliable)
        try:
            return self._get_schema_via_native_sdk(table_name)
        except Exception as sdk_error:
            logger.debug(f"Native SDK failed for {table_name}: {sdk_error}")
        
        # Method 2: Information Schema (SQL fallback)
        if self.warehouse_id:
            try:
                return self._get_schema_via_information_schema(table_name)
            except Exception as info_error:
                logger.debug(f"Information Schema failed for {table_name}: {info_error}")
        
        # Method 3: DESCRIBE TABLE (Last resort)
        if self.warehouse_id:
            try:
                return self._get_schema_via_describe_table(table_name)
            except Exception as desc_error:
                logger.debug(f"DESCRIBE TABLE failed for {table_name}: {desc_error}")
        
        raise SchemaDetectionError(f"Could not determine schema for {table_name} using any available method")
    
    def _get_schema_via_native_sdk(self, table_name: str) -> list[tuple[str, str]]:
        """Get schema using native Databricks SDK.
        
        Advantages:
        - No SQL execution required
        - No warehouse_id dependency
        - Type-safe responses
        - No clustering metadata pollution
        """
        table_info = self.client.tables.get(table_name)
        if not table_info.columns:
            raise ValueError(f"Table {table_name} has no columns metadata")
            
        # Convert ColumnTypeName enums to strings
        columns = [(col.name, col.type_name.value) for col in table_info.columns]
        logger.debug(f"Native SDK success for {table_name}: {len(columns)} columns")
        return columns
    
    def _get_schema_via_information_schema(self, table_name: str) -> list[tuple[str, str]]:
        """Get schema using Information Schema (standard SQL approach)."""
        table_parts = table_name.split('.')
        if len(table_parts) != 3:
            raise ValueError(f"Table name must be in format 'catalog.schema.table': {table_name}")
            
        catalog, schema, table = table_parts
        result = self.client.statement_execution.execute_statement(
            statement=f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_catalog = '{catalog}' 
                  AND table_schema = '{schema}' 
                  AND table_name = '{table}' 
                ORDER BY ordinal_position
            """,
            warehouse_id=self.warehouse_id,
            wait_timeout="30s"
        )
        
        if not (result.result and result.result.data_array):
            raise ValueError(f"Information Schema returned no data for {table_name}")
            
        columns = [(row[0], row[1]) for row in result.result.data_array if row[0]]
        if not columns:
            raise ValueError(f"Information Schema returned empty column list for {table_name}")
            
        logger.debug(f"Information Schema success for {table_name}: {len(columns)} columns")
        return columns
    
    def _get_schema_via_describe_table(self, table_name: str) -> list[tuple[str, str]]:
        """Get schema using DESCRIBE TABLE with intelligent parsing.
        
        Note: DESCRIBE TABLE includes clustering metadata that causes duplicates.
        This method intelligently parses only the column definition section.
        """
        result = self.client.statement_execution.execute_statement(
            statement=f"DESCRIBE {table_name}", 
            warehouse_id=self.warehouse_id, 
            wait_timeout="30s"
        )
        
        if not (result.result and result.result.data_array):
            raise ValueError(f"DESCRIBE TABLE returned no data for {table_name}")
        
        columns = []
        for row in result.result.data_array:
            col_name = row[0] if len(row) > 0 else None
            col_type = row[1] if len(row) > 1 else None
            
            # Stop at metadata sections (partition info, clustering info)
            if not col_name or col_name.startswith('#') or col_name.lower().startswith('clustering'):
                break
            
            columns.append((col_name, col_type))
        
        if not columns:
            raise ValueError(f"DESCRIBE TABLE found no valid columns for {table_name}")
            
        logger.debug(f"DESCRIBE TABLE success for {table_name}: {len(columns)} columns")
        return columns