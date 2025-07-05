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
    
    def scrape_website(self, url: str) -> ScrapedData:
        """Scrape complete website data"""
        logger.info(f"Starting to scrape: {url}")
        
        start_time = time.time()
        
        try:
            # Setup driver if not already initialized
            if self.driver is None:
                self._setup_driver()
            
            # Navigate to URL
            self.driver.get(url)
            
            # Wait for page load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page metadata
            title = self.driver.title
            current_url = self.driver.current_url
            
            # Get page source
            html_content = self.driver.page_source
            
            # Extract all elements
            forms = self._extract_forms()
            buttons = self._extract_buttons()
            links = self._extract_links()
            inputs = self._extract_inputs()
            images = self._extract_images()
            meta_tags = self._extract_meta_tags()
            page_structure = self._analyze_page_structure()
            
            end_time = time.time()
            load_time = end_time - start_time
            
            scraped_data = ScrapedData(
                url=current_url,
                title=title,
                html_content=html_content,
                forms=forms,
                links=links,
                buttons=buttons,
                inputs=inputs,
                images=images,
                meta_tags=meta_tags,
                page_structure=page_structure,
                load_time=load_time,
                status_code=200  # Assuming success if we got here
            )
            
            logger.info(f"Successfully scraped {url} in {load_time:.2f}s")
            return scraped_data
            
        except Exception as e:
            logger.error(f"Error scraping website {url}: {e}")
            raise
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else ""
    
    def _extract_forms(self) -> List[Dict]:
        """Extract all forms from the page"""
        forms = []
        try:
            form_elements = self.driver.find_elements(By.TAG_NAME, "form")
            
            for form in form_elements:
                form_data = {
                    'id': form.get_attribute('id') or '',
                    'name': form.get_attribute('name') or '',
                    'action': form.get_attribute('action') or '',
                    'method': form.get_attribute('method') or 'get',
                    'fields': []
                }
                
                # Find input fields within form
                inputs = form.find_elements(By.TAG_NAME, "input")
                for inp in inputs:
                    field = {
                        'name': inp.get_attribute('name') or '',
                        'type': inp.get_attribute('type') or 'text',
                        'id': inp.get_attribute('id') or '',
                        'placeholder': inp.get_attribute('placeholder') or '',
                        'required': inp.get_attribute('required') == 'true'
                    }
                    form_data['fields'].append(field)
                
                forms.append(form_data)
                
        except Exception as e:
            logger.warning(f"Error extracting forms: {e}")
            
        return forms
    
    def _extract_links(self) -> List[Dict]:
        """Extract all links from the page"""
        links = []
        try:
            link_elements = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in link_elements:
                href = link.get_attribute('href')
                if href:  # Only include links with href
                    link_data = {
                        'text': link.text.strip() or '',
                        'href': href,
                        'title': link.get_attribute('title') or '',
                        'target': link.get_attribute('target') or '',
                        'class': link.get_attribute('class') or ''
                    }
                    links.append(link_data)
                    
        except Exception as e:
            logger.warning(f"Error extracting links: {e}")
            
        return links
    
    def _extract_buttons(self) -> List[Dict]:
        """Extract all buttons from the page"""
        buttons = []
        try:
            # Find button elements
            button_elements = self.driver.find_elements(By.TAG_NAME, "button")
            input_buttons = self.driver.find_elements(By.XPATH, "//input[@type='button' or @type='submit']")
            
            all_buttons = button_elements + input_buttons
            
            for button in all_buttons:
                button_data = {
                    'text': button.text or button.get_attribute('value') or '',
                    'id': button.get_attribute('id') or '',
                    'name': button.get_attribute('name') or '',
                    'type': button.get_attribute('type') or 'button',
                    'class': button.get_attribute('class') or '',
                    'onclick': button.get_attribute('onclick') or ''
                }
                buttons.append(button_data)
                
        except Exception as e:
            logger.warning(f"Error extracting buttons: {e}")
            
        return buttons
    
    def _extract_inputs(self) -> List[Dict]:
        """Extract all input elements from the page"""
        inputs = []
        try:
            input_elements = self.driver.find_elements(By.TAG_NAME, "input")
            
            for inp in input_elements:
                input_data = {
                    'name': inp.get_attribute('name') or '',
                    'type': inp.get_attribute('type') or 'text',
                    'id': inp.get_attribute('id') or '',
                    'placeholder': inp.get_attribute('placeholder') or '',
                    'value': inp.get_attribute('value') or '',
                    'required': inp.get_attribute('required') == 'true',
                    'class': inp.get_attribute('class') or ''
                }
                inputs.append(input_data)
                
        except Exception as e:
            logger.warning(f"Error extracting inputs: {e}")
            
        return inputs
    
    def _extract_images(self) -> List[Dict]:
        """Extract all images from the page"""
        images = []
        try:
            img_elements = self.driver.find_elements(By.TAG_NAME, "img")
            
            for img in img_elements:
                src = img.get_attribute('src')
                if src:  # Only include images with src
                    image_data = {
                        'src': src,
                        'alt': img.get_attribute('alt') or '',
                        'title': img.get_attribute('title') or '',
                        'class': img.get_attribute('class') or '',
                        'width': img.get_attribute('width') or '',
                        'height': img.get_attribute('height') or ''
                    }
                    images.append(image_data)
                    
        except Exception as e:
            logger.warning(f"Error extracting images: {e}")
            
        return images
    
    def _extract_meta_tags(self) -> List[Dict]:
        """Extract meta tags from the page"""
        meta_tags = []
        try:
            meta_elements = self.driver.find_elements(By.TAG_NAME, "meta")
            
            for meta in meta_elements:
                meta_data = {
                    'name': meta.get_attribute('name') or '',
                    'property': meta.get_attribute('property') or '',
                    'content': meta.get_attribute('content') or '',
                    'charset': meta.get_attribute('charset') or ''
                }
                meta_tags.append(meta_data)
                
        except Exception as e:
            logger.warning(f"Error extracting meta tags: {e}")
            
        return meta_tags
    
    def _analyze_page_structure(self) -> Dict:
        """Analyze page structure"""
        structure = {}
        try:
            # Count main elements
            structure['total_elements'] = len(self.driver.find_elements(By.XPATH, "//*"))
            structure['divs'] = len(self.driver.find_elements(By.TAG_NAME, "div"))
            structure['spans'] = len(self.driver.find_elements(By.TAG_NAME, "span"))
            structure['paragraphs'] = len(self.driver.find_elements(By.TAG_NAME, "p"))
            structure['headings'] = len(self.driver.find_elements(By.XPATH, "//h1 | //h2 | //h3 | //h4 | //h5 | //h6"))
            structure['tables'] = len(self.driver.find_elements(By.TAG_NAME, "table"))
            structure['lists'] = len(self.driver.find_elements(By.XPATH, "//ul | //ol"))
            
        except Exception as e:
            logger.warning(f"Error analyzing page structure: {e}")
            
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