from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from tqdm import tqdm
import pandas as pd
import time
import os
import re

def setup_chrome_driver(download_dir):
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            'profile.default_content_setting_values.automatic_downloads': 1
    }
    options.add_experimental_option("prefs", prefs)

    # Set up the Selenium WebDriver with the modified options
    driver = webdriver.Chrome(
        service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
        options=options
    )

    return driver

def download_data(url):
    # Extract the final part of the URL as the type name
    download_type = url.split('/')[-1]

    # make the download directory if it doesn't exist
    download_dir = os.path.join(os.getcwd(), 'download', download_type)
    os.makedirs(download_dir, exist_ok=True)

    # Set up the Selenium WebDriver with Chrome options
    driver = setup_chrome_driver(download_dir)

    time.sleep(5)

    # Open the website
    driver.get(url)

    # Wait for the JavaScript to load
    time.sleep(5)  # Adjust this depending on your internet speed and website response time

    # Scrape the table data
    table = driver.find_element(By.CLASS_NAME, 'b-table')
    rows = table.find_elements(By.TAG_NAME, 'tr')

    # Process the rows and extract data
    data = []
    download_links = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, 'td')
        if cols:
            data.append([col.text for col in cols])
            # Find the download link in the third column
            download_links.append(cols[2].find_element(By.TAG_NAME, 'a'))

    for link in tqdm(download_links, desc=f'Downloading {download_type}'):
        driver.execute_script("arguments[0].click();", link)
        time.sleep(10)

    # Close the browser
    driver.quit()

# URLs for downloads
urls = [
    "https://reporter.nih.gov/exporter/projects",
    "https://reporter.nih.gov/exporter/abstracts",
    "https://reporter.nih.gov/exporter/clinicalstudies"
]

# Run the downloads for each URL
for url in urls:
    download_data(url)
