"""Clustering validators for Databricks table clustering compliance."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from tests.utils.clustering_config_loader import get_clustering_config_loader

if TYPE_CHECKING:
    from tests.utils.discovery import TableInfo


class ClusteringValidator:
    """Validator for clustering compliance of Databricks tables.

    Supports multiple clustering scenarios including:
    - Explicit clustering columns detection
    - Auto-clustering detection
    - Clustering exemptions
    - Size-based clustering requirements
    """

    def __init__(self) -> None:
        """Initialize validator with configuration from YAML file."""
        self._config_loader = get_clustering_config_loader()

        # Load clustering configuration values from YAML
        self.clustering_property_name = self._config_loader.get_clustering_property_name()
        self.require_explicit_clustering = self._config_loader.get_require_explicit_clustering()
        self.max_clustering_columns = self._config_loader.get_max_clustering_columns()
        self.allow_empty_clustering = self._config_loader.get_allow_empty_clustering()

        # Load auto-clustering configuration values
        self.cluster_by_auto_property = self._config_loader.get_cluster_by_auto_property()
        self.cluster_by_auto_value = self._config_loader.get_cluster_by_auto_value()
        self.require_cluster_by_auto = self._config_loader.get_require_cluster_by_auto()

        # Load delta auto-optimization configuration values
        self.optimize_write_property = self._config_loader.get_optimize_write_property()
        self.optimize_write_value = self._config_loader.get_optimize_write_value()
        self.auto_compact_property = self._config_loader.get_auto_compact_property()
        self.auto_compact_value = self._config_loader.get_auto_compact_value()
        self.require_both_delta_flags = self._config_loader.get_require_both_delta_flags()

        # Load exemption configuration values
        self.honor_exclusion_flag = self._config_loader.get_honor_exclusion_flag()
        self.exclusion_property_name = self._config_loader.get_exclusion_property_name()
        self.size_threshold_bytes = self._config_loader.get_size_threshold_bytes()
        self.test_size_threshold_bytes = self._config_loader.get_test_size_threshold_bytes()
        self.exempt_small_tables = self._config_loader.get_exempt_small_tables()

    def _parse_clustering_data(self, table: TableInfo) -> list[list[str]]:
        """Parse clustering data from table properties.

        Handles both JSON string format (from Databricks) and list format (from unit tests).

        Args:
            table: TableInfo object containing table metadata

        Returns:
            Parsed clustering data as nested list format [["col1"],["col2"]]
        """
        if not table.properties:
            return []

        clustering_raw = table.properties.get(self.clustering_property_name)
        if not clustering_raw:
            return []

        # Handle string format (JSON from Databricks)
        if isinstance(clustering_raw, str):
            try:
                result = json.loads(clustering_raw)
                return result if isinstance(result, list) else []
            except (json.JSONDecodeError, TypeError):
                return []

        # Handle list format (from unit tests)
        elif isinstance(clustering_raw, list):
            return clustering_raw

        return []

    def has_clustering_columns(self, table: TableInfo) -> bool:
        """
        Check if table has explicit clustering columns defined.

        Based on feasibility research:
        - Clustering info stored in table.properties['clusteringColumns']
        - Format is nested lists: [["col1"],["col2"]]
        - Available in metadata without data scanning
        - Works on empty tables

        Args:
            table: TableInfo object containing table metadata

        Returns:
            bool: True if table has clustering columns, False otherwise
        """
        clustering_data = self._parse_clustering_data(table)
        return bool(clustering_data and len(clustering_data) > 0)

    def get_clustering_columns(self, table: TableInfo) -> list[str]:
        """
        Get list of clustering column names for a table.

        Args:
            table: TableInfo object containing table metadata

        Returns:
            list[str]: List of clustering column names, empty list if no clustering
        """
        clustering_data = self._parse_clustering_data(table)
        if not clustering_data:
            return []

        # Convert nested list format [["col1"],["col2"]] to flat list ["col1", "col2"]
        column_names = []
        for cluster_group in clustering_data:
            if isinstance(cluster_group, list) and len(cluster_group) > 0:
                column_names.append(cluster_group[0])  # Take first item from each group

        return column_names

    def count_clustering_columns(self, table: TableInfo) -> int:
        """
        Count number of clustering columns for a table.

        Args:
            table: TableInfo object containing table metadata

        Returns:
            int: Number of clustering columns (0 if no clustering)
        """
        return len(self.get_clustering_columns(table))

    def validates_clustering_column_limits(self, table: TableInfo) -> bool:
        """
        Check if table's clustering columns are within recommended limits.

        Args:
            table: TableInfo object containing table metadata

        Returns:
            bool: True if within limits, False if too many clustering columns
        """
        column_count = self.count_clustering_columns(table)
        return column_count <= self.max_clustering_columns

    # Auto-clustering detection methods

    def has_auto_clustering(self, table: TableInfo) -> bool:
        """
        Check if table has automatic clustering enabled.

        Based on feasibility research:
        - Auto-clustering enabled via CLUSTER BY AUTO SQL clause
        - Detected via table.properties['clusterByAuto'] = 'true'
        - Available immediately after table creation
        - System may auto-select clustering columns over time

        Args:
            table: TableInfo object containing table metadata

        Returns:
            bool: True if table has automatic clustering enabled, False otherwise
        """
        if table.properties is None:
            return False

        cluster_by_auto_value = table.properties.get(self.cluster_by_auto_property)
        if not cluster_by_auto_value:
            return False

        # Handle string comparison (property values are typically strings)
        return str(cluster_by_auto_value).lower() == str(self.cluster_by_auto_value).lower()

    def get_auto_clustering_status(self, table: TableInfo) -> str:
        """
        Get the automatic clustering status for a table.

        Args:
            table: TableInfo object containing table metadata

        Returns:
            str: Auto-clustering status ("enabled", "disabled", or "unknown")
        """
        # No properties at all = unknown
        if table.properties is None:
            return "unknown"

        # Has properties dict (even if empty) = can check for clusterByAuto
        cluster_by_auto_value = table.properties.get(self.cluster_by_auto_property)

        if cluster_by_auto_value is None:
            return "disabled"  # Property missing = disabled
        if str(cluster_by_auto_value).lower() == str(self.cluster_by_auto_value).lower():
            return "enabled"
        return "disabled"

    def has_any_clustering_approach(self, table: TableInfo) -> bool:
        """
        Check if table has any form of clustering (explicit or automatic).

        This method combines both explicit clustering columns detection and
        automatic clustering detection to determine if a table has any
        clustering configuration.

        Args:
            table: TableInfo object containing table metadata

        Returns:
            bool: True if table has explicit clustering OR automatic clustering, False otherwise
        """
        return (
            self.has_clustering_columns(table)
            or self.has_auto_clustering(table)
            or self.has_delta_auto_optimization(table)
        )

    def has_optimize_write(self, table: TableInfo) -> bool:
        """Check if table has optimizeWrite enabled.

        Args:
            table: TableInfo object containing table metadata

        Returns:
            bool: True if optimizeWrite is enabled, False otherwise
        """
        if table.properties is None:
            return False

        optimize_write_value = table.properties.get(self.optimize_write_property)
        if not optimize_write_value:
            return False

        return str(optimize_write_value).lower() == str(self.optimize_write_value).lower()

    def has_auto_compact(self, table: TableInfo) -> bool:
        """Check if table has autoCompact enabled.

        Args:
            table: TableInfo object containing table metadata

        Returns:
            bool: True if autoCompact is enabled, False otherwise
        """
        if table.properties is None:
            return False

        auto_compact_value = table.properties.get(self.auto_compact_property)
        if not auto_compact_value:
            return False

        return str(auto_compact_value).lower() == str(self.auto_compact_value).lower()

    def has_delta_auto_optimization(self, table: TableInfo) -> bool:
        """Check if table has delta auto-optimization enabled.

        Delta auto-optimization requires both optimizeWrite=true AND autoCompact=true
        based on the configuration setting require_both_flags.

        Args:
            table: TableInfo object containing table metadata

        Returns:
            bool: True if delta auto-optimization is properly configured, False otherwise
        """
        if self.require_both_delta_flags:
            # Both optimizeWrite and autoCompact must be enabled
            return self.has_optimize_write(table) and self.has_auto_compact(table)
        # Either optimizeWrite or autoCompact is sufficient
        return self.has_optimize_write(table) or self.has_auto_compact(table)

    def get_delta_auto_optimization_status(self, table: TableInfo) -> dict[str, Any]:
        """Get detailed delta auto-optimization status for a table.

        Args:
            table: TableInfo object containing table metadata

        Returns:
            dict: Status information including individual flag states and overall status
        """
        has_optimize_write = self.has_optimize_write(table)
        has_auto_compact = self.has_auto_compact(table)
        has_delta_optimization = self.has_delta_auto_optimization(table)

        return {
            "has_optimize_write": has_optimize_write,
            "has_auto_compact": has_auto_compact,
            "has_delta_auto_optimization": has_delta_optimization,
            "optimize_write_property": self.optimize_write_property,
            "auto_compact_property": self.auto_compact_property,
            "require_both_flags": self.require_both_delta_flags,
        }

    # Clustering exemption methods

    def has_cluster_exclusion(self, table: TableInfo) -> bool:
        """Check if table has cluster exclusion flag set.

        Based on feasibility research:
        - Cluster exclusion enabled via TBLPROPERTIES ('cluster_exclusion' = 'true')
        - Property accessible via table.properties['cluster_exclusion']
        - Property value is string 'true' when enabled
        - Exempts table from clustering requirements when enabled

        Args:
            table: TableInfo object containing table metadata

        Returns:
            bool: True if table has cluster_exclusion='true', False otherwise
        """
        if not self.honor_exclusion_flag:
            return False

        if table.properties is None:
            return False

        exclusion_value = table.properties.get(self.exclusion_property_name)
        if not exclusion_value:
            return False

        # Handle string comparison (property values are typically strings)
        return str(exclusion_value).lower() == "true"

    def get_cluster_exclusion_status(self, table: TableInfo) -> str:
        """Get cluster exclusion status for a table.

        Args:
            table: TableInfo object containing table metadata

        Returns:
            str: Exclusion status ("excluded", "not_excluded", "unknown", or "disabled")
        """
        if not self.honor_exclusion_flag:
            return "disabled"

        if table.properties is None:
            return "unknown"

        exclusion_value = table.properties.get(self.exclusion_property_name)

        if exclusion_value is None:
            return "not_excluded"  # Property missing = not excluded
        if str(exclusion_value).lower() == "true":
            return "excluded"
        return "not_excluded"

    def is_exempt_from_clustering_requirements(self, table: TableInfo) -> bool:
        """Check if table is exempt from clustering requirements.

        A table is exempt from clustering requirements if:
        1. It has cluster_exclusion='true' property, OR
        2. It's below the size threshold (if exempt_small_tables is enabled)

        Note: Size-based exemption is not implemented in this method as it requires
        additional table size data not available in TableInfo. This method focuses
        on the cluster_exclusion property exemption only.

        Args:
            table: TableInfo object containing table metadata

        Returns:
            bool: True if table is exempt from clustering requirements, False otherwise
        """
        return self.has_cluster_exclusion(table)

    def should_enforce_clustering_requirements(self, table: TableInfo) -> bool:
        """Check if clustering requirements should be enforced for this table.

        This is the inverse of is_exempt_from_clustering_requirements.
        Used for validation logic to determine if a table must have clustering.

        Args:
            table: TableInfo object containing table metadata

        Returns:
            bool: True if clustering requirements should be enforced, False if exempt
        """
        return not self.is_exempt_from_clustering_requirements(table)
