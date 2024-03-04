import pandas as pd
import requests
import json
import os

# Load the xlsx file
xlsx_file = pd.read_excel('articles_to_post.xlsx', engine='openpyxl')

# Iterate over the rows in the DataFrame.
for index, row in xlsx_file.iterrows():
    txt_file_name = row['txt_file_name']
    title = row['title']
    author_id = row['author_id']          # Column name in your xlsx file for author IDs
    category_id = row['category_id']      # Column name in your xlsx file for category IDs
    slug = row['slug']                    # Column for slug

    # Read the content of the txt file
    if os.path.isfile(txt_file_name):
        with open(txt_file_name, 'r') as file:
            content = file.read()

        # Construct the payload
        payload = json.dumps({
            "title": title,
            "content": content,
            "status": "draft",
            "categories": [category_id],
            "author": author_id,
            "slug": slug
        })

        # Add your code to send the payload to the WordPress REST API here (similar to the previous examples)
        url = "https://softwaretested.com/wp-json/wp/v2/posts"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'YOUR AUTHORIZATION HEADER',
            'Cookie': 'YOUR AUTHORIZATION COOKIE'
        }

        response = requests.post(url, data=payload, headers=headers)

        # Check the response
        if response.status_code == 201 or response.status_code == 200:
            print(f"Successfully created post for {txt_file_name}")
        else:
            print(f"Failed to create post for {txt_file_name}. Status code: {response.status_code}")
            print(response.text)
    else:
        print(f"File {txt_file_name} not found.")
