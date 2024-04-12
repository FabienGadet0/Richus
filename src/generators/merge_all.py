import pandas as pd


def merge_item_runes():
    # in data/bronze/item_runes/
    pass


def merge_hdv_brisage_ids():
    df1 = pd.read_csv("data/bronze/item_ids_matching.csv")
    df2 = pd.read_csv("data/bronze/hdv_prices.csv")
    df3 = pd.read_csv("data/bronze/brisage_coeff.csv")

    # Merge the two dataframes on the "name" column
    merged_df = pd.merge(pd.merge(df1, df2, left_on="name",
                         right_on="Nom de l'objet", how='inner'), df3, left_on="id", right_on="item", how="inner")

    # Drop duplicates
    merged_df = merged_df.drop_duplicates()

    # Remove rows where the "id" column is equal to 666
    merged_df = merged_df[merged_df["id"] != 666]
    merged_df.dropna(axis=1, inplace=True)
    # Save the merged dataframe to a CSV file
    merged_df.to_csv("data/silver/hdv_brisage_items.csv", index=False)
    print("merged dataframe saved to id_hdv_prices.csv")
