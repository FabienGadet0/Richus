import csv
import pandas as pd
import sqlalchemy as sa
import os
from src.db.db import create_connector


# this replace everything
def insert_csv_to_db_initial_dump(csv_file_path, table_name):
    engine = create_connector()
    df = pd.read_csv(csv_file_path)
    date_columns = [col for col in df.columns if col in ['last_updated', 'last_updated_fr', 'datetime']]

    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')  # Coerce any errors in conversion to NaT

    with engine.begin() as connection:
        try:
            if date_columns:
                df.to_sql(name=table_name, con=connection, if_exists='replace', index=False, dtype={col: sa.types.DateTime() for col in date_columns})
            else:
                df.to_sql(name=table_name, con=connection, if_exists='replace', index=False)
        except Exception as e:
            print(f"Error inserting data from {csv_file_path} into {table_name}: {e}")
            print(f"Error type: {type(e)}")
            raise

    print(f"Data from {csv_file_path} inserted into {table_name} [LOCAL : {os.environ.get('IS_LOCAL')}] . {df.shape} rows")

def import_to_db_from_csv():
    try:
        data_directory = "data"
        for subdir, dirs, files in os.walk(data_directory):
            for filename in files:
                if filename.endswith(".csv"):
                    csv_file_path = os.path.join(subdir, filename)
                    subdir_name = os.path.basename(subdir)  # bronze, silver, or gold
                    table_name = f"{subdir_name}_{filename[:-4]}"  # Remove '.csv' extension and prepend subdir_name
                    insert_csv_to_db_initial_dump(csv_file_path, table_name)
    except Exception as e:
        print(f"Failed to import data: {e}")
        raise

def main():
    import_to_db_from_csv()

if __name__ == "__main__":
    main()
