# This script is an advanced version of the CMS detection and email scraping tool, designed to process a list of URLs from a CSV file, detect the Content Management System (CMS) used by each site, and scrape up to five email addresses from each site and its specific pages like "contact" or "about us". The script utilizes Python's requests and BeautifulSoup libraries for web requests and HTML parsing, pandas for data manipulation, and re for regular expression operations.

import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import time

# Define the list of suffixes to append to the URLs
suffixes = ['contact', 'contact-us', 'contacts', 'about-us', 'support', 'feedback']

# Define the headers for the output CSV file
headers = ['URL', 'CMS', 'Email 1', 'Email 2', 'Email 3', 'Email 4', 'Email 5']

# Define a regular expression pattern to extract email addresses
email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'


def is_wordpress(soup, headers):
    wp_tags = soup.select('link[href*="wp-content"], link[href*="wp-includes"], link[href*="wp-json"]')
    if wp_tags:
        logging.info("Checked Wordpress — TRUE")
        return True
    else:
        logging.info("Checked Wordpress — FALSE")
    return False


def is_drupal(soup, headers):
    generator_header = headers.get('X-Generator', '')
    if 'Drupal' in generator_header:
        logging.info("Checked Drupal — TRUE")
        return True
    else:
        logging.info("Checked Drupal — FALSE")
    return False


def is_joomla(soup, headers):
    powered_by_header = headers.get('X-CF-Powered-By', '')
    if 'CF-Joomla' in powered_by_header:
        logging.info("Checked Joomla — TRUE")
        return True
    else:
        logging.info("Checked Joomla — FALSE")
    return False


def is_wix(soup, headers):
    meta_generator = soup.find('meta', {'name': 'generator'})
    if meta_generator and 'Wix.com Website Builder' in meta_generator.get('content', ''):
        logging.info("Checked Wix — TRUE")
        return True
    else:
        logging.info("Checked Wix — FALSE")
    return False


def is_squarespace(soup, headers):
    elements = soup.find_all(lambda tag: tag.has_attr('href') or tag.has_attr('src') or tag.has_attr('content'))
    squarespace_present = any('squarespace' in element.get('href', '') or 'squarespace' in element.get('src',
                                                                                                       '') or 'squarespace' in element.get(
        'content', '') for element in elements)

    if squarespace_present:
        logging.info("Checked Squarespace — TRUE")
        return True
    else:
        logging.info("Checked Squarespace — FALSE")
    return False


def is_hubspot(soup, headers):
    script_tags = soup.find_all('script')
    for script_tag in script_tags:
        if script_tag.string and 'hbspt' in script_tag.string:
            logging.info("Checked Hubspot — TRUE")
            return True

    logging.info("Checked Hubspot — FALSE")
    return False


# Работает!
def is_modx(soup, headers):
    # Find all tags with 'src', 'srcset', or 'href' attributes
    elements = soup.find_all(lambda tag: tag.has_attr('src') or tag.has_attr('srcset') or tag.has_attr('href'))

    # Check if any of the attributes contain 'assets/images' or 'assets/files'
    assets_present = any(
        'assets/images' in element.get('src', '') or 'assets/images' in element.get('srcset', '') or 'assets/images' in element.get('href', '') or
        'assets/files' in element.get('src', '') or 'assets/files' in element.get('srcset', '') or 'assets/files' in element.get('href', '') for
        element in elements)

    # Check if any of the attributes contain 'squarespace'
    squarespace_present = any('squarespace' in element.get('src', '') or 'squarespace' in element.get('srcset',
                                                                                                      '') or 'squarespace' in element.get(
        'href', '') for element in elements)

    if assets_present and not squarespace_present:
        logging.info("Checked MODX — TRUE")
        return True

    logging.info("Checked MODX — FALSE")
    return False


cms_detectors = [
    ('WordPress', is_wordpress),
    ('Joomla', is_joomla),
    ('Wix', is_wix),
    ('Squarespace', is_squarespace),
    ('Hubspot', is_hubspot),
    ('MODX', is_modx),
    ('Drupal', is_drupal)
]


def detect_cms(url):
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        time.sleep(2)
        if 200 <= response.status_code < 300:
            content = response.content
            soup = BeautifulSoup(content, 'html.parser')
            headers = response.headers

            for cms_name, detector in cms_detectors:
                if detector(soup, headers):
                    return cms_name
        else:
            logging.error(f"Error fetching '{url}': Received status code {response.status_code}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching '{url}' during CMS detection: {e}")
    return 'Unknown'


def process_csv_file(input_file):
    df = pd.read_csv(input_file)
    urls_and_emails_and_cms = []

    total_urls = len(df['urls'])

    def extract_emails(page_url):
        logging.info("def extract_emails(page_url):")
        response = requests.get(page_url, timeout=10)
        time.sleep(2)
        logging.info(" response = requests.get(page_url)")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            logging.info("soup = BeautifulSoup(response.content, 'html.parser')")
            matches = re.findall(email_pattern, soup.get_text())
            logging.info("matches = re.findall(email_pattern, soup.get_text())")
            for i, match in enumerate(matches):
                if i < 5:
                    logging.info("if i < 5 — i < 5")
                    emails[i] = match
                    logging.info("emails[i] = match")

            if all(email == '' for email in emails):
                email_tags = soup.find_all('a', href=lambda href: href and 'mailto:' in href)
                logging.info(" email_tags = soup.find_all('a', href=lambda href: href and 'mailto:' in href)")
                for i, email_tag in enumerate(email_tags):
                    if i < 5:
                        logging.info("if i < 5:")
                        email = email_tag.get('href').replace('mailto:', '').strip()
                        emails[i] = email
                        logging.info("end")

    for index, url in enumerate(df['urls']):
        logging.info(f"Processing URL {index + 1}/{total_urls}: {url}")
        try:
            url = url.strip()  # Get the URL and remove any leading/trailing white space

            if not url.startswith('https://'):
                url = 'https://' + url

            emails = ['', '', '', '', '']  # Set up a list to store the email addresses



            # Extract emails from homepage
            extract_emails(url)

            for suffix in suffixes:
                contact_url = url + '/' + suffix
                # Extract emails from contact URL
                extract_emails(contact_url)

            # Detect the CMS
            cms = detect_cms(url)

            url_and_emails_and_cms = {'URL': url, 'CMS': cms, 'Email 1': emails[0], 'Email 2': emails[1],
                                      'Email 3': emails[2],
                                      'Email 4': emails[3], 'Email 5': emails[4]}
            urls_and_emails_and_cms.append(url_and_emails_and_cms)

            logging.info(f'URL: {url}')
            for i, email in enumerate(emails):
                logging.info(f'Email {i + 1}: {email}')
            logging.info(f'CMS: {cms}')

        except Exception as e:
            logging.error(f'{url} ; ERROR ; {e}')

        # if update_progress:
        #     progress = (index + 1) / total_urls * 100
        #     update_progress(progress)

    results = pd.DataFrame(urls_and_emails_and_cms, columns=headers)

    return results
