import pandas as pd
import numpy as np
from src.db.db import *


def main():
    # Pdb = 3 _ jet _ poids_rune _ lvl / 200 + 1
    # total = Pdb _ (coeff /100)

    df_item_runes = fetch_all_data("bronze_item_runes")
    df_hdv_prices = fetch_all_data("silver_hdv_prices")
    df_brisage_coeff = fetch_all_data_from_query("./src/sql/last_brisage_coeff_per_item.sql")
    df_items = fetch_all_data("bronze_items")

    df_item_runes_filtered = df_item_runes.drop(columns=["idk", "exo"])
    df_merged = pd.merge(df_item_runes_filtered, df_brisage_coeff, on="item_id")
    df_merged.drop_duplicates(inplace=True)
    df_item_runes_filtered["jet"] = ((df_item_runes_filtered["max"] + df_item_runes_filtered["min"]) / 2).round().astype(int)
    df_item_runes_filtered.drop(columns=["min","max"],inplace=True)
    df_final = pd.merge(df_item_runes_filtered, df_items[['item_id', 'level']], on="item_id")
    df_final.drop_duplicates(inplace=True)
    df_final = pd.merge(df_final, df_brisage_coeff[['item_id', 'coefficient']], on="item_id")
    df_final.drop_duplicates(inplace=True)

    # Poids de brisage
    df_final["pdb"] = ((((3 * df_final["jet"] * df_final["rune_weight"] * df_final["level"]) / 200) + 1)/df_final["rune_weight"])
    df_final["pdb"] = df_final["pdb"].apply(lambda x: np.ceil(x * 10) / 10 if x > 0 else 0)

    # Coeff
    df_final["generated_runes_qty"] = df_final["pdb"] * (df_final["coefficient"] / 100)

    # round
    df_final["generated_runes_qty"] = df_final["generated_runes_qty"].apply(lambda x: 0 if x < 0 else x)

    def calculate_focus_runes_qty(row, grouped_df):
        current_pdb = row['pdb']
        other_pdb = grouped_df.get_group(row['item_id'])['pdb'].sum() - current_pdb
        focus_runes_qty = (other_pdb * 0.5) + (current_pdb)
        return focus_runes_qty

    grouped_by_item_id = df_final.groupby('item_id')
    df_final['focus_runes_qty'] = df_final.apply(lambda row: (calculate_focus_runes_qty(row, grouped_by_item_id) / row["rune_weight"]) * (row['coefficient'] / 100), axis=1)

    batch_insert_to_db(df_final,"silver_runes_pdb_focus")


if __name__ == "__main__":
    main()
