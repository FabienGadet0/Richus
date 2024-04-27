import sqlalchemy as sa
import os
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

MAX_WORKER = 3


def create_connector(is_local: bool = os.environ.get("IS_LOCAL") == "True"):
    DATABASE_HOST_NAME = os.environ.get("DATABASE_HOST_NAME")
    DATABASE_HOST_NAME_LOCAL = os.environ.get("DATABASE_HOST_NAME_LOCAL")
    AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
    # CONN_URL = DATABASE_HOST_NAME_LOCAL if is_local  else f"sqlite+libsql://{DATABASE_HOST_NAME}/?authToken={AUTH_TOKEN}&secure=true"
    # CONN_URL = f"postgresql+psycopg2://postgres:1@localhost:5432/postgres"
    CONN_URL = os.environ.get("DATABASE_URL")
    return sa.create_engine(CONN_URL)


def fetch_all_data_from_query(query_file, limit=3000):
    with open(query_file) as f:
        query = f.read()

    def fetch_data(offset, limit):
        engine = create_connector()
        paginated_query = f"{query} LIMIT {limit} OFFSET {offset}"
        with engine.connect() as conn:
            return pd.read_sql(paginated_query, conn)

    data_frames = []
    offset = 0

    while True:
        with ThreadPoolExecutor(max_workers=MAX_WORKER) as executor:
            futures = []
            # Spawn a new set of futures.
            for _ in range(3):
                future = executor.submit(fetch_data, offset, limit)
                futures.append(future)
                offset += (
                    limit  # Prepare the offset for the next potential set of fetches
                )

            empty_dataframes = 0
            for future in futures:
                try:
                    df = future.result()
                    if not df.empty:
                        data_frames.append(df)
                    else:
                        empty_dataframes += 1
                except Exception as e:
                    print(f"Error fetching data: {e}")

            # If all futures returned empty DataFrames, exit the loop, since we've fetched all data.
            if empty_dataframes == len(futures):
                break

    if data_frames:
        df = pd.concat(data_frames, ignore_index=True)
        print(f"Data retrieved from query in {query_file}: {df.shape}")
        return df
    else:
        print(f"No data found for query in {query_file}")
        return pd.DataFrame()


def fetch_all_data(table_name, limit=3000):

    # Function to fetch data with given offset and limit
    def fetch_data(offset, limit):
        engine = create_connector()
        query = f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"
        with engine.connect() as conn:
            return pd.read_sql(query, conn)

    # Initialize list to store chunks of DataFrames
    data_frames = []
    # Initial offset and limit
    offset = 0

    while True:
        with ThreadPoolExecutor(max_workers=MAX_WORKER) as executor:
            futures = []
            # Dynamically add futures for fetching data
            for _ in range(3):
                futures.append(executor.submit(fetch_data, offset, limit))
                offset += limit  # prepare offset for next chunk

            empty_dataframes = 0
            for future in futures:
                df = future.result()
                if not df.empty:
                    data_frames.append(df)
                else:
                    empty_dataframes += 1

            # if all fetched chunks are empty, it means we've fetched all data
            if empty_dataframes == len(futures):
                break

    # Concatenate all fetched DataFrames into a single DataFrame
    if data_frames:
        df = pd.concat(data_frames, ignore_index=True)
        print(f"Table {table_name} retrieved: {df.shape[0]} rows")
        return df
    else:
        print(f"Table {table_name} is empty")
        return pd.DataFrame()


def batch_insert_to_db(dataframe, table_name, date_columns=None, if_exists="append"):
    batch_size = 10000
    engine = create_connector()
    if date_columns is None:
        date_columns = []
    for start_row in range(0, dataframe.shape[0], batch_size):
        end_row = min(start_row + batch_size, dataframe.shape[0])
        batch = dataframe.iloc[start_row:end_row]
        with engine.begin() as conn:  # Start a new transaction
            try:
                batch.to_sql(
                    table_name,
                    conn,
                    if_exists=if_exists,
                    index=False,
                    dtype={col: sa.types.DateTime() for col in date_columns},
                )
            except Exception as e:
                print(f"Failed to insert batch into {table_name}: {repr(e)}")
                conn.close()
                raise
            finally:
                print(f"Data inserted to {table_name} {batch.shape}")


def execute_query_from_file(query_file):
    engine = create_connector()
    with open(query_file) as f:
        queries = f.read().split(";")
    for query in queries:
        if query.strip():
            with engine.begin() as conn:  # Start a new transaction for each query
                conn.execute(sa.text(query))
