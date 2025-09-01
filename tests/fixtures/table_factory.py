"""Test table factory for documentation scenarios.

Implements Layer 2 integration test support with real Databricks table creation.
Supports multiple documentation compliance scenarios.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from databricks.sdk import WorkspaceClient

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TestTableSpec:
    """Immutable test table specification for various scenarios."""

    name: str
    comment: str | None
    expected_pass: bool
    scenario_type: str = "table_comment"


@dataclass(frozen=True)
class TestTableSpecWithColumns:
    """Immutable test table specification with custom column definitions."""

    name: str
    comment: str | None
    expected_pass: bool
    columns: list[tuple[str, str, str | None]]  # (name, type, comment)
    scenario_type: str = "critical_columns"


@dataclass(frozen=True)
class TestTableSpecWithClustering:
    """Immutable test table specification with clustering column definitions."""

    name: str
    comment: str | None
    expected_pass: bool
    columns: list[tuple[str, str, str | None]]  # (name, type, comment)
    clustering_columns: list[str]  # Column names to use for clustering
    scenario_type: str = "explicit_clustering"


@dataclass(frozen=True)
class TestTableSpecWithProperties:
    """Immutable test table specification with custom table properties."""

    name: str
    comment: str | None
    expected_pass: bool
    columns: list[tuple[str, str, str | None]]  # (name, type, comment)
    properties: dict[str, str]  # Table properties to set
    scenario_type: str = "table_properties"


class TestTableFactory:
    """Context manager for test table lifecycle.

    Creates real Databricks tables for integration testing.
    Supports multiple documentation compliance scenarios.
    """

    def __init__(self, client: WorkspaceClient, catalog: str = "workspace", schema: str = "pytest_test_data") -> None:
        self.client = client
        self.catalog = catalog
        self.schema = schema
        self.created_tables: list[str] = []

    def __enter__(self) -> TestTableFactory:
        """Enter context manager."""
        logger.info(f"Starting test table factory for {self.catalog}.{self.schema}")
        self._ensure_schema_exists()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager with cleanup."""
        logger.info(f"Cleaning up {len(self.created_tables)} test tables")
        for table_name in self.created_tables:
            try:
                full_name = f"{self.catalog}.{self.schema}.{table_name}"
                self.client.tables.delete(full_name)
                logger.info(f"Deleted test table: {full_name}")
            except Exception as e:
                logger.warning(f"Failed to delete test table {full_name}: {e}")

    def _ensure_schema_exists(self) -> None:
        """Ensure test schema exists."""
        try:
            self.client.schemas.get(f"{self.catalog}.{self.schema}")
            logger.debug(f"Schema {self.catalog}.{self.schema} already exists")
        except Exception:
            logger.info(f"Creating test schema: {self.catalog}.{self.schema}")
            self.client.schemas.create(
                name=self.schema, catalog_name=self.catalog, comment="Test schema for pytest integration tests"
            )

    def create_table(self, spec: TestTableSpec) -> str:
        """Create a test table from specification.

        Args:
            spec: Test table specification

        Returns:
            Full table name (catalog.schema.table)
        """
        full_name = f"{self.catalog}.{self.schema}.{spec.name}"

        # Build CREATE TABLE statement
        comment_clause = f"COMMENT '{spec.comment}'" if spec.comment else ""

        sql = f"""
        CREATE TABLE {full_name} (
            id INT COMMENT 'Test ID column',
            name STRING COMMENT 'Test name column',
            created_at TIMESTAMP COMMENT 'Creation timestamp'
        )
        USING DELTA
        {comment_clause}
        """

        logger.info(f"Creating test table: {full_name}")
        logger.debug(f"SQL: {sql}")

        # Execute table creation
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        if warehouse_id is None:
            raise ValueError("DATABRICKS_WAREHOUSE_ID environment variable is required")

        self.client.statement_execution.execute_statement(statement=sql, warehouse_id=warehouse_id)

        self.created_tables.append(spec.name)
        logger.info(f"Successfully created test table: {full_name}")

        return full_name

    def create_table_with_columns(self, spec: TestTableSpecWithColumns) -> str:
        """Create a test table with custom columns from specification.

        Args:
            spec: Test table specification with custom columns

        Returns:
            Full table name (catalog.schema.table)
        """
        full_name = f"{self.catalog}.{self.schema}.{spec.name}"

        # Build column definitions
        column_definitions = []
        for col_name, col_type, col_comment in spec.columns:
            comment_part = f" COMMENT '{col_comment}'" if col_comment else ""
            column_definitions.append(f"    {col_name} {col_type}{comment_part}")

        columns_sql = ",\n".join(column_definitions)

        # Build CREATE TABLE statement
        table_comment_clause = f"COMMENT '{spec.comment}'" if spec.comment else ""

        sql = f"""
        CREATE TABLE {full_name} (
{columns_sql}
        )
        USING DELTA
        {table_comment_clause}
        """

        logger.info(f"Creating test table with custom columns: {full_name}")
        logger.debug(f"SQL: {sql}")

        # Execute table creation
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        if warehouse_id is None:
            raise ValueError("DATABRICKS_WAREHOUSE_ID environment variable is required")

        self.client.statement_execution.execute_statement(statement=sql, warehouse_id=warehouse_id)

        self.created_tables.append(spec.name)
        logger.info(f"Successfully created test table with custom columns: {full_name}")

        return full_name

    def create_table_with_clustering(self, spec: TestTableSpecWithClustering) -> str:
        """Create a test table with clustering columns from specification.

        Args:
            spec: Test table specification with clustering column definitions

        Returns:
            Full table name (catalog.schema.table)
        """
        full_name = f"{self.catalog}.{self.schema}.{spec.name}"

        # Build column definitions
        column_definitions = []
        for col_name, col_type, col_comment in spec.columns:
            comment_part = f" COMMENT '{col_comment}'" if col_comment else ""
            column_definitions.append(f"    {col_name} {col_type}{comment_part}")
        columns_sql = ",\n".join(column_definitions)

        # Build clustering clause if clustering columns are specified
        clustering_clause = ""
        if spec.clustering_columns:
            clustering_cols = ", ".join(spec.clustering_columns)
            clustering_clause = f"CLUSTER BY ({clustering_cols})"

        # Build CREATE TABLE statement
        table_comment_clause = f"COMMENT '{spec.comment}'" if spec.comment else ""

        sql = f"""
        CREATE TABLE {full_name} (
{columns_sql}
        )
        USING DELTA
        {clustering_clause}
        {table_comment_clause}
        """

        logger.info(f"Creating test table with clustering: {full_name}")
        logger.debug(f"Clustering columns: {spec.clustering_columns}")
        logger.debug(f"SQL: {sql}")

        # Execute table creation
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        if warehouse_id is None:
            raise ValueError("DATABRICKS_WAREHOUSE_ID environment variable is required")

        self.client.statement_execution.execute_statement(statement=sql, warehouse_id=warehouse_id)
        self.created_tables.append(spec.name)
        logger.info(f"Successfully created test table with clustering: {full_name}")
        return full_name

    def create_table_with_cluster_by_auto(self, spec) -> str:
        """Create a test table with automatic clustering (CLUSTER BY AUTO).

        Creates a Delta table with or without automatic clustering based on the spec.
        Used for testing cluster-by-auto detection scenarios.

        Args:
            spec: ClusterByAutoTableSpec defining the table structure and clustering

        Returns:
            str: Full table name (catalog.schema.table)
        """
        full_name = f"{self.catalog}.{self.schema}.{spec.name}"

        # Build column definitions
        columns_sql = ""
        for col_name, col_type, col_comment in spec.columns:
            comment_clause = f"COMMENT '{col_comment}'" if col_comment else ""
            columns_sql += f"            {col_name} {col_type} {comment_clause},\n"
        columns_sql = columns_sql.rstrip(",\n")

        # Build clustering clause based on spec
        clustering_clause = ""
        if spec.auto_clustering_enabled:
            clustering_clause = "CLUSTER BY AUTO"

        # Build CREATE TABLE statement
        sql = f"""
        CREATE TABLE {full_name} (
{columns_sql}
        )
        USING DELTA
        {clustering_clause}
        """

        logger.info(f"Creating test table with cluster-by-auto: {full_name}")
        logger.debug(f"Auto clustering enabled: {spec.auto_clustering_enabled}")
        logger.debug(f"SQL: {sql}")

        # Execute table creation
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        if warehouse_id is None:
            raise ValueError("DATABRICKS_WAREHOUSE_ID environment variable is required")

        self.client.statement_execution.execute_statement(statement=sql, warehouse_id=warehouse_id)
        self.created_tables.append(spec.name)
        logger.info(f"Successfully created test table with cluster-by-auto: {full_name}")
        return full_name

    def create_table_with_delta_auto_optimization(self, spec) -> str:
        """Create a test table with delta auto-optimization properties.

        Creates a Delta table with optimizeWrite and/or autoCompact properties enabled
        based on the spec. Used for testing delta auto-optimization detection scenarios.

        Args:
            spec: DeltaAutoOptimizationTableSpec defining the table structure and optimization settings

        Returns:
            str: Full table name (catalog.schema.table)
        """
        full_name = f"{self.catalog}.{self.schema}.{spec.name}"

        # Build column definitions
        columns_sql = ""
        for col_name, col_type, col_comment in spec.columns:
            comment_clause = f"COMMENT '{col_comment}'" if col_comment else ""
            columns_sql += f"            {col_name} {col_type} {comment_clause},\n"
        columns_sql = columns_sql.rstrip(",\n")

        # Build TBLPROPERTIES for delta auto-optimization
        table_properties = []
        if spec.optimize_write_enabled:
            table_properties.append("'delta.autoOptimize.optimizeWrite' = 'true'")
        if spec.auto_compact_enabled:
            table_properties.append("'delta.autoOptimize.autoCompact' = 'true'")

        tblproperties_clause = ""
        if table_properties:
            tblproperties_clause = f"TBLPROPERTIES ({', '.join(table_properties)})"

        # Build CREATE TABLE statement
        sql = f"""
        CREATE TABLE {full_name} (
{columns_sql}
        )
        USING DELTA
        {tblproperties_clause}
        """

        logger.info(f"Creating test table with delta auto-optimization: {full_name}")
        logger.debug(f"OptimizeWrite enabled: {spec.optimize_write_enabled}")
        logger.debug(f"AutoCompact enabled: {spec.auto_compact_enabled}")
        logger.debug(f"SQL: {sql}")

        # Execute table creation
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        if warehouse_id is None:
            raise ValueError("DATABRICKS_WAREHOUSE_ID environment variable is required")

        self.client.statement_execution.execute_statement(statement=sql, warehouse_id=warehouse_id)
        self.created_tables.append(spec.name)
        logger.info(f"Successfully created test table with delta auto-optimization: {full_name}")
        return full_name

    def create_table_with_properties(self, spec: TestTableSpecWithProperties) -> str:
        """Create a test table with custom properties.

        Args:
            spec: Test table specification with properties

        Returns:
            str: Fully qualified table name

        Raises:
            ValueError: If required environment variables are missing
        """
        full_name = f"{self.catalog}.{self.schema}.{spec.name}"
        logger.info(f"Creating test table with properties: {full_name}")

        # Build column definitions
        column_defs = []
        for col_name, col_type, col_comment in spec.columns:
            if col_comment:
                column_defs.append(f"    {col_name} {col_type} COMMENT '{col_comment}'")
            else:
                column_defs.append(f"    {col_name} {col_type}")

        # Build table comment
        table_comment = f"COMMENT '{spec.comment}'" if spec.comment else ""

        # Build properties clause
        properties_list = []
        if spec.properties:
            for prop_key, prop_value in spec.properties.items():
                properties_list.append(f"    '{prop_key}' = '{prop_value}'")

        properties_clause = ""
        if properties_list:
            properties_separator = ",\n"
            properties_clause = f"TBLPROPERTIES (\n{properties_separator.join(properties_list)}\n)"

        # Construct CREATE TABLE statement
        column_separator = ",\n"
        sql = f"""
        CREATE TABLE {full_name} (
{column_separator.join(column_defs)}
        )
        USING DELTA
        {table_comment}
        {properties_clause}
        """

        logger.debug(f"SQL for table with properties:\n{sql}")

        # Execute table creation
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        if warehouse_id is None:
            raise ValueError("DATABRICKS_WAREHOUSE_ID environment variable is required")

        self.client.statement_execution.execute_statement(statement=sql, warehouse_id=warehouse_id)
        self.created_tables.append(spec.name)
        logger.info(f"Successfully created test table with properties: {full_name}")
        return full_name

    def _insert_test_data_for_size_testing(self, table_name: str, target_size: str) -> None:
        """Insert test data to achieve target table sizes for size exemption testing.
        
        Args:
            table_name: Full table name (catalog.schema.table)
            target_size: Target size category ('small', 'large', 'boundary')
        """
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        if not warehouse_id:
            logger.warning("DATABRICKS_WAREHOUSE_ID not set, skipping data insertion")
            return
            
        # Get the table schema to understand column structure
        try:
            describe_result = self.client.statement_execution.execute_statement(
                statement=f"DESCRIBE {table_name}", 
                warehouse_id=warehouse_id, 
                wait_timeout="30s"
            )
            
            columns_info = []
            if (describe_result.result and describe_result.result.data_array and 
                describe_result.manifest and describe_result.manifest.schema and describe_result.manifest.schema.columns):
                
                # Get column names and types from DESCRIBE output
                for row in describe_result.result.data_array:
                    col_name = row[0]  # Column name is first column
                    col_type = row[1]  # Column type is second column
                    if col_name and not col_name.startswith('#'):  # Skip partition info
                        columns_info.append((col_name, col_type))
            
            logger.info(f"Table {table_name} has columns: {columns_info}")
            
        except Exception as e:
            logger.warning(f"Could not describe table {table_name}: {e}")
            # Fall back to assume standard (id, data) structure
            columns_info = [('id', 'BIGINT'), ('data', 'STRING')]
            
        # Build appropriate INSERT statement based on table column structure
        if target_size == "large":
            row_count = 12000
            if len(columns_info) >= 2:
                col1_name, col1_type = columns_info[0]
                col2_name, col2_type = columns_info[1]
                
                # Build SELECT clause based on column types
                select_parts = [
                    "id"  # First column is always ID
                ]
                
                # Second column - adapt to its type
                if 'STRING' in col2_type.upper():
                    select_parts.append(f"""
                        CONCAT(
                            UUID(),  -- 36 chars unique
                            '_row_', CAST(id AS STRING), '_',
                            UUID(),  -- Another 36 chars unique
                            '_data_',
                            REPEAT(SUBSTR(UUID(), 1, 8), 30),  -- 240 chars of varied UUIDs
                            '_end_', CAST(id * 17 AS STRING)  -- Varied multiplier
                        ) as {col2_name}
                    """)
                elif 'DOUBLE' in col2_type.upper() or 'FLOAT' in col2_type.upper():
                    select_parts.append(f"CAST(id * 1.5 AS DOUBLE) as {col2_name}")
                elif 'INT' in col2_type.upper():
                    select_parts.append(f"CAST(id * 2 AS BIGINT) as {col2_name}")
                else:
                    # Default to string representation
                    select_parts.append(f"CAST(id AS STRING) as {col2_name}")
                
                # Handle additional columns if present (e.g., clustering columns)
                for i in range(2, len(columns_info)):
                    col_name, col_type = columns_info[i]
                    if 'STRING' in col_type.upper():
                        select_parts.append(f"CONCAT('col{i}_', CAST(id % 100 AS STRING)) as {col_name}")
                    elif 'DOUBLE' in col_type.upper() or 'FLOAT' in col_type.upper():
                        select_parts.append(f"CAST((id % 1000) / 10.0 AS DOUBLE) as {col_name}")
                    elif 'INT' in col_type.upper():
                        select_parts.append(f"CAST(id % 1000 AS BIGINT) as {col_name}")
                    elif 'TIMESTAMP' in col_type.upper():
                        select_parts.append(f"CURRENT_TIMESTAMP() as {col_name}")
                    else:
                        select_parts.append(f"CAST(id AS STRING) as {col_name}")
                
                sql = f"""
                    INSERT INTO {table_name} 
                    SELECT 
                        {','.join(select_parts)}
                    FROM (SELECT explode(sequence(1, {row_count})) as id)
                """
            else:
                logger.warning(f"Could not determine column structure for {table_name}")
                return
            
        elif target_size == "boundary":
            # Insert data close to 1MB boundary (~900KB)
            row_count = 1000
            if len(columns_info) >= 2:
                col1_name, col1_type = columns_info[0]
                col2_name, col2_type = columns_info[1]
                
                select_parts = ["id"]
                
                if 'STRING' in col2_type.upper():
                    select_parts.append(f"CONCAT(REPEAT('b', 900), CAST(id AS STRING)) as {col2_name}")
                elif 'DOUBLE' in col2_type.upper() or 'FLOAT' in col2_type.upper():
                    select_parts.append(f"CAST(id * 1.1 AS DOUBLE) as {col2_name}")
                elif 'INT' in col2_type.upper():
                    select_parts.append(f"CAST(id AS BIGINT) as {col2_name}")
                else:
                    select_parts.append(f"CAST(id AS STRING) as {col2_name}")
                
                # Handle additional columns
                for i in range(2, len(columns_info)):
                    col_name, col_type = columns_info[i]
                    if 'STRING' in col_type.upper():
                        select_parts.append(f"CONCAT('boundary_col{i}_', CAST(id % 50 AS STRING)) as {col_name}")
                    elif 'DOUBLE' in col_type.upper() or 'FLOAT' in col_type.upper():
                        select_parts.append(f"CAST((id % 100) / 5.0 AS DOUBLE) as {col_name}")
                    elif 'INT' in col_type.upper():
                        select_parts.append(f"CAST(id % 100 AS BIGINT) as {col_name}")
                    elif 'TIMESTAMP' in col_type.upper():
                        select_parts.append(f"CURRENT_TIMESTAMP() as {col_name}")
                    else:
                        select_parts.append(f"CAST(id AS STRING) as {col_name}")
                
                sql = f"""
                    INSERT INTO {table_name}
                    SELECT 
                        {','.join(select_parts)}
                    FROM (SELECT explode(sequence(1, {row_count})) as id)
                """
            else:
                logger.warning(f"Could not determine column structure for {table_name}")
                return
            
        else:  # target_size == "small" 
            # Insert minimal data to keep under threshold
            if len(columns_info) >= 2:
                col1_name, col1_type = columns_info[0]
                col2_name, col2_type = columns_info[1]
                
                # Create appropriate values for each column type
                values_rows = []
                for i in range(1, 4):  # Insert 3 small rows
                    row_values = [str(i)]  # ID column
                    
                    # Second column value based on type
                    if 'STRING' in col2_type.upper():
                        row_values.append(f"'small_test_data_{i}'")
                    elif 'DOUBLE' in col2_type.upper() or 'FLOAT' in col2_type.upper():
                        row_values.append(f"{i * 1.5}")
                    elif 'INT' in col2_type.upper():
                        row_values.append(str(i * 10))
                    else:
                        row_values.append(f"'value_{i}'")
                    
                    # Additional columns
                    for j in range(2, len(columns_info)):
                        col_name, col_type = columns_info[j]
                        if 'STRING' in col_type.upper():
                            row_values.append(f"'col{j}_{i}'")
                        elif 'DOUBLE' in col_type.upper() or 'FLOAT' in col_type.upper():
                            row_values.append(f"{i * 0.5}")
                        elif 'INT' in col_type.upper():
                            row_values.append(str(i))
                        elif 'TIMESTAMP' in col_type.upper():
                            row_values.append("CURRENT_TIMESTAMP()")
                        else:
                            row_values.append(f"'val_{i}'")
                    
                    values_rows.append(f"({', '.join(row_values)})")
                
                sql = f"""
                    INSERT INTO {table_name}
                    VALUES {', '.join(values_rows)}
                """
            else:
                logger.warning(f"Could not determine column structure for {table_name}")
                return
            
        try:
            result = self.client.statement_execution.execute_statement(statement=sql, warehouse_id=warehouse_id)
            logger.info(f"Inserted test data for {target_size} size scenario: {table_name}")
            
            # Check if there was an error in the result
            if result.status and hasattr(result.status, 'error') and result.status.error:
                logger.error(f"Insert failed for {table_name}: {result.status.error}")
            
            # For large tables, wait a moment and verify the size was updated
            if target_size == "large":
                import time
                time.sleep(2)  # Give Delta Lake time to update table metadata
                
                # Verify the table is actually large
                try:
                    size_result = self.client.statement_execution.execute_statement(
                        statement=f"DESCRIBE DETAIL {table_name}", 
                        warehouse_id=warehouse_id, 
                        wait_timeout="30s"
                    )
                    
                    if (size_result.result and size_result.result.data_array and 
                        size_result.manifest and size_result.manifest.schema and size_result.manifest.schema.columns):
                        columns = [col.name for col in size_result.manifest.schema.columns]
                        row_data = size_result.result.data_array[0]
                        detail_dict = dict(zip(columns, row_data))
                        size_in_bytes = detail_dict.get("sizeInBytes")
                        
                        if isinstance(size_in_bytes, (int, str)):
                            actual_size = int(size_in_bytes)
                            size_mb = actual_size / (1024 * 1024)
                            logger.info(f"Verified large table {table_name}: {actual_size} bytes ({size_mb:.2f} MB)")
                except Exception as verify_e:
                    logger.warning(f"Could not verify size for large table {table_name}: {verify_e}")
                    
        except Exception as e:
            logger.warning(f"Failed to insert test data for {table_name}: {e}")
            # Continue anyway - some tests can work with empty tables


