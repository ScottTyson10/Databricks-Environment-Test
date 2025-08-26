"""Table specifications for table comment scenarios.

Contains test table specs for:
- Tables must have a comment
- Table comments must be at least 10 characters
"""

from tests.fixtures.table_factory import TestTableSpec

# Predefined test table specifications for "Tables must have a comment" scenario
TABLE_SPECS_HAS_COMMENT = {
    "with_comment": TestTableSpec(
        name="test_table_with_comment", comment="This table has a valid comment for testing", expected_pass=True
    ),
    "without_comment": TestTableSpec(name="test_table_without_comment", comment=None, expected_pass=False),
    "empty_comment": TestTableSpec(name="test_table_empty_comment", comment="", expected_pass=False),
    "whitespace_comment": TestTableSpec(
        name="test_table_whitespace_comment", comment="   \n\t   ", expected_pass=False
    ),
}

# Predefined test table specifications for "Comments must be at least 10 characters" scenario
TABLE_SPECS_COMMENT_LENGTH = {
    "long_comment": TestTableSpec(
        name="length_test_long_comment",
        comment="This is a sufficiently long comment that meets the minimum length requirement",
        expected_pass=True,
    ),
    "exactly_10_chars": TestTableSpec(name="length_test_exactly_10", comment="TenCharact", expected_pass=True),
    "exactly_9_chars": TestTableSpec(name="length_test_exactly_9", comment="Nine char", expected_pass=False),
    "short_comment": TestTableSpec(name="length_test_short", comment="Short", expected_pass=False),
    "unicode_comment": TestTableSpec(
        name="length_test_unicode", comment="Test🚀🎯💻🔥🌟⭐", expected_pass=True  # 12 chars with Unicode
    ),
    "whitespace_10_chars": TestTableSpec(
        name="length_test_whitespace", comment="  test    ", expected_pass=True  # 10 chars including spaces
    ),
    "none_comment": TestTableSpec(name="length_test_none", comment=None, expected_pass=False),
    "empty_comment": TestTableSpec(name="length_test_empty", comment="", expected_pass=False),
}
