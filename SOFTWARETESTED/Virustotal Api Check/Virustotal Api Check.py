import pandas as pd
import requests
import json
import time

# Define the API key and URL
api_key = "YOUR API KEY"
base_url = "https://www.virustotal.com/api/v3/domains/"

# Read domains from CSV file using Pandas
df = pd.read_csv('domains.csv')  # Replace 'domains.csv' with your CSV file containing domains
domains = df['domain'].tolist()  # Assuming the CSV has a column named 'domain'

# Initialize an empty list to store results and counters for rate limiting
results = []
request_count_minute = 0
request_count_day = 0

# Loop through each domain to check it with VirusTotal
for domain in domains:
    if request_count_day >= 500:
        print("Reached the daily limit of 500 requests. Exiting.")
        break

    # Make the API request
    headers = {
        'x-apikey': api_key,
    }
    response = requests.get(base_url + domain, headers=headers)

    request_count_minute += 1
    request_count_day += 1

    if response.status_code == 200:
        data = response.json()

        # Extract relevant information from the response
        attributes = data.get('data', {}).get('attributes', {})
        last_update_date = attributes.get('last_update_date', '')
        categories = attributes.get('categories', {})
        total_votes = attributes.get('total_votes', {})

        # Store in results
        results.append({
            'domain': domain,
            'last_update_date': last_update_date,
            'categories': json.dumps(categories),
            'total_votes': json.dumps(total_votes)
        })

        print(f"Checked {domain}.")
    else:
        print(f"Failed to check {domain}. Status Code: {response.status_code}")

    # Sleep if we have reached 4 requests in the last minute
    if request_count_minute >= 4:
        print("Reached 4 requests per minute. Sleeping for 60 seconds.")
        time.sleep(60)
        request_count_minute = 0

# Save the results back to a new CSV file
results_df = pd.DataFrame(results)
results_df.to_csv('checked_domains.csv', index=False)
