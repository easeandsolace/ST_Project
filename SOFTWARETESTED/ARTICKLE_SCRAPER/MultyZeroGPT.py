# This script is designed to scrape text from a list of URLs and then analyze the scraped text using a web-based application named "ZeroGPT". It follows a similar structure to the previous script with a few key differences in its purpose and the analysis tool it interacts with. Here's a detailed breakdown of its operations:
#
# Import Libraries: It imports necessary Python libraries for web scraping, web automation (using Selenium), handling HTTP requests, parsing HTML (using BeautifulSoup), manipulating data (using pandas), and simulating keyboard actions.
#
# Function scrape_text_from_url(url): This function takes a URL, makes an HTTP request to fetch the page content, and parses the HTML to extract text from all paragraph (<p>) elements. It concatenates and returns this text as a single string, or None if an error occurs or the request fails.
#
# Function analyze_text_with_zero_gpt(driver, url, text): This function takes a Selenium WebDriver instance, a URL, and the text to be analyzed. It simulates keyboard actions to paste the text into an input field on the "ZeroGPT" website, initiates the text analysis by clicking the appropriate button on the page, and waits for the analysis result to appear. Once the result is available, it extracts and returns the result along with the URL. The result is presumed to be some form of text analysis or extraction performed by "ZeroGPT".
#
# Selenium WebDriver Setup: Initializes a Chrome WebDriver, which is used to control a Chrome browser instance programmatically. The script navigates to the "ZeroGPT" website and locates the input field for text analysis.
#
# Read URLs from CSV: Reads a list of URLs from a CSV file named 'urls.csv' into a pandas DataFrame, with each URL meant for processing by the script.
#
# Process Each URL: For every URL in the DataFrame, the script extracts text using the scrape_text_from_url function and then analyzes this text with "ZeroGPT" using the analyze_text_with_zero_gpt function. Each analysis result is collected into a list.
#
# Save Results to CSV: Converts the list of results into a pandas DataFrame and exports it to a CSV file named 'analysis_results_zerogpt.csv'. This file contains the analysis results for each URL processed.
#
# Clean Up: Quits the WebDriver, effectively closing the browser window.

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip
import re

def scrape_text_from_url(url):
    print(f"Start scraping URL: {url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text() for p in paragraphs])
            return text
        else:
            print(f"Failed to get content from {url}, status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def analyze_text_with_zero_gpt(driver, url, text):
    print("Analyzing text with ZeroGPT...")
    try:
        ActionChains(driver).click(editor_field).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(
            Keys.BACKSPACE).perform()
        pyperclip.copy(text)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        time.sleep(1)
        detect_text_button = driver.find_element(By.CSS_SELECTOR, "#app > div > div > div:nth-child(2) > div:nth-child(1) > div > div.features-and-textarea > div.card.text-card > div.button-container > div.buttons > button")
        driver.execute_script("arguments[0].scrollIntoView();", detect_text_button)
        time.sleep(1)
        detect_text_button.click()

        xpath_to_scrape = "/html/body/div[1]/div/div/div[2]/div[1]/div/div[3]/div/div/div[1]/span"
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath_to_scrape)))
        element = driver.find_element(By.XPATH, xpath_to_scrape)
        print(f"{url}; {element.text}")

        return {"url": url, "Extracted Text": element.text}
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

options = Options()
# options.add_argument('--headless')
webdriver_service = webdriver.Chrome(ChromeDriverManager().install(), options=options)
df = pd.read_csv('urls.csv')
results = []

webdriver_service.get("https://www.zerogpt.com/")
WebDriverWait(webdriver_service, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='textArea']")))
editor_field = webdriver_service.find_element(By.XPATH, "//*[@id='textArea']")

for idx, row in df.iterrows():
    scraped_text = scrape_text_from_url(row['url'])
    if scraped_text:
        analysis_result = analyze_text_with_zero_gpt(webdriver_service, row['url'], scraped_text)
        if analysis_result:
            results.append(analysis_result)
    time.sleep(10)

df_results = pd.DataFrame(results)
df_results.to_csv('analysis_results_zerogpt.csv', index=False)
webdriver_service.quit()
