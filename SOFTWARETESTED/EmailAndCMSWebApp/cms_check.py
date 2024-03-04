# This script defines a set of functions for detecting the Content Management System (CMS) used by a given website, and a function to process a list of websites from a CSV file to identify their CMS. The detection is based on specific patterns or markers in the website's HTML content or HTTP headers that are characteristic of certain CMS platforms

import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging

#Работает!
def is_wordpress(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for common WordPress HTML tags
            wp_tags = soup.select('link[href*="wp-content"], link[href*="wp-includes"], link[href*="wp-json"]')

            # If any WordPress tags were found, assume the site is running on WordPress
            if wp_tags:
                logging.info("Checkes Wordpress — TRUE")
                return True
    except requests.exceptions.RequestException as e:
        logging.info("Checked Wordpress — FALSE")
        logging.error(f"Error fetching '{url}': {e}")
    return False


# Доработать друпал, не все версии определяет
def is_drupal(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            generator_header = response.headers.get('X-Generator', '')
            logging.info("Checked Drupal")
            return 'Drupal' in generator_header


    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching '{url}': {e}")
    return False


def is_joomla(url):
    try:
        response = requests.get(url, timeout=10)

        def is_joomla(url):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    powered_by_header = response.headers.get('X-CF-Powered-By', '')
                    logging.info("Checked Joomla")
                    return 'CF-Joomla' in powered_by_header
            except requests.exceptions.RequestException as e:

                logging.error(f"Error fetching '{url}': {e}")
            return False

        return False

    except requests.exceptions.RequestException as e:
        logging.error(f"Error: {e}")
        return False


# Работает!
def is_wix(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for the Wix-specific generator meta tag
            meta_generator = soup.find('meta', {'name': 'generator'})
            if meta_generator and 'Wix.com Website Builder' in meta_generator.get('content', ''):
                logging.info("Checked Wix — TRUE")
                return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching '{url}': {e}")
    logging.info("Checked Wix — FALSE")
    return False

# Работает!
def is_squarespace(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all tags with 'href', 'src', or 'content' attributes
            elements = soup.find_all(lambda tag: tag.has_attr('href') or tag.has_attr('src') or tag.has_attr('content'))

            # Check if any of the attributes contain 'squarespace'
            squarespace_present = any('squarespace' in element.get('href', '') or 'squarespace' in element.get('src', '') or 'squarespace' in element.get('content', '') for element in elements)

            if squarespace_present:
                logging.info("Checked Squarespace — TRUE")

                return True

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching '{url}': {e}")

    logging.info("Checked Squarespace — FALSE")

    return False

# Работает!
def is_hubspot(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all script tags
            script_tags = soup.find_all('script')

            # Check if any script tag contains 'hbspt'
            for script_tag in script_tags:
                if script_tag.string and 'hbspt' in script_tag.string:
                    logging.info("Checked Hubspot — TRUE")
                    return True

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching '{url}': {e}")

    logging.info("Checked Hubspot — FALSE")

    return False

# Работает!
def is_modx(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all tags with 'src', 'srcset', or 'href' attributes
            elements = soup.find_all(lambda tag: tag.has_attr('src') or tag.has_attr('srcset') or tag.has_attr('href'))

            # Check if any of the attributes contain 'assets'
            assets_present = any('assets' in element.get('src', '') or 'assets' in element.get('srcset', '') or 'assets' in element.get('href', '') for element in elements)

            # Check if any of the attributes contain 'squarespace'
            squarespace_present = any('squarespace' in element.get('src', '') or 'squarespace' in element.get('srcset', '') or 'squarespace' in element.get('href', '') for element in elements)

            if assets_present and not squarespace_present:
                return True

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching '{url}': {e}")

    return False

# Function to detect the CMS for a given site
def detect_cms(url):
    cms_detectors = [
        ('WordPress', is_wordpress),
        ('Joomla', is_joomla),
        ('Wix', is_wix),
        ('Squarespace', is_squarespace),
        ('Hubspot', is_hubspot),
        ('MODX', is_modx),
        ('Drupal', is_drupal)
    ]

    for cms_name, detector in cms_detectors:
        if detector(url):
            return cms_name

    return 'Unknown'


# New function to process CSV file
def process_csv_file(filename, progress_callback):
    # Read sites from the CSV file using pandas
    df = pd.read_csv(filename)
    sites = df['urls'].tolist()

    # Prepare an empty DataFrame to store the results
    results = pd.DataFrame(columns=['site', 'cms'])

    # Detect and print the CMS for each site
    for i, site in enumerate(sites):
        # Check if site starts with http:// or https://
        if not (site.startswith("http://") or site.startswith("https://")):
            # If not, prepend https://
            site = "https://" + site

        cms = detect_cms(site)
        temp_df = pd.DataFrame([{'site': site, 'cms': cms}], columns=['site', 'cms'])
        results = pd.concat([results, temp_df], ignore_index=True)

        # Update progress
        progress = (i + 1) / len(sites) * 100
        progress_callback(progress)

    # Save results to DataFrame
    results_df = pd.DataFrame(results, columns=['site', 'cms'])

    # Return the DataFrame instead of writing it to a CSV
    return results_df