"""
Main Orchestrator Module
Coordinates all components of the AI Test Automation system
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger
import yaml
import json
import os
from dataclasses import dataclass

# Import all modules
from src.ai.ai_client import AIClient
from src.scraper.web_scraper import WebScraper
from src.bdd.bdd_generator import BDDGenerator
from src.automation.test_generator import TestGenerator
from src.reporting.report_generator import ReportGenerator


@dataclass
class ExecutionConfig:
    """Execution configuration"""
    url: str
    ai_model: str
    output_dir: str
    headless: bool = True
    parallel_tests: bool = True
    generate_reports: bool = True
    save_artifacts: bool = True


@dataclass
class ExecutionResult:
    """Complete execution result"""
    success: bool
    execution_time: float
    scraped_data: Dict
    ai_analysis: Dict
    bdd_features: List[Dict]
    test_results: Any
    reports: Dict[str, str]
    error_message: Optional[str] = None
    artifacts_saved: bool = False


class MainOrchestrator:
    """Main orchestrator for the AI Test Automation system"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize components
        self.ai_client = AIClient(config_path)
        self.web_scraper = WebScraper(config_path)
        self.bdd_generator = BDDGenerator(config_path)
        self.test_generator = TestGenerator(config_path)
        self.report_generator = ReportGenerator(config_path)
        
        # Performance metrics
        self.performance_metrics = {
            'start_time': None,
            'end_time': None,
            'page_load_time': 0,
            'ai_response_time': 0,
            'test_execution_time': 0,
            'total_execution_time': 0
        }
        
        logger.info("Main Orchestrator initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            raise
    
    def execute_full_automation(self, url: str) -> bool:
        """Execute complete automation workflow"""
        logger.info(f"Starting full automation for: {url}")
        
        start_time = time.time()
        self.performance_metrics['start_time'] = datetime.now()
        
        try:
            # Step 1: Web Scraping
            logger.info("Step 1: Web Scraping")
            scraped_data = self._scrape_website(url)
            
            # Step 2: AI Analysis
            logger.info("Step 2: AI Analysis")
            ai_analysis = self._analyze_with_ai(scraped_data, self.config.get('ai', {}).get('model', 'llama3:latest'))
            
            # Step 3: BDD Generation
            logger.info("Step 3: BDD Generation")
            bdd_features = self._generate_bdd_scenarios(scraped_data, ai_analysis)
            
            # Step 4: Test Code Generation
            logger.info("Step 4: Test Code Generation")
            test_code_path = self._generate_test_code(bdd_features, scraped_data)
            
            # Step 5: Test Execution
            logger.info("Step 5: Test Execution")
            test_results = self._execute_tests(test_code_path)
            
            # Step 6: Report Generation
            logger.info("Step 6: Report Generation")
            reports = self._generate_reports(test_results, bdd_features, scraped_data, ai_analysis)
            
            # Calculate final metrics
            end_time = time.time()
            self.performance_metrics['end_time'] = datetime.now()
            self.performance_metrics['total_execution_time'] = end_time - start_time
            
            logger.info(f"Full automation completed in {self.performance_metrics['total_execution_time']:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during automation execution: {e}")
            return False
            
        finally:
            # Cleanup
            self._cleanup()
    
    def _scrape_website(self, url: str) -> Dict:
        """Scrape website and extract data"""
        scrape_start = time.time()
        
        try:
            scraped_data = self.web_scraper.scrape_website(url)
            
            scrape_end = time.time()
            self.performance_metrics['page_load_time'] = scrape_end - scrape_start
            
            logger.info(f"Website scraped successfully in {self.performance_metrics['page_load_time']:.2f}s")
            
            # Convert to dict for JSON serialization
            return {
                'url': scraped_data.url,
                'title': scraped_data.title,
                'html_content': scraped_data.html_content[:1000],  # Truncate for storage
                'forms': scraped_data.forms,
                'links': scraped_data.links,
                'buttons': scraped_data.buttons,
                'inputs': scraped_data.inputs,
                'images': scraped_data.images,
                'meta_tags': scraped_data.meta_tags,
                'page_structure': scraped_data.page_structure,
                'load_time': scraped_data.load_time,
                'status_code': scraped_data.status_code
            }
            
        except Exception as e:
            logger.error(f"Error scraping website: {e}")
            raise
    
    def _analyze_with_ai(self, scraped_data: Dict, ai_model: str) -> Dict:
        """Analyze scraped data with AI"""
        ai_start = time.time()
        
        try:
            # Set AI model
            self.ai_client.set_model(ai_model)
            
            # HTML Analysis
            html_analysis = self.ai_client.analyze_html(
                scraped_data['html_content'], 
                scraped_data['url']
            )
            
            # Parse HTML analysis result
            try:
                html_analysis_dict = json.loads(html_analysis.content)
            except json.JSONDecodeError:
                logger.warning("AI response not in JSON format, using raw response")
                html_analysis_dict = {
                    'raw_response': html_analysis.content,
                    'forms': [],
                    'buttons': [],
                    'links': [],
                    'navigation': []
                }
            
            # Generate BDD scenarios
            bdd_response = self.ai_client.generate_bdd_scenarios(html_analysis_dict)
            
            ai_end = time.time()
            self.performance_metrics['ai_response_time'] = ai_end - ai_start
            
            logger.info(f"AI analysis completed in {self.performance_metrics['ai_response_time']:.2f}s")
            
            return {
                'html_analysis': html_analysis_dict,
                'bdd_scenarios': bdd_response.content,
                'ai_model': ai_model,
                'tokens_used': html_analysis.tokens_used + bdd_response.tokens_used,
                'response_time': self.performance_metrics['ai_response_time']
            }
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            raise
    
    def _generate_bdd_scenarios(self, scraped_data: Dict, ai_analysis: Dict) -> List[Dict]:
        """Generate BDD scenarios"""
        try:
            # Generate BDD features
            bdd_features = self.bdd_generator.generate_bdd_from_analysis(
                scraped_data, ai_analysis['bdd_scenarios']
            )
            
            # Generate feature files
            feature_files = self.bdd_generator.generate_all_feature_files(bdd_features)
            
            # Convert to dict format
            features_dict = []
            for feature in bdd_features:
                scenarios_dict = []
                for scenario in feature.scenarios:
                    scenarios_dict.append({
                        'scenario': scenario.scenario,
                        'given': scenario.given,
                        'when': scenario.when,
                        'then': scenario.then,
                        'tags': scenario.tags,
                        'priority': scenario.priority,
                        'test_type': scenario.test_type
                    })
                
                features_dict.append({
                    'name': feature.name,
                    'description': feature.description,
                    'scenarios': scenarios_dict,
                    'background': feature.background,
                    'tags': feature.tags
                })
            
            logger.info(f"Generated {len(features_dict)} BDD features")
            return features_dict
            
        except Exception as e:
            logger.error(f"Error generating BDD scenarios: {e}")
            raise
    
    def _generate_test_code(self, bdd_features: List[Dict], scraped_data: Dict) -> str:
        """Generate test code"""
        try:
            # Generate test code
            test_code = self.test_generator.generate_test_code(bdd_features, scraped_data)
            
            # Save test code
            test_file_path = self.test_generator.save_test_code(test_code)
            
            logger.info(f"Test code generated and saved: {test_file_path}")
            return test_file_path
            
        except Exception as e:
            logger.error(f"Error generating test code: {e}")
            raise
    
    def _execute_tests(self, test_file_path: str) -> Any:
        """Execute tests"""
        try:
            # Run tests
            test_results = self.test_generator.run_tests(test_file_path)
            
            logger.info(f"Tests executed in {test_results.total_duration:.2f}s")
            return test_results
            
        except Exception as e:
            logger.error(f"Error executing tests: {e}")
            raise
    
    def _generate_reports(self, test_results: Any, bdd_features: List[Dict], 
                         scraped_data: Dict, ai_analysis: Dict) -> Dict[str, str]:
        """Generate reports"""
        try:
            # Create report data using the report generator's helper method
            report_data = self.report_generator.create_report_data(
                test_results, bdd_features, scraped_data, ai_analysis, self.performance_metrics
            )
            
            # Generate comprehensive report
            generated_reports = self.report_generator.generate_comprehensive_report(report_data)
            
            logger.info(f"Reports generated successfully")
            return generated_reports
            
        except Exception as e:
            logger.error(f"Error generating reports: {e}")
            raise
    
    def _cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'web_scraper'):
                self.web_scraper.close()
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_available_ai_models(self) -> List[str]:
        """Get list of available AI models"""
        try:
            return self.ai_client.get_available_models()
        except Exception as e:
            logger.error(f"Error getting AI models: {e}")
            return []
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        required_keys = ['ai', 'scraper', 'bdd', 'automation', 'reporting']
        
        for key in required_keys:
            if key not in self.config:
                logger.error(f"Missing configuration section: {key}")
                return False
        
        logger.info("Configuration validation passed")
        return True
    
    def quick_test(self, url: str, ai_model: str = None) -> bool:
        """Run quick test (scraping and AI analysis only)"""
        logger.info(f"Running quick test for: {url}")
        
        if not ai_model:
            ai_model = self.config.get('ai', {}).get('model', 'llama3:latest')
        
        try:
            # Step 1: Scrape website
            scraped_data = self._scrape_website(url)
            
            # Step 2: AI Analysis
            ai_analysis = self._analyze_with_ai(scraped_data, ai_model)
            
            logger.info("Quick test completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error in quick test: {e}")
            return False
        
        finally:
            self._cleanup()
    
    def get_execution_status(self) -> Dict:
        """Get current execution status"""
        return {
            'performance_metrics': self.performance_metrics,
            'config_valid': self.validate_config(),
            'available_models': self.get_available_ai_models()
        } 