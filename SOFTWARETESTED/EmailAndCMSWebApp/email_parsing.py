# This refined version of the script is designed to extract email addresses from websites listed in a CSV file and optionally track the progress of this operation. It utilizes Python's requests library for making HTTP requests, BeautifulSoup for parsing HTML content, re for regular expression matching to find email addresses, and pandas for handling data in a tabular format.

import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging

# Define the list of suffixes to append to the URLs
suffixes = ['contact', 'contact-us', 'contacts', 'about-us', 'support', 'feedback']

# Define the headers for the output CSV file
headers = ['URL', 'Email 1', 'Email 2', 'Email 3', 'Email 4', 'Email 5']

# Define a regular expression pattern to extract email addresses
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def process_csv_file(input_file, update_progress):
    df = pd.read_csv(input_file)
    urls_and_emails = []

    total_urls = len(df['urls'])  # Add this line to get the total number of URLs

    for index, url in enumerate(df['urls']):
        logging.info(f"Processing URL {index + 1}/{total_urls}: {url}")  # Add this log statement
        try:
            url = url.strip()  # Get the URL and remove any leading/trailing white space

            # Check if 'https://' is present in the URL or not, and add it if it's absent
            if not url.startswith('https://'):
                url = 'https://' + url

            emails = ['', '', '', '', '']  # Set up a list to store the email addresses

            # Function to extract emails from given URL
            def extract_emails(page_url):
                logging.info("def extract_emails(page_url):")
                response = requests.get(page_url, timeout=10)
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

            # Extract emails from homepage
            extract_emails(url)

            # Loop through each suffix and try to form a contact URL
            for suffix in suffixes:
                contact_url = url + '/' + suffix
                # Extract emails from contact URL
                extract_emails(contact_url)

            # Add the URL and email addresses to the results list
            url_and_emails = {'URL': url, 'Email 1': emails[0], 'Email 2': emails[1], 'Email 3': emails[2],
                              'Email 4': emails[3], 'Email 5': emails[4]}
            urls_and_emails.append(url_and_emails)

            # Print the results to the console
            logging.info(f'URL: {url}')
            for i, email in enumerate(emails):
                logging.info(f'Email {i + 1}: {email}')
        except Exception as e:
            logging.error(f'{url} ; ERROR ; {e}')

        if update_progress:  # Add this block to update the progress
            progress = (index + 1) / total_urls * 100
            update_progress(progress)

    # Convert the list of dictionaries to a pandas dataframe
    results = pd.DataFrame(urls_and_emails, columns=headers)

    # Return the DataFrame instead of writing it to a CSV
    return results