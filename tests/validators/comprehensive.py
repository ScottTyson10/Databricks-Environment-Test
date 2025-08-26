"""Comprehensive Documentation Compliance Validator.

Combines all individual documentation checks into a single comprehensive
assessment for production readiness. All checks must pass for a table
to be considered comprehensively compliant.
"""

import logging
from dataclasses import dataclass
from typing import Any

from tests.utils.config_loader import get_config_loader
from tests.utils.discovery import TableInfo
from tests.validators.documentation import DocumentationValidator

logger = logging.getLogger(__name__)


@dataclass
class ComprehensiveComplianceResult:
    """Result of a comprehensive compliance check for a single table."""

    table: TableInfo
    overall_compliant: bool
    individual_results: dict[str, bool]
    failure_reasons: list[str]

    @property
    def compliance_summary(self) -> str:
        """Human-readable compliance summary."""
        passed_checks = [k for k, v in self.individual_results.items() if v]
        failed_checks = [k for k, v in self.individual_results.items() if not v]

        return (
            f"Passed: {len(passed_checks)}/{len(self.individual_results)} checks. " + f"Failed: {failed_checks}"
            if failed_checks
            else "All checks passed"
        )


class ComprehensiveDocumentationValidator:
    """Validator that combines all documentation checks for comprehensive assessment."""

    def __init__(self) -> None:
        """Initialize comprehensive validator with configuration."""
        self._config_loader = get_config_loader()
        self._doc_validator = DocumentationValidator()

        # Load comprehensive rules configuration
        try:
            self._required_checks = self._config_loader.get_comprehensive_rules()["required_checks"]
        except KeyError:
            # Fallback to default comprehensive checks
            self._required_checks = [
                "table_has_comment",
                "table_comment_length",
                "no_placeholder_comments",
                "column_coverage >= 80",
                "critical_columns_documented",
            ]

        logger.info(f"Initialized comprehensive validator with {len(self._required_checks)} checks")

    def evaluate_table_compliance(self, table: TableInfo) -> ComprehensiveComplianceResult:
        """Evaluate comprehensive compliance for a single table."""

        # Run all individual validators
        individual_results = self._run_individual_validators(table)

        # Check all required rules
        failure_reasons = []
        overall_compliant = True

        for check in self._required_checks:
            if not self._evaluate_check(check, table, individual_results):
                overall_compliant = False
                failure_reasons.append(f"Failed: {check}")

        return ComprehensiveComplianceResult(
            table=table,
            overall_compliant=overall_compliant,
            individual_results=individual_results,
            failure_reasons=failure_reasons,
        )

    def _run_individual_validators(self, table: TableInfo) -> dict[str, bool]:
        """Run all individual documentation validators."""
        return {
            "table_has_comment": self._doc_validator.has_comment(table),
            "table_comment_length": self._doc_validator.has_minimum_length(table),
            "no_placeholder_comments": not self._doc_validator.has_placeholder_comment(table),
            "column_coverage_80": self._doc_validator.meets_column_documentation_threshold(table, 80.0),
            "critical_columns_documented": self._doc_validator.has_all_critical_columns_documented(table),
        }

    def _evaluate_check(self, check: str, table: TableInfo, individual_results: dict[str, bool]) -> bool:
        """Evaluate a single check."""
        # Direct lookup for simple checks
        if check in individual_results:
            return individual_results[check]

        # Handle threshold checks like "column_coverage >= 80"
        if ">=" in check:
            metric, threshold_str = check.split(">=")
            metric = metric.strip()
            threshold = float(threshold_str.strip())

            if metric == "column_coverage":
                return self._doc_validator.meets_column_documentation_threshold(table, threshold)

        logger.warning(f"Unknown check: {check}")
        return False

    def evaluate_tables(self, tables: list[TableInfo]) -> tuple[list[ComprehensiveComplianceResult], dict[str, Any]]:
        """Evaluate comprehensive compliance for multiple tables with summary."""
        results = []

        for table in tables:
            result = self.evaluate_table_compliance(table)
            results.append(result)

        # Calculate summary statistics
        total_tables = len(results)
        compliant_tables = sum(1 for r in results if r.overall_compliant)
        compliance_rate = (compliant_tables / total_tables * 100) if total_tables > 0 else 0

        # Aggregate individual check statistics
        check_stats = {}
        if results:
            all_checks: set[str] = set()
            for result in results:
                all_checks.update(result.individual_results.keys())

            for check in all_checks:
                passed = sum(1 for r in results if r.individual_results.get(check, False))
                check_stats[check] = {
                    "passed": passed,
                    "failed": total_tables - passed,
                    "pass_rate": (passed / total_tables * 100) if total_tables > 0 else 0,
                }

        # Common failure reasons
        failure_counts: dict[str, int] = {}
        for result in results:
            if not result.overall_compliant:
                for reason in result.failure_reasons:
                    failure_counts[reason] = failure_counts.get(reason, 0) + 1

        summary = {
            "total_tables": total_tables,
            "comprehensive_compliant": compliant_tables,
            "comprehensive_compliance_rate": compliance_rate,
            "individual_check_stats": check_stats,
            "common_failures": failure_counts,
            "required_checks": self._required_checks,
        }

        return results, summary
