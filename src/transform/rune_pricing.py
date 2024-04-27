from src.db.db import *


def main():
    try:
        df = fetch_all_data_from_query(
            "src/sql/runes_focus_with_prices.sql", limit=1000
        )

        for column in df.select_dtypes(include=["float"]).columns:
            df[column] = df[column].round(2)

        df = df.drop_duplicates()
        batch_insert_to_db(df, "gold_item_rune_price", if_exists="replace")
    except Exception as e:
        print(f"Failed to process: {e}")
        raise


if __name__ == "__main__":
    main()