# Context manager convenience functions for each scenario
@contextmanager
def create_test_tables_for_comment_scenario(client: WorkspaceClient) -> Iterator[dict[str, str]]:
    """Context manager providing test tables for comment scenario.

    Creates all tables needed for "Tables must have a comment" testing.

    Args:
        client: Databricks workspace client

    Yields:
        Dictionary mapping spec names to full table names
    """
    from tests.fixtures.documentation.table_comment_specs import TABLE_SPECS_HAS_COMMENT

    with TestTableFactory(client) as factory:
        table_names = {}

        for spec_name, spec in TABLE_SPECS_HAS_COMMENT.items():
            full_name = factory.create_table(spec)
            table_names[spec_name] = full_name

        logger.info(f"Created {len(table_names)} test tables for has_comment scenario")
        yield table_names


@contextmanager
def create_test_tables_for_comment_length_scenario(client: WorkspaceClient) -> Iterator[dict[str, str]]:
    """Context manager providing test tables for comment length scenario.

    Creates all tables needed for "Comments must be at least 10 characters" testing.

    Args:
        client: Databricks workspace client

    Yields:
        Dictionary mapping spec names to full table names
    """
    from tests.fixtures.documentation.table_comment_specs import TABLE_SPECS_COMMENT_LENGTH

    with TestTableFactory(client) as factory:
        table_names = {}

        for spec_name, spec in TABLE_SPECS_COMMENT_LENGTH.items():
            full_name = factory.create_table(spec)
            table_names[spec_name] = full_name

        logger.info(f"Created {len(table_names)} test tables for comment_length scenario")
        yield table_names


@contextmanager
def create_test_tables_for_placeholder_detection_scenario(client: WorkspaceClient) -> Iterator[dict[str, str]]:
    """Context manager providing test tables for placeholder detection scenario.

    Creates all tables needed for "Table comments must not be placeholder text" testing.

    Args:
        client: Databricks workspace client

    Yields:
        Dictionary mapping spec names to full table names
    """
    from tests.fixtures.documentation.placeholder_detection_specs import TABLE_SPECS_PLACEHOLDER_DETECTION

    with TestTableFactory(client) as factory:
        table_names = {}

        for spec_name, spec in TABLE_SPECS_PLACEHOLDER_DETECTION.items():
            full_name = factory.create_table(spec)
            table_names[spec_name] = full_name

        logger.info(f"Created {len(table_names)} test tables for placeholder_detection scenario")
        yield table_names


@contextmanager
def create_test_tables_for_critical_columns_scenario(client: WorkspaceClient) -> Iterator[dict[str, str]]:
    """Context manager providing test tables for critical columns scenario.

    Creates all tables needed for "Critical columns must be documented" testing.

    Args:
        client: Databricks workspace client

    Yields:
        Dictionary mapping spec names to full table names
    """
    from tests.fixtures.documentation.critical_columns_specs import TABLE_SPECS_CRITICAL_COLUMNS

    with TestTableFactory(client) as factory:
        table_names = {}

        for spec_name, spec in TABLE_SPECS_CRITICAL_COLUMNS.items():
            full_name = factory.create_table_with_columns(spec)
            table_names[spec_name] = full_name

        logger.info(f"Created {len(table_names)} test tables for critical_columns scenario")
        yield table_names


