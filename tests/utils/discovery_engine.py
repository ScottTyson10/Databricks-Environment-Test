"""Discovery engine for finding Databricks tables.

Implements configurable discovery for both integration tests (specific catalogs)
and production use (all accessible catalogs).
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import TableInfo as SdkTableInfo

from tests.utils.discovery import TableInfo

logger = logging.getLogger(__name__)


@dataclass
class DiscoveryConfig:
    """Configuration for table discovery.

    For integration tests: specify target_catalogs=["workspace"]
    For production: use defaults to discover all accessible catalogs
    """

    target_catalogs: list[str] | None = None  # None = discover all
    target_schemas: list[str] | None = None  # None = discover all
    max_tables_per_schema: int = 1000
    max_total_tables: int = 5000
    include_system_catalogs: bool = False


class DatabricksDiscovery:
    """Discovery engine for Databricks tables.

    Configurable for both integration tests and production use.
    """

    def __init__(self, client: WorkspaceClient, config: DiscoveryConfig | None = None):
        self.client = client
        self.config = config or DiscoveryConfig()

    def discover_tables(self) -> list[TableInfo]:
        """Discover tables based on configuration.

        Returns:
            List of discovered tables as TableInfo objects
        """
        logger.info(f"Starting table discovery with config: {self.config}")

        discovered_tables = []

        for catalog_name in self._get_target_catalogs():
            try:
                catalog_tables = list(self._discover_catalog_tables(catalog_name))
                discovered_tables.extend(catalog_tables)
                logger.info(f"Discovered {len(catalog_tables)} tables in catalog '{catalog_name}'")

                # Safety limit check
                if len(discovered_tables) >= self.config.max_total_tables:
                    logger.warning(f"Reached max_total_tables limit ({self.config.max_total_tables})")
                    break

            except Exception as e:
                logger.warning(f"Failed to discover tables in catalog '{catalog_name}': {e}")
                continue

        logger.info(f"Discovery complete: {len(discovered_tables)} total tables")
        return discovered_tables

    def _get_target_catalogs(self) -> list[str]:
        """Get list of catalogs to search.

        Returns either configured catalogs or discovers all accessible ones.
        """
        if self.config.target_catalogs:
            # Integration test mode - use specific catalogs
            logger.info(f"Using configured catalogs: {self.config.target_catalogs}")
            return self.config.target_catalogs

        # Production mode - discover all accessible catalogs
        logger.info("Discovering all accessible catalogs")
        discovered_catalogs = []

        try:
            for catalog in self.client.catalogs.list():
                catalog_name = catalog.name
                if catalog_name is None:
                    continue

                # Skip system catalogs unless explicitly included
                if not self.config.include_system_catalogs and catalog_name in {"system", "information_schema"}:
                    logger.debug(f"Skipping system catalog: {catalog_name}")
                    continue

                discovered_catalogs.append(catalog_name)
                logger.debug(f"Found catalog: {catalog_name}")

        except Exception as e:
            logger.error(f"Failed to discover catalogs: {e}")
            return []

        logger.info(f"Discovered {len(discovered_catalogs)} accessible catalogs")
        return discovered_catalogs

    def _discover_catalog_tables(self, catalog_name: str) -> Iterator[TableInfo]:
        """Discover tables in a specific catalog.

        Args:
            catalog_name: Name of catalog to search

        Yields:
            TableInfo objects for each discovered table
        """
        try:
            # Get schemas in catalog
            schemas = list(self.client.schemas.list(catalog_name=catalog_name))
            logger.debug(f"Found {len(schemas)} schemas in catalog '{catalog_name}'")

            for schema in schemas:
                schema_name = schema.name
                if schema_name is None:
                    continue

                # Filter schemas if configured
                if self.config.target_schemas and schema_name not in self.config.target_schemas:
                    logger.debug(f"Skipping schema '{schema_name}' (not in target list)")
                    continue

                try:
                    tables_list = list(self.client.tables.list(catalog_name=catalog_name, schema_name=schema_name))
                    for schema_tables, table in enumerate(tables_list, 1):
                        # Convert SDK TableInfo to our TableInfo
                        table_info = self._convert_sdk_table(table, catalog_name, schema_name)
                        yield table_info

                        if schema_tables >= self.config.max_tables_per_schema:
                            logger.warning(f"Reached max_tables_per_schema limit in {catalog_name}.{schema_name}")
                            break

                except Exception as e:
                    logger.warning(f"Failed to list tables in {catalog_name}.{schema_name}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to list schemas in catalog '{catalog_name}': {e}")
            return

    def _convert_sdk_table(self, sdk_table: SdkTableInfo, catalog_name: str, schema_name: str) -> TableInfo:
        """Convert SDK TableInfo to our TableInfo.

        Args:
            sdk_table: Databricks SDK table info
            catalog_name: Catalog name
            schema_name: Schema name

        Returns:
            Our TableInfo object
        """
        # Extract column information if available
        from tests.utils.discovery import ColumnInfo

        columns: tuple[ColumnInfo, ...] = ()
        if sdk_table.columns:
            columns = tuple(
                ColumnInfo(name=col.name or "unknown", type_text=col.type_text or "unknown", comment=col.comment)
                for col in sdk_table.columns
            )

        table_name = sdk_table.name or "unknown"

        # Extract properties if available (needed for clustering detection)
        properties = None
        if hasattr(sdk_table, "properties") and sdk_table.properties:
            properties = dict(sdk_table.properties)

        return TableInfo(
            catalog=catalog_name,
            schema=schema_name,
            table=table_name,
            comment=sdk_table.comment,
            columns=columns,
            properties=properties,
        )


def create_integration_discovery(
    client: WorkspaceClient, test_catalog: str = "workspace", test_schema: str = "pytest_test_data"
) -> DatabricksDiscovery:
    """Create discovery engine configured for integration testing.

    Args:
        client: Databricks workspace client
        test_catalog: Catalog containing test tables
        test_schema: Schema containing test tables

    Returns:
        Discovery engine configured for integration tests
    """
    config = DiscoveryConfig(
        target_catalogs=[test_catalog],
        target_schemas=[test_schema],
        max_tables_per_schema=100,  # Lower limits for testing
        max_total_tables=500,
    )

    logger.info(f"Created integration discovery for {test_catalog}.{test_schema}")
    return DatabricksDiscovery(client, config)


def create_production_discovery(client: WorkspaceClient) -> DatabricksDiscovery:
    """Create discovery engine configured for production use.

    Uses environment variables for configuration:
    - DISCOVERY_TARGET_CATALOGS: Comma-separated list (e.g., "workspace,samples")
    - DISCOVERY_TARGET_SCHEMAS: Comma-separated list (e.g., "pytest_test_data,information_schema")
    - DISCOVERY_MAX_TABLES: Maximum total tables to discover (default: 5000)
    - DISCOVERY_MAX_PER_SCHEMA: Maximum tables per schema (default: 1000)

    Args:
        client: Databricks workspace client

    Returns:
        Discovery engine configured for production
    """
    import os

    # Get configuration from environment variables
    target_catalogs_env = os.getenv("DISCOVERY_TARGET_CATALOGS")
    target_schemas_env = os.getenv("DISCOVERY_TARGET_SCHEMAS")
    max_tables = int(os.getenv("DISCOVERY_MAX_TABLES", "5000"))
    max_per_schema = int(os.getenv("DISCOVERY_MAX_PER_SCHEMA", "1000"))
    include_system = os.getenv("DISCOVERY_INCLUDE_SYSTEM", "false").lower() == "true"

    # Parse comma-separated lists
    target_catalogs = None
    if target_catalogs_env:
        target_catalogs = [cat.strip() for cat in target_catalogs_env.split(",") if cat.strip()]

    target_schemas = None
    if target_schemas_env:
        target_schemas = [schema.strip() for schema in target_schemas_env.split(",") if schema.strip()]

    config = DiscoveryConfig(
        target_catalogs=target_catalogs,
        target_schemas=target_schemas,
        max_tables_per_schema=max_per_schema,
        max_total_tables=max_tables,
        include_system_catalogs=include_system,
    )

    # Log configuration for visibility
    if target_catalogs:
        logger.info(f"Production discovery targeting catalogs: {target_catalogs}")
    else:
        logger.info("Production discovery targeting all accessible catalogs")

    if target_schemas:
        logger.info(f"Production discovery targeting schemas: {target_schemas}")
    else:
        logger.info("Production discovery targeting all schemas")

    logger.info(f"Discovery limits: {max_per_schema} per schema, {max_tables} total")

    return DatabricksDiscovery(client, config)
