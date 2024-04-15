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


def get_rune_for_ids(item_ids):
    threads = []
    lock = Lock()
    max_threads = min(len(item_ids), 20)
    for i in range(0, len(item_ids), max_threads):
        threads = []
        for item_id in item_ids[i:i+max_threads]:
            t = Thread(target=download_rune_for_item_id, args=(server_id,item_id, lock))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

def get_rune_for_ids_from_file(file_path):
    df = pd.read_csv(file_path)
    get_rune_for_ids(df['id'].tolist())

def download_rune_for_item_id(server_id, item_id,lock):
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
        lock.acquire()
        filename = "data/bronze/item_runes.csv"
        df.rename(columns={"id":"idk","stats.id":"stat_id","stats.name":"rune_stat_name","stats.weight":"rune_weight","stats.rune":"rune_stats"}, inplace=True)
        df.drop(columns=['stats.price'], inplace=True)
        df["item_id"] = item_id
        try:
            df.to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)
        except:
            print(f"Error writing to file {filename}")
            lock.release()
        finally:
            lock.release()
        print(
            f"Downloaded item stats for item {item_id} (server {server_id}): {filename}")
    except Exception as e:
        print(
            f"Error downloading item stats for item {item_id} (server {server_id}): {e}")


def main():
    num_args = len(sys.argv)
    data_dir = "data/bronze/item_runes"
    # Create directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)

    if num_args == 1:
        get_rune_for_ids_from_file("data/bronze/items.csv")
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