@contextmanager
def create_test_tables_for_column_coverage_threshold_scenario(client: WorkspaceClient) -> Iterator[dict[str, str]]:
    """Context manager providing test tables for column coverage threshold scenario.

    Creates all tables needed for "Column documentation must meet 80% threshold" testing.

    Args:
        client: Databricks workspace client

    Yields:
        Dictionary mapping spec names to full table names
    """
    from tests.fixtures.documentation.column_coverage_specs import TABLE_SPECS_COLUMN_COVERAGE_THRESHOLD

    with TestTableFactory(client) as factory:
        table_names = {}

        for spec_name, spec in TABLE_SPECS_COLUMN_COVERAGE_THRESHOLD.items():
            full_name = factory.create_table_with_columns(spec)
            table_names[spec_name] = full_name

        logger.info(f"Created {len(table_names)} test tables for column_coverage_threshold scenario")
        yield table_names


@contextmanager
def create_test_tables_for_explicit_clustering_columns_scenario(client: WorkspaceClient) -> Iterator[dict[str, str]]:
    """Context manager providing test tables for explicit clustering columns scenario.

    Creates all tables needed for "Explicit clustering columns detection" testing.

    Args:
        client: Databricks workspace client

    Yields:
        Dictionary mapping spec names to full table names
    """
    from tests.fixtures.clustering.explicit_clustering_specs import TABLE_SPECS_EXPLICIT_CLUSTERING

    with TestTableFactory(client) as factory:
        table_names = {}

        for spec_name, spec in TABLE_SPECS_EXPLICIT_CLUSTERING.items():
            full_name = factory.create_table_with_clustering(spec)
            table_names[spec_name] = full_name

        logger.info(f"Created {len(table_names)} test tables for explicit_clustering_columns scenario")
        yield table_names


