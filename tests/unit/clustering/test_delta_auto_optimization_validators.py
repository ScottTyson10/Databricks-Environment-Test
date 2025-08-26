"""Unit tests for delta auto-optimization validation functionality.

Layer 1 tests for delta auto-optimization detection methods in ClusteringValidator.
Tests focus on optimizeWrite and autoCompact flag detection and combination logic.
"""

from typing import Any

import pytest

from tests.utils.discovery import TableInfo
from tests.validators.clustering import ClusteringValidator


class TestDeltaAutoOptimizationValidators:
    """Test suite for delta auto-optimization validation methods."""

    @pytest.fixture
    def validator(self) -> ClusteringValidator:
        """Create clustering validator for testing."""
        return ClusteringValidator()

    @pytest.fixture
    def table_with_both_flags(self) -> TableInfo:
        """Table with both optimizeWrite and autoCompact enabled."""
        return TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table_both",
            comment="Test table with both delta optimization flags",
            columns=(),
            properties={
                "delta.autoOptimize.optimizeWrite": "true",
                "delta.autoOptimize.autoCompact": "true",
            },
        )

    @pytest.fixture
    def table_with_optimize_write_only(self) -> TableInfo:
        """Table with only optimizeWrite enabled."""
        return TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table_optimize_only",
            comment="Test table with only optimizeWrite",
            columns=(),
            properties={
                "delta.autoOptimize.optimizeWrite": "true",
            },
        )

    @pytest.fixture
    def table_with_auto_compact_only(self) -> TableInfo:
        """Table with only autoCompact enabled."""
        return TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table_compact_only",
            comment="Test table with only autoCompact",
            columns=(),
            properties={
                "delta.autoOptimize.autoCompact": "true",
            },
        )

    @pytest.fixture
    def table_with_no_optimization(self) -> TableInfo:
        """Table with no delta auto-optimization flags."""
        return TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table_no_optimization",
            comment="Test table without optimization",
            columns=(),
            properties={
                "some_other_property": "value",
            },
        )

    @pytest.fixture
    def table_with_no_properties(self) -> TableInfo:
        """Table with no properties at all."""
        return TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table_no_props",
            comment="Test table with no properties",
            columns=(),
            properties=None,
        )

    def test_has_optimize_write_with_enabled_flag(
        self, validator: ClusteringValidator, table_with_both_flags: TableInfo
    ):
        """Test optimizeWrite detection when flag is enabled."""
        assert validator.has_optimize_write(table_with_both_flags) is True

    def test_has_optimize_write_with_disabled_table(
        self, validator: ClusteringValidator, table_with_auto_compact_only: TableInfo
    ):
        """Test optimizeWrite detection when flag is not present."""
        assert validator.has_optimize_write(table_with_auto_compact_only) is False

    def test_has_optimize_write_with_no_properties(
        self, validator: ClusteringValidator, table_with_no_properties: TableInfo
    ):
        """Test optimizeWrite detection with no properties."""
        assert validator.has_optimize_write(table_with_no_properties) is False

    def test_has_auto_compact_with_enabled_flag(self, validator: ClusteringValidator, table_with_both_flags: TableInfo):
        """Test autoCompact detection when flag is enabled."""
        assert validator.has_auto_compact(table_with_both_flags) is True

    def test_has_auto_compact_with_disabled_table(
        self, validator: ClusteringValidator, table_with_optimize_write_only: TableInfo
    ):
        """Test autoCompact detection when flag is not present."""
        assert validator.has_auto_compact(table_with_optimize_write_only) is False

    def test_has_auto_compact_with_no_properties(
        self, validator: ClusteringValidator, table_with_no_properties: TableInfo
    ):
        """Test autoCompact detection with no properties."""
        assert validator.has_auto_compact(table_with_no_properties) is False

    def test_has_delta_auto_optimization_with_both_flags(
        self, validator: ClusteringValidator, table_with_both_flags: TableInfo
    ):
        """Test delta auto-optimization detection when both flags are enabled."""
        # Default config requires both flags
        assert validator.has_delta_auto_optimization(table_with_both_flags) is True

    def test_has_delta_auto_optimization_with_optimize_write_only(
        self, validator: ClusteringValidator, table_with_optimize_write_only: TableInfo
    ):
        """Test delta auto-optimization detection with only optimizeWrite."""
        # Default config requires both flags, so this should be False
        assert validator.has_delta_auto_optimization(table_with_optimize_write_only) is False

    def test_has_delta_auto_optimization_with_auto_compact_only(
        self, validator: ClusteringValidator, table_with_auto_compact_only: TableInfo
    ):
        """Test delta auto-optimization detection with only autoCompact."""
        # Default config requires both flags, so this should be False
        assert validator.has_delta_auto_optimization(table_with_auto_compact_only) is False

    def test_has_delta_auto_optimization_with_no_flags(
        self, validator: ClusteringValidator, table_with_no_optimization: TableInfo
    ):
        """Test delta auto-optimization detection with no optimization flags."""
        assert validator.has_delta_auto_optimization(table_with_no_optimization) is False

    def test_get_delta_auto_optimization_status_comprehensive(
        self, validator: ClusteringValidator, table_with_both_flags: TableInfo
    ):
        """Test comprehensive delta auto-optimization status reporting."""
        status = validator.get_delta_auto_optimization_status(table_with_both_flags)

        expected_status = {
            "has_optimize_write": True,
            "has_auto_compact": True,
            "has_delta_auto_optimization": True,
            "optimize_write_property": "delta.autoOptimize.optimizeWrite",
            "auto_compact_property": "delta.autoOptimize.autoCompact",
            "require_both_flags": True,
        }

        assert status == expected_status

    def test_get_delta_auto_optimization_status_partial(
        self, validator: ClusteringValidator, table_with_optimize_write_only: TableInfo
    ):
        """Test status reporting for table with partial optimization."""
        status = validator.get_delta_auto_optimization_status(table_with_optimize_write_only)

        expected_status = {
            "has_optimize_write": True,
            "has_auto_compact": False,
            "has_delta_auto_optimization": False,  # Requires both flags by default
            "optimize_write_property": "delta.autoOptimize.optimizeWrite",
            "auto_compact_property": "delta.autoOptimize.autoCompact",
            "require_both_flags": True,
        }

        assert status == expected_status

    def test_has_any_clustering_approach_includes_delta_optimization(
        self, validator: ClusteringValidator, table_with_both_flags: TableInfo
    ):
        """Test that has_any_clustering_approach includes delta auto-optimization."""
        # Table has delta optimization but no explicit clustering or cluster-by-auto
        assert validator.has_any_clustering_approach(table_with_both_flags) is True

    def test_case_insensitive_flag_detection(self, validator: ClusteringValidator):
        """Test that delta auto-optimization detection is case insensitive."""
        table_with_mixed_case = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_mixed_case",
            comment="Test mixed case",
            columns=(),
            properties={
                "delta.autoOptimize.optimizeWrite": "TRUE",  # Uppercase
                "delta.autoOptimize.autoCompact": "True",  # Mixed case
            },
        )

        assert validator.has_optimize_write(table_with_mixed_case) is True
        assert validator.has_auto_compact(table_with_mixed_case) is True
        assert validator.has_delta_auto_optimization(table_with_mixed_case) is True

    def test_invalid_flag_values_detection(self, validator: ClusteringValidator):
        """Test detection with invalid flag values."""
        table_with_invalid_values = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_invalid",
            comment="Test invalid values",
            columns=(),
            properties={
                "delta.autoOptimize.optimizeWrite": "false",  # Should not match "true"
                "delta.autoOptimize.autoCompact": "maybe",  # Invalid value
            },
        )

        assert validator.has_optimize_write(table_with_invalid_values) is False
        assert validator.has_auto_compact(table_with_invalid_values) is False
        assert validator.has_delta_auto_optimization(table_with_invalid_values) is False

    def test_configuration_property_names_respected(self, validator: ClusteringValidator):
        """Test that validator respects configured property names."""
        # Verify default configuration values are loaded correctly
        assert validator.optimize_write_property == "delta.autoOptimize.optimizeWrite"
        assert validator.optimize_write_value == "true"
        assert validator.auto_compact_property == "delta.autoOptimize.autoCompact"
        assert validator.auto_compact_value == "true"
        assert validator.require_both_delta_flags is True

    @pytest.mark.parametrize(
        "optimize_write_value,auto_compact_value,expected_has_optimize,expected_has_compact,expected_has_delta",
        [
            ("true", "true", True, True, True),  # Both enabled
            ("true", "false", True, False, False),  # Only optimize write
            ("false", "true", False, True, False),  # Only auto compact
            ("false", "false", False, False, False),  # Neither enabled
            ("True", "TRUE", True, True, True),  # Case variations
            ("", "true", False, True, False),  # Empty value
            (None, "true", False, True, False),  # None value
        ],
    )
    def test_parametrized_flag_combinations(
        self,
        validator: ClusteringValidator,
        optimize_write_value: str | None,
        auto_compact_value: str | None,
        expected_has_optimize: bool,
        expected_has_compact: bool,
        expected_has_delta: bool,
    ):
        """Test various combinations of delta auto-optimization flags."""
        properties: dict[str, Any] = {}

        if optimize_write_value is not None:
            properties["delta.autoOptimize.optimizeWrite"] = optimize_write_value
        if auto_compact_value is not None:
            properties["delta.autoOptimize.autoCompact"] = auto_compact_value

        table = TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="test_parametrized",
            comment="Parametrized test table",
            columns=(),
            properties=properties,
        )

        assert validator.has_optimize_write(table) is expected_has_optimize
        assert validator.has_auto_compact(table) is expected_has_compact
        assert validator.has_delta_auto_optimization(table) is expected_has_delta
