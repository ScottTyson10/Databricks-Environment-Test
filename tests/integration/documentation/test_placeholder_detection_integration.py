"""Integration tests for placeholder text detection in table comments.

Layer 2: Integration Tests that work with real Databricks tables.
Tests the "Table comments must not be placeholder text" scenario end-to-end.
"""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

from tests.fixtures.documentation.placeholder_detection_specs import TABLE_SPECS_PLACEHOLDER_DETECTION
from tests.fixtures.table_factory import create_test_tables_for_placeholder_detection_scenario
from tests.utils.discovery_engine import create_integration_discovery
from tests.validators.documentation import DocumentationValidator

# Load environment variables
load_dotenv()


# Test data setup
@pytest.fixture(scope="class")
def databricks_client():
    """Class-scoped Databricks client fixture."""
    from databricks.sdk import WorkspaceClient

    return WorkspaceClient()


@pytest.fixture(scope="class")
@pytest.mark.skipif(
    os.getenv("CREATE_TEST_TABLES") != "true", reason="Integration tests require CREATE_TEST_TABLES=true"
)
def placeholder_detection_test_tables(databricks_client):
    """Class-scoped test tables - create for each test class, cleanup after."""
    with create_test_tables_for_placeholder_detection_scenario(databricks_client) as created_tables:
        yield created_tables


@pytest.fixture(scope="class")
def validator():
    """Documentation validator fixture - reused across all tests in a class."""
    return DocumentationValidator()


