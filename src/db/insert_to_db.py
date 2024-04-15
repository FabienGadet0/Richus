import csv
import pandas as pd
import sqlalchemy as sa
import os
import dotenv

dotenv.config()

DATABASE_HOST_NAME = os.environ.get("DATABASE_HOST_NAME")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
CONN_URL = f"sqlite+libsql://{DATABASE_HOST_NAME}/?authToken={AUTH_TOKEN}&secure=true"

# this replace everything , so use it only for initial dump
def insert_csv_to_db_initial_dump(csv_file_path, table_name):
    engine = sa.create_engine(CONN_URL)
    df = pd.read_csv(csv_file_path)
    try:
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
    except Exception as e:
        engine.execute(f"ROLLBACK")
        print(f"Error inserting data from {csv_file_path} into {table_name}: {e}")
    else:
        print(f"Data from {csv_file_path} inserted into {table_name} table. {df.shape} length")

def import_to_db_from_csv():
    data_directory = "data"
    for subdir, dirs, files in os.walk(data_directory):
        for filename in files:
            if filename.endswith(".csv"):
                csv_file_path = os.path.join(subdir, filename)
                subdir_name = os.path.basename(subdir)  # bronze, silver, or gold
                table_name = f"{subdir_name}_{filename[:-4]}"  # Remove '.csv' extension and prepend subdir_name
                insert_csv_to_db_initial_dump(csv_file_path, table_name)

def main():
    import_to_db_from_csv()

if __name__ == "__main__":
    main()
