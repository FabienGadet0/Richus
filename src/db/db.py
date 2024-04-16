import sqlalchemy as sa
import os
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

def create_connector(is_local : bool = os.environ.get("IS_LOCAL") == "True"):
    DATABASE_HOST_NAME = os.environ.get("DATABASE_HOST_NAME")
    DATABASE_HOST_NAME_LOCAL = os.environ.get("DATABASE_HOST_NAME_LOCAL")
    AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
    CONN_URL = DATABASE_HOST_NAME_LOCAL if is_local  else f"sqlite+libsql://{DATABASE_HOST_NAME}/?authToken={AUTH_TOKEN}&secure=true"
    return sa.create_engine(CONN_URL)


def fetch_all_data_from_query(query_file,limit=3000):
    engine = create_connector()
    with open(query_file) as f:
        query = f.read()

    def fetch_data(offset, limit):
        paginated_query = f"{query} LIMIT {limit} OFFSET {offset}"
        return pd.read_sql(paginated_query, engine)

    data_frames = []
    offset = 0
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for _ in range(3):
            futures.append(executor.submit(fetch_data, offset, limit))
            offset += limit
        for future in futures:
            df = future.result()
            if not df.empty:
                data_frames.append(df)

    if data_frames:
        df = pd.concat(data_frames, ignore_index=True)
        print(f"Data retrieved from query in {query_file} {df.shape} ")
        return df
    else:
        print(f"No data found for query in {query_file}")
        return pd.DataFrame()

def fetch_all_data(table_name):
    engine = create_connector()
    def fetch_data(offset, limit):
        query = f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"
        return pd.read_sql(query, engine)
    data_frames = []
    offset = 0
    limit = 10000
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for _ in range(3):
            futures.append(executor.submit(fetch_data, offset, limit))
            offset += limit
        for future in futures:
            df = future.result()
            if not df.empty:
                data_frames.append(df)

    if data_frames:
        df = pd.concat(data_frames, ignore_index=True)
        print(f"table {table_name} retrieved {df.shape}")
        return df
    else:
        print(f"{table_name} empty")
        return pd.DataFrame()

def batch_insert_to_db(dataframe, table_name):
    batch_size = 10000
    engine = create_connector()
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for start_row in range(0, dataframe.shape[0], batch_size):
            end_row = min(start_row + batch_size, dataframe.shape[0])
            batch = dataframe.iloc[start_row:end_row]
            futures.append(executor.submit(batch.to_sql, table_name, engine, if_exists='append', index=False))
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Failed to insert batch into {table_name}: {e}")
    print(f"Data inserted to {table_name} {dataframe.shape}")

def execute_query_from_file(query_file):
    engine = create_connector()
    with open(query_file) as f:
        queries = f.read().split(';')
    with engine.begin() as conn:
        for query in queries:
            if query.strip():
                conn.execute(sa.text(query))
