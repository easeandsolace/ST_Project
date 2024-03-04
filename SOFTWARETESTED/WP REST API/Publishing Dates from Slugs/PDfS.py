import pandas as pd
import requests
import datetime

# Load the slugs from a CSV file
slugs_file = pd.read_csv('slugs.csv')  # Assuming the CSV file is named slugs.csv and has a 'slugs' column

# Base URL for the WordPress REST API
base_url = "https://softwaretested.com/wp-json/wp/v2/posts"

# Headers including the authorization credentials
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'YOUR AUTHORIZATION HEADER',
    'Cookie': 'YOUR AUTHORIZATION COOKIE'
}


# Function to format date in a more readable format
def format_date(iso_date):
    # Convert ISO date to a datetime object
    date_obj = datetime.datetime.fromisoformat(iso_date)
    # Format the date in a more readable format, e.g., "February 12, 2024"
    formatted_date = date_obj.strftime("%B %d, %Y")
    return formatted_date


# Iterate over the slugs in the CSV file
for index, row in slugs_file.iterrows():
    slug = row['slugs']
    # Retrieve the post by slug to get its ID and publishing date
    response = requests.get(f"{base_url}?slug={slug}", headers=headers)
    if response.status_code == 200:
        posts = response.json()
        if posts:
            post_id = posts[0]['id']
            publish_date = posts[0]['date']  # The publishing date in ISO 8601 format

            # Convert the publish date to a more readable format
            formatted_date = format_date(publish_date)

            # Print the slug and its formatted publishing date
            print(slug, ";", formatted_date)
        else:
            print(slug, "; No post found")
    else:
        print(slug, "; Error retrieving post. Status code:", response.status_code)
