from src.db.db import *

def create_mapping():
   execute_query_from_file("src/sql/rune_mapping.sql")

def main():
    df = fetch_all_data_from_query("src/sql/runes_focus_with_prices.sql")

    df["Lot [1]"] = pd.to_numeric(df["Lot [1]"], errors='coerce')
    df["focus_profitability"] = round(df["Lot [1]"] * df["focus_runes_qty"], 2)
    df["profitability"] = round(df["Lot [1]"] * df["generated_runes_qty"], 2)

    print(df[df["item_id"] == 14082][["item_id", "rune_stat_name","jet", "coefficient", "Lot [1]","pdb", "generated_runes_qty", "focus_profitability", "profitability"]])

if __name__ == "__main__":
    main()
