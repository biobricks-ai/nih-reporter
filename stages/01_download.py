from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
import pandas as pd
import time
import os
import re

# DOWNLOAD PROJECTS ============================================================
def download_projects():
    # make the download/projects directory if it doesn't exist
    download_dir = os.path.join(os.getcwd(), 'download', 'projects')
    os.makedirs(download_dir, exist_ok=True)

    # URL of the website
    url = "https://reporter.nih.gov/exporter"

    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    prefs = {"download.default_directory": download_dir}
    options.add_experimental_option("prefs", prefs)

    # Set up the Selenium WebDriver with the modified options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

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

    for link in tqdm(download_links, desc='Downloading projects'):
        # link.click()
        driver.execute_script("arguments[0].click();", link)
        time.sleep(10)

    # Close the browser
    driver.quit()

download_projects()

# DOWNLOAD ABSTRACTS ============================================================
def download_abstracts():
    download_dir = os.path.join(os.getcwd(), 'download', 'abstracts')
    os.makedirs(download_dir, exist_ok=True)

    # URL of the website
    url = "https://reporter.nih.gov/exporter/abstracts"

    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    prefs = {"download.default_directory": download_dir}
    options.add_experimental_option("prefs", prefs)

    # Set up the Selenium WebDriver with the modified options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

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

    for link in tqdm(download_links, desc='Downloading abstracts'):
        # link.click()
        driver.execute_script("arguments[0].click();", link)
        time.sleep(10)

    # Close the browser
    driver.quit()

download_abstracts()