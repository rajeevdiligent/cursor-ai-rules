#!/usr/bin/env python3
"""
Code Review Parser and Analyzer

This script parses code review results from AI analysis and generates
structured reports with metrics, violations, and recommendations.

Usage:
    python review_parser.py --input <review_data> --output CODE_REVIEW_SUMMARY.md
"""

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


class Severity(Enum):
    """Severity levels for code review findings"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueCategory(Enum):
    """Categories of code review issues"""
    ARCHITECTURE = "architecture"
    CODE_QUALITY = "code_quality"
    TESTING = "testing"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    ANTI_PATTERN = "anti_pattern"


@dataclass
class CodeIssue:
    """Represents a code review issue"""
    category: IssueCategory
    severity: Severity
    message: str
    file_path: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    rule_id: Optional[str] = None


@dataclass
class LayerMetrics:
    """Metrics for architectural layers"""
    name: str
    file_count: int = 0
    line_count: int = 0
    violation_count: int = 0
    test_coverage: float = 0.0


@dataclass
class CodeMetrics:
    """Overall code metrics"""
    total_files: int = 0
    total_lines: int = 0
    avg_complexity: float = 0.0
    test_coverage: float = 0.0
    duplication_percentage: float = 0.0
    technical_debt_ratio: float = 0.0
    layer_metrics: Dict[str, LayerMetrics] = field(default_factory=dict)


@dataclass
class ReviewResult:
    """Complete review result"""
    timestamp: datetime
    metrics: CodeMetrics
    issues: List[CodeIssue] = field(default_factory=list)
    passed: bool = True
    score: float = 0.0


class ReviewParser:
    """Parses and analyzes code review data"""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the parser with optional configuration"""
        self.config = self._load_config(config_path)
        self.severity_thresholds = {
            Severity.CRITICAL: 0,
            Severity.ERROR: 0,
            Severity.WARNING: 10,
            Severity.INFO: float('inf')
        }

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load configuration from cursor.json"""
        if config_path and config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}

    def parse_review_data(self, data: Dict) -> ReviewResult:
        """Parse review data into structured result"""
        result = ReviewResult(
            timestamp=datetime.now(),
            metrics=self._extract_metrics(data),
            issues=self._extract_issues(data)
        )
        result.score = self._calculate_score(result)
        result.passed = self._determine_pass_status(result)
        return result

    def _extract_metrics(self, data: Dict) -> CodeMetrics:
        """Extract code metrics from review data"""
        metrics = CodeMetrics()
        
        if 'metrics' in data:
            m = data['metrics']
            metrics.total_files = m.get('total_files', 0)
            metrics.total_lines = m.get('total_lines', 0)
            metrics.avg_complexity = m.get('avg_complexity', 0.0)
            metrics.test_coverage = m.get('test_coverage', 0.0)
            metrics.duplication_percentage = m.get('duplication', 0.0)
            metrics.technical_debt_ratio = m.get('tech_debt_ratio', 0.0)
            
            # Extract layer metrics
            if 'layers' in m:
                for layer_name, layer_data in m['layers'].items():
                    metrics.layer_metrics[layer_name] = LayerMetrics(
                        name=layer_name,
                        file_count=layer_data.get('files', 0),
                        line_count=layer_data.get('lines', 0),
                        violation_count=layer_data.get('violations', 0),
                        test_coverage=layer_data.get('coverage', 0.0)
                    )
        
        return metrics

    def _extract_issues(self, data: Dict) -> List[CodeIssue]:
        """Extract code issues from review data"""
        issues = []
        
        if 'issues' in data:
            for issue_data in data['issues']:
                try:
                    issue = CodeIssue(
                        category=IssueCategory(issue_data.get('category', 'code_quality')),
                        severity=Severity(issue_data.get('severity', 'info')),
                        message=issue_data['message'],
                        file_path=issue_data['file'],
                        line_number=issue_data.get('line'),
                        suggestion=issue_data.get('suggestion'),
                        rule_id=issue_data.get('rule_id')
                    )
                    issues.append(issue)
                except (KeyError, ValueError) as e:
                    print(f"Warning: Skipping malformed issue: {e}")
        
        return issues

    def _calculate_score(self, result: ReviewResult) -> float:
        """Calculate overall review score (0-100)"""
        base_score = 100.0
        
        # Deduct points for issues based on severity
        severity_weights = {
            Severity.CRITICAL: 10.0,
            Severity.ERROR: 5.0,
            Severity.WARNING: 1.0,
            Severity.INFO: 0.1
        }
        
        for issue in result.issues:
            base_score -= severity_weights.get(issue.severity, 0)
        
        # Adjust for metrics
        if result.metrics.test_coverage < 80:
            base_score -= (80 - result.metrics.test_coverage) * 0.2
        
        if result.metrics.duplication_percentage > 5:
            base_score -= (result.metrics.duplication_percentage - 5) * 2
        
        return max(0.0, min(100.0, base_score))

    def _determine_pass_status(self, result: ReviewResult) -> bool:
        """Determine if the review passes based on severity thresholds"""
        severity_counts = {severity: 0 for severity in Severity}
        
        for issue in result.issues:
            severity_counts[issue.severity] += 1
        
        # Check thresholds
        for severity, threshold in self.severity_thresholds.items():
            if severity_counts[severity] > threshold:
                return False
        
        return True

    def generate_markdown_report(self, result: ReviewResult) -> str:
        """Generate markdown report from review result"""
        timestamp_str = result.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        report_lines = [
            "# Code Review Summary",
            "",
            f"**Generated:** {timestamp_str}",
            "**Reviewer:** AI Code Review System",
            "**Version:** 1.0.0",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"### Overall Score: {result.score:.1f}/100.0",
            "",
            f"**Status:** {'✅ PASSED' if result.passed else '❌ FAILED'}",
            "",
        ]
        
        # Add metrics section
        report_lines.extend(self._generate_metrics_section(result.metrics))
        
        # Add issues section
        report_lines.extend(self._generate_issues_section(result.issues))
        
        # Add recommendations
        report_lines.extend(self._generate_recommendations(result))
        
        return "\n".join(report_lines)

    def _generate_metrics_section(self, metrics: CodeMetrics) -> List[str]:
        """Generate metrics section of report"""
        lines = [
            "## 📊 Metrics",
            "",
            "### Code Quality Metrics",
            "| Metric | Value | Threshold | Status |",
            "|--------|-------|-----------|--------|",
            f"| Lines of Code | {metrics.total_lines:,} | - | ✅ |",
            f"| Avg Complexity | {metrics.avg_complexity:.1f} | 10 | {'✅' if metrics.avg_complexity <= 10 else '❌'} |",
            f"| Test Coverage | {metrics.test_coverage:.1f}% | 80% | {'✅' if metrics.test_coverage >= 80 else '⚠️'} |",
            f"| Code Duplication | {metrics.duplication_percentage:.1f}% | < 5% | {'✅' if metrics.duplication_percentage < 5 else '⚠️'} |",
            f"| Technical Debt | {metrics.technical_debt_ratio:.1f}% | < 5% | {'✅' if metrics.technical_debt_ratio < 5 else '⚠️'} |",
            "",
        ]
        
        # Add layer metrics if available
        if metrics.layer_metrics:
            lines.extend([
                "### Architecture Metrics",
                "| Layer | Files | Lines | Violations | Coverage |",
                "|-------|-------|-------|------------|----------|"
            ])
            for layer in metrics.layer_metrics.values():
                lines.append(
                    f"| {layer.name} | {layer.file_count} | {layer.line_count:,} | "
                    f"{layer.violation_count} | {layer.test_coverage:.1f}% |"
                )
            lines.append("")
        
        return lines

    def _generate_issues_section(self, issues: List[CodeIssue]) -> List[str]:
        """Generate issues section of report"""
        lines = [
            "## 🔍 Code Quality Issues",
            ""
        ]
        
        # Group issues by severity
        issues_by_severity = {severity: [] for severity in Severity}
        for issue in issues:
            issues_by_severity[issue.severity].append(issue)
        
        # Critical issues
        if issues_by_severity[Severity.CRITICAL]:
            lines.extend([
                "### 🚨 Critical Issues (Must Fix)",
                ""
            ])
            for issue in issues_by_severity[Severity.CRITICAL]:
                lines.extend(self._format_issue(issue))
            lines.append("")
        
        # Errors
        if issues_by_severity[Severity.ERROR]:
            lines.extend([
                "### ❌ Errors (Should Fix)",
                ""
            ])
            for issue in issues_by_severity[Severity.ERROR]:
                lines.extend(self._format_issue(issue))
            lines.append("")
        
        # Warnings
        if issues_by_severity[Severity.WARNING]:
            lines.extend([
                "### ⚠️ Warnings",
                ""
            ])
            for issue in issues_by_severity[Severity.WARNING]:
                lines.extend(self._format_issue(issue))
            lines.append("")
        
        return lines

    def _format_issue(self, issue: CodeIssue) -> List[str]:
        """Format a single issue for the report"""
        lines = [
            f"#### {issue.category.value.replace('_', ' ').title()}",
            f"- **File:** `{issue.file_path}`"
        ]
        
        if issue.line_number:
            lines.append(f"- **Line:** {issue.line_number}")
        
        if issue.rule_id:
            lines.append(f"- **Rule:** {issue.rule_id}")
        
        lines.append(f"- **Issue:** {issue.message}")
        
        if issue.suggestion:
            lines.append(f"- **Suggestion:** {issue.suggestion}")
        
        lines.append("")
        return lines

    def _generate_recommendations(self, result: ReviewResult) -> List[str]:
        """Generate recommendations based on review results"""
        lines = [
            "## 💡 Recommendations",
            ""
        ]
        
        high_priority = []
        medium_priority = []
        low_priority = []
        
        # Analyze issues and metrics to generate recommendations
        if result.metrics.test_coverage < 80:
            high_priority.append(
                f"Increase test coverage from {result.metrics.test_coverage:.1f}% to at least 80%"
            )
        
        critical_count = sum(1 for i in result.issues if i.severity == Severity.CRITICAL)
        if critical_count > 0:
            high_priority.append(f"Fix {critical_count} critical security/architecture issues")
        
        if result.metrics.duplication_percentage > 5:
            medium_priority.append(
                f"Reduce code duplication from {result.metrics.duplication_percentage:.1f}% to below 5%"
            )
        
        arch_violations = sum(
            1 for i in result.issues if i.category == IssueCategory.ARCHITECTURE
        )
        if arch_violations > 0:
            high_priority.append(f"Address {arch_violations} clean architecture violations")
        
        # Format recommendations
        if high_priority:
            lines.extend(["### High Priority", ""])
            for i, rec in enumerate(high_priority, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        if medium_priority:
            lines.extend(["### Medium Priority", ""])
            for i, rec in enumerate(medium_priority, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        if low_priority:
            lines.extend(["### Low Priority", ""])
            for i, rec in enumerate(low_priority, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        return lines


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="Parse and analyze code review results"
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input JSON file with review data"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("CODE_REVIEW_SUMMARY.md"),
        help="Output markdown file"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("cursor.json"),
        help="Configuration file"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Use strict mode (fail on warnings)"
    )
    
    args = parser.parse_args()
    
    # Load review data
    try:
        with open(args.input, 'r') as f:
            review_data = json.load(f)
    except Exception as e:
        print(f"Error loading review data: {e}")
        return 1
    
    # Parse and analyze
    review_parser = ReviewParser(args.config if args.config.exists() else None)
    result = review_parser.parse_review_data(review_data)
    
    # Generate report
    report = review_parser.generate_markdown_report(result)
    
    # Write output
    try:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Review report generated: {args.output}")
    except Exception as e:
        print(f"Error writing report: {e}")
        return 1
    
    # Exit with appropriate code
    if not result.passed:
        print(f"❌ Review FAILED (Score: {result.score:.1f}/100)")
        return 1
    else:
        print(f"✅ Review PASSED (Score: {result.score:.1f}/100)")
        return 0


if __name__ == "__main__":
    exit(main())

