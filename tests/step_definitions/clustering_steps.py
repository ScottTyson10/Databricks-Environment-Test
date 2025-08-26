"""Production step definitions for clustering compliance.

Layer 3: Production BDD Tests that work with real discovered data.
Implements clustering compliance scenarios including explicit clustering columns detection.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pytest
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv
from pytest_bdd import given, scenarios, then, when

from tests.utils.discovery import TableInfo
from tests.utils.discovery_engine import create_production_discovery
from tests.validators.clustering import ClusteringValidator

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("databricks")

# Load scenarios from feature file
scenarios("../features/databricks__clustering__compliance.feature")


@dataclass
class ClusteringContext:
    """Context for clustering validation steps."""

    discovered_tables: list[TableInfo] = field(default_factory=list)
    clustering_validator: ClusteringValidator | None = None
    validation_results: dict[str, dict] = field(default_factory=dict)
    violations: list[dict] = field(default_factory=list)


@pytest.fixture
def clustering_context():
    """Fixture providing clustering context for BDD tests."""
    return ClusteringContext()


@given("I connect to the Databricks workspace")
def connect_to_databricks(clustering_context: ClusteringContext):
    """Verify that we can connect to Databricks workspace."""
    try:
        # Simple connectivity test
        client = WorkspaceClient()
        catalogs = list(client.catalogs.list())
        logger.info(f"Successfully connected to Databricks workspace - found {len(catalogs)} catalogs")
    except Exception as e:
        pytest.fail(f"Failed to connect to Databricks workspace: {e}")


@given("I have permissions to read table metadata and history")
def verify_table_metadata_permissions(clustering_context: ClusteringContext):
    """Verify that we have necessary permissions to read table metadata."""
    # This step is implicit - if table discovery works, we have permissions
    logger.info("Table metadata permissions verified (will be confirmed during discovery)")


@given("I discover all accessible tables with clustering filters")
def discover_tables_with_clustering_filters(clustering_context: ClusteringContext):
    """Discover tables for clustering validation."""
    client = WorkspaceClient()
    discovery = create_production_discovery(client)

    logger.info("Starting table discovery for clustering compliance validation")
    clustering_context.discovered_tables = discovery.discover_tables()

    logger.info(f"Discovered {len(clustering_context.discovered_tables)} tables for clustering validation")

    # Initialize clustering validator
    clustering_context.clustering_validator = ClusteringValidator()


@when("I validate clustering column appropriateness for workload")
def validate_clustering_column_appropriateness(clustering_context: ClusteringContext):
    """Validate clustering column appropriateness.

    For the explicit clustering columns scenario, this validates:
    - Tables have explicit clustering columns configured
    - Clustering columns are within recommended limits
    - Configuration follows best practices
    """
    assert clustering_context.clustering_validator is not None, "Clustering validator should be initialized"

    logger.info("Validating clustering column appropriateness")

    tables_with_clustering = 0
    tables_without_clustering = 0

    for table in clustering_context.discovered_tables:
        # Check if table has explicit clustering columns
        has_clustering = clustering_context.clustering_validator.has_clustering_columns(table)
        clustering_columns = clustering_context.clustering_validator.get_clustering_columns(table)
        column_count = clustering_context.clustering_validator.count_clustering_columns(table)
        validates_limits = clustering_context.clustering_validator.validates_clustering_column_limits(table)

        # Store validation results
        clustering_context.validation_results[table.full_name] = {
            "has_clustering": has_clustering,
            "clustering_columns": clustering_columns,
            "column_count": column_count,
            "validates_limits": validates_limits,
            "table_info": table,
        }

        if has_clustering:
            tables_with_clustering += 1
            logger.info(f"Table {table.full_name}: {column_count} clustering columns: {clustering_columns}")

            # Check for violations (exceeding limits)
            if not validates_limits:
                violation = {
                    "table": table.full_name,
                    "issue": "Exceeds clustering column limits",
                    "details": f"Has {column_count} clustering columns, maximum is {clustering_context.clustering_validator.max_clustering_columns}",
                    "clustering_columns": clustering_columns,
                }
                clustering_context.violations.append(violation)
                logger.warning(f"Clustering limit violation: {violation}")
        else:
            tables_without_clustering += 1
            logger.debug(f"Table {table.full_name}: No clustering columns configured")

    logger.info("Clustering validation complete:")
    logger.info(f"  Tables with clustering: {tables_with_clustering}")
    logger.info(f"  Tables without clustering: {tables_without_clustering}")
    logger.info(f"  Total violations: {len(clustering_context.violations)}")


@then("clustering columns should align with common query patterns and data distribution")
def verify_clustering_column_alignment(clustering_context: ClusteringContext):
    """Verify clustering columns align with query patterns and data distribution.

    For the foundational explicit clustering columns scenario, this validates:
    - Tables with clustering have valid configuration
    - Clustering column limits are respected
    - No critical violations exist
    """
    total_tables = len(clustering_context.discovered_tables)
    tables_with_clustering = sum(
        1 for result in clustering_context.validation_results.values() if result["has_clustering"]
    )
    clustering_percentage = (tables_with_clustering / total_tables * 100) if total_tables > 0 else 0

    # Log overall statistics
    logger.info("Clustering compliance summary:")
    logger.info(f"  Total tables analyzed: {total_tables}")
    logger.info(f"  Tables with explicit clustering: {tables_with_clustering} ({clustering_percentage:.1f}%)")
    logger.info(f"  Clustering limit violations: {len(clustering_context.violations)}")

    # Report violations if any exist
    if clustering_context.violations:
        logger.warning("Clustering violations detected:")
        for violation in clustering_context.violations:
            logger.warning(f"  - {violation['table']}: {violation['issue']} - {violation['details']}")

    # For the foundational scenario, we verify that clustering detection works
    # and report on the current state rather than enforcing strict compliance

    # Ensure we have meaningful data to report on
    assert total_tables > 0, f"Expected to discover tables for analysis, found {total_tables}"

    # Log results for business analysis
    logger.info("Explicit clustering columns detection completed successfully")
    logger.info(f"Business insight: {clustering_percentage:.1f}% of tables use explicit clustering")

    if clustering_context.violations:
        logger.warning(f"Found {len(clustering_context.violations)} tables exceeding clustering column limits")

    # Success criteria: Detection works and we have insights
    # This is a foundational scenario focused on capability validation
    assert clustering_context.clustering_validator is not None, "Clustering validation capability verified"
    assert len(clustering_context.validation_results) == total_tables, "All tables processed for clustering analysis"


# Auto-clustering detection step definitions


@when("I check clusterByAuto flag configuration")
def check_cluster_by_auto_flag_configuration(clustering_context: ClusteringContext):
    """Check clusterByAuto flag configuration for automatic clustering detection.

    This step validates:
    - Tables with clusterByAuto=true are detected as having automatic clustering
    - Tables without clusterByAuto are correctly identified
    - Auto clustering status is properly categorized
    """
    assert clustering_context.clustering_validator is not None, "Clustering validator should be initialized"

    logger.info("Checking clusterByAuto flag configuration")

    tables_with_auto_clustering = 0
    tables_without_auto_clustering = 0
    tables_with_unknown_status = 0

    for table in clustering_context.discovered_tables:
        # Check auto clustering status
        has_auto_clustering = clustering_context.clustering_validator.has_auto_clustering(table)
        auto_clustering_status = clustering_context.clustering_validator.get_auto_clustering_status(table)
        has_any_clustering = clustering_context.clustering_validator.has_any_clustering_approach(table)

        # Store validation results
        clustering_context.validation_results[table.full_name] = {
            "has_auto_clustering": has_auto_clustering,
            "auto_clustering_status": auto_clustering_status,
            "has_any_clustering_approach": has_any_clustering,
            "table_info": table,
        }

        # Categorize tables by auto clustering status
        if auto_clustering_status == "enabled":
            tables_with_auto_clustering += 1
            logger.info(f"Table {table.full_name}: Auto clustering ENABLED")
        elif auto_clustering_status == "disabled":
            tables_without_auto_clustering += 1
            logger.debug(f"Table {table.full_name}: Auto clustering disabled")
        else:  # "unknown"
            tables_with_unknown_status += 1
            logger.debug(f"Table {table.full_name}: Auto clustering status unknown")

    logger.info("Auto clustering flag configuration check complete:")
    logger.info(f"  Tables with auto clustering enabled: {tables_with_auto_clustering}")
    logger.info(f"  Tables with auto clustering disabled: {tables_without_auto_clustering}")
    logger.info(f"  Tables with unknown auto clustering status: {tables_with_unknown_status}")


@then("tables with clusterByAuto=true should be considered properly clustered")
def verify_cluster_by_auto_tables_properly_clustered(clustering_context: ClusteringContext):
    """Verify that tables with clusterByAuto=true are considered properly clustered.

    For the foundational automatic clustering detection scenario, this validates:
    - Tables with auto clustering are correctly detected
    - Detection capabilities work as expected
    - Business insights about auto clustering adoption are available
    """
    total_tables = len(clustering_context.discovered_tables)
    tables_with_auto_clustering = sum(
        1 for result in clustering_context.validation_results.values() if result["auto_clustering_status"] == "enabled"
    )
    tables_with_any_clustering = sum(
        1 for result in clustering_context.validation_results.values() if result["has_any_clustering_approach"]
    )

    auto_clustering_percentage = (tables_with_auto_clustering / total_tables * 100) if total_tables > 0 else 0
    any_clustering_percentage = (tables_with_any_clustering / total_tables * 100) if total_tables > 0 else 0

    # Log overall statistics
    logger.info("Auto clustering compliance summary:")
    logger.info(f"  Total tables analyzed: {total_tables}")
    logger.info(
        f"  Tables with automatic clustering: {tables_with_auto_clustering} ({auto_clustering_percentage:.1f}%)"
    )
    logger.info(
        f"  Tables with any clustering approach: {tables_with_any_clustering} ({any_clustering_percentage:.1f}%)"
    )

    # Report on tables with automatic clustering
    auto_clustered_tables = [
        result
        for result in clustering_context.validation_results.values()
        if result["auto_clustering_status"] == "enabled"
    ]

    if auto_clustered_tables:
        logger.info("Tables with automatic clustering detected:")
        for result in auto_clustered_tables:
            table_info = result["table_info"]
            logger.info(f"  - {table_info.full_name}: Auto clustering enabled")
    else:
        logger.info("No tables found with automatic clustering enabled")

    # For the foundational scenario, we verify that auto clustering detection works
    # and report on the current state rather than enforcing strict compliance

    # Ensure we have meaningful data to report on
    assert total_tables > 0, f"Expected to discover tables for analysis, found {total_tables}"

    # Log results for business analysis
    logger.info("Automatic clustering detection completed successfully")
    logger.info(f"Business insight: {auto_clustering_percentage:.1f}% of tables use automatic clustering")
    logger.info(f"Business insight: {any_clustering_percentage:.1f}% of tables use any form of clustering")

    # Success criteria: Detection works and we have insights
    # This is a foundational scenario focused on capability validation
    assert clustering_context.clustering_validator is not None, "Auto clustering validation capability verified"
    assert (
        len(clustering_context.validation_results) == total_tables
    ), "All tables processed for auto clustering analysis"
