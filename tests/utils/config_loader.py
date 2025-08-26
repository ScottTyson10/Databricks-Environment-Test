"""Configuration loader for documentation validation settings."""

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]


class ConfigLoader:
    """Loads and provides access to documentation validation configuration."""

    def __init__(self, config_path: str | Path | None = None) -> None:
        """Initialize config loader.

        Args:
            config_path: Optional path to config file. If None, uses default location.
        """
        if config_path is None:
            # Default to tests/config/documentation_config.yaml relative to this file
            current_dir = Path(__file__).parent
            self.config_path = current_dir.parent / "config" / "documentation_config.yaml"
        else:
            self.config_path = Path(config_path)

        self._config: dict[str, Any] | None = None

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with self.config_path.open(encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if not isinstance(config, dict):
            raise ValueError(f"Configuration file must contain a YAML dictionary: {self.config_path}")

        return config

    @property
    def config(self) -> dict[str, Any]:
        """Get loaded configuration, loading if necessary."""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def get_config_section(self, section_name: str, default: Any = None) -> Any:
        """Get a configuration section with safe fallback."""
        return self.config.get(section_name, default or {})

    def get_config_value(self, section_name: str, key_name: str, default: Any = None) -> Any:
        """Get a specific configuration value from a section."""
        section = self.get_config_section(section_name, {})
        if not isinstance(section, dict):
            return default
        return section.get(key_name, default)

    def get_patterns_from_section(self, section_name: str, patterns_key: str = "patterns") -> list[str]:
        """Extract patterns from a configuration section, handling both dict and list formats."""
        patterns = self.get_config_section(section_name, [])

        if isinstance(patterns, list):
            # Handle list of pattern objects or simple strings
            if patterns and isinstance(patterns[0], dict):
                return [p.get("pattern", "") for p in patterns if "pattern" in p]
            # Simple list of strings
            return [str(p) for p in patterns]
        if isinstance(patterns, dict):
            # Patterns nested under a key in the section
            nested_patterns = patterns.get(patterns_key, [])
            return [str(p) for p in nested_patterns] if isinstance(nested_patterns, list) else []

        return []

    def get_critical_column_patterns(self) -> list[str]:
        """Get list of critical column patterns (backward compatibility)."""
        return self.get_patterns_from_section("critical_column_patterns")

    def get_critical_column_patterns_with_boundaries(self) -> list[dict[str, Any]]:
        """Get critical column patterns with word boundary settings.

        Returns:
            List of pattern dictionaries with 'pattern', 'word_boundary', etc.
        """
        patterns_config = self.get_config_section("critical_column_patterns", [])
        if not isinstance(patterns_config, list):
            return []

        # Ensure each pattern has required fields with defaults
        result = []
        for item in patterns_config:
            if isinstance(item, dict) and "pattern" in item:
                pattern_info = {
                    "pattern": item["pattern"],
                    "word_boundary": item.get("word_boundary", False),  # Default to substring matching
                    "case_sensitive": item.get("case_sensitive", False),
                    "description": item.get("description", ""),
                }
                result.append(pattern_info)

        return result

    def get_validation_threshold(self, threshold_name: str, default_value: int | float = 0) -> int | float:
        """Get a validation threshold by name."""
        value = self.get_config_value("validation_thresholds", threshold_name, default_value)
        return int(value) if isinstance(default_value, int) else float(value)

    def get_placeholder_patterns(self) -> list[str]:
        """Get placeholder detection patterns."""
        return self.get_patterns_from_section("placeholder_detection", "patterns")

    def get_placeholder_detection_config(self) -> dict[str, Any]:
        """Get complete placeholder detection configuration."""
        config = self.get_config_section("placeholder_detection")
        return dict(config) if isinstance(config, dict) else {}

    def get_comment_validation_config(self) -> dict[str, Any]:
        """Get comment validation configuration."""
        config = self.get_config_section("comment_validation")
        return dict(config) if isinstance(config, dict) else {}

    def get_comprehensive_rules(self) -> dict[str, Any]:
        """Get comprehensive documentation rules configuration."""
        config = self.get_config_section("comprehensive_rules")
        return dict(config) if isinstance(config, dict) else {}


# Global config loader instance
_config_loader: ConfigLoader | None = None


def get_config_loader() -> ConfigLoader:
    """Get singleton configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader
