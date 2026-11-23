import os
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = os.getenv("BASE_URL", "http://cicd-assignment-web")


@pytest.fixture
def driver():

    options = Options()

    options.binary_location = os.getenv(
        "CHROME_BIN", "/usr/bin/chromium"
    )

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1365,900")

    service = Service(
        os.getenv("CHROMEDRIVER", "/usr/bin/chromedriver")
    )

    browser = webdriver.Chrome(
        service=service,
        options=options
    )

    browser.get(BASE_URL)

    yield browser

    browser.quit()


def test_page_title(driver):

    assert driver.title == "CI/CD Assignment | FA23-BCT-047"

    driver.save_screenshot(
        "/app/screenshots/homepage.png"
    )


def test_main_heading(driver):

    heading = driver.find_element(
        By.ID, "main-heading"
    )

    assert heading.is_displayed()

    assert heading.text == "CI/CD Assignment - FA23-BCT-047"


def test_button_click(driver):

    button = driver.find_element(
        By.ID, "message-button"
    )

    button.click()

    message = driver.find_element(
        By.ID, "button-message"
    )

    WebDriverWait(driver, 5).until(
        lambda d: message.text != ""
    )

    assert message.text == "Hello! Button clicked successfully!"


def test_textbox_input(driver):

    textbox = driver.find_element(
        By.ID, "user-input"
    )

    textbox.send_keys("Selenium Testing Successful")

    submit_button = driver.find_element(
        By.ID, "submit-button"
    )

    submit_button.click()

    result = driver.find_element(
        By.ID, "submitted-text"
    )

    assert result.text == "You entered: Selenium Testing Successful"
