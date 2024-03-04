# This script automates the process of extracting metadata, specifically titles and descriptions, from a list of URLs provided in a CSV file. It outputs the results to another CSV file named "TitlesAndDescriptions.csv".

import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd

def read_csv(file_path):
    urls = []
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            urls.append(row[0])
    return urls


def fetch_url(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")


def extract_metadata(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('title')
    meta_title = title.text.strip() if title else "N/A"

    description = soup.find('meta', attrs={'name': 'description'})
    meta_description = description['content'].strip() if description else "N/A"

    return meta_title, meta_description


def main():
    csv_file_path = "urls.csv"  # Replace with the path to your CSV file containing the URLs

    urls = read_csv(csv_file_path)

    objects = []
    for url in urls:
        try:
            html = fetch_url(url)
            if html:
                meta_title, meta_description = extract_metadata(html)
                obj = {'URL': url, 'Title': meta_title, 'Description': meta_description}
                objects.append(obj)
                print(f"{url}; {meta_title}; {meta_description}")
        except Exception as e:
            print(f"Error fetching '{url}': {e}")

    # Convert the list of objects to a pandas dataframe
    df = pd.DataFrame(objects)

    # Write the dataframe to a CSV file
    df.to_csv('TitlesAndDescriptions.csv', index=False, sep=';', quoting=csv.QUOTE_ALL)


if __name__ == "__main__":
    main()