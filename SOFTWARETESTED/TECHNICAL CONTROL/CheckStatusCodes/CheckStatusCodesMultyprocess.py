import csv
import requests
from multiprocessing import Pool

def get_status_code(url):
    try:
        response = requests.get(url, timeout=10,  allow_redirects=False)
        print(url, ";", response.status_code)
        if 300 <= response.status_code < 400:
            final_response = requests.get(url, timeout=10, allow_redirects=True)
            final_status = final_response.status_code
        else:
            final_status = response.status_code

        print(url, ";", response.status_code, ";", final_status)
        return (url, (response.status_code, final_status))
    except requests.RequestException:
        return (url, "Error")

def worker(urls):
    return [get_status_code(url) for url in urls]

def check_urls_in_csv(input_filename, output_filename, num_processes):
    with open(input_filename, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        all_urls = [row['url'] for row in reader]

    # Divide the URLs into chunks for each process
    chunk_size = len(all_urls) // num_processes
    chunks = [all_urls[i:i + chunk_size] for i in range(0, len(all_urls), chunk_size)]

    with Pool(num_processes) as p:
        results = p.map(worker, chunks)

    # Flatten the results
    flattened_results = [item for sublist in results for item in sublist]

    non_200_urls = [result for result in flattened_results if isinstance(result[1], tuple) and (result[1][0] != 200 or result[1][1] != 200) or isinstance(result[1], str)]

    # Save non 200 URLs to a new CSV
    with open(output_filename, 'w', newline='') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerow(['URL', 'Initial Status Code', 'Final Status Code'])

        for result in non_200_urls:
            url, status_info = result
            if isinstance(status_info, tuple):
                writer.writerow([url] + list(status_info))
            else:  # This is the case where an error occurred
                writer.writerow([url, status_info, status_info])  # Marking both status codes as "Error"

if __name__ == "__main__":
    input_filename = "checkStatusCodes.csv"
    output_filename = "NON200.csv"
    num_processes = 1  # You can adjust this based on your experiments
    check_urls_in_csv(input_filename, output_filename, num_processes)
