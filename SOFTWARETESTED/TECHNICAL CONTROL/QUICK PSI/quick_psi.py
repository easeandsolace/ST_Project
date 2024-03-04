# This script is designed to read a list of URLs from a CSV file, fetch web performance metrics for each URL using Google's PageSpeed Insights (PSI) API, and save the results to a new CSV file. It uses both "mobile" and "desktop" strategies for analysis.


import requests
import pandas as pd

def read_urls_from_csv(file_path):
    df = pd.read_csv(file_path)
    if "URL" not in df.columns:
        print("CSV file does not contain 'URL' column.")
        return []
    return df["URL"].tolist()

def fetch_psi_metrics(url, api_key, strategy="mobile"):
    endpoint = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy={strategy}&key={api_key}"
    response = requests.get(endpoint)

    if response.status_code != 200:
        print(f"Error fetching data for {url}. Status code: {response.status_code}")
        try:
            error_details = response.json()["error"]["message"]
            print(f"Error details: {error_details}")
        except (KeyError, ValueError):
            print("Could not extract detailed error message from response.")
        return None

    data = response.json()
    lighthouse_result = data["lighthouseResult"]

    # Extract desired metrics
    metrics = {
        "Performance Score": lighthouse_result["categories"]["performance"]["score"] * 100,
        "Cumulative Layout Shift": lighthouse_result["audits"]["cumulative-layout-shift"]["numericValue"],
        "First Contentful Paint Time (ms)": lighthouse_result["audits"]["first-contentful-paint"]["numericValue"],
        "Largest Contentful Paint Time (ms)": lighthouse_result["audits"]["largest-contentful-paint"]["numericValue"],
        "Time to Interactive (ms)": lighthouse_result["audits"]["interactive"]["numericValue"],
        "Total Blocking Time (ms)": lighthouse_result["audits"]["total-blocking-time"]["numericValue"],
        "Server Response Times (TTFB) (ms)": lighthouse_result["audits"]["server-response-time"]["numericValue"]
    }

    return metrics

def main():
    api_key = "YOUR API Key"
    urls = read_urls_from_csv("urls.csv")  # the path to your CSV file.
    strategies = ["mobile", "desktop"]
    all_metrics = []

    for url in urls:
        for strategy in strategies:
            metrics = fetch_psi_metrics(url, api_key, strategy)
            if metrics:
                print(f"{url} ({strategy});" + ';'.join([str(v) for v in metrics.values()]))
                all_metrics.append([url, strategy] + list(metrics.values()))

    # Handle case when all_metrics is empty
    if not all_metrics:
        print("No valid metrics found for the provided URLs.")
        return

    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(all_metrics, columns=["URL", "Strategy"] + list(metrics.keys()))
    df.to_csv("psi_metrics.csv", index=False)

if __name__ == "__main__":
    main()
