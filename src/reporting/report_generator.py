"""
Report Generator Module
Generates detailed automation reports in multiple formats
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from loguru import logger
import yaml
from jinja2 import Template, Environment, FileSystemLoader
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path
import base64


@dataclass
class ReportData:
    """Report data structure"""
    execution_summary: Dict
    test_results: List[Dict]
    bdd_scenarios: List[Dict]
    scraped_data: Dict
    ai_analysis: Dict
    performance_metrics: Dict
    screenshots: List[str]
    logs: List[str]
    timestamp: str
    duration: float


class ReportGenerator:
    """Generates comprehensive automation reports"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.report_formats = self.config['reporting']['format']
        self.include_screenshots = self.config['reporting']['include_screenshots']
        self.include_logs = self.config['reporting']['include_logs']
        self.template_dir = "src/reporting/templates"
        self.output_dir = "reports"
        
        # Create output directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/screenshots", exist_ok=True)
        os.makedirs(f"{self.output_dir}/assets", exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            raise
    
    def generate_comprehensive_report(self, report_data: ReportData) -> Dict[str, str]:
        """Generate comprehensive report in multiple formats"""
        logger.info("Generating comprehensive automation report")
        
        generated_reports = {}
        
        # Generate HTML report
        if "html" in self.report_formats:
            html_report = self.generate_html_report(report_data)
            generated_reports["html"] = html_report
            
        # Generate JSON report
        if "json" in self.report_formats:
            json_report = self.generate_json_report(report_data)
            generated_reports["json"] = json_report
            
        # Generate PDF report
        if "pdf" in self.report_formats:
            pdf_report = self.generate_pdf_report(report_data)
            generated_reports["pdf"] = pdf_report
        
        logger.info(f"Generated {len(generated_reports)} report formats")
        return generated_reports
    
    def generate_html_report(self, report_data) -> str:
        """Generate HTML report"""
        logger.info("Generating HTML report")
        
        # Create charts
        charts = self._create_charts(report_data)
        
        # Generate HTML content
        html_content = self._generate_html_content(report_data, charts)
        
        # Save HTML report
        report_path = f"{self.output_dir}/automation_report.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {report_path}")
        return report_path
    
    def generate_json_report(self, report_data: ReportData) -> str:
        """Generate JSON report"""
        logger.info("Generating JSON report")
        
        # Custom JSON encoder for datetime objects
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)
        
        # Convert dataclass to dict
        report_dict = asdict(report_data)
        
        # Save JSON report
        report_path = f"{self.output_dir}/automation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
        
        logger.info(f"JSON report generated: {report_path}")
        return report_path
    
    def generate_pdf_report(self, report_data: ReportData) -> str:
        """Generate PDF report"""
        logger.info("Generating PDF report")
        
        # For now, generate HTML and convert to PDF
        # In production, would use libraries like weasyprint or pdfkit
        html_path = self.generate_html_report(report_data)
        
        # Placeholder for PDF generation
        pdf_path = f"{self.output_dir}/automation_report.pdf"
        
        # Copy HTML content as PDF placeholder
        import shutil
        shutil.copy(html_path, pdf_path.replace('.pdf', '_pdf.html'))
        
        logger.info(f"PDF report generated: {pdf_path}")
        return pdf_path
    
    def _create_charts(self, report_data) -> Dict[str, str]:
        """Create charts for the report"""
        charts = {}
        
        # Handle both dict and ReportData object
        if isinstance(report_data, dict):
            test_results = report_data.get('test_results', [])
            bdd_scenarios = report_data.get('bdd_scenarios', [])
            performance_metrics = report_data.get('performance_metrics', {})
        else:
            test_results = report_data.test_results
            bdd_scenarios = report_data.bdd_scenarios
            performance_metrics = report_data.performance_metrics
        
        # Test Results Pie Chart
        if test_results:
            charts['test_results_pie'] = self._create_test_results_pie_chart(test_results)
            
        # Test Execution Timeline
        charts['execution_timeline'] = self._create_execution_timeline(test_results)
        
        # BDD Scenarios Distribution
        if bdd_scenarios:
            charts['bdd_distribution'] = self._create_bdd_distribution_chart(bdd_scenarios)
            
        # Performance Metrics
        if performance_metrics:
            charts['performance_metrics'] = self._create_performance_chart(performance_metrics)
        
        return charts
    
    def _create_test_results_pie_chart(self, test_results: List[Dict]) -> str:
        """Create test results pie chart"""
        # Count test statuses
        status_counts = {}
        for test in test_results:
            status = test.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Create pie chart
        fig = go.Figure(data=[
            go.Pie(
                labels=list(status_counts.keys()),
                values=list(status_counts.values()),
                hole=0.3,
                marker_colors=['#2E8B57', '#DC143C', '#FFD700', '#808080']
            )
        ])
        
        fig.update_layout(
            title="Test Results Distribution",
            font=dict(size=12),
            showlegend=True,
            width=400,
            height=300
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='test-results-pie')
    
    def _create_execution_timeline(self, test_results: List[Dict]) -> str:
        """Create test execution timeline"""
        if not test_results:
            return ""
        
        # Prepare data
        test_names = [test.get('test_name', f'Test {i}') for i, test in enumerate(test_results)]
        durations = [test.get('duration', 0) for test in test_results]
        statuses = [test.get('status', 'unknown') for test in test_results]
        
        # Create bar chart
        fig = px.bar(
            x=test_names,
            y=durations,
            color=statuses,
            title="Test Execution Timeline",
            labels={'x': 'Test Cases', 'y': 'Duration (seconds)'},
            color_discrete_map={
                'passed': '#2E8B57',
                'failed': '#DC143C',
                'skipped': '#FFD700'
            }
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            width=800,
            height=400
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='execution-timeline')
    
    def _create_bdd_distribution_chart(self, bdd_scenarios: List[Dict]) -> str:
        """Create BDD scenarios distribution chart"""
        # Count by priority
        priority_counts = {}
        type_counts = {}
        
        for scenario in bdd_scenarios:
            priority = scenario.get('priority', 'unknown')
            test_type = scenario.get('test_type', 'unknown')
            
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            type_counts[test_type] = type_counts.get(test_type, 0) + 1
        
        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('By Priority', 'By Type'),
            specs=[[{"type": "pie"}, {"type": "pie"}]]
        )
        
        # Priority pie chart
        fig.add_trace(
            go.Pie(
                labels=list(priority_counts.keys()),
                values=list(priority_counts.values()),
                name="Priority"
            ),
            row=1, col=1
        )
        
        # Type pie chart
        fig.add_trace(
            go.Pie(
                labels=list(type_counts.keys()),
                values=list(type_counts.values()),
                name="Type"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title="BDD Scenarios Distribution",
            width=800,
            height=400
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='bdd-distribution')
    
    def _create_performance_chart(self, performance_metrics: Dict) -> str:
        """Create performance metrics chart"""
        # Extract metrics
        metrics = ['page_load_time', 'test_execution_time', 'ai_response_time']
        values = [performance_metrics.get(metric, 0) for metric in metrics]
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=metrics,
                y=values,
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c']
            )
        ])
        
        fig.update_layout(
            title="Performance Metrics",
            xaxis_title="Metrics",
            yaxis_title="Time (seconds)",
            width=600,
            height=400
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='performance-metrics')
    
    def _generate_html_content(self, report_data, charts: Dict) -> str:
        """Generate HTML report content"""
        html_template = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Test Automation Report</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .card h3 {
            margin: 0 0 10px 0;
            color: #333;
        }
        .card .value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .chart-container {
            margin: 20px 0;
        }
        .test-list {
            margin-top: 20px;
        }
        .test-item {
            padding: 10px;
            margin: 5px 0;
            border-left: 4px solid #ddd;
            background: #f9f9f9;
        }
        .test-item.passed {
            border-left-color: #2E8B57;
        }
        .test-item.failed {
            border-left-color: #DC143C;
        }
        .test-item.skipped {
            border-left-color: #FFD700;
        }
        .log-container {
            background: #1e1e1e;
            color: #fff;
            padding: 20px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            max-height: 300px;
            overflow-y: auto;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #666;
            border-top: 1px solid #ddd;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .screenshot {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI Test Automation Report</h1>
        <p>Generated on {{ timestamp }}</p>
    </div>

    <div class="summary-cards">
        <div class="card">
            <h3>Total Tests</h3>
            <div class="value">{{ execution_summary.total_tests }}</div>
        </div>
        <div class="card">
            <h3>Passed</h3>
            <div class="value" style="color: #2E8B57;">{{ execution_summary.passed_tests }}</div>
        </div>
        <div class="card">
            <h3>Failed</h3>
            <div class="value" style="color: #DC143C;">{{ execution_summary.failed_tests }}</div>
        </div>
        <div class="card">
            <h3>Duration</h3>
            <div class="value">{{ "%.2f"|format(duration) }}s</div>
        </div>
    </div>

    <div class="section">
        <h2>📊 Test Results Overview</h2>
        <div class="chart-container">
            {{ charts.test_results_pie|safe }}
        </div>
        <div class="chart-container">
            {{ charts.execution_timeline|safe }}
        </div>
    </div>

    <div class="section">
        <h2>📋 BDD Scenarios</h2>
        <div class="chart-container">
            {{ charts.bdd_distribution|safe }}
        </div>
        <h3>Scenario Details</h3>
        <table>
            <thead>
                <tr>
                    <th>Feature</th>
                    <th>Scenario</th>
                    <th>Priority</th>
                    <th>Type</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for scenario in bdd_scenarios %}
                <tr>
                    <td>{{ scenario.feature }}</td>
                    <td>{{ scenario.scenario }}</td>
                    <td>{{ scenario.priority }}</td>
                    <td>{{ scenario.test_type }}</td>
                    <td>{{ scenario.status or 'N/A' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>⚡ Performance Metrics</h2>
        <div class="chart-container">
            {{ charts.performance_metrics|safe }}
        </div>
    </div>

    <div class="section">
        <h2>🔍 Test Details</h2>
        <div class="test-list">
            {% for test in test_results %}
            <div class="test-item {{ test.status }}">
                <h4>{{ test.test_name }}</h4>
                <p><strong>Status:</strong> {{ test.status }}</p>
                <p><strong>Duration:</strong> {{ "%.2f"|format(test.duration) }}s</p>
                {% if test.error_message %}
                <p><strong>Error:</strong> {{ test.error_message }}</p>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>

    {% if include_logs and logs %}
    <div class="section">
        <h2>📝 Execution Logs</h2>
        <div class="log-container">
            {% for log in logs %}
            <div>{{ log }}</div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <div class="footer">
        <p>Generated by AI Test Automation Assistant</p>
        <p>Report generated at {{ timestamp }}</p>
    </div>
</body>
</html>
        """
        
        # Handle both dict and ReportData object
        if isinstance(report_data, dict):
            timestamp = report_data.get('timestamp', datetime.now().isoformat())
            execution_summary = report_data.get('execution_stats', {})
            test_results = report_data.get('test_results', [])
            bdd_scenarios = report_data.get('bdd_scenarios', [])
            performance_metrics = report_data.get('performance_metrics', {})
            duration = report_data.get('duration', 0)
            logs = report_data.get('logs', [])
        else:
            timestamp = report_data.timestamp
            execution_summary = report_data.execution_summary
            test_results = report_data.test_results
            bdd_scenarios = report_data.bdd_scenarios
            performance_metrics = report_data.performance_metrics
            duration = report_data.duration
            logs = report_data.logs

        template = Template(html_template)
        return template.render(
            timestamp=timestamp,
            execution_summary=execution_summary,
            test_results=test_results,
            bdd_scenarios=bdd_scenarios,
            performance_metrics=performance_metrics,
            duration=duration,
            charts=charts,
            include_logs=self.include_logs,
            logs=logs
        )
    
    def create_report_data(self, 
                          test_suite: Any,
                          bdd_features: List[Dict],
                          scraped_data: Dict,
                          ai_analysis: Dict,
                          performance_metrics: Dict) -> ReportData:
        """Create report data from various sources"""
        
        # Extract execution summary
        execution_summary = {
            'total_tests': len(test_suite.tests) if test_suite else 0,
            'passed_tests': test_suite.passed_count if test_suite else 0,
            'failed_tests': test_suite.failed_count if test_suite else 0,
            'skipped_tests': test_suite.skipped_count if test_suite else 0,
            'start_time': test_suite.start_time.isoformat() if test_suite else datetime.now().isoformat(),
            'end_time': test_suite.end_time.isoformat() if test_suite else datetime.now().isoformat()
        }
        
        # Extract test results
        test_results = []
        if test_suite:
            for test in test_suite.tests:
                test_results.append({
                    'test_name': test.test_name,
                    'status': test.status,
                    'duration': test.duration,
                    'error_message': test.error_message,
                    'screenshot_path': test.screenshot_path
                })
        
        # Extract BDD scenarios
        bdd_scenarios = []
        for feature in bdd_features:
            for scenario in feature.get('scenarios', []):
                bdd_scenarios.append({
                    'feature': feature.get('name', ''),
                    'scenario': scenario.get('scenario', ''),
                    'priority': scenario.get('priority', 'medium'),
                    'test_type': scenario.get('test_type', 'functional'),
                    'status': None  # Would be populated after test execution
                })
        
        return ReportData(
            execution_summary=execution_summary,
            test_results=test_results,
            bdd_scenarios=bdd_scenarios,
            scraped_data=scraped_data,
            ai_analysis=ai_analysis,
            performance_metrics=performance_metrics,
            screenshots=[],
            logs=[],
            timestamp=datetime.now().isoformat(),
            duration=test_suite.total_duration if test_suite else 0
        ) 