@contextmanager
def create_test_tables_for_cluster_by_auto_scenario(client: WorkspaceClient) -> Iterator[dict[str, str]]:
    """Context manager providing test tables for cluster-by-auto scenario.

    Creates all tables needed for "Tables can use clusterByAuto flag for automatic clustering" testing.

    Args:
        client: Databricks workspace client

    Yields:
        Dictionary mapping spec names to full table names
    """
    from tests.fixtures.clustering.cluster_by_auto_specs import TABLE_SPECS_CLUSTER_BY_AUTO

    with TestTableFactory(client) as factory:
        table_names = {}

        for spec_name, spec in TABLE_SPECS_CLUSTER_BY_AUTO.items():
            full_name = factory.create_table_with_cluster_by_auto(spec)
            table_names[spec_name] = full_name

        logger.info(f"Created {len(table_names)} test tables for cluster_by_auto scenario")
        yield table_names


@contextmanager
def create_test_tables_for_delta_auto_optimization_scenario(client: WorkspaceClient) -> Iterator[dict[str, str]]:
    """Context manager providing test tables for delta auto-optimization scenario.

    Creates test tables with various delta auto-optimization configurations and
    ensures proper cleanup after tests complete (or fail).

    Args:
        client: Databricks workspace client

    Yields:
        Dictionary mapping test case names to fully qualified table names

    Example:
        >>> with create_test_tables_for_delta_auto_optimization_scenario(client) as tables:
        ...     table_name = tables["both_flags_enabled"]
        ...     # Run tests with table_name
    """
    from tests.fixtures.clustering.delta_auto_optimization_specs import TABLE_SPECS_DELTA_AUTO_OPTIMIZATION

    with TestTableFactory(client) as factory:
        created_tables = {}
        for spec_name, spec in TABLE_SPECS_DELTA_AUTO_OPTIMIZATION.items():
            table_name = factory.create_table_with_delta_auto_optimization(spec)
            created_tables[spec_name] = table_name
        yield created_tables


