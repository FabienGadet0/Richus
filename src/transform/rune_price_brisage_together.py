from src.db.db import fetch_all_data_from_query, batch_insert_to_db
import numpy as np
import pandas as pd


def main():
    try:
        df = fetch_all_data_from_query(
            "src/sql/gold_price_brisage.sql", limit=1000)

        for column in df.select_dtypes(include=['float']).columns:
            df[column] = df[column].round(2)

        df['prix'] = pd.to_numeric(df['prix'], errors='coerce')
        df['craft'] = pd.to_numeric(df['craft'], errors='coerce')

        df['craft_vs_focus_diff'] = (
            df['focus_rentabilite'] - df['craft']).round(2)
        df['craft_vs_prix_diff'] = (df['prix'] - df['craft']).round(2)
        df['craft_vs_total_profit_non_focus_diff'] = (
            df['total_profit_non_focus'] - df['craft']).round(2)
        df['meilleur_renta_valeur'] = (
            df[['craft_vs_focus_diff', 'craft_vs_prix_diff', 'craft_vs_total_profit_non_focus_diff']].max(axis=1)).round(0)
        df['meilleur_renta'] = df[['craft_vs_focus_diff', 'craft_vs_prix_diff',
                                   'craft_vs_total_profit_non_focus_diff']].idxmax(axis=1)
        df['meilleur_renta'] = np.where((df['meilleur_renta_valeur'] <= 0) |
                                        df['meilleur_renta_valeur'].isnull(), 'non_rentable', df['meilleur_renta'])
        df['meilleur_renta'] = df['meilleur_renta'].replace(
            {'craft_vs_focus_diff': 'craft_brisage_focus', 'craft_vs_prix_diff': 'craft_revente', 'craft_vs_total_profit_non_focus_diff': 'craft_brisage'})
        df['meilleur_renta_percent'] = (
            ((df['meilleur_renta_valeur']) / df['craft']) * 100).round(2)

        df = df.drop_duplicates()
        batch_insert_to_db(df, "gold_price_brisage")
    except Exception as e:
        print(f"Failed to process: {e}")
        raise


if __name__ == "__main__":
    main()
