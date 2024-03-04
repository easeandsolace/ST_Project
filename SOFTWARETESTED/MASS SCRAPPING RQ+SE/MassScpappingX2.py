# This script is designed to extract text content from websites listed in an Excel file using both BeautifulSoup and Selenium, then save the combined results into text files organized by keywords.

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options

# Common setup
excel_file = 'KwSites.xlsx'
df = pd.read_excel(excel_file)
grouped = df.groupby('Фраза')

# BeautifulSoup scrape function
def scrape_url_bs(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        text = [tag.get_text(separator="\n", strip=True) for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])]
        return "\n".join(text)
    except Exception as e:
        print(f"BS error on {url}: {e}")
        return ""

# Selenium scrape function
def scrape_url_selenium(driver, url):
    try:
        driver.get(url)
        elements = driver.find_elements(By.XPATH, "//h1 | //h2 | //h3 | //h4 | //h5 | //h6 | //p")
        text = ' '.join([elem.text for elem in elements if elem.text])
        return text
    except Exception as e:
        print(f"Selenium error on {url}: {e}")
        return ""

# Set chrome options for headless mode and initialize driver
options = Options()
options.add_argument('--headless')
webdriver_service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=webdriver_service, options=options)

# Main loop
for keyword, group in grouped:
    all_texts_bs = []
    all_texts_selenium = []

    for index, row in group.iterrows():
        url = row['url']
        print(f"Scraping {url} with BeautifulSoup")
        text_bs = scrape_url_bs(url)
        all_texts_bs.append(f"URL: {url}\n{text_bs}")

        print(f"Scraping {url} with Selenium")
        text_selenium = scrape_url_selenium(driver, url)
        all_texts_selenium.append(f"URL: {url}\n{text_selenium}")

    combined_text = "\n\n".join(all_texts_bs + all_texts_selenium)
    sanitized_keyword = "".join([c for c in keyword if c.isalnum() or c.isspace()]).rstrip().replace(' ', '_')
    filename = f"{sanitized_keyword}.txt"

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(combined_text)
    print(f"Saved all content for keyword '{keyword}' to '{filename}'.")


driver.quit()
print("Scraping completed.")
