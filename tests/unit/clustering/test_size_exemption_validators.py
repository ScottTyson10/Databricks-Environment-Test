"""Unit tests for size-based clustering exemption validators."""

import pytest

from tests.utils.discovery import TableInfo
from tests.validators.clustering import ClusteringValidator


class TestSizeExemptionValidators:
    """Test size-based clustering exemption logic."""

    @pytest.fixture
    def validator(self):
        """Create ClusteringValidator instance for testing."""
        return ClusteringValidator()

    @pytest.fixture
    def small_table(self):
        """Create a small test table under 1GB."""
        return TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="small_table",
            comment="A small test table",
            properties={},  # No cluster_exclusion property
        )

    @pytest.fixture
    def large_table(self):
        """Create a large test table over 1GB."""
        return TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="large_table",
            comment="A large test table",
            properties={},  # No cluster_exclusion property
        )

    @pytest.fixture
    def test_table(self):
        """Create a test table (in pytest_test_data schema)."""
        return TableInfo(
            catalog="workspace",
            schema="pytest_test_data",  # This makes is_test_table = True
            table="test_table",
            comment="A test table",
            properties={},
        )

    @pytest.fixture
    def excluded_table(self):
        """Create a table with manual cluster_exclusion flag."""
        return TableInfo(
            catalog="test_catalog",
            schema="test_schema",
            table="excluded_table",
            comment="Manually excluded table",
            properties={"cluster_exclusion": "true"},
        )

    def test_is_small_table_under_threshold(self, validator, small_table):
        """Test that tables under size threshold are considered small."""
        # Size under 1GB (1073741824 bytes)
        size_bytes = 500_000_000  # 500MB

        result = validator.is_small_table(small_table, validator.size_threshold_bytes, size_bytes)

        assert result is True

    def test_is_small_table_over_threshold(self, validator, large_table):
        """Test that tables over size threshold are not considered small."""
        # Size over 1GB
        size_bytes = 2_000_000_000  # 2GB

        result = validator.is_small_table(large_table, validator.size_threshold_bytes, size_bytes)

        assert result is False

    def test_is_small_table_exactly_at_threshold(self, validator, large_table):
        """Test table exactly at threshold (should not be considered small)."""
        # Size exactly 1GB
        size_bytes = 1_073_741_824  # 1GB exactly

        result = validator.is_small_table(large_table, validator.size_threshold_bytes, size_bytes)

        assert result is False

    def test_is_small_table_test_threshold(self, validator, test_table):
        """Test that test tables use the test threshold (1MB)."""
        # Size under test threshold (1MB = 1048576 bytes)
        size_bytes = 500_000  # 500KB

        result = validator.is_small_table(test_table, validator.test_size_threshold_bytes, size_bytes)

        assert result is True

    def test_is_small_table_test_over_threshold(self, validator, test_table):
        """Test that test tables over test threshold are not small."""
        # Size over test threshold (1MB)
        size_bytes = 2_000_000  # 2MB

        result = validator.is_small_table(test_table, validator.test_size_threshold_bytes, size_bytes)

        assert result is False

    def test_is_small_table_disabled(self, validator, small_table, monkeypatch):
        """Test that size exemption can be disabled via configuration."""
        # Disable small table exemption
        monkeypatch.setattr(validator, "exempt_small_tables", False)

        size_bytes = 500_000_000  # 500MB (normally small)

        result = validator.is_small_table(small_table, validator.size_threshold_bytes, size_bytes)

        assert result is False

    def test_is_small_table_no_size_data(self, validator, small_table):
        """Test behavior when size cannot be determined."""
        # No size_bytes provided and no warehouse_id
        result = validator.is_small_table(small_table, validator.size_threshold_bytes, None)

        assert result is False

    def test_is_exempt_size_based_small_table(self, validator, small_table):
        """Test that small tables are exempt from clustering requirements."""
        size_bytes = 500_000_000  # 500MB

        result = validator.is_exempt_from_clustering_requirements(
            small_table, validator.size_threshold_bytes, size_bytes
        )

        assert result is True

    def test_is_exempt_size_based_large_table(self, validator, large_table):
        """Test that large tables are NOT exempt from clustering requirements."""
        size_bytes = 2_000_000_000  # 2GB

        result = validator.is_exempt_from_clustering_requirements(
            large_table, validator.size_threshold_bytes, size_bytes
        )

        assert result is False

    def test_is_exempt_manual_exclusion_takes_precedence(self, validator, excluded_table):
        """Test that manual cluster_exclusion flag overrides size check."""
        size_bytes = 2_000_000_000  # 2GB (large table)

        result = validator.is_exempt_from_clustering_requirements(
            excluded_table, validator.size_threshold_bytes, size_bytes
        )

        # Should be exempt due to manual exclusion flag despite large size
        assert result is True

    def test_is_exempt_both_conditions_true(self, validator, excluded_table):
        """Test exemption when both manual exclusion and small size are true."""
        size_bytes = 500_000_000  # 500MB (small)

        result = validator.is_exempt_from_clustering_requirements(
            excluded_table, validator.size_threshold_bytes, size_bytes
        )

        assert result is True

    def test_is_exempt_neither_condition_true(self, validator, large_table):
        """Test no exemption when table is large and has no exclusion flag."""
        size_bytes = 2_000_000_000  # 2GB

        result = validator.is_exempt_from_clustering_requirements(
            large_table, validator.size_threshold_bytes, size_bytes
        )

        assert result is False

    def test_should_enforce_clustering_small_table(self, validator, small_table):
        """Test that clustering should NOT be enforced for small tables."""
        size_bytes = 500_000_000  # 500MB

        result = validator.should_enforce_clustering_requirements(
            small_table, validator.size_threshold_bytes, size_bytes
        )

        assert result is False  # Should NOT enforce for small tables

    def test_should_enforce_clustering_large_table(self, validator, large_table):
        """Test that clustering SHOULD be enforced for large tables."""
        size_bytes = 2_000_000_000  # 2GB

        result = validator.should_enforce_clustering_requirements(
            large_table, validator.size_threshold_bytes, size_bytes
        )

        assert result is True  # Should enforce for large tables

    def test_edge_case_zero_size(self, validator, small_table):
        """Test handling of zero-size tables."""
        size_bytes = 0

        result = validator.is_small_table(small_table, validator.size_threshold_bytes, size_bytes)

        assert result is True  # Zero size is under threshold

    def test_edge_case_negative_size(self, validator, small_table):
        """Test handling of negative size (invalid data)."""
        size_bytes = -1

        # Negative size should still be "less than" threshold
        result = validator.is_small_table(small_table, validator.size_threshold_bytes, size_bytes)

        assert result is True

    @pytest.mark.parametrize(
        "size_mb,expected",
        [
            (0, True),  # 0MB - small
            (1, True),  # 1MB - small
            (500, True),  # 500MB - small
            (999, True),  # 999MB - small
            (1024, False),  # 1024MB (1GB) - not small
            (1025, False),  # 1025MB - not small
            (2048, False),  # 2048MB (2GB) - not small
        ],
    )
    def test_size_thresholds_parametrized(self, validator, small_table, size_mb, expected):
        """Test various size thresholds with parameterized test."""
        size_bytes = size_mb * 1024 * 1024  # Convert MB to bytes

        result = validator.is_small_table(small_table, validator.size_threshold_bytes, size_bytes)

        assert result is expected

    def test_configuration_values_loaded(self, validator):
        """Test that configuration values are properly loaded."""
        # These should match the values in clustering_config.yaml
        assert validator.size_threshold_bytes == 1_073_741_824  # 1GB
        assert validator.test_size_threshold_bytes == 1_048_576  # 1MB
        assert validator.exempt_small_tables is True
