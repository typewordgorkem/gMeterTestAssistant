# Auto-generated test code for Ofix.com
# Generated at: 2025-07-05T23:29:44.367703

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from loguru import logger
import os


class OfixWebsitePage:
    """Page Object for https://www.ofix.com/"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.url = "https://www.ofix.com/"
    
    def load_page(self):
        """Load the Ofix page"""
        self.driver.get(self.url)
        logger.info("Page loaded: https://www.ofix.com/")
        return self
    
    def wait_for_page_load(self):
        """Wait for page to load completely"""
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)  # Additional wait for dynamic content
            logger.info("Page fully loaded")
        except TimeoutException:
            logger.error("Page load timeout")
            raise
    
    def find_search_button(self):
        """Find search button on page"""
        try:
            # Try different search button selectors
            search_selectors = [
                "//button[contains(text(), 'Ara')]",
                "//button[contains(@class, 'search')]",
                "//input[@type='submit']",
                "//button[@type='submit']",
                ".search-button",
                "#search-button"
            ]
            
            for selector in search_selectors:
                try:
                    if selector.startswith("//"):
                        element = self.driver.find_element(By.XPATH, selector)
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return element
                except NoSuchElementException:
                    continue
            
            logger.warning("Search button not found")
            return None
        except Exception as e:
            logger.error(f"Error finding search button: {e}")
            return None
    
    def find_navigation_links(self):
        """Find navigation links"""
        try:
            # Find all navigation links
            nav_links = self.driver.find_elements(By.CSS_SELECTOR, "nav a, .nav a, .navbar a, .menu a")
            if not nav_links:
                nav_links = self.driver.find_elements(By.TAG_NAME, "a")
            
            # Filter only visible links
            visible_links = []
            for link in nav_links[:10]:  # Limit to first 10 links
                if link.is_displayed() and link.text.strip():
                    visible_links.append(link)
            
            return visible_links
        except Exception as e:
            logger.error(f"Error finding navigation links: {e}")
            return []
    
    def take_screenshot(self, filename: str):
        """Take screenshot"""
        try:
            # Ensure screenshots directory exists
            os.makedirs("reports/screenshots", exist_ok=True)
            
            screenshot_path = f"reports/screenshots/{filename}"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None


class TestOfixWebsite:
    """Automated tests for Ofix.com website"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Setup WebDriver for testing"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Use webdriver manager for Chrome
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        driver.implicitly_wait(10)
        
        # Execute script to hide automation
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        yield driver
        driver.quit()
    
    @pytest.fixture(scope="function")
    def page(self, driver):
        """Setup page object for each test"""
        page = OfixWebsitePage(driver)
        try:
            page.load_page()
            page.wait_for_page_load()
            return page
        except Exception as e:
            logger.error(f"Failed to load page: {e}")
            pytest.fail(f"Page load failed: {e}")
    
    def test_page_load(self, page):
        """Test page loads successfully"""
        try:
            logger.info("Testing page load...")
            
            # Check if page URL is correct
            assert "ofix.com" in page.driver.current_url
            
            # Check page title
            title = page.driver.title
            assert title is not None and len(title) > 0
            logger.info(f"Page title: {title}")
            
            # Take screenshot
            page.take_screenshot("ofix_page_load_test.png")
            
            logger.info("✅ Page load test passed")
            
        except Exception as e:
            logger.error(f"❌ Page load test failed: {e}")
            page.take_screenshot("ofix_page_load_test_failure.png")
            raise
    
    def test_page_elements(self, page):
        """Test basic page elements are present"""
        try:
            logger.info("Testing page elements...")
            
            # Check if body element exists
            body = page.driver.find_element(By.TAG_NAME, "body")
            assert body is not None
            
            # Check if there are any links on the page
            links = page.driver.find_elements(By.TAG_NAME, "a")
            assert len(links) > 0
            logger.info(f"Found {len(links)} links on page")
            
            # Check if there are any buttons
            buttons = page.driver.find_elements(By.TAG_NAME, "button")
            logger.info(f"Found {len(buttons)} buttons on page")
            
            # Take screenshot
            page.take_screenshot("ofix_page_elements_test.png")
            
            logger.info("✅ Page elements test passed")
            
        except Exception as e:
            logger.error(f"❌ Page elements test failed: {e}")
            page.take_screenshot("ofix_page_elements_test_failure.png")
            raise
    
    def test_navigation_links(self, page):
        """Test navigation links are present and accessible"""
        try:
            logger.info("Testing navigation links...")
            
            # Find navigation links
            nav_links = page.find_navigation_links()
            assert len(nav_links) > 0
            
            logger.info(f"Found {len(nav_links)} navigation links")
            
            # Test first few links
            for i, link in enumerate(nav_links[:3]):
                try:
                    link_text = link.text.strip()
                    link_href = link.get_attribute("href")
                    
                    if link_text and link_href:
                        logger.info(f"Link {i+1}: {link_text} -> {link_href}")
                        assert link.is_displayed()
                        assert link.is_enabled()
                    
                except Exception as e:
                    logger.warning(f"Issue with link {i+1}: {e}")
                    continue
            
            # Take screenshot
            page.take_screenshot("ofix_navigation_links_test.png")
            
            logger.info("✅ Navigation links test passed")
            
        except Exception as e:
            logger.error(f"❌ Navigation links test failed: {e}")
            page.take_screenshot("ofix_navigation_links_test_failure.png")
            raise
    
    def test_search_functionality(self, page):
        """Test search functionality if available"""
        try:
            logger.info("Testing search functionality...")
            
            # Find search button
            search_button = page.find_search_button()
            
            if search_button:
                logger.info("Search button found")
                assert search_button.is_displayed()
                
                # Take screenshot
                page.take_screenshot("ofix_search_functionality_test.png")
                
                logger.info("✅ Search functionality test passed")
            else:
                logger.info("⚠️ Search button not found - test skipped")
                page.take_screenshot("ofix_search_functionality_test_no_button.png")
                pytest.skip("Search button not found on page")
            
        except Exception as e:
            logger.error(f"❌ Search functionality test failed: {e}")
            page.take_screenshot("ofix_search_functionality_test_failure.png")
            raise
    
    def test_responsive_design(self, page):
        """Test responsive design at different screen sizes"""
        try:
            logger.info("Testing responsive design...")
            
            # Test different screen sizes
            screen_sizes = [
                (1920, 1080, "desktop"),
                (768, 1024, "tablet"),
                (375, 667, "mobile")
            ]
            
            for width, height, device in screen_sizes:
                try:
                    # Set window size
                    page.driver.set_window_size(width, height)
                    time.sleep(2)  # Wait for layout to adjust
                    
                    # Check if page is still functional
                    body = page.driver.find_element(By.TAG_NAME, "body")
                    assert body is not None
                    
                    # Take screenshot
                    page.take_screenshot(f"ofix_responsive_test_{device}_{width}x{height}.png")
                    
                    logger.info(f"✅ Responsive test passed for {device} ({width}x{height})")
                    
                except Exception as e:
                    logger.error(f"❌ Responsive test failed for {device}: {e}")
                    page.take_screenshot(f"ofix_responsive_test_{device}_{width}x{height}_failure.png")
                    continue
            
            # Reset to default size
            page.driver.set_window_size(1920, 1080)
            
            logger.info("✅ Responsive design test completed")
            
        except Exception as e:
            logger.error(f"❌ Responsive design test failed: {e}")
            page.take_screenshot("ofix_responsive_design_test_failure.png")
            raise 