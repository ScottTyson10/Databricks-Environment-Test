"""Table specifications for placeholder text detection scenarios.

Contains test table specs for:
- Table comments must not be placeholder text
"""

from tests.fixtures.table_factory import TestTableSpec

# Predefined test table specifications for "Table comments must not be placeholder text" scenario
TABLE_SPECS_PLACEHOLDER_DETECTION = {
    "todo_placeholder": TestTableSpec(name="placeholder_test_todo", comment="TODO", expected_pass=False),
    "fixme_placeholder": TestTableSpec(name="placeholder_test_fixme", comment="FIXME", expected_pass=False),
    "tbd_placeholder": TestTableSpec(name="placeholder_test_tbd", comment="TBD", expected_pass=False),
    "xxx_placeholder": TestTableSpec(name="placeholder_test_xxx", comment="XXX", expected_pass=False),
    "hack_placeholder": TestTableSpec(name="placeholder_test_hack", comment="HACK", expected_pass=False),
    "placeholder_placeholder": TestTableSpec(
        name="placeholder_test_placeholder", comment="PLACEHOLDER", expected_pass=False
    ),
    "temp_placeholder": TestTableSpec(name="placeholder_test_temp", comment="TEMP", expected_pass=False),
    "na_placeholder": TestTableSpec(name="placeholder_test_na", comment="N/A", expected_pass=False),
    "todo_with_description": TestTableSpec(
        name="placeholder_test_todo_desc", comment="TODO: Add proper documentation", expected_pass=False
    ),
    "fixme_with_description": TestTableSpec(
        name="placeholder_test_fixme_desc", comment="FIXME: Update this comment", expected_pass=False
    ),
    "case_variations": TestTableSpec(name="placeholder_test_case", comment="todo", expected_pass=False),
    "valid_comment": TestTableSpec(
        name="placeholder_test_valid", comment="User authentication and session management table", expected_pass=True
    ),
    "valid_with_similar_words": TestTableSpec(
        name="placeholder_test_similar", comment="Product catalog with pricing information", expected_pass=True
    ),
    "none_comment": TestTableSpec(
        name="placeholder_test_none", comment=None, expected_pass=True  # None is not a placeholder
    ),
    "empty_comment": TestTableSpec(
        name="placeholder_test_empty", comment="", expected_pass=True  # Empty is not a placeholder
    ),
}
