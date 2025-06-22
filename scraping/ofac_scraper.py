import logging
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from config import settings

logger = logging.getLogger(__name__)

class OfacScraper:
    """
    Handles web scraping of the OFAC sanctions list search platform.

    This class automates the process of searching for individuals on the OFAC platform,
    parsing the results, taking screenshots, and resetting the search form.
    """

    def __init__(self):
        """
        Initializes the Selenium WebDriver with Chrome in headless mode.
        Raises an exception if the driver cannot be initialized.
        """
        try:
            service = ChromeService(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument("--headless") # Run Chrome without UI
            options.add_argument("--no-sandbox") # Disable sandbox (needed in some environments)
            options.add_argument("--disable-dev-shm-usage") # Avoid /dev/shm issues in containers
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 70)
            logger.info("WebDriver initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def search_person(self, name: str, address: str, country: str) -> int:
        """
        Performs a search on the OFAC platform for a given person.

        Args:
            name    (str): The person's name to search for.
            address (str): The person's address.
            country (str): The country to select in the dropdown.

        Returns:
            int: The number of results found, or -1 if an error occurs.
        """
        try:
            self.driver.get(settings.OFAC_URL)

            # Fill in the search form fields
            self.wait.until(EC.presence_of_element_located((By.ID, "ctl00_MainContent_txtLastName"))).send_keys(name)
            self.driver.find_element(By.ID, "ctl00_MainContent_txtAddress").send_keys(address)
            country_dropdown = Select(self.driver.find_element(By.ID, "ctl00_MainContent_ddlCountry"))
            country_dropdown.select_by_visible_text(country)

            # Submit the search form
            self.driver.find_element(By.ID, "ctl00_MainContent_btnSearch").click()

            # Wait for and parse the results
            results_element = self.wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_MainContent_lblResults"))
            )
            return self._parse_results(results_element.text)

        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Error searching for '{name}': Element not found or timed out. Details: {e}")
            return -1
        except Exception as e:
            logger.error(f"Unexpected error during search for '{name}': {e}")
            return -1

    def _parse_results(self, result_text: str) -> int:
        """
        Extracts the number of matches from the result text.

        Args:
            result_text (str): The text containing the result count.

        Returns:
            int: The parsed number of results, or 0 if parsing fails.
        """
        match = re.search(r'(\d+)', result_text)
        if match:
            count = int(match.group(1))
            logger.info(f"Parsed result count: {count}")
            return count
        logger.warning(f"Could not parse result count from text: '{result_text}'")
        return 0

    def take_screenshot(self, person_id: int):
        """
        Takes a screenshot of the current page and saves it with a standardized filename.

        Args:
            person_id (int): The ID of the person being searched.
        """
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            today = datetime.now().strftime('%Y%m%d')
            filename = f"{today}_{person_id}.png"
            filepath = settings.SCREENSHOTS_DIR / filename
            self.driver.save_screenshot(str(filepath))
            logger.info(f"Screenshot saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to take screenshot for person ID {person_id}: {e}")

    def reset_search_form(self):
        """
        Resets the search form to clear all fields for the next search.
        """
        try:
            self.driver.find_element(By.ID, "ctl00_MainContent_btnReset").click()
            logger.info("Search form has been reset.")
        except Exception as e:
            logger.error(f"Could not reset the search form: {e}")

    def close(self):
        """
        Closes the Selenium WebDriver.
        """
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed.")