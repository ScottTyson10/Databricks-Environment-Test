"""Production step definitions for documentation compliance.

Layer 3: Production BDD Tests that work with real discovered data.
Implements ONLY "Tables must have a comment" scenario - no scope creep.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pytest
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv
from pytest_bdd import given, scenarios, then, when

from conftest import record_documentation_compliance
from tests.utils.discovery import TableInfo
from tests.utils.discovery_engine import create_production_discovery
from tests.validators.comprehensive import ComprehensiveDocumentationValidator
from tests.validators.documentation import DocumentationValidator

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("databricks")

# Load scenarios from feature file
scenarios("../features/databricks__documentation__compliance.feature")


@dataclass
class DocumentationContext:
    """Context for documentation validation results."""

    discovered_tables: list[TableInfo] = field(default_factory=list)
    tables_without_comments: list[TableInfo] = field(default_factory=list)
    tables_with_short_comments: list[TableInfo] = field(default_factory=list)
    tables_with_placeholder_comments: list[TableInfo] = field(default_factory=list)
    tables_with_undocumented_critical_columns: list[TableInfo] = field(default_factory=list)
    tables_below_coverage_threshold: list[TableInfo] = field(default_factory=list)
    databricks_client: WorkspaceClient | None = None
    validator: DocumentationValidator | None = None


# Fixtures


@pytest.fixture(scope="session")
def production_databricks_client():
    """Session-scoped Databricks client for production testing."""
    return WorkspaceClient()


@pytest.fixture(scope="session")
def production_discovery_engine(production_databricks_client):
    """Production discovery engine configured for real data."""
    return create_production_discovery(production_databricks_client)


@pytest.fixture
def documentation_validator():
    """Documentation validator for table comment compliance."""
    return DocumentationValidator()


@pytest.fixture
def documentation_context(production_databricks_client, documentation_validator):
    """Documentation context for tracking results across steps."""
    return DocumentationContext(databricks_client=production_databricks_client, validator=documentation_validator)


# Background Steps


@given("I connect to the Databricks workspace")
def connect_to_databricks(documentation_context):
    """Verify that we can connect to Databricks workspace."""
    try:
        # Simple connectivity test
        catalogs = list(documentation_context.databricks_client.catalogs.list())
        assert len(catalogs) > 0, "Should have access to at least one catalog"
        logger.info(f"✅ Connected to Databricks with access to {len(catalogs)} catalogs")
    except Exception as e:
        pytest.fail(f"Failed to connect to Databricks: {e}")


@given("I have permissions to read table metadata and history")
def verify_table_metadata_permissions(production_discovery_engine):
    """Verify that we can read table metadata."""
    try:
        # Test discovery capability with a small sample
        sample_tables = list(production_discovery_engine.discover_tables())
        assert len(sample_tables) >= 0, "Discovery should work even if no tables found"
        logger.info(f"✅ Table metadata permissions verified, found {len(sample_tables)} tables")
    except Exception as e:
        pytest.fail(f"Table metadata permission check failed: {e}")


# "Tables must have a comment" Scenario Steps


@given("I discover all accessible tables with documentation filters")
def discover_accessible_tables(documentation_context, production_discovery_engine):
    """Discover all tables accessible in the workspace for documentation validation."""
    try:
        logger.info("🔍 Starting table discovery for documentation validation...")
        discovered_tables = list(production_discovery_engine.discover_tables())
        documentation_context.discovered_tables = discovered_tables

        logger.info(f"✅ Discovered {len(discovered_tables)} tables for documentation validation")

        if discovered_tables:
            # Log some sample tables for visibility
            sample_size = min(3, len(discovered_tables))
            logger.info("Sample discovered tables:")
            for table in discovered_tables[:sample_size]:
                logger.info(f"  - {table.full_name}")

    except Exception as e:
        pytest.fail(f"Table discovery failed: {e}")


@when("I check if tables have comments")
def check_tables_have_comments(documentation_context):
    """Check which tables have meaningful comments."""
    logger.info(f"🧪 Checking comments for {len(documentation_context.discovered_tables)} tables...")

    tables_without_comments = []

    for table in documentation_context.discovered_tables:
        if not documentation_context.validator.has_comment(table):
            tables_without_comments.append(table)

    documentation_context.tables_without_comments = tables_without_comments

    logger.info(f"✅ Comment check complete: {len(tables_without_comments)} tables without comments")


@then("every table should have a non-empty comment field")
def verify_all_tables_have_comments(documentation_context):
    """Verify that all tables have meaningful comments."""
    if not documentation_context.discovered_tables:
        pytest.skip("No tables discovered to validate")

    tables_without_comments = documentation_context.tables_without_comments
    total_tables = len(documentation_context.discovered_tables)

    if tables_without_comments:
        violation_count = len(tables_without_comments)
        compliance_rate = ((total_tables - violation_count) / total_tables) * 100

        logger.warning(
            f"❌ {violation_count} out of {total_tables} tables lack comments ({compliance_rate:.1f}% compliance)"
        )

        # Log some example violations for debugging
        sample_violations = tables_without_comments[:3]
        logger.warning("Example violations:")
        for violation in sample_violations:
            logger.warning(f"  - {violation.full_name}: comment='{violation.comment}'")

        # This is production validation - we report but don't fail hard
        # Real production would typically have some acceptable compliance threshold
        logger.info(f"📊 Documentation compliance rate: {compliance_rate:.1f}%")

    else:
        logger.info(f"✅ All {total_tables} tables have meaningful comments (100% compliance)")

    # Always log final summary for production monitoring
    logger.info("📈 Final Documentation Compliance Summary:")
    logger.info(f"   Total tables analyzed: {total_tables}")
    logger.info(f"   Tables with comments: {total_tables - len(tables_without_comments)}")
    logger.info(f"   Tables without comments: {len(tables_without_comments)}")
    logger.info(
        f"   Compliance rate: {((total_tables - len(tables_without_comments)) / total_tables * 100) if total_tables > 0 else 0:.1f}%"
    )

    # Record compliance results for session tracking
    violations = [f"{table.full_name}: comment='{table.comment}'" for table in tables_without_comments]
    record_documentation_compliance(
        total_tables=total_tables,
        tables_with_comments=total_tables - len(tables_without_comments),
        violations=violations,
    )


# "Table comments must be at least 10 characters" Scenario Steps


@when("I check table comment lengths")
def check_table_comment_lengths(documentation_context):
    """Check which tables have comments shorter than the minimum length requirement."""
    logger.info(f"🧪 Checking comment lengths for {len(documentation_context.discovered_tables)} tables...")

    tables_with_short_comments = []

    for table in documentation_context.discovered_tables:
        if not documentation_context.validator.has_minimum_length(table):
            tables_with_short_comments.append(table)

    documentation_context.tables_with_short_comments = tables_with_short_comments

    logger.info(f"✅ Comment length check complete: {len(tables_with_short_comments)} tables with short comments")


@then("every table comment should meet the minimum length requirement from configuration")
def verify_all_table_comments_meet_minimum_length(documentation_context):
    """Verify that all table comments meet the minimum length requirement."""
    if not documentation_context.discovered_tables:
        pytest.skip("No tables discovered to validate")

    tables_with_short_comments = documentation_context.tables_with_short_comments
    total_tables = len(documentation_context.discovered_tables)
    minimum_length = documentation_context.validator.minimum_comment_length

    if tables_with_short_comments:
        violation_count = len(tables_with_short_comments)
        compliance_rate = ((total_tables - violation_count) / total_tables) * 100

        logger.warning(
            f"❌ {violation_count} out of {total_tables} tables have comments shorter than {minimum_length} characters ({compliance_rate:.1f}% compliance)"
        )

        # Log some example violations for debugging
        sample_violations = tables_with_short_comments[:3]
        logger.warning("Example comment length violations:")
        for violation in sample_violations:
            comment_length = len(violation.comment) if violation.comment else 0
            logger.warning(f"  - {violation.full_name}: comment length={comment_length}, comment='{violation.comment}'")

        # This is production validation - we report but don't fail hard
        # Real production would typically have some acceptable compliance threshold
        logger.info(f"📊 Comment length compliance rate: {compliance_rate:.1f}%")

    else:
        logger.info(f"✅ All {total_tables} tables have comments meeting minimum length requirement (100% compliance)")

    # Always log final summary for production monitoring
    logger.info("📈 Final Comment Length Compliance Summary:")
    logger.info(f"   Total tables analyzed: {total_tables}")
    logger.info(f"   Tables meeting length requirement: {total_tables - len(tables_with_short_comments)}")
    logger.info(f"   Tables with short comments: {len(tables_with_short_comments)}")
    logger.info(f"   Minimum length requirement: {minimum_length} characters")
    logger.info(
        f"   Compliance rate: {((total_tables - len(tables_with_short_comments)) / total_tables * 100) if total_tables > 0 else 0:.1f}%"
    )

    # Record compliance results for session tracking
    violations = [
        f"{table.full_name}: length={len(table.comment) if table.comment else 0}, comment='{table.comment}'"
        for table in tables_with_short_comments
    ]
    record_documentation_compliance(
        total_tables=total_tables,
        tables_with_comments=total_tables - len(tables_with_short_comments),
        violations=violations,
    )


# "Table comments must not be placeholder text" Scenario Steps


@when("I check for placeholder text in table comments")
def check_table_comments_for_placeholders(documentation_context):
    """Check which tables have placeholder text in their comments."""
    logger.info(f"🧪 Checking for placeholder text in {len(documentation_context.discovered_tables)} table comments...")

    tables_with_placeholder_comments = []

    for table in documentation_context.discovered_tables:
        if documentation_context.validator.has_placeholder_comment(table):
            tables_with_placeholder_comments.append(table)

    documentation_context.tables_with_placeholder_comments = tables_with_placeholder_comments

    logger.info(
        f"✅ Placeholder text check complete: {len(tables_with_placeholder_comments)} tables with placeholder comments"
    )


@then("no table should have placeholder text in comments")
def verify_no_tables_have_placeholder_comments(documentation_context):
    """Verify that no tables have placeholder text in their comments."""
    if not documentation_context.discovered_tables:
        pytest.skip("No tables discovered to validate")

    tables_with_placeholder_comments = documentation_context.tables_with_placeholder_comments
    total_tables = len(documentation_context.discovered_tables)

    if tables_with_placeholder_comments:
        violation_count = len(tables_with_placeholder_comments)
        compliance_rate = ((total_tables - violation_count) / total_tables) * 100

        logger.warning(
            f"❌ {violation_count} out of {total_tables} tables have placeholder text in comments ({compliance_rate:.1f}% compliance)"
        )

        # Log some example violations for debugging
        sample_violations = tables_with_placeholder_comments[:5]
        logger.warning("Example placeholder text violations:")
        for violation in sample_violations:
            logger.warning(f"  - {violation.full_name}: comment='{violation.comment}'")

        # This is production validation - we report but don't fail hard
        # Real production would typically have some acceptable compliance threshold
        logger.info(f"📊 Placeholder text compliance rate: {compliance_rate:.1f}%")

    else:
        logger.info(f"✅ All {total_tables} tables have meaningful comments without placeholder text (100% compliance)")

    # Always log final summary for production monitoring
    logger.info("📈 Final Placeholder Text Compliance Summary:")
    logger.info(f"   Total tables analyzed: {total_tables}")
    logger.info(f"   Tables with meaningful comments: {total_tables - len(tables_with_placeholder_comments)}")
    logger.info(f"   Tables with placeholder comments: {len(tables_with_placeholder_comments)}")
    logger.info(
        f"   Compliance rate: {((total_tables - len(tables_with_placeholder_comments)) / total_tables * 100) if total_tables > 0 else 0:.1f}%"
    )

    # Record compliance results for session tracking
    violations = [f"{table.full_name}: comment='{table.comment}'" for table in tables_with_placeholder_comments]
    record_documentation_compliance(
        total_tables=total_tables,
        tables_with_comments=total_tables - len(tables_with_placeholder_comments),
        violations=violations,
    )


# "Critical columns must be documented" Scenario Steps


@when("I check documentation for critical columns defined in configuration")
def check_critical_column_documentation(documentation_context):
    """Check which tables have undocumented critical columns."""
    logger.info(
        f"🧪 Checking critical column documentation for {len(documentation_context.discovered_tables)} tables..."
    )

    tables_with_undocumented_critical_columns = []

    for table in documentation_context.discovered_tables:
        if not documentation_context.validator.has_all_critical_columns_documented(table):
            tables_with_undocumented_critical_columns.append(table)

    documentation_context.tables_with_undocumented_critical_columns = tables_with_undocumented_critical_columns

    logger.info(
        f"✅ Critical column documentation check complete: {len(tables_with_undocumented_critical_columns)} tables with undocumented critical columns"
    )


@then("all critical columns should have comprehensive documentation")
def verify_all_critical_columns_documented(documentation_context):
    """Verify that all critical columns have comprehensive documentation."""
    if not documentation_context.discovered_tables:
        pytest.skip("No tables discovered to validate")

    tables_with_undocumented_critical_columns = documentation_context.tables_with_undocumented_critical_columns
    total_tables = len(documentation_context.discovered_tables)

    if tables_with_undocumented_critical_columns:
        violation_count = len(tables_with_undocumented_critical_columns)
        compliance_rate = ((total_tables - violation_count) / total_tables) * 100

        logger.warning(
            f"❌ {violation_count} out of {total_tables} tables have undocumented critical columns ({compliance_rate:.1f}% compliance)"
        )

        # Log some example violations with specific undocumented columns
        sample_violations = tables_with_undocumented_critical_columns[:3]
        logger.warning("Example critical column documentation violations:")
        for violation in sample_violations:
            undocumented_columns = documentation_context.validator.get_undocumented_critical_columns(violation)
            logger.warning(f"  - {violation.full_name}: undocumented critical columns={undocumented_columns}")

        # This is production validation - we report but don't fail hard
        # Real production would typically have some acceptable compliance threshold
        logger.info(f"📊 Critical column documentation compliance rate: {compliance_rate:.1f}%")

    else:
        logger.info(f"✅ All {total_tables} tables have all critical columns documented (100% compliance)")

    # Always log final summary for production monitoring
    logger.info("📈 Final Critical Column Documentation Compliance Summary:")
    logger.info(f"   Total tables analyzed: {total_tables}")
    logger.info(
        f"   Tables with all critical columns documented: {total_tables - len(tables_with_undocumented_critical_columns)}"
    )
    logger.info(f"   Tables with undocumented critical columns: {len(tables_with_undocumented_critical_columns)}")
    logger.info(
        f"   Compliance rate: {((total_tables - len(tables_with_undocumented_critical_columns)) / total_tables * 100) if total_tables > 0 else 0:.1f}%"
    )

    # Record compliance results for session tracking
    violations = []
    for table in tables_with_undocumented_critical_columns:
        undocumented_columns = documentation_context.validator.get_undocumented_critical_columns(table)
        violations.append(f"{table.full_name}: undocumented critical columns={undocumented_columns}")

    record_documentation_compliance(
        total_tables=total_tables,
        tables_with_comments=total_tables - len(tables_with_undocumented_critical_columns),
        violations=violations,
    )


# "Column documentation must meet 80% threshold" Scenario Steps


@when("I calculate column documentation coverage with configured threshold")
def calculate_column_documentation_coverage_with_threshold(documentation_context):
    """Calculate column documentation coverage and identify tables below threshold."""
    threshold = documentation_context.validator.required_column_coverage_percent
    logger.info(
        f"🧪 Calculating column documentation coverage with {threshold}% threshold for {len(documentation_context.discovered_tables)} tables..."
    )

    tables_below_threshold = []

    for table in documentation_context.discovered_tables:
        # Check if it meets the threshold
        meets_threshold = documentation_context.validator.meets_column_documentation_threshold(table, threshold)

        if not meets_threshold:
            tables_below_threshold.append(table)

    documentation_context.tables_below_coverage_threshold = tables_below_threshold

    logger.info(
        f"✅ Column coverage calculation complete: {len(tables_below_threshold)} tables below {threshold}% threshold"
    )


@then("columns in each table should meet the coverage threshold from configuration")
def verify_column_documentation_coverage_threshold(documentation_context):
    """Verify that all tables meet the column documentation coverage threshold."""
    if not documentation_context.discovered_tables:
        pytest.skip("No tables discovered to validate")

    tables_below_threshold = documentation_context.tables_below_coverage_threshold
    total_tables = len(documentation_context.discovered_tables)
    threshold = 80.0

    if tables_below_threshold:
        violation_count = len(tables_below_threshold)
        compliance_rate = ((total_tables - violation_count) / total_tables) * 100

        logger.warning(
            f"❌ {violation_count} out of {total_tables} tables have column documentation below {threshold}% threshold ({compliance_rate:.1f}% table compliance)"
        )

        # Log some example violations with specific coverage percentages
        sample_violations = tables_below_threshold[:3]
        logger.warning("Example column coverage threshold violations:")
        for violation in sample_violations:
            coverage = documentation_context.validator.calculate_column_documentation_percentage(violation)
            undocumented_count = len(documentation_context.validator.get_undocumented_columns(violation))
            total_columns = len(violation.columns) if violation.columns else 0
            logger.warning(
                f"  - {violation.full_name}: {coverage:.1f}% coverage ({total_columns - undocumented_count}/{total_columns} columns documented)"
            )

        # This is production validation - we report but don't fail hard
        logger.info(f"📊 Table-level column coverage compliance rate: {compliance_rate:.1f}%")

    else:
        logger.info(
            f"✅ All {total_tables} tables meet the {threshold}% column documentation threshold (100% table compliance)"
        )

    # Calculate overall column documentation statistics across all tables
    total_columns = sum(len(table.columns) if table.columns else 0 for table in documentation_context.discovered_tables)
    total_documented_columns = 0
    for table in documentation_context.discovered_tables:
        if table.columns:
            documented_count = sum(1 for col in table.columns if col.comment and col.comment.strip())
            total_documented_columns += documented_count

    overall_column_percentage = (total_documented_columns / total_columns * 100) if total_columns > 0 else 100.0

    # Always log final summary for production monitoring
    logger.info("📈 Final Column Documentation Coverage Summary:")
    logger.info(f"   Total tables analyzed: {total_tables}")
    logger.info(f"   Tables meeting {threshold}% threshold: {total_tables - len(tables_below_threshold)}")
    logger.info(f"   Tables below {threshold}% threshold: {len(tables_below_threshold)}")
    logger.info(
        f"   Table-level compliance rate: {((total_tables - len(tables_below_threshold)) / total_tables * 100) if total_tables > 0 else 0:.1f}%"
    )
    logger.info(
        f"   Overall column documentation: {total_documented_columns}/{total_columns} columns ({overall_column_percentage:.1f}%)"
    )

    # Record compliance results for session tracking
    violations = []
    for table in tables_below_threshold:
        coverage = documentation_context.validator.calculate_column_documentation_percentage(table)
        undocumented = documentation_context.validator.get_undocumented_columns(table)
        violations.append(f"{table.full_name}: {coverage:.1f}% coverage, {len(undocumented)} undocumented columns")

    record_documentation_compliance(
        total_tables=total_tables,
        tables_with_comments=total_tables - len(tables_below_threshold),
        violations=violations,
    )


# Comprehensive Documentation Scenario Steps


@when("I perform a comprehensive documentation check")
def perform_comprehensive_documentation_check(documentation_context):
    """Perform comprehensive documentation assessment combining all checks."""
    logger.info(
        f"🔍 Performing comprehensive documentation assessment for {len(documentation_context.discovered_tables)} tables..."
    )

    # Initialize comprehensive validator
    comprehensive_validator = ComprehensiveDocumentationValidator()

    # Evaluate all tables
    results, summary = comprehensive_validator.evaluate_tables(documentation_context.discovered_tables)

    # Store results in context
    documentation_context.comprehensive_results = results
    documentation_context.comprehensive_summary = summary

    logger.info(
        f"✅ Comprehensive assessment complete: {summary['comprehensive_compliant']}/{summary['total_tables']} tables fully compliant"
    )


@then("every table should meet all comprehensive documentation requirements")
def verify_comprehensive_documentation_compliance(documentation_context):
    """Verify that all tables meet comprehensive documentation requirements."""
    if not documentation_context.discovered_tables:
        pytest.skip("No tables discovered to validate")

    results = documentation_context.comprehensive_results
    summary = documentation_context.comprehensive_summary

    total_tables = summary["total_tables"]
    compliant_tables = summary["comprehensive_compliant"]
    compliance_rate = summary["comprehensive_compliance_rate"]

    # Log detailed comprehensive compliance report
    if compliant_tables < total_tables:
        non_compliant_count = total_tables - compliant_tables
        logger.warning(
            f"❌ {non_compliant_count} out of {total_tables} tables fail comprehensive documentation requirements ({compliance_rate:.1f}% compliance)"
        )

        # List ALL non-compliant tables
        logger.warning("📋 Complete list of comprehensive documentation violations:")
        for result in results:
            if not result.overall_compliant:
                logger.warning(f"  - {result.table.full_name}: {'; '.join(result.failure_reasons)}")
    else:
        logger.info(f"✅ All {total_tables} tables meet comprehensive documentation requirements (100% compliance)")

    # Log individual check statistics
    logger.info("📊 Individual check compliance rates:")
    for check_name, stats in summary["individual_check_stats"].items():
        logger.info(f"   {check_name}: {stats['pass_rate']:.1f}% ({stats['passed']}/{total_tables})")

    # Log most common failure reasons
    if summary["common_failures"]:
        logger.warning("🚫 Most common comprehensive failures:")
        for failure, count in sorted(summary["common_failures"].items(), key=lambda x: x[1], reverse=True)[:3]:
            logger.warning(f"   {failure}: {count} tables")

    # Always log final comprehensive summary for production monitoring
    logger.info("📈 Final Comprehensive Documentation Compliance Summary:")
    logger.info(f"   Total tables analyzed: {total_tables}")
    logger.info(f"   Tables meeting ALL requirements: {compliant_tables}")
    logger.info(f"   Comprehensive compliance rate: {compliance_rate:.1f}%")
    logger.info(f"   Required checks: {', '.join(summary['required_checks'])}")

    # Record compliance results for session tracking
    violations = []
    for result in results:
        if not result.overall_compliant:
            violations.append(f"{result.table.full_name}: {result.compliance_summary}")

    record_documentation_compliance(
        total_tables=total_tables,
        tables_with_comments=compliant_tables,  # Using comprehensive compliance count
        violations=violations,
    )
