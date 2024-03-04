import csv
import requests


def get_status_code(url):
    try:
        # Initial response without following redirects
        response = requests.get(url, timeout=10, allow_redirects=False)
        initial_status = response.status_code

        # If it's a redirect (3xx status code), then get the final status
        if 300 <= initial_status < 400:
            final_response = requests.get(url, timeout=10, allow_redirects=True)
            final_status = final_response.status_code
        else:
            final_status = initial_status

        print(f"{url} ; Initial: {initial_status} ; Final: {final_status}")
        return (url, (initial_status, final_status))

    except requests.RequestException:
        return (url, ("Error", "Error"))


def check_urls_in_csv(input_filename, output_filename):
    non_200_urls = []

    with open(input_filename, 'r') as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            url = row['url']
            status = get_status_code(url)
            print(f"{url} ; {status}")

            if status != 200:
                non_200_urls.append((url, status))

    # Save non 200 URLs to a new CSV
    with open(output_filename, 'w', newline='') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerow(['URL', 'Status Code'])

        for url, status in non_200_urls:
            writer.writerow([url, status])


if __name__ == "__main__":
    input_filename = "checkStatusCodes.csv"
    output_filename = "NON200.csv"
    check_urls_in_csv(input_filename, output_filename)