@pytest.fixture(scope="class")
def integration_discovery(databricks_client):
    """Discovery engine configured for integration testing - reused across all tests in a class."""
    return create_integration_discovery(databricks_client)


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("CREATE_TEST_TABLES") != "true", reason="Integration tests require CREATE_TEST_TABLES=true"
)
class TestPlaceholderDetectionIntegration:
    """Integration tests for placeholder text detection.

    Tests the "Table comments must not be placeholder text" scenario end-to-end with real Databricks tables.
    """

    def _get_table_by_fixture_key(self, fixture_dict, key, discovered_tables):
        """Helper to get a table by fixture key from discovered tables."""
        table_name = fixture_dict[key]
        for table in discovered_tables:
            if table.full_name == table_name:
                return table
        return None

    def test_end_to_end_placeholder_detection_validation(
        self, placeholder_detection_test_tables, validator, integration_discovery
    ):
        """Test complete end-to-end flow: create → discover → validate placeholder detection."""
        # Verify we created the expected tables
        expected_count = len(TABLE_SPECS_PLACEHOLDER_DETECTION)
        assert (
            len(placeholder_detection_test_tables) == expected_count
        ), f"Expected {expected_count} tables, created {len(placeholder_detection_test_tables)}"

        # Discover the tables we just created
        discovered_tables = integration_discovery.discover_tables()

        # Filter to only our placeholder test tables
        discovered_placeholder_tables = [
            table for table in discovered_tables if table.table.startswith("placeholder_test_")
        ]

        # Should have discovered all our test tables
        assert (
            len(discovered_placeholder_tables) == expected_count
        ), f"Expected {expected_count} tables, found {len(discovered_placeholder_tables)}"

        # Validate each discovered table for placeholder detection
        placeholder_results = {}
        for table in discovered_placeholder_tables:
            validation_result = validator.has_placeholder_comment(table)
            placeholder_results[table.table] = validation_result

        # Check placeholder detection results match expectations
        expected_placeholder_results = {
            "placeholder_test_todo": True,  # TODO is placeholder
            "placeholder_test_fixme": True,  # FIXME is placeholder
            "placeholder_test_tbd": True,  # TBD is placeholder
            "placeholder_test_xxx": True,  # XXX is placeholder
            "placeholder_test_hack": True,  # HACK is placeholder
            "placeholder_test_placeholder": True,  # PLACEHOLDER is placeholder
            "placeholder_test_temp": True,  # TEMP is placeholder
            "placeholder_test_na": True,  # N/A is placeholder
            "placeholder_test_todo_desc": True,  # TODO: description is placeholder
            "placeholder_test_fixme_desc": True,  # FIXME: description is placeholder
            "placeholder_test_case": True,  # Case variation (todo) is placeholder
            "placeholder_test_valid": False,  # Valid comment is not placeholder
            "placeholder_test_similar": False,  # Valid comment with similar words is not placeholder
            "placeholder_test_none": False,  # None comment is not placeholder
            "placeholder_test_empty": False,  # Empty comment is not placeholder
        }

        assert (
            placeholder_results == expected_placeholder_results
        ), f"Placeholder validation results mismatch: {placeholder_results}"

    def test_standard_placeholder_patterns_integration(
        self, placeholder_detection_test_tables, validator, integration_discovery
    ):
        """Test detection of standard placeholder patterns with real Databricks tables."""
        discovered_tables = integration_discovery.discover_tables()

        # Test each standard placeholder pattern
        standard_patterns = ["todo", "fixme", "tbd", "xxx", "hack", "placeholder", "temp", "na"]

        for pattern in standard_patterns:
            # Find the table for this pattern
            pattern_table = self._get_table_by_fixture_key(
                placeholder_detection_test_tables, f"{pattern}_placeholder", discovered_tables
            )

            assert pattern_table is not None, f"Should find test table for pattern: {pattern}"
            assert validator.has_placeholder_comment(pattern_table) is True, f"Should detect '{pattern}' as placeholder"

    def test_valid_comments_not_flagged_integration(
        self, placeholder_detection_test_tables, validator, integration_discovery
    ):
        """Test that valid documentation comments are not flagged as placeholders in integration environment."""
        discovered_tables = integration_discovery.discover_tables()

        # Test valid comments
        valid_keys = ["valid_comment", "valid_with_similar_words"]

        for key in valid_keys:
            table = self._get_table_by_fixture_key(placeholder_detection_test_tables, key, discovered_tables)
            assert table is not None, f"Should find test table for key: {key}"
            assert (
                validator.has_placeholder_comment(table) is False
            ), f"Should NOT flag valid comment as placeholder: {table.comment}"

    def test_case_insensitive_detection_integration(
        self, placeholder_detection_test_tables, validator, integration_discovery
    ):
        """Test that placeholder detection is case-insensitive in integration environment."""
        discovered_tables = integration_discovery.discover_tables()

        # Test case variation (lowercase "todo")
        case_table = self._get_table_by_fixture_key(
            placeholder_detection_test_tables, "case_variations", discovered_tables
        )

        assert case_table is not None, "Should find case variation test table"
        assert case_table.comment == "todo", f"Expected lowercase 'todo', got: {case_table.comment}"
        assert validator.has_placeholder_comment(case_table) is True, "Should detect lowercase 'todo' as placeholder"

    def test_placeholder_with_descriptions_integration(
        self, placeholder_detection_test_tables, validator, integration_discovery
    ):
        """Test that placeholders with descriptions are still detected as placeholders."""
        discovered_tables = integration_discovery.discover_tables()

        # Test TODO with description
        todo_desc_table = self._get_table_by_fixture_key(
            placeholder_detection_test_tables, "todo_with_description", discovered_tables
        )

        assert todo_desc_table is not None, "Should find TODO description test table"
        assert (
            todo_desc_table.comment == "TODO: Add proper documentation"
        ), f"Unexpected comment: {todo_desc_table.comment}"
        assert (
            validator.has_placeholder_comment(todo_desc_table) is True
        ), "Should detect 'TODO: description' as placeholder"

        # Test FIXME with description
        fixme_desc_table = self._get_table_by_fixture_key(
            placeholder_detection_test_tables, "fixme_with_description", discovered_tables
        )

        assert fixme_desc_table is not None, "Should find FIXME description test table"
        assert (
            fixme_desc_table.comment == "FIXME: Update this comment"
        ), f"Unexpected comment: {fixme_desc_table.comment}"
        assert (
            validator.has_placeholder_comment(fixme_desc_table) is True
        ), "Should detect 'FIXME: description' as placeholder"

    def test_none_and_empty_comments_not_placeholders_integration(
        self, placeholder_detection_test_tables, validator, integration_discovery
    ):
        """Test that None and empty comments are not flagged as placeholders in integration environment."""
        discovered_tables = integration_discovery.discover_tables()

        # Test None comment
        none_table = self._get_table_by_fixture_key(
            placeholder_detection_test_tables, "none_comment", discovered_tables
        )

        assert none_table is not None, "Should find None comment test table"
        assert none_table.comment is None, "Comment should be None"
        assert (
            validator.has_placeholder_comment(none_table) is False
        ), "None comment should not be flagged as placeholder"

        # Test empty comment (Databricks converts empty strings to None)
        empty_table = self._get_table_by_fixture_key(
            placeholder_detection_test_tables, "empty_comment", discovered_tables
        )

        assert empty_table is not None, "Should find empty comment test table"
        # NOTE: Databricks converts empty string comments to None when stored
        assert empty_table.comment is None, "Comment should be None (Databricks converts empty strings to None)"
        assert (
            validator.has_placeholder_comment(empty_table) is False
        ), "Empty comment should not be flagged as placeholder"

    @pytest.mark.parametrize(
        "fixture_key,expected_is_placeholder",
        [
            ("todo_placeholder", True),
            ("fixme_placeholder", True),
            ("tbd_placeholder", True),
            ("xxx_placeholder", True),
            ("hack_placeholder", True),
            ("placeholder_placeholder", True),
            ("temp_placeholder", True),
            ("na_placeholder", True),
            ("todo_with_description", True),
            ("fixme_with_description", True),
            ("case_variations", True),
            ("valid_comment", False),
            ("valid_with_similar_words", False),
            ("none_comment", False),
            ("empty_comment", False),
        ],
    )
    def test_individual_placeholder_validation_parametrized(
        self, placeholder_detection_test_tables, validator, integration_discovery, fixture_key, expected_is_placeholder
    ):
        """Test validation of individual placeholder detection tables using parametrize."""
        # Use the fixture to get the specific table
        target_table = self._get_table_by_fixture_key(
            placeholder_detection_test_tables, fixture_key, integration_discovery.discover_tables()
        )

        assert target_table is not None, f"Could not find test table for fixture key: {fixture_key}"

        # Validate the table
        result = validator.has_placeholder_comment(target_table)
        assert (
            result is expected_is_placeholder
        ), f"Table {target_table.full_name} placeholder detection mismatch. Expected {expected_is_placeholder}, got {result}. Comment: '{target_table.comment}'"

    def test_placeholder_vs_other_validations_independence_integration(
        self, placeholder_detection_test_tables, validator, integration_discovery
    ):
        """Test that placeholder validation is independent of other validations in integration environment."""
        discovered_tables = integration_discovery.discover_tables()

        # A long placeholder comment should pass length validation but fail placeholder validation
        todo_desc_table = self._get_table_by_fixture_key(
            placeholder_detection_test_tables, "todo_with_description", discovered_tables
        )

        assert validator.has_comment(todo_desc_table) is True  # Has content
        assert validator.has_minimum_length(todo_desc_table) is True  # Long enough (>10 chars)
        assert validator.has_placeholder_comment(todo_desc_table) is True  # But is placeholder

        # A short valid comment should pass comment and placeholder validation but fail length validation
        # Note: Our valid comments are all long enough, so let's test a standard pattern instead
        temp_table = self._get_table_by_fixture_key(
            placeholder_detection_test_tables, "temp_placeholder", discovered_tables
        )

        assert validator.has_comment(temp_table) is True  # Has content
        assert validator.has_minimum_length(temp_table) is False  # Too short (4 chars)
        assert validator.has_placeholder_comment(temp_table) is True  # Is placeholder

        # None comment fails all validations
        none_table = self._get_table_by_fixture_key(
            placeholder_detection_test_tables, "none_comment", discovered_tables
        )

        assert validator.has_comment(none_table) is False
        assert validator.has_minimum_length(none_table) is False
        assert validator.has_placeholder_comment(none_table) is False

    def test_discovery_finds_all_placeholder_test_tables(
        self, placeholder_detection_test_tables, integration_discovery
    ):
        """Test that discovery engine finds all our placeholder detection test tables."""
        # Verify tables were created
        expected_count = len(TABLE_SPECS_PLACEHOLDER_DETECTION)
        assert len(placeholder_detection_test_tables) == expected_count, "Should have created all test tables"

        discovered_tables = integration_discovery.discover_tables()
        # Should find all placeholder test tables in pytest_test_data schema
        placeholder_test_tables = [table for table in discovered_tables if table.table.startswith("placeholder_test_")]

        assert (
            len(placeholder_test_tables) == expected_count
        ), f"Discovery should find all {expected_count} placeholder test tables, found {len(placeholder_test_tables)}"
