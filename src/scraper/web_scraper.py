"""
Web Scraper Module
Extracts HTML content from websites using Selenium and BeautifulSoup
"""

import time
import asyncio
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import requests
from loguru import logger
import yaml
from pydantic import BaseModel
from urllib.parse import urljoin, urlparse
import json


class ScrapedData(BaseModel):
    """Scraped data structure"""
    url: str
    title: str
    html_content: str
    forms: List[Dict]
    links: List[Dict]
    buttons: List[Dict]
    inputs: List[Dict]
    images: List[Dict]
    meta_tags: List[Dict]
    page_structure: Dict
    load_time: float
    status_code: int


class WebScraper:
    """Web scraper for extracting HTML content and page elements"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.browser_type = self.config['scraper']['browser']
        self.headless = self.config['scraper']['headless']
        self.timeout = self.config['scraper']['timeout']
        self.wait_time = self.config['scraper']['wait_time']
        self.user_agent = self.config['scraper']['user_agent']
        self.driver = None
        
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
    
    def _setup_driver(self):
        """Setup WebDriver based on configuration"""
        if self.browser_type.lower() == 'chrome':
            options = ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument(f'--user-agent={self.user_agent}')
            options.add_argument('--window-size=1920,1080')
            
            # Use webdriver manager for automatic ChromeDriver management
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
        elif self.browser_type.lower() == 'firefox':
            options = FirefoxOptions()
            if self.headless:
                options.add_argument('--headless')
            options.set_preference("general.useragent.override", self.user_agent)
            
            self.driver = webdriver.Firefox(options=options)
            
        else:
            raise ValueError(f"Unsupported browser: {self.browser_type}")
        
        self.driver.set_page_load_timeout(self.timeout)
        self.driver.implicitly_wait(self.wait_time)
        logger.info(f"WebDriver setup completed: {self.browser_type}")
    
    async def scrape_website(self, url: str) -> ScrapedData:
        """Scrape website and extract all relevant data"""
        if not self.driver:
            self._setup_driver()
            
        start_time = time.time()
        
        try:
            logger.info(f"Starting to scrape: {url}")
            
            # Navigate to the website
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(self.wait_time)
            
            # Get page source
            html_content = self.driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract page data
            scraped_data = ScrapedData(
                url=url,
                title=self._extract_title(soup),
                html_content=html_content,
                forms=self._extract_forms(soup),
                links=self._extract_links(soup, url),
                buttons=self._extract_buttons(soup),
                inputs=self._extract_inputs(soup),
                images=self._extract_images(soup, url),
                meta_tags=self._extract_meta_tags(soup),
                page_structure=self._analyze_page_structure(soup),
                load_time=time.time() - start_time,
                status_code=200  # Assuming success if no exception
            )
            
            logger.info(f"Successfully scraped {url} in {scraped_data.load_time:.2f}s")
            return scraped_data
            
        except TimeoutException:
            logger.error(f"Timeout while loading {url}")
            raise
        except WebDriverException as e:
            logger.error(f"WebDriver error for {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while scraping {url}: {e}")
            raise
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else ""
    
    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all forms from the page"""
        forms = []
        
        for form in soup.find_all('form'):
            form_data = {
                'id': form.get('id', ''),
                'name': form.get('name', ''),
                'action': form.get('action', ''),
                'method': form.get('method', 'GET').upper(),
                'enctype': form.get('enctype', ''),
                'fields': []
            }
            
            # Extract form fields
            for field in form.find_all(['input', 'textarea', 'select']):
                field_data = {
                    'tag': field.name,
                    'type': field.get('type', 'text'),
                    'name': field.get('name', ''),
                    'id': field.get('id', ''),
                    'placeholder': field.get('placeholder', ''),
                    'required': field.has_attr('required'),
                    'value': field.get('value', ''),
                    'class': field.get('class', [])
                }
                
                if field.name == 'select':
                    field_data['options'] = [
                        {'value': opt.get('value', ''), 'text': opt.text.strip()}
                        for opt in field.find_all('option')
                    ]
                
                form_data['fields'].append(field_data)
            
            forms.append(form_data)
        
        return forms
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all links from the page"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            absolute_url = urljoin(base_url, href)
            
            link_data = {
                'text': link.text.strip(),
                'href': href,
                'absolute_url': absolute_url,
                'title': link.get('title', ''),
                'class': link.get('class', []),
                'id': link.get('id', ''),
                'target': link.get('target', ''),
                'is_external': urlparse(absolute_url).netloc != urlparse(base_url).netloc
            }
            
            links.append(link_data)
        
        return links
    
    def _extract_buttons(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all buttons from the page"""
        buttons = []
        
        # Find button tags
        for button in soup.find_all('button'):
            button_data = {
                'tag': 'button',
                'type': button.get('type', 'button'),
                'text': button.text.strip(),
                'id': button.get('id', ''),
                'name': button.get('name', ''),
                'class': button.get('class', []),
                'onclick': button.get('onclick', ''),
                'disabled': button.has_attr('disabled')
            }
            buttons.append(button_data)
        
        # Find input buttons
        for input_btn in soup.find_all('input', type=['button', 'submit', 'reset']):
            button_data = {
                'tag': 'input',
                'type': input_btn.get('type'),
                'text': input_btn.get('value', ''),
                'id': input_btn.get('id', ''),
                'name': input_btn.get('name', ''),
                'class': input_btn.get('class', []),
                'onclick': input_btn.get('onclick', ''),
                'disabled': input_btn.has_attr('disabled')
            }
            buttons.append(button_data)
        
        return buttons
    
    def _extract_inputs(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all input fields from the page"""
        inputs = []
        
        for input_field in soup.find_all('input'):
            input_data = {
                'type': input_field.get('type', 'text'),
                'name': input_field.get('name', ''),
                'id': input_field.get('id', ''),
                'placeholder': input_field.get('placeholder', ''),
                'value': input_field.get('value', ''),
                'class': input_field.get('class', []),
                'required': input_field.has_attr('required'),
                'readonly': input_field.has_attr('readonly'),
                'disabled': input_field.has_attr('disabled'),
                'maxlength': input_field.get('maxlength', ''),
                'minlength': input_field.get('minlength', ''),
                'pattern': input_field.get('pattern', '')
            }
            inputs.append(input_data)
        
        return inputs
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all images from the page"""
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src', '')
            absolute_url = urljoin(base_url, src) if src else ''
            
            image_data = {
                'src': src,
                'absolute_url': absolute_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'class': img.get('class', []),
                'id': img.get('id', ''),
                'width': img.get('width', ''),
                'height': img.get('height', '')
            }
            images.append(image_data)
        
        return images
    
    def _extract_meta_tags(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract meta tags from the page"""
        meta_tags = []
        
        for meta in soup.find_all('meta'):
            meta_data = {
                'name': meta.get('name', ''),
                'content': meta.get('content', ''),
                'property': meta.get('property', ''),
                'charset': meta.get('charset', ''),
                'http_equiv': meta.get('http-equiv', '')
            }
            meta_tags.append(meta_data)
        
        return meta_tags
    
    def _analyze_page_structure(self, soup: BeautifulSoup) -> Dict:
        """Analyze page structure and hierarchy"""
        structure = {
            'headings': {},
            'sections': [],
            'navigation': [],
            'footer': [],
            'sidebar': []
        }
        
        # Extract headings
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            if headings:
                structure['headings'][f'h{i}'] = [h.text.strip() for h in headings]
        
        # Extract sections
        for section in soup.find_all(['section', 'article', 'div'], class_=True):
            class_names = section.get('class', [])
            structure['sections'].append({
                'tag': section.name,
                'class': class_names,
                'id': section.get('id', '')
            })
        
        # Extract navigation
        for nav in soup.find_all(['nav', 'div'], class_=lambda x: x and any('nav' in str(c).lower() for c in x)):
            nav_links = nav.find_all('a')
            structure['navigation'].append({
                'class': nav.get('class', []),
                'links': [{'text': link.text.strip(), 'href': link.get('href', '')} for link in nav_links]
            })
        
        return structure
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot of the current page"""
        if not self.driver:
            raise Exception("WebDriver not initialized")
        
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
        
        screenshot_path = f"reports/screenshots/{filename}"
        self.driver.save_screenshot(screenshot_path)
        logger.info(f"Screenshot saved: {screenshot_path}")
        return screenshot_path
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("WebDriver closed")
    
    def __del__(self):
        """Cleanup on object deletion"""
        self.close() 