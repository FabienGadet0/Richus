import pandas as pd
import requests
import os
from threading import Thread, Lock
from fake_useragent import UserAgent

ua = UserAgent()

headers = {'User-Agent': ua.random,
           'Content-Type': 'application/json'}


def download_brisage_coeff(server_id, item_id):
    """Downloads JSON data for a specific item and saves it with timestamp."""

    url = "https://api.brifus.fr/coeff"
    # now = datetime.now().strftime("%d-%H")  # Detailed timestamp format
    body = "{" + f"\"item\": {item_id}, \"server\": {server_id}" + "}"
    try:
        response = requests.post(url, headers=headers, data=body)
        if response.status_code != 200:
            # print(
            #     f"Error downloading item stats for item {item_id} : {response.status_code}")
            return
        df = pd.DataFrame(response.json(), index=[0])
        # check if file exist
        file_exist = os.path.isfile("data/bronze/brisage_coeff.csv")
        df.to_csv("data/silver/brisage_coeff.csv",
                  mode='a', header=(not file_exist), index=False)
        # print(f"new line added for id {item_id}")

    except Exception as e:
        print(
            f"Error downloading item stats for item {item_id} : {str(e)}")


def get_brisage_coeff_for_ids(server_id, item_ids):
    """Multithreaded execution for downloading item stats."""

    max_threads = len(item_ids) if len(item_ids) < 20 else 20
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

            download_brisage_coeff(server_id, item_id)

        # Create and start threads
    for _ in range(max_threads):
        thread = Thread(target=download_worker)
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print("All item stats downloads complete!")


def main():
    data_dir = "data/silver"
    os.makedirs(data_dir, exist_ok=True)

    df = pd.read_csv("data/silver/id_hdv_prices.csv")
    get_brisage_coeff_for_ids(2, df['id'].tolist())


if __name__ == "__main__":
    main()
