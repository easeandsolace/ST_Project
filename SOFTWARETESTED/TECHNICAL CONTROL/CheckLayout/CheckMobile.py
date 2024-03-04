import time

import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import cv2
import os
import numpy as np
import hashlib
import json


# Function to sanitize filename using URL hash
def sanitize_filename(url):
    # Use a hash function to shorten the filename
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    return url_hash


# Function to compare screenshots and calculate the percentage of change
def compare_screenshots(new, old):
    if not old or not os.path.exists(old) or not os.path.exists(new):
        print(f"Missing screenshot for comparison: new={new}, old={old}")
        return None

    image1 = cv2.imread(new)
    image2 = cv2.imread(old)
    if image1 is None or image2 is None:
        print(f"Failed to read images for comparison: new={new}, old={old}")
        return None

    diff = cv2.absdiff(image1, image2)
    non_zero_count = np.count_nonzero(diff)
    total_pixels = image1.size // image1.shape[2]  # Divide by number of channels
    percent_changed = (non_zero_count / total_pixels) * 100
    return percent_changed


# Function to get the index for the next screenshot
def get_next_screenshot_index(url_hash, screenshot_dir):
    # List all files in the directory and filter out non-numeric filenames
    files = [f for f in os.listdir(screenshot_dir) if f.split('.')[0].isdigit()]
    if not files:
        return 1  # Start with 1 if no files found
    # Get the highest current index
    highest_index = max(int(f.split('.')[0]) for f in files)
    return highest_index + 1  # Increment by 1


# Read URLs from CSV
df = pd.read_csv('urls.csv')
urls = df['urls'].tolist()

# Setup WebDriver with mobile emulation
options = webdriver.ChromeOptions()
options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone X"})
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Directory for storing screenshots
base_screenshot_dir = r'C:Screenshots'  # Simplified base directory

# Create a dictionary to hold the latest index for each URL
index_dict = {}

for url in urls:
    driver.get(url)
    time.sleep(5)
    sanitized_url = sanitize_filename(url)

    # Create a unique subfolder for each URL
    screenshot_dir = os.path.join(base_screenshot_dir, sanitized_url)
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)

    # Get the next screenshot index
    if sanitized_url not in index_dict:
        index_dict[sanitized_url] = get_next_screenshot_index(sanitized_url, screenshot_dir)
    else:
        index_dict[sanitized_url] += 1
    screenshot_filename = os.path.join(screenshot_dir, f"{index_dict[sanitized_url]}.png")

    # Save the screenshot
    success = driver.save_screenshot(screenshot_filename)
    if success:
        print(f"Screenshot saved: {screenshot_filename}")
    else:
        print(f"Failed to save screenshot for {url}")
        continue

    # Find and compare with the previous screenshot
    old_screenshot_filename = os.path.join(screenshot_dir, f"{index_dict[sanitized_url] - 1}.png")
    if os.path.exists(old_screenshot_filename):
        change_percentage = compare_screenshots(screenshot_filename, old_screenshot_filename)
        if change_percentage is not None:
            print(f"Change detected in {url}: {change_percentage:.2f}%")
    else:
        print(f"No previous screenshot to compare with for {url}")

# Close the browser
driver.quit()

# Optionally save the index dictionary to a file if you want to maintain state between script runs
with open('screenshot_index.json', 'w') as index_file:
    json.dump(index_dict, index_file)
