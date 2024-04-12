import json
import sys
import requests
import csv
import random
import time
from threading import Thread, Lock
from fake_useragent import UserAgent
ua = UserAgent()
lock = Lock()


def download_item_data(item_id,  base_url="https://api.dofusdb.fr/items/"):
    """Downloads item data from the API and saves it to CSV."""

    url = f"{base_url}{item_id}?lang=fr"
    headers = {'User-Agent': ua.random}
    try:
        # Send an HTTP GET request with a random delay (0.1-0.5 seconds) to avoid overwhelming the server
        time.sleep(random.uniform(0.1, 0.5))
        response = requests.get(url, headers)

        # Check for successful response
        if response.status_code != 200:
            print(f"error status code : {response.status_code}")
            return

        # print(
        #     f"Error retrieving item with ID {item_id}: {response.status_code}")
        time.sleep(1)  # Backoff for 1 second on error

    except Exception as e:
        print(f"Error downloading item data for ID {item_id}: {e}")
        time.sleep(2)  # Backoff for 2 seconds on other errors

    try:
        # Parse the JSON data from the response
        item_data = json.loads(response.text)

        # Extract desired information, skipping item with ID 666
        if item_data["id"] != 666:
            item_dict = {"id": item_data["id"],
                         "name": item_data["name"]["fr"], "level": item_data["level"],
                         "type": item_data["superType"]["name"]["fr"]}

            with lock:  # Thread-safe access to CSV file
                with open("data/bronze/item_ids_matching.csv", "a+", newline="") as csvfile:
                    # print("hello wassup")
                    writer = csv.DictWriter(csvfile, fieldnames=[
                                            "id", "name", "level", "type"])
                    if csvfile.tell() == 0:
                        writer.writeheader()

                    writer.writerow(item_dict)

            print(
                f"{item_data['id']}: {item_data['name']['fr']} OK"
            )
        else:
            print(f"id : {item_id} KO")

    except Exception as e:
        print(f"Error parsing JSON for item ID {item_id} -> {e}")


def run(id_range=(0, 4000)):
    """Multithreaded execution for downloading item data with a maximum of 30 threads."""

    base_url = "https://api.dofusdb.fr/items/"
    item_ids = range(int(id_range[0]), int(
        id_range[1]) + 1)  # Ensure inclusive range

    # Use a Lock for thread-safe CSV file access

    threads = []

    max_threads = 30

    # Create and start threads
    for item_id in item_ids:
        if len(threads) >= max_threads:
            # Wait for a thread to finish before starting a new one
            for thread in threads:
                thread.join()
            threads.clear()

        thread = Thread(target=download_item_data,
                        args=(item_id, base_url))
        thread.start()
        threads.append(thread)

    # Wait for all remaining threads to finish
    for thread in threads:
        thread.join()

    print(f"Done {len(item_ids)} items")


def main():
    """Handles script arguments and calls the `run` function."""

    num_args = len(sys.argv)

    if num_args < 3:
        print("Error: Please provide at least two arguments (excluding the script name).")
        sys.exit(1)

    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    run((arg1, arg2))


if __name__ == "__main__":
    main()
