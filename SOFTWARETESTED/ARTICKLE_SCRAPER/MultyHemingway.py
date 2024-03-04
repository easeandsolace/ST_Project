# This script performs two main tasks: scraping text from a list of URLs and analyzing the scraped text using the Hemingway App for readability. Here's a step-by-step breakdown of what the script does:
#
# Import necessary libraries: The script imports various Python libraries and modules necessary for web scraping, driving a web browser programmatically (Selenium), handling HTTP requests, parsing HTML content (BeautifulSoup), and working with data structures (pandas).
#
# Function scrape_text_from_url(url): This function takes a URL as input and attempts to scrape all text contained within paragraph (<p>) tags on that page using the requests library to fetch the page content and BeautifulSoup to parse the HTML. It returns the concatenated text of these paragraphs as a single string or None if there's an error or if the HTTP request fails.
#
# Function analyze_text_with_hemingway(driver, editor_field, text): This function takes a Selenium WebDriver instance, a reference to the editor field in the Hemingway App web page, and a text string to be analyzed. It uses Selenium's ActionChains to simulate keyboard actions for clearing the Hemingway App's editor field and pasting the text for analysis. After a brief pause to allow the app to process the text, it scrapes the analysis results (such as the use of adverbs, instances of passive voice, suggestions for simpler alternatives, readability grades, etc.) from the web page and returns them in a dictionary.
#
# Setup Selenium WebDriver: The script initializes a Chrome WebDriver using ChromeDriverManager, which is used to programmatically control a Chrome browser instance. It also navigates to the Hemingway App's web page and locates the editor field for later use.
#
# Read URLs from CSV: It reads a list of URLs from a CSV file named 'urls.csv' into a pandas DataFrame. Each URL is intended to be processed by the script.
#
# Process each URL: For each URL in the DataFrame, the script scrapes the text from the URL, analyzes the text using the Hemingway App through the previously defined function, and collects the results along with the URL into a list.
#
# Save results to CSV: After processing all URLs, it converts the list of results into a pandas DataFrame and exports this DataFrame to a CSV file named 'analysis_results.csv'. This file contains the readability analysis for each URL processed.
#
# Clean up: Finally, the script quits the WebDriver, closing the browser window.

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager  # Added this line
import time
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip


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


def analyze_text_with_hemingway(driver, editor_field, text):
    print("Analyzing text with Hemingway App...")
    try:
        # Assuming you are already on the Hemingway App page

        # Clear text from editor using Ctrl+A followed by Backspace
        ActionChains(driver).click(editor_field).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(
            Keys.BACKSPACE).perform()

        # Store the text in the clipboard
        pyperclip.copy(text)

        # Paste text from clipboard using Ctrl+V
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        time.sleep(1)

        # Rest of your code remains unchanged

        time.sleep(1)

        elements_to_scrape = [
            "//*[@id='hemingway-container']/div[1]/div[2]/div[3]/div[1]/strong",
            "//*[@id='hemingway-container']/div[1]/div[2]/div[3]/div[2]/strong",
            "//*[@id='hemingway-container']/div[1]/div[2]/div[3]/div[3]/strong",
            "//*[@id='hemingway-container']/div[1]/div[2]/div[3]/div[4]/strong",
            "//*[@id='hemingway-container']/div[1]/div[2]/div[3]/div[5]/strong",
            "//*[@id='hemingway-container']/div[1]/div[2]/div[1]/h4",
            "//*[@id='hemingway-container']/div[1]/div[2]/div[2]/div[1]/strong",
        ]

        names = ["Adverbs", "Passive", "Simpler", "Hard", "Very Hard", "Grade", "words"]
        result = {}

        for xpath, name in zip(elements_to_scrape, names):
            element = driver.find_element(By.XPATH, xpath)
            result[name] = element.text

        return result
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


options = Options()
webdriver_service = webdriver.Chrome(ChromeDriverManager().install(), options=options)  # Fixed this line
df = pd.read_csv('urls.csv')
results = []

# Navigate to Hemingway App and find the editor field once
webdriver_service.get("https://hemingwayapp.com/")
WebDriverWait(webdriver_service, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@data-block='true']")))
editor_field = webdriver_service.find_element(By.XPATH, "//div[@data-block='true']")

# Loop through the URLs
for idx, row in df.iterrows():
    scraped_text = scrape_text_from_url(row['url'])
    if scraped_text:
        analysis_result = analyze_text_with_hemingway(webdriver_service, editor_field, scraped_text)
        if analysis_result:
            analysis_result['url'] = row['url']
            print(f"{row['url']} ; {analysis_result}")
            results.append(analysis_result)
    time.sleep(10)

df_results = pd.DataFrame(results)
df_results.to_csv('analysis_results.csv', index=False)
webdriver_service.quit()