@contextmanager
def create_test_tables_for_cluster_exclusion_scenario(client: WorkspaceClient) -> Iterator[dict[str, str]]:
    """Context manager providing test tables for cluster exclusion scenario.

    Creates test tables with various cluster_exclusion property configurations and
    ensures proper cleanup after tests complete (or fail).

    Args:
        client: Databricks workspace client

    Yields:
        Dictionary mapping test case names to fully qualified table names

    Example:
        >>> with create_test_tables_for_cluster_exclusion_scenario(client) as tables:
        ...     table_name = tables["excluded_table"]
        ...     # Run tests with table_name
    """
    from tests.fixtures.clustering.cluster_exclusion_specs import TABLE_SPECS_CLUSTER_EXCLUSION

    with TestTableFactory(client) as factory:
        created_tables = {}
        for spec_name, spec in TABLE_SPECS_CLUSTER_EXCLUSION.items():
            table_name = factory.create_table_with_properties(spec)
            created_tables[spec_name] = table_name
        logger.info(f"Created {len(created_tables)} test tables for cluster_exclusion scenario")
        yield created_tables


@contextmanager
def create_test_tables_for_size_exemption_scenario(client: WorkspaceClient) -> Iterator[dict[str, str]]:
    """Context manager providing test tables for size-based clustering exemption scenario.
    
    Creates test tables with various sizes and configurations to test automatic
    size-based exemption logic. Ensures proper cleanup after tests complete.
    
    Args:
        client: Databricks workspace client
        
    Yields:
        Dictionary mapping test case names to fully qualified table names
        
    Example:
        >>> with create_test_tables_for_size_exemption_scenario(client) as tables:
        ...     small_table = tables["small_exempt_table"] 
        ...     # Run size exemption tests
    """
    from tests.fixtures.clustering.size_exemption_specs import TABLE_SPECS_SIZE_EXEMPTION
    
    with TestTableFactory(client) as factory:
        created_tables = {}
        for spec_name, spec in TABLE_SPECS_SIZE_EXEMPTION.items():
            # Create table based on spec type
            if hasattr(spec, 'clustering_columns') and spec.clustering_columns:
                # Table with clustering columns
                table_name = factory.create_table_with_clustering(spec)
            else:
                # Regular table with properties
                table_name = factory.create_table_with_properties(spec)
            
            # Add different amounts of data based on table purpose
            if "large" in spec_name:
                # Insert enough data to exceed test threshold (1MB)
                factory._insert_test_data_for_size_testing(table_name, target_size="large")
            elif "boundary" in spec_name:
                # Insert data close to threshold boundary
                factory._insert_test_data_for_size_testing(table_name, target_size="boundary") 
            elif "empty" not in spec_name:
                # Insert minimal data for small tables (not empty)
                factory._insert_test_data_for_size_testing(table_name, target_size="small")
            # empty tables get no data inserted
            
            created_tables[spec_name] = table_name
            
        logger.info(f"Created {len(created_tables)} test tables for size_exemption scenario")
        yield created_tables
