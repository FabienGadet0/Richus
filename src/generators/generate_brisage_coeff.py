import pandas as pd
import requests
import os
from threading import Thread, Lock
from fake_useragent import UserAgent
import datetime

ua = UserAgent()

headers = {'User-Agent': ua.random}

def download_brisage_history(server_id, item_id):
    """Downloads JSON data for a specific item and saves it with timestamp."""

    url = f"https://api.brifus.fr/coeff/evolution?serverId={server_id}&itemId={item_id}"
    now = datetime.datetime.now().strftime("%d-%H")  # Detailed timestamp format
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
             # print(f"Error downloading item stats for item {item_id} : {response.status_code}")
             return
        df = pd.DataFrame(response.json())
        if not df.empty:
            df.rename(columns={'item': 'item_id','server':'server_id','dateTime':'last_updated','datetime':'last_updated'}, inplace=True)
            df['last_updated'] = pd.to_datetime(df['last_updated'], format='%d/%m/%Y %H:%M')
            df['last_updated'] = df['last_updated'].dt.strftime('%m/%d/%Y %H:%M')

            # check if file exist
            file_exist = os.path.isfile("data/bronze/brisage_coeff_history.csv")
            df.to_csv("data/bronze/brisage_coeff_history.csv",
                      mode='a', header=(not file_exist), index=False)
            print(f"new line added for id {item_id}")

    except Exception as e:
        print(
            f"Error downloading item stats for item {item_id} : {str(e)}")
        raise

def get_brisage_coeff_for_ids(server_id, item_ids):
    """Multithreaded execution for downloading item stats."""

    max_threads = len(item_ids) if len(item_ids) < 10 else 10
    is_first = True
    # item_ids = ids

    threads = []
    lock = Lock()  # Lock for thread-safe queue management

    def download_worker():
        while item_ids:
            with lock:  # Acquire lock for thread-safe access to item_ids
                if not item_ids:
                    break
                    # Remove the first item ID from the list
                item_id = item_ids.pop(0)

            if is_first:
                download_brisage_history(server_id, item_id)

        # Create and start threads
    for _ in range(max_threads):
        thread = Thread(target=download_worker)
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print("All item stats downloads complete!")



def initial_dump():
    data_dir = "data/silver"
    os.makedirs(data_dir, exist_ok=True)

    df = pd.read_csv("data/silver/hdv_prices.csv")
    get_brisage_coeff_for_ids(2, df['item_id'].tolist())

def daily():
    print("todo")

if __name__ == "__main__":
    initial_dump()
