import sys
import pandas as pd
import requests
import os
from datetime import datetime
from threading import Thread, Lock
from fake_useragent import UserAgent
import json

ua = UserAgent()

headers = {'User-Agent': ua.random}
server_id = 2  # Draconiros


def download_item_stats(server_id, item_id):
    """Downloads JSON data for a specific item and saves it with timestamp."""

    url = f"https://api.brifus.fr/itemStats?serverId={server_id}&itemId={item_id}"
    now = datetime.now().strftime("%m-%d")  # Detailed timestamp format
    try:
        response = requests.get(url, headers)

        if response.status_code != 200:
            print(
                f"Error downloading item stats for item {item_id} (server {server_id}): {response.status_code}")
            return
        df = pd.json_normalize(json.loads(response.content))
        filename = f"data/bronze/item_runes/{item_id}_{now}.csv"
        df.to_csv(filename,
                  mode='a', header=True, index=False)

        # with open(os.path.join(data_dir, filename), "wb") as f:
        #     f.write(response.content)

        print(
            f"Downloaded item stats for item {item_id} (server {server_id}): {filename}")
    except Exception as e:
        print(
            f"Error downloading item stats for item {item_id} (server {server_id}): {e}")


def download_worker(id, lock):
    with lock:  # Acquire lock for thread-safe access to item_ids
        if not id:
            return
            # Remove the first item ID from the list

        download_item_stats(server_id, id)


def get_rune_for_ids(item_ids):  # sourcery skip: avoid-builtin-shadow
    """Multithreaded execution for downloading item stats."""

    max_threads = min(len(item_ids), 20)

    threads = []
    lock = Lock()  # Lock for thread-safe queue management

    while item_ids:
        # Create and start threads
        for _ in range(max_threads):
            id = item_ids.pop(0)
            thread = Thread(target=download_worker, args=(id, lock))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    print("All item stats downloads complete!")


def main():
    num_args = len(sys.argv)
    data_dir = "data/bronze/item_runes"
    # Create directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)

    if num_args == 1:
        df = pd.read_csv("data/silver/hdv_brisage_items.csv")
        get_rune_for_ids(df['id'].tolist())
    elif num_args == 2:
        arg1 = sys.argv[1]
        # arg1 is a path to a file , check if it exists and if its a csv
        if not os.path.exists(arg1) or not arg1.endswith(".csv"):
            print(
                "Error: Please provide a valid path to a CSV file that has an id field.")
            sys.exit(1)
        get_rune_for_ids(arg1)
    else:
        print("Error: Please provide at least two arguments (excluding the script name).")
        sys.exit(1)


if __name__ == "__main__":
    main()
