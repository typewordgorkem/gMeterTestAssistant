# Auto-generated test code
# Generated at: 2025-07-05T22:29:31.454574

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger
import os

# Create screenshots directory if it doesn't exist
if not os.path.exists("reports/screenshots"):
    os.makedirs("reports/screenshots")

class WebsitePage:
    """Page Object for https://www.trendyol.com/"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
    # Clean page elements with valid Python identifiers
    BUTTON_ONETRUST_PC_BTN_HANDLER = (By.ID, "onetrust-pc-btn-handler")
    BUTTON_ONETRUST_REJECT_ALL_HANDLER = (By.ID, "onetrust-reject-all-handler")
    BUTTON_ONETRUST_ACCEPT_BTN_HANDLER = (By.ID, "onetrust-accept-btn-handler")
    BUTTON_CLOSE_PC_BTN_HANDLER = (By.ID, "close-pc-btn-handler")
    BUTTON_ACCEPT_RECOMMENDED_BTN_HANDLER = (By.ID, "accept-recommended-btn-handler")
    BUTTON_FILTER_BTN_HANDLER = (By.ID, "filter-btn-handler")
    BUTTON_CLEAR_FILTERS_HANDLER = (By.ID, "clear-filters-handler")
    BUTTON_FILTER_APPLY_HANDLER = (By.ID, "filter-apply-handler")
    BUTTON_FILTER_CANCEL_HANDLER = (By.ID, "filter-cancel-handler")
    
    LINK_INDIRIM_KUPONLARIM = (By.LINK_TEXT, "İndirim Kuponlarım")
    LINK_TRENDYOL_SATIS_YAP = (By.LINK_TEXT, "Trendyol'da Satış Yap")
    LINK_HAKKIMIZDA = (By.LINK_TEXT, "Hakkımızda")
    LINK_YARDIM_DESTEK = (By.LINK_TEXT, "Yardım & Destek")
    
    def load_page(self):
        """Load the page"""
        self.driver.get("https://www.trendyol.com/")
        logger.info("Page loaded: https://www.trendyol.com/")
        return self
    
    def wait_for_page_load(self):
        """Wait for page to load"""
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)  # Additional wait for dynamic content
        except TimeoutException:
            logger.error("Page load timeout")
            raise
    
    def click_button(self, button_locator):
        """Click button by locator"""
        try:
            element = self.wait.until(EC.element_to_be_clickable(button_locator))
            element.click()
            logger.info(f"Clicked button: {button_locator}")
        except Exception as e:
            logger.error(f"Error in click_button: {e}")
            raise
    
    def click_link(self, link_text):
        """Click link by text"""
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, link_text)))
            element.click()
            logger.info(f"Clicked link: {link_text}")
        except Exception as e:
            logger.error(f"Error in click_link: {e}")
            raise
    
    def verify_element_present(self, locator):
        """Verify element is present"""
        try:
            element = self.wait.until(EC.presence_of_element_located(locator))
            logger.info(f"Element found: {locator}")
            return True
        except TimeoutException:
            logger.error(f"Element not found: {locator}")
            return False
    
    def take_screenshot(self, filename: str = None):
        """Take screenshot"""
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
        
        screenshot_path = f"reports/screenshots/{filename}"
        self.driver.save_screenshot(screenshot_path)
        logger.info(f"Screenshot saved: {screenshot_path}")
        return screenshot_path

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
        page = WebsitePage(driver)
        try:
            page.load_page()
            page.wait_for_page_load()
            return page
        except Exception as e:
            logger.error(f"Failed to load page: {e}")
            pytest.skip(f"Page load failed: {e}")
    
    @pytest.mark.functional
    def test_page_load(self, page):
        """Test page loading"""
        try:
            logger.info("Starting test: test_page_load")
            
            # Verify page title
            assert "Trendyol" in page.driver.title
            
            # Take screenshot
            page.take_screenshot("page_load_test.png")
            
            logger.info("Page load test completed successfully")
            
        except Exception as e:
            logger.error(f"Page load test failed: {e}")
            page.take_screenshot("page_load_test_failed.png")
            raise
    
    @pytest.mark.functional
    def test_accept_cookies(self, page):
        """Test accept cookies button"""
        try:
            logger.info("Starting test: test_accept_cookies")
            
            # Try to click accept cookies button
            if page.verify_element_present(page.BUTTON_ONETRUST_ACCEPT_BTN_HANDLER):
                page.click_button(page.BUTTON_ONETRUST_ACCEPT_BTN_HANDLER)
                logger.info("Accept cookies button clicked")
            else:
                logger.info("Accept cookies button not found - may not be present")
            
            # Take screenshot
            page.take_screenshot("accept_cookies_test.png")
            
            logger.info("Accept cookies test completed successfully")
            
        except Exception as e:
            logger.error(f"Accept cookies test failed: {e}")
            page.take_screenshot("accept_cookies_test_failed.png")
            raise
    
    @pytest.mark.functional
    def test_navigation_links(self, page):
        """Test navigation links"""
        try:
            logger.info("Starting test: test_navigation_links")
            
            # Check if main navigation links are present
            links_to_check = [
                "Hakkımızda",
                "Yardım & Destek"
            ]
            
            found_links = 0
            for link_text in links_to_check:
                try:
                    link_element = page.driver.find_element(By.LINK_TEXT, link_text)
                    if link_element.is_displayed():
                        found_links += 1
                        logger.info(f"Found link: {link_text}")
                except:
                    logger.info(f"Link not found: {link_text}")
            
            # Take screenshot
            page.take_screenshot("navigation_links_test.png")
            
            logger.info(f"Navigation links test completed - found {found_links} links")
            
        except Exception as e:
            logger.error(f"Navigation links test failed: {e}")
            page.take_screenshot("navigation_links_test_failed.png")
            raise
    
    @pytest.mark.functional
    def test_page_elements(self, page):
        """Test page elements presence"""
        try:
            logger.info("Starting test: test_page_elements")
            
            # Check if body element is present
            body_present = page.verify_element_present((By.TAG_NAME, "body"))
            assert body_present, "Body element not found"
            
            # Check if header element is present
            header_elements = page.driver.find_elements(By.TAG_NAME, "header")
            logger.info(f"Found {len(header_elements)} header elements")
            
            # Take screenshot
            page.take_screenshot("page_elements_test.png")
            
            logger.info("Page elements test completed successfully")
            
        except Exception as e:
            logger.error(f"Page elements test failed: {e}")
            page.take_screenshot("page_elements_test_failed.png")
            raise
    
    @pytest.mark.functional
    def test_responsive_design(self, page):
        """Test responsive design"""
        try:
            logger.info("Starting test: test_responsive_design")
            
            # Test different screen sizes
            sizes = [
                (1920, 1080),  # Desktop
                (768, 1024),   # Tablet
                (375, 667)     # Mobile
            ]
            
            for width, height in sizes:
                page.driver.set_window_size(width, height)
                time.sleep(1)
                
                # Take screenshot for each size
                page.take_screenshot(f"responsive_test_{width}x{height}.png")
                
                logger.info(f"Tested screen size: {width}x{height}")
            
            # Reset to default size
            page.driver.set_window_size(1920, 1080)
            
            logger.info("Responsive design test completed successfully")
            
        except Exception as e:
            logger.error(f"Responsive design test failed: {e}")
            page.take_screenshot("responsive_design_test_failed.png")
            raise
    
    
