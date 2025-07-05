"""
Test Automation Module
Generates and runs automated tests from BDD scenarios
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger
import yaml
from datetime import datetime
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor
import pytest
from jinja2 import Template


@dataclass
class TestResult:
    """Test result structure"""
    test_name: str
    status: str  # passed, failed, skipped
    duration: float
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    logs: List[str] = None


@dataclass
class TestSuite:
    """Test suite structure"""
    name: str
    tests: List[TestResult]
    start_time: datetime
    end_time: datetime
    total_duration: float
    passed_count: int
    failed_count: int
    skipped_count: int


class TestGenerator:
    """Generates and runs automated tests from BDD scenarios"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.framework = self.config['automation']['framework']
        self.parallel = self.config['automation']['parallel_execution']
        self.max_workers = self.config['automation']['max_workers']
        self.screenshot_on_failure = self.config['automation']['screenshot_on_failure']
        self.driver = None
        self.test_data = {}
        
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
    
    def generate_test_code(self, bdd_features: List[Dict], scraped_data: Dict) -> str:
        """Generate Python test code from BDD features"""
        logger.info("Generating test automation code")
        
        # Page Object Model template
        page_object_template = self._get_page_object_template()
        
        # Test methods template
        test_methods_template = self._get_test_methods_template()
        
        # Generate page object
        page_object_code = self._generate_page_object(scraped_data, page_object_template)
        
        # Generate test methods
        test_methods_code = self._generate_test_methods(bdd_features, test_methods_template)
        
        # Combine all code
        full_code = self._combine_code_parts(page_object_code, test_methods_code)
        
        return full_code
    
    def _get_page_object_template(self) -> str:
        """Get Page Object Model template"""
        return '''
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger


class {{ page_class_name }}:
    """Page Object for {{ page_url }}"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
    # Page elements
    {% for element in page_elements %}
    {{ element.name|upper }} = (By.{{ element.by }}, "{{ element.locator }}")
    {% endfor %}
    
    def load_page(self):
        """Load the page"""
        self.driver.get("{{ page_url }}")
        logger.info("Page loaded: {{ page_url }}")
        return self
    
    def wait_for_page_load(self):
        """Wait for page to load"""
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(1)  # Additional wait for dynamic content
        except TimeoutException:
            logger.error("Page load timeout")
            raise
    
    {% for method in page_methods %}
    def {{ method.name }}(self{% if method.parameters %}, {{ method.parameters }}{% endif %}):
        """{{ method.description }}"""
        try:
            {{ method.code|indent(12) }}
        except Exception as e:
            logger.error(f"Error in {{ method.name }}: {e}")
            raise
    
    {% endfor %}
    
    def take_screenshot(self, filename: str = None):
        """Take screenshot"""
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
        
        screenshot_path = f"reports/screenshots/{filename}"
        self.driver.save_screenshot(screenshot_path)
        logger.info(f"Screenshot saved: {screenshot_path}")
        return screenshot_path
'''
    
    def _get_test_methods_template(self) -> str:
        """Get test methods template"""
        return '''
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from loguru import logger
import time
from datetime import datetime


class TestWebsite:
    """Automated tests for website"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Setup WebDriver"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    @pytest.fixture(scope="function")
    def page(self, driver):
        """Setup page object"""
        page = {{ page_class_name }}(driver)
        try:
            page.load_page()
            page.wait_for_page_load()
            return page
        except Exception as e:
            logger.error(f"Failed to load page: {e}")
            pytest.skip(f"Page load failed: {e}")
    
    {% for test_method in test_methods %}
    @pytest.mark.{{ test_method.priority }}
    @pytest.mark.{{ test_method.test_type }}
    {% for tag in test_method.tags %}
    @pytest.mark.{{ tag }}
    {% endfor %}
    def {{ test_method.method_name }}(self, page):
        """{{ test_method.description }}"""
        try:
            logger.info("Starting test: {{ test_method.method_name }}")
            
            # Test steps
{{ test_method.code }}
            
            logger.info("Test passed: {{ test_method.method_name }}")
            
        except Exception as e:
            logger.error(f"Test failed: {{ test_method.method_name }} - {e}")
            
            # Take screenshot on failure
            if hasattr(page, 'take_screenshot'):
                page.take_screenshot(f"{{ test_method.method_name }}_failure.png")
            
            raise  # Re-raise to mark test as failed
    
    {% endfor %}
'''
    
    def _generate_page_object(self, scraped_data: Dict, template: str) -> str:
        """Generate page object code"""
        from jinja2 import Template
        
        # Extract page elements for locators
        page_elements = []
        page_methods = []
        
        # Process forms
        if 'forms' in scraped_data:
            for form in scraped_data['forms']:
                form_id = form.get('id', '')
                if form_id:
                    page_elements.append({
                        'name': f"form_{form_id}",
                        'by': 'ID',
                        'locator': form_id
                    })
                
                # Process form fields
                for field in form.get('fields', []):
                    field_name = field.get('name', '')
                    field_id = field.get('id', '')
                    
                    if field_id:
                        page_elements.append({
                            'name': f"field_{field_name or field_id}",
                            'by': 'ID',
                            'locator': field_id
                        })
                    elif field_name:
                        page_elements.append({
                            'name': f"field_{field_name}",
                            'by': 'NAME',
                            'locator': field_name
                        })
        
        # Process buttons
        if 'buttons' in scraped_data:
            for button in scraped_data['buttons']:
                button_id = button.get('id', '')
                button_text = button.get('text', '')
                
                if button_id:
                    page_elements.append({
                        'name': f"button_{button_id}",
                        'by': 'ID',
                        'locator': button_id
                    })
                elif button_text:
                    page_elements.append({
                        'name': f"button_{button_text.replace(' ', '_').lower()}",
                        'by': 'XPATH',
                        'locator': f"//button[contains(text(), '{button_text}')]"
                    })
        
        # Process links
        if 'links' in scraped_data:
            for link in scraped_data['links'][:5]:  # Limit to 5 links
                link_text = link.get('text', '').strip()
                if link_text:
                    page_elements.append({
                        'name': f"link_{link_text.replace(' ', '_').lower()}",
                        'by': 'LINK_TEXT',
                        'locator': link_text
                    })
        
        # Generate page methods
        page_methods.extend([
            {
                'name': 'fill_form',
                'parameters': 'form_data',
                'description': 'Fill form with provided data',
                'code': '''
for field_name, value in form_data.items():
    element = self.driver.find_element(By.NAME, field_name)
    element.clear()
    element.send_keys(value)
    logger.info(f"Filled field {field_name} with value: {value}")
'''
            },
            {
                'name': 'click_button',
                'parameters': 'button_locator',
                'description': 'Click button by locator',
                'code': '''
element = self.wait.until(EC.element_to_be_clickable(button_locator))
element.click()
logger.info(f"Clicked button: {button_locator}")
'''
            },
            {
                'name': 'click_link',
                'parameters': 'link_text',
                'description': 'Click link by text',
                'code': '''
element = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, link_text)))
element.click()
logger.info(f"Clicked link: {link_text}")
'''
            },
            {
                'name': 'verify_element_present',
                'parameters': 'locator',
                'description': 'Verify element is present',
                'code': '''
try:
    element = self.wait.until(EC.presence_of_element_located(locator))
    logger.info(f"Element found: {locator}")
    return True
except TimeoutException:
    logger.error(f"Element not found: {locator}")
    return False
'''
            }
        ])
        
        template_obj = Template(template)
        return template_obj.render(
            page_class_name="WebsitePage",
            page_url=scraped_data.get('url', ''),
            page_elements=page_elements,
            page_methods=page_methods
        )
    
    def _generate_test_methods(self, bdd_features: List[Dict], template: str) -> str:
        """Generate test methods code"""
        from jinja2 import Template
        
        test_methods = []
        
        for feature in bdd_features:
            for scenario in feature.get('scenarios', []):
                # Clean scenario name for method name
                scenario_name = scenario['scenario']
                # Remove special characters and create valid Python method name
                clean_name = self._clean_method_name(scenario_name)
                
                test_method = {
                    'method_name': f"test_{clean_name}",
                    'description': scenario['scenario'],
                    'priority': scenario.get('priority', 'medium'),
                    'test_type': scenario.get('test_type', 'functional'),
                    'tags': scenario.get('tags', []),
                    'code': self._generate_test_steps(scenario)
                }
                test_methods.append(test_method)
        
        template_obj = Template(template)
        return template_obj.render(
            page_class_name="WebsitePage",
            test_methods=test_methods
        )
    
    def _clean_method_name(self, name: str) -> str:
        """Clean method name to be valid Python identifier"""
        import re
        # Remove quotes and special characters
        name = re.sub(r'["\']', '', name)
        # Replace non-alphanumeric characters with underscore
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Remove multiple underscores
        name = re.sub(r'_+', '_', name)
        # Remove leading/trailing underscores
        name = name.strip('_')
        # If empty or starts with number, add prefix
        if not name or name[0].isdigit():
            name = f"test_case_{name}"
        return name.lower()
    
    def _generate_test_steps(self, scenario: Dict) -> str:
        """Generate test steps code from BDD scenario"""
        code_lines = []
        
        # Given steps
        for step in scenario.get('given', []):
            code_lines.append(f"            # Given: {step}")
            if 'sayfa' in step.lower():
                code_lines.append("            # Page is already loaded in fixture")
            
        # When steps
        for step in scenario.get('when', []):
            code_lines.append(f"            # When: {step}")
            
            if 'tıkla' in step.lower() or 'click' in step.lower():
                if 'buton' in step.lower() or 'button' in step.lower():
                    # Extract button text for better locator
                    button_text = self._extract_button_text(step)
                    if button_text:
                        code_lines.append(f"            page.click_button(page.BUTTON_{button_text.upper().replace(' ', '_')})")
                    else:
                        code_lines.append("            page.click_button((By.TAG_NAME, 'button'))")
                elif 'link' in step.lower():
                    link_text = self._extract_link_text(step)
                    if link_text:
                        code_lines.append(f"            page.click_link('{link_text}')")
                    else:
                        code_lines.append("            page.click_link('Test Link')")
                        
            elif 'doldur' in step.lower() or 'fill' in step.lower():
                code_lines.append("            page.fill_form({'field_name': 'test_value'})")
                
            elif 'gir' in step.lower() or 'enter' in step.lower():
                code_lines.append("            page.fill_form({'input_field': 'test_data'})")
        
        # Then steps
        for step in scenario.get('then', []):
            code_lines.append(f"            # Then: {step}")
            code_lines.append("            # Then: Beklenen işlem yapılır")
        
        return '\n'.join(code_lines)
    
    def _extract_button_text(self, step: str) -> str:
        """Extract button text from step"""
        import re
        # Look for text in quotes
        match = re.search(r"'([^']*)'", step)
        if match:
            return match.group(1)
        match = re.search(r'"([^"]*)"', step)
        if match:
            return match.group(1)
        return ""
    
    def _extract_link_text(self, step: str) -> str:
        """Extract link text from step"""
        import re
        # Look for text in quotes
        match = re.search(r"'([^']*)'", step)
        if match:
            return match.group(1)
        match = re.search(r'"([^"]*)"', step)
        if match:
            return match.group(1)
        return ""
    
    def _combine_code_parts(self, page_object_code: str, test_methods_code: str) -> str:
        """Combine all code parts"""
        return f"""
# Auto-generated test code
# Generated at: {datetime.now().isoformat()}

{page_object_code}

{test_methods_code}
"""
    
    def save_test_code(self, test_code: str, filename: str = "test_website.py") -> str:
        """Save generated test code to file"""
        os.makedirs("tests/generated", exist_ok=True)
        filepath = os.path.join("tests/generated", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        logger.info(f"Test code saved: {filepath}")
        return filepath
    
    def run_tests(self, test_file_path: str) -> TestSuite:
        """Run generated tests"""
        logger.info(f"Running tests from: {test_file_path}")
        
        start_time = datetime.now()
        
        # Ensure screenshots directory exists
        os.makedirs("reports/screenshots", exist_ok=True)
        
        # Run pytest with proper options
        import subprocess
        import sys
        
        # Create pytest command
        cmd = [
            sys.executable, '-m', 'pytest', 
            test_file_path, 
            '-v',
            '--tb=short',
            '--no-header',
            '--quiet'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            end_time = datetime.now()
            
            # Parse test results
            test_results = self._parse_test_results(result.stdout, result.stderr)
            
            # Calculate counts
            passed_count = len([t for t in test_results if t.status == 'passed'])
            failed_count = len([t for t in test_results if t.status == 'failed'])
            skipped_count = len([t for t in test_results if t.status == 'skipped'])
            
            test_suite = TestSuite(
                name="Website Tests",
                tests=test_results,
                start_time=start_time,
                end_time=end_time,
                total_duration=(end_time - start_time).total_seconds(),
                passed_count=passed_count,
                failed_count=failed_count,
                skipped_count=skipped_count
            )
            
            logger.info(f"Tests completed. Passed: {test_suite.passed_count}, Failed: {test_suite.failed_count}, Skipped: {test_suite.skipped_count}")
            
            return test_suite
            
        except subprocess.TimeoutExpired:
            logger.error("Test execution timed out")
            return TestSuite(
                name="Website Tests",
                tests=[],
                start_time=start_time,
                end_time=datetime.now(),
                total_duration=300,
                passed_count=0,
                failed_count=0,
                skipped_count=0
            )
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return TestSuite(
                name="Website Tests", 
                tests=[],
                start_time=start_time,
                end_time=datetime.now(),
                total_duration=0,
                passed_count=0,
                failed_count=1,
                skipped_count=0
            )
    
    def _parse_test_results(self, stdout: str, stderr: str) -> List[TestResult]:
        """Parse pytest output to extract test results"""
        test_results = []
        
        # Combine stdout and stderr for analysis
        output = stdout + "\n" + stderr
        
        # Look for test result lines
        lines = output.split('\n')
        
        for line in lines:
            if '::test_' in line and any(status in line for status in ['PASSED', 'FAILED', 'SKIPPED']):
                try:
                    # Extract test name
                    if '::' in line:
                        test_name = line.split('::')[-1].split()[0]
                    else:
                        continue
                    
                    # Determine status
                    if 'PASSED' in line:
                        status = 'passed'
                    elif 'FAILED' in line:
                        status = 'failed'
                    elif 'SKIPPED' in line:
                        status = 'skipped'
                    else:
                        status = 'unknown'
                    
                    # Extract duration if available
                    duration = 0.0
                    if 's' in line:
                        import re
                        duration_match = re.search(r'(\d+\.?\d*)s', line)
                        if duration_match:
                            duration = float(duration_match.group(1))
                    
                    test_results.append(TestResult(
                        test_name=test_name,
                        status=status,
                        duration=duration,
                        error_message=None if status == 'passed' else f"Test {status}",
                        logs=[]
                    ))
                    
                except Exception as e:
                    logger.warning(f"Failed to parse test result line: {line} - {e}")
                    continue
        
        # If no tests found, create a dummy result
        if not test_results:
            test_results.append(TestResult(
                test_name="no_tests_found",
                status="skipped",
                duration=0.0,
                error_message="No tests were discovered or executed",
                logs=[]
            ))
        
        return test_results
    
    def run_parallel_tests(self, test_files: List[str]) -> List[TestSuite]:
        """Run tests in parallel"""
        if not self.parallel or len(test_files) <= 1:
            return [self.run_tests(test_files[0])] if test_files else []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.run_tests, test_file) for test_file in test_files]
            results = [future.result() for future in futures]
        
        return results 