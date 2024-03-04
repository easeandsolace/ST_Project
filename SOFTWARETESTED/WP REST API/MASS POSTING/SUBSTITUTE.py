import pandas as pd
import requests
import json
import os


# Function to substitute symbols in the content
def substitute_symbols(content):
    substitutions = {
        "**": "",
        "###": "",
        "##": "",
        "вЂњ": '"',
        "вЂќ": '"',
        "itвЂ™s": "it is",
    }
    for old, new in substitutions.items():
        content = content.replace(old, new)
    return content


# Load the slugs from a CSV file
slugs_file = pd.read_csv('slugs.csv')  # Assuming the CSV file is named slugs.csv and has a 'slugs' column

# Base URL for the WordPress REST API
base_url = "https://softwaretested.com/wp-json/wp/v2/posts"
# Headers including the authorization credentials
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'YOUR AUTH HEADER',
}

# Iterate over the slugs in the CSV file
for index, row in slugs_file.iterrows():
    slug = row['slugs']
    # Find the post ID using the slug
    # response = requests.get(f"{base_url}?slug={slug}", headers=headers)
    response = requests.get(f"{base_url}?slug={slug}&status=draft", headers=headers)
    if response.status_code == 200:
        posts = response.json()
        if posts:
            post_id = posts[0]['id']
            content = posts[0]['content']['rendered']

            # Substitute symbols in the content
            new_content = substitute_symbols(content)

            # Update the post with the new content
            update_payload = json.dumps({
                "content": new_content,
            })
            update_response = requests.post(f"{base_url}/{post_id}", headers=headers, data=update_payload)


            if update_response.status_code in [200, 201]:
                print(f"Successfully updated post for slug: {slug}")
            else:
                print(f"Failed to update post for slug: {slug}. Status code: {update_response.status_code}")
                print(update_response.text)
        else:
            print(f"No posts found for slug: {slug}")
    else:
        print(f"Error searching for post with slug: {slug}. Status code: {response.status_code}")
        print(response.text)
