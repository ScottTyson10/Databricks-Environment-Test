"""pytest-bdd configuration with Results tracking system.

Provides session-wide results tracking across three-layer testing architecture:
- Layer 1: Unit tests
- Layer 2: Integration tests  
- Layer 3: Production BDD tests
"""
import pytest
import time
from typing import Dict, Any
from results.results import get_results_manager, record_test_result, record_compliance_result

@pytest.fixture(scope="session")
def results_manager():
    """Session-scoped results manager for tracking test outcomes."""
    return get_results_manager()

@pytest.fixture(autouse=True)
def track_test_results(request, results_manager):
    """Automatically track test results for all tests."""
    start_time = time.time()
    
    yield
    
    # Determine test layer from file path
    test_file = str(request.fspath)
    if "unit" in test_file:
        layer = "unit"
    elif "integration" in test_file:
        layer = "integration"
    elif "step_definitions" in test_file:
        layer = "production"
    else:
        layer = "unknown"
    
    # Record test result
    duration = time.time() - start_time
    status = "passed" if request.node.rep_call.passed else "failed"
    
    record_test_result(
        test_name=request.node.nodeid,
        layer=layer,
        status=status,
        duration=duration
    )

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

@pytest.fixture(scope="session", autouse=True)
def session_results_summary(results_manager):
    """Print session summary at end of test run."""
    yield
    
    # Generate and save session results
    session_file = results_manager.save_session()
    html_report = results_manager.generate_html_report()
    
    summary = results_manager.get_session_summary()
    
    print(f"\n{'='*60}")
    print(f"TEST SESSION SUMMARY - {summary['session_id']}")
    print(f"{'='*60}")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"\nTests by Layer:")
    print(f"  Unit: {summary['test_results_by_layer']['unit']}")
    print(f"  Integration: {summary['test_results_by_layer']['integration']}")
    print(f"  Production: {summary['test_results_by_layer']['production']}")
    
    if summary['compliance_results'] > 0:
        print(f"\nCompliance Results: {summary['compliance_results']} recorded")
    
    print(f"\nResults saved to: {session_file}")
    print(f"HTML report: {html_report}")
    print(f"{'='*60}")

def record_documentation_compliance(total_tables: int, tables_with_comments: int, violations: list):
    """Helper to record documentation compliance results."""
    record_compliance_result(
        domain="documentation",
        total_objects=total_tables,
        compliant_objects=tables_with_comments,
        violations=violations
    )