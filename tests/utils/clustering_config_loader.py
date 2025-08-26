"""Configuration loader for clustering validation settings."""

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]


class ClusteringConfigLoader:
    """Loads and provides access to clustering validation configuration."""

    def __init__(self, config_path: str | Path | None = None) -> None:
        """Initialize clustering config loader.

        Args:
            config_path: Optional path to config file. If None, uses default location.
        """
        if config_path is None:
            # Default to tests/config/clustering_config.yaml relative to this file
            current_dir = Path(__file__).parent
            self.config_path = current_dir.parent / "config" / "clustering_config.yaml"
        else:
            self.config_path = Path(config_path)

        self._config: dict[str, Any] | None = None

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with self.config_path.open(encoding="utf-8") as f:
            loaded_config = yaml.safe_load(f)
            return loaded_config if loaded_config is not None else {}

    @property
    def config(self) -> dict[str, Any]:
        """Get configuration dictionary, loading it if necessary."""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def get_clustering_detection_config(self) -> dict[str, Any]:
        """Get clustering detection configuration."""
        result = self.config.get("clustering_detection", {})
        return result if isinstance(result, dict) else {}

    def get_clustering_validation_config(self) -> dict[str, Any]:
        """Get clustering validation configuration."""
        result = self.config.get("clustering_validation", {})
        return result if isinstance(result, dict) else {}

    def get_clustering_property_name(self) -> str:
        """Get the property name for clustering columns."""
        result = self.get_clustering_detection_config().get("clustering_property_name", "clusteringColumns")
        return str(result)

    def get_max_clustering_columns(self) -> int:
        """Get maximum recommended clustering columns."""
        result = self.get_clustering_detection_config().get("max_clustering_columns", 4)
        return int(result)

    def get_require_explicit_clustering(self) -> bool:
        """Get whether explicit clustering is required."""
        result = self.get_clustering_detection_config().get("require_explicit_clustering", False)
        return bool(result)

    def get_allow_empty_clustering(self) -> bool:
        """Get whether tables without clustering are allowed."""
        result = self.get_clustering_validation_config().get("allow_empty_clustering", True)
        return bool(result)

    def get_validate_column_limits(self) -> bool:
        """Get whether to validate clustering column limits."""
        result = self.get_clustering_validation_config().get("validate_column_limits", True)
        return bool(result)

    def get_validation_messages(self) -> dict[str, str]:
        """Get validation messages configuration."""
        result = self.config.get("validation_messages", {})
        if isinstance(result, dict):
            # Convert all values to strings
            return {str(k): str(v) for k, v in result.items()}
        return {}

    def get_auto_clustering_detection_config(self) -> dict[str, Any]:
        """Get auto-clustering detection configuration."""
        result = self.config.get("auto_clustering_detection", {})
        return result if isinstance(result, dict) else {}

    def get_cluster_by_auto_property(self) -> str:
        """Get the property name for clusterByAuto flag."""
        result = self.get_auto_clustering_detection_config().get("cluster_by_auto_property", "clusterByAuto")
        return str(result)

    def get_cluster_by_auto_value(self) -> str:
        """Get the expected value for clusterByAuto when enabled."""
        result = self.get_auto_clustering_detection_config().get("cluster_by_auto_value", "true")
        return str(result)

    def get_require_cluster_by_auto(self) -> bool:
        """Get whether automatic clustering is required."""
        result = self.get_auto_clustering_detection_config().get("require_cluster_by_auto", False)
        return bool(result)

    def get_delta_auto_optimization_config(self) -> dict[str, Any]:
        """Get delta auto-optimization configuration."""
        result = self.config.get("delta_auto_optimization", {})
        return result if isinstance(result, dict) else {}

    def get_optimize_write_property(self) -> str:
        """Get the property name for optimizeWrite flag."""
        result = self.get_delta_auto_optimization_config().get(
            "optimize_write_property", "delta.autoOptimize.optimizeWrite"
        )
        return str(result)

    def get_optimize_write_value(self) -> str:
        """Get the expected value for optimizeWrite when enabled."""
        result = self.get_delta_auto_optimization_config().get("optimize_write_value", "true")
        return str(result)

    def get_auto_compact_property(self) -> str:
        """Get the property name for autoCompact flag."""
        result = self.get_delta_auto_optimization_config().get(
            "auto_compact_property", "delta.autoOptimize.autoCompact"
        )
        return str(result)

    def get_auto_compact_value(self) -> str:
        """Get the expected value for autoCompact when enabled."""
        result = self.get_delta_auto_optimization_config().get("auto_compact_value", "true")
        return str(result)

    def get_require_both_delta_flags(self) -> bool:
        """Get whether both optimizeWrite and autoCompact are required."""
        result = self.get_delta_auto_optimization_config().get("require_both_flags", True)
        return bool(result)


_singleton_instance: ClusteringConfigLoader | None = None


def get_clustering_config_loader() -> ClusteringConfigLoader:
    """Get a singleton instance of ClusteringConfigLoader."""
    global _singleton_instance
    if _singleton_instance is None:
        _singleton_instance = ClusteringConfigLoader()
    return _singleton_instance
