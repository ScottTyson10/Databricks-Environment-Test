"""Results tracking system for three-layer testing architecture.

Provides centralized result tracking across:
- Layer 1: Unit tests
- Layer 2: Integration tests 
- Layer 3: Production BDD tests

TODO: Integrate with SonarQube for code quality metrics and test coverage reporting
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Individual test result."""
    test_name: str
    layer: str  # "unit", "integration", "production"
    status: str  # "passed", "failed", "skipped"
    duration: float
    timestamp: str
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

@dataclass 
class ComplianceResult:
    """Compliance analysis result for production tests."""
    domain: str  # "documentation", "clustering", etc.
    total_objects: int
    compliant_objects: int
    non_compliant_objects: int
    compliance_rate: float
    violations: List[str]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

class ResultsManager:
    """Manages test results across all three layers."""
    
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.logs_dir = self.results_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Session tracking
        self.session_id = self._generate_session_id()
        self.test_results: List[TestResult] = []
        self.compliance_results: List[ComplianceResult] = []
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    def add_test_result(self, test_result: TestResult) -> None:
        """Add a test result."""
        self.test_results.append(test_result)
        logger.debug(f"Added {test_result.layer} test result: {test_result.test_name} - {test_result.status}")
    
    def add_compliance_result(self, compliance_result: ComplianceResult) -> None:
        """Add a compliance result."""
        self.compliance_results.append(compliance_result)
        logger.info(f"Added compliance result: {compliance_result.domain} - {compliance_result.compliance_rate:.1f}% compliant")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current test session."""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "passed"])
        failed_tests = len([r for r in self.test_results if r.status == "failed"])
        
        return {
            "session_id": self.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "compliance_results": len(self.compliance_results),
            "test_results_by_layer": {
                "unit": len([r for r in self.test_results if r.layer == "unit"]),
                "integration": len([r for r in self.test_results if r.layer == "integration"]),
                "production": len([r for r in self.test_results if r.layer == "production"])
            }
        }
    
    def save_session(self) -> str:
        """Save current session to file."""
        session_file = self.results_dir / f"session_{self.session_id}.json"
        
        session_data = {
            "summary": self.get_session_summary(),
            "test_results": [result.to_dict() for result in self.test_results],
            "compliance_results": [result.to_dict() for result in self.compliance_results]
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        logger.info(f"Session saved to {session_file}")
        return str(session_file)
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a previous session."""
        session_file = self.results_dir / f"session_{session_id}.json"
        
        if not session_file.exists():
            logger.warning(f"Session file not found: {session_file}")
            return None
        
        with open(session_file, 'r') as f:
            data: dict[str, Any] = json.load(f)
            return data
    
    def get_latest_compliance(self, domain: str) -> Optional[ComplianceResult]:
        """Get latest compliance result for a domain."""
        domain_results = [r for r in self.compliance_results if r.domain == domain]
        return domain_results[-1] if domain_results else None
    
    def generate_html_report(self) -> str:
        """Generate HTML report of current session."""
        html_file = self.results_dir / f"report_{self.session_id}.html"
        summary = self.get_session_summary()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Results - Session {self.session_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .compliance {{ margin: 20px 0; }}
                .layer {{ margin: 15px 0; padding: 10px; border-left: 3px solid #007acc; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Test Results - Session {self.session_id}</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Total Tests:</strong> {summary['total_tests']}</p>
                <p><strong>Passed:</strong> <span class="passed">{summary['passed_tests']}</span></p>
                <p><strong>Failed:</strong> <span class="failed">{summary['failed_tests']}</span></p>
                <p><strong>Success Rate:</strong> {summary['success_rate']:.1f}%</p>
                <p><strong>Timestamp:</strong> {summary['timestamp']}</p>
            </div>
            
            <div class="layer">
                <h2>Tests by Layer</h2>
                <ul>
                    <li><strong>Unit Tests:</strong> {summary['test_results_by_layer']['unit']}</li>
                    <li><strong>Integration Tests:</strong> {summary['test_results_by_layer']['integration']}</li>
                    <li><strong>Production Tests:</strong> {summary['test_results_by_layer']['production']}</li>
                </ul>
            </div>
        """
        
        if self.compliance_results:
            html_content += """
            <div class="compliance">
                <h2>Compliance Results</h2>
                <table>
                    <tr>
                        <th>Domain</th>
                        <th>Total Objects</th>
                        <th>Compliant</th>
                        <th>Non-Compliant</th>
                        <th>Compliance Rate</th>
                    </tr>
            """
            
            for result in self.compliance_results:
                html_content += f"""
                    <tr>
                        <td>{result.domain}</td>
                        <td>{result.total_objects}</td>
                        <td class="passed">{result.compliant_objects}</td>
                        <td class="failed">{result.non_compliant_objects}</td>
                        <td>{result.compliance_rate:.1f}%</td>
                    </tr>
                """
            
            html_content += """
                </table>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {html_file}")
        return str(html_file)

# Global results manager instance
_results_manager = None

def get_results_manager() -> ResultsManager:
    """Get or create global results manager."""
    global _results_manager
    if _results_manager is None:
        _results_manager = ResultsManager()
    return _results_manager

def record_test_result(test_name: str, layer: str, status: str, duration: float, details: Optional[Dict[str, Any]] = None) -> None:
    """Convenience function to record a test result."""
    result = TestResult(
        test_name=test_name,
        layer=layer,
        status=status,
        duration=duration,
        timestamp=datetime.now(timezone.utc).isoformat(),
        details=details
    )
    get_results_manager().add_test_result(result)

def record_compliance_result(domain: str, total_objects: int, compliant_objects: int, 
                           violations: List[str]) -> None:
    """Convenience function to record a compliance result."""
    result = ComplianceResult(
        domain=domain,
        total_objects=total_objects,
        compliant_objects=compliant_objects,
        non_compliant_objects=total_objects - compliant_objects,
        compliance_rate=(compliant_objects / total_objects * 100) if total_objects > 0 else 0,
        violations=violations,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    get_results_manager().add_compliance_result(result)