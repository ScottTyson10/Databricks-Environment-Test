"""Table specifications for column coverage threshold scenarios.

Contains test table specs for:
- Column documentation must meet 80% threshold

Based on research: research/documentation/column_coverage_threshold/COLUMN_COVERAGE_THRESHOLD_FEASIBILITY_CHECK.md
"""

from tests.fixtures.table_factory import TestTableSpecWithColumns

# Column Coverage Threshold Test Specifications
TABLE_SPECS_COLUMN_COVERAGE_THRESHOLD = {
    # Edge cases
    "zero_columns": TestTableSpecWithColumns(
        name="coverage_test_zero_columns",
        comment="Test table with zero columns for coverage threshold validation",
        columns=[],
        expected_pass=True,  # 0 columns = vacuously true = 100% compliant
    ),
    "single_documented": TestTableSpecWithColumns(
        name="coverage_test_single_documented",
        comment="Test table with single documented column",
        columns=[
            ("col1", "STRING", "This column is documented"),
        ],
        expected_pass=True,  # 1/1 = 100%
    ),
    "single_undocumented": TestTableSpecWithColumns(
        name="coverage_test_single_undocumented",
        comment="Test table with single undocumented column",
        columns=[
            ("col1", "STRING", None),
        ],
        expected_pass=False,  # 0/1 = 0%
    ),
    # Percentage variations
    "zero_percent": TestTableSpecWithColumns(
        name="coverage_test_0_percent",
        comment="Test table with 0% column documentation coverage",
        columns=[
            ("col1", "INT", None),
            ("col2", "STRING", None),
            ("col3", "FLOAT", None),
            ("col4", "BOOLEAN", None),
        ],
        expected_pass=False,  # 0/4 = 0%
    ),
    "fifty_percent": TestTableSpecWithColumns(
        name="coverage_test_50_percent",
        comment="Test table with 50% column documentation coverage",
        columns=[
            ("col1", "INT", "Documented column 1"),
            ("col2", "STRING", None),
            ("col3", "FLOAT", "Documented column 3"),
            ("col4", "BOOLEAN", None),
        ],
        expected_pass=False,  # 2/4 = 50%
    ),
    # Boundary conditions around 80% threshold
    "seventy_nine_percent": TestTableSpecWithColumns(
        name="coverage_test_79_percent",
        comment="Test table with ~79% column documentation coverage (just below threshold)",
        columns=[
            ("col1", "STRING", "Doc 1"),
            ("col2", "STRING", "Doc 2"),
            ("col3", "STRING", "Doc 3"),
            ("col4", "STRING", "Doc 4"),
            ("col5", "STRING", "Doc 5"),
            ("col6", "STRING", "Doc 6"),
            ("col7", "STRING", "Doc 7"),
            ("col8", "STRING", "Doc 8"),
            ("col9", "STRING", "Doc 9"),
            ("col10", "STRING", "Doc 10"),
            ("col11", "STRING", "Doc 11"),
            ("col12", "STRING", "Doc 12"),
            ("col13", "STRING", "Doc 13"),
            ("col14", "STRING", "Doc 14"),
            ("col15", "STRING", "Doc 15"),
            ("col16", "STRING", "Doc 16"),
            ("col17", "STRING", "Doc 17"),
            ("col18", "STRING", "Doc 18"),
            ("col19", "STRING", "Doc 19"),
            ("col20", "STRING", None),  # 19/20 = 95%
            ("col21", "STRING", None),  # 19/21 = 90.48%
            ("col22", "STRING", None),  # 19/22 = 86.36%
            ("col23", "STRING", None),  # 19/23 = 82.61%
            ("col24", "STRING", None),  # 19/24 = 79.17% (just below 80%)
        ],
        expected_pass=False,  # 19/24 = 79.17% (just below 80% threshold)
    ),
    "eighty_percent": TestTableSpecWithColumns(
        name="coverage_test_80_percent",
        comment="Test table with exactly 80% column documentation coverage (at threshold)",
        columns=[
            ("col1", "INT", "Column 1 documentation"),
            ("col2", "STRING", "Column 2 documentation"),
            ("col3", "FLOAT", "Column 3 documentation"),
            ("col4", "BOOLEAN", "Column 4 documentation"),
            ("col5", "DATE", None),  # Undocumented
        ],
        expected_pass=True,  # 4/5 = 80%
    ),
    "eighty_one_percent": TestTableSpecWithColumns(
        name="coverage_test_81_percent",
        comment="Test table with ~81% column documentation coverage (just above threshold)",
        columns=[
            ("col1", "STRING", "Doc 1"),
            ("col2", "STRING", "Doc 2"),
            ("col3", "STRING", "Doc 3"),
            ("col4", "STRING", "Doc 4"),
            ("col5", "STRING", "Doc 5"),
            ("col6", "STRING", "Doc 6"),
            ("col7", "STRING", "Doc 7"),
            ("col8", "STRING", "Doc 8"),
            ("col9", "STRING", "Doc 9"),
            ("col10", "STRING", "Doc 10"),
            ("col11", "STRING", "Doc 11"),
            ("col12", "STRING", "Doc 12"),
            ("col13", "STRING", "Doc 13"),
            ("col14", "STRING", "Doc 14"),
            ("col15", "STRING", "Doc 15"),
            ("col16", "STRING", "Doc 16"),
            ("col17", "STRING", "Doc 17"),
            ("col18", "STRING", "Doc 18"),
            ("col19", "STRING", "Doc 19"),
            ("col20", "STRING", "Doc 20"),
            ("col21", "STRING", "Doc 21"),
            ("col22", "STRING", None),  # 21/22 = 95.45%
            ("col23", "STRING", None),  # 21/23 = 91.30%
            ("col24", "STRING", None),  # 21/24 = 87.50%
            ("col25", "STRING", None),  # 21/25 = 84%
            ("col26", "STRING", None),  # 21/26 = 80.77%
        ],
        expected_pass=True,  # 21/26 = 80.77% (just above 80%)
    ),
    "hundred_percent": TestTableSpecWithColumns(
        name="coverage_test_100_percent",
        comment="Test table with 100% column documentation coverage",
        columns=[
            ("col1", "INT", "Fully documented column 1"),
            ("col2", "STRING", "Fully documented column 2"),
            ("col3", "FLOAT", "Fully documented column 3"),
            ("col4", "BOOLEAN", "Fully documented column 4"),
        ],
        expected_pass=True,  # 4/4 = 100%
    ),
    # Whitespace handling
    "whitespace_comments": TestTableSpecWithColumns(
        name="coverage_test_whitespace",
        comment="Test table with various whitespace comment scenarios",
        columns=[
            ("good_col", "STRING", "Valid documentation"),
            ("empty_col", "STRING", ""),  # Empty string
            ("space_col", "STRING", "   "),  # Whitespace only
            ("none_col", "STRING", None),  # None
            ("tab_col", "STRING", "\t\n  "),  # Tabs and newlines
        ],
        expected_pass=False,  # 1/5 = 20% (only good_col counts)
    ),
}
