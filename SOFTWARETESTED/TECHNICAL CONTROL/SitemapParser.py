import requests
import xml.etree.ElementTree as ET
import csv

all_urls = []  # List to store all extracted URLs
SITEMAP_NAMESPACE = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


def fetch_sitemap_urls(sitemap_url, origin_sitemap_url=None):
    if origin_sitemap_url is None:
        origin_sitemap_url = sitemap_url

    # Fetch the content of the sitemap or sitemap index
    response = requests.get(sitemap_url)
    response.raise_for_status()
    sitemap_content = response.content

    # Parse the content
    root = ET.fromstring(sitemap_content)

    # Check if it's a sitemap index
    if root.tag == SITEMAP_NAMESPACE + 'sitemapindex':
        for sitemap in root.findall(SITEMAP_NAMESPACE + 'sitemap'):
            loc_element = sitemap.find(SITEMAP_NAMESPACE + 'loc')
            if loc_element is not None:
                fetch_sitemap_urls(loc_element.text, origin_sitemap_url)
    else:
        # Extract URLs and append to the all_urls list
        for url_element in root.findall(SITEMAP_NAMESPACE + 'url'):
            loc_element = url_element.find(SITEMAP_NAMESPACE + 'loc')
            if loc_element is not None:
                print(f"Sitemap: {origin_sitemap_url}, URL: {loc_element.text}")
                all_urls.append(loc_element.text)


# Initial list of sitemap URLs

initial_sitemaps = [
    "https://softwaretested.com/post-sitemap.xml", "https://softwaretested.com/post-sitemap2.xml",
    "https://softwaretested.com/post-sitemap3.xml", "https://softwaretested.com/post-sitemap4.xml",
    "https://softwaretested.com/page-sitemap.xml", "https://softwaretested.com/category-sitemap.xml",
    "https://softwaretested.com/de/file-library/sitemaps/sitemap_file_library_001.xml",
    "https://softwaretested.com/de/file-library/sitemaps/sitemap_file_library_002.xml",
    "https://softwaretested.com/de/file-library/sitemaps/sitemap_file_library_003.xml",
    "https://softwaretested.com/de/file-library/sitemaps/sitemap_file_library_004.xml",
    "https://softwaretested.com/de/file-library/sitemaps/sitemap_file_library_005.xml",
    "https://softwaretested.com/de/file-library/sitemaps/sitemap_file_library_006.xml",
    "https://softwaretested.com/de/file-library/sitemaps/sitemap_file_library_007.xml",
    "https://softwaretested.com/de/file-library/sitemaps/sitemap_file_library_008.xml",
    "https://softwaretested.com/en/file-library/sitemaps/sitemap_file_library_001.xml",
    "https://softwaretested.com/en/file-library/sitemaps/sitemap_file_library_002.xml",
    "https://softwaretested.com/en/file-library/sitemaps/sitemap_file_library_003.xml",
    "https://softwaretested.com/en/file-library/sitemaps/sitemap_file_library_004.xml",
    "https://softwaretested.com/en/file-library/sitemaps/sitemap_file_library_005.xml",
    "https://softwaretested.com/en/file-library/sitemaps/sitemap_file_library_006.xml",
    "https://softwaretested.com/en/file-library/sitemaps/sitemap_file_library_007.xml",
    "https://softwaretested.com/en/file-library/sitemaps/sitemap_file_library_008.xml",
    "https://softwaretested.com/fr/file-library/sitemaps/sitemap_file_library_001.xml",
    "https://softwaretested.com/fr/file-library/sitemaps/sitemap_file_library_002.xml",
    "https://softwaretested.com/fr/file-library/sitemaps/sitemap_file_library_003.xml",
    "https://softwaretested.com/fr/file-library/sitemaps/sitemap_file_library_004.xml",
    "https://softwaretested.com/fr/file-library/sitemaps/sitemap_file_library_005.xml",
    "https://softwaretested.com/fr/file-library/sitemaps/sitemap_file_library_006.xml",
    "https://softwaretested.com/fr/file-library/sitemaps/sitemap_file_library_007.xml",
    "https://softwaretested.com/fr/file-library/sitemaps/sitemap_file_library_008.xml",
    "https://softwaretested.com/de/drivers/sitemaps/sitemap_drivers_001.xml",
    "https://softwaretested.com/de/drivers/sitemaps/sitemap_drivers_002.xml",
    "https://softwaretested.com/de/drivers/sitemaps/sitemap_drivers_003.xml",
    "https://softwaretested.com/de/drivers/sitemaps/sitemap_drivers_004.xml",
    "https://softwaretested.com/de/drivers/sitemaps/sitemap_drivers_005.xml",
    "https://softwaretested.com/de/drivers/sitemaps/sitemap_drivers_006.xml",
    "https://softwaretested.com/en/drivers/sitemaps/sitemap_drivers_001.xml",
    "https://softwaretested.com/en/drivers/sitemaps/sitemap_drivers_002.xml",
    "https://softwaretested.com/en/drivers/sitemaps/sitemap_drivers_003.xml",
    "https://softwaretested.com/en/drivers/sitemaps/sitemap_drivers_004.xml",
    "https://softwaretested.com/en/drivers/sitemaps/sitemap_drivers_005.xml",
    "https://softwaretested.com/en/drivers/sitemaps/sitemap_drivers_006.xml",
    "https://softwaretested.com/fr/drivers/sitemaps/sitemap_drivers_001.xml",
    "https://softwaretested.com/fr/drivers/sitemaps/sitemap_drivers_002.xml",
    "https://softwaretested.com/fr/drivers/sitemaps/sitemap_drivers_003.xml",
    "https://softwaretested.com/fr/drivers/sitemaps/sitemap_drivers_004.xml",
    "https://softwaretested.com/fr/drivers/sitemaps/sitemap_drivers_005.xml",
    "https://softwaretested.com/fr/drivers/sitemaps/sitemap_drivers_006.xml"
]

for sitemap_url in initial_sitemaps:
    fetch_sitemap_urls(sitemap_url)

# Write to a CSV file
with open('extracted_urls.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['URL'])  # Header row
    for url in all_urls:
        writer.writerow([url])
