import pandas as pd
from bs4 import BeautifulSoup
import re
import pytz
from datetime import datetime

HTML_FILE_PATH = 'data/raw/c.html'


def parse_html_to_csv():
    # Use pandas to directly read tables from the HTML file
    tables = pd.read_html(HTML_FILE_PATH, encoding='utf-8')

    # Assume the table with ID 'scanTable' is the first table
    df = tables[0]

    df.dropna(axis=1, how='all', inplace=True)
    file_name= "data/bronze/no_id_hdv_prices.csv"
    df.rename(columns={'id': 'item_id',"Nom de l'objet":"nom_de_lobjet"}, inplace=True)

    df['nom_de_lobjet'] = df['nom_de_lobjet'].str.extract(r'^(.+?)\s*\[')
    df['nom_de_lobjet'] = df['nom_de_lobjet'].str.strip()

    df['Craft'] = df['Craft'].str.extract(r':\s*(.*)')
    df['Craft'] = df['Craft'].str.replace('\u2006','')
    df['Craft'] = df['Craft'].str.strip()

    df['Lot [1]'] = df['Lot [1]'].str.replace('\u2006','')
    df['Lot [10]'] = df['Lot [10]'].str.replace('\u2006','')
    df['Lot [100]'] = df['Lot [100]'].str.replace('\u2006','')
    df.dropna(axis=1, how='all', inplace=True)

    df['last_updated_fr'] = datetime.now(pytz.timezone('Europe/Paris')).strftime('%Y-%m-%d %H:%M:%S')
    df.to_csv(file_name, index=False)
    print(f"{file_name} saved , total rows : {df.shape}")

def merge_hdv_id():
    df1 = pd.read_csv("data/bronze/items.csv")
    df2 = pd.read_csv("data/bronze/no_id_hdv_prices.csv")

    # Merge the two dataframes on the "name" column
    merged_df = pd.merge(df1, df2, left_on="name",right_on="nom_de_lobjet", how='inner')

   # Clean
    merged_df = merged_df.drop_duplicates()
    merged_df = merged_df[merged_df["item_id"] != 666]
    # merged_df.dropna(axis=1, inplace=True)


    # Save the merged dataframe to a CSV file
    file_name ="data/silver/hdv_prices.csv"
    merged_df.to_csv(file_name, index=False)

    print(f"{file_name} saved , total rows : {merged_df.shape}")

def main():
    print("parsing html")
    df = parse_html_to_csv()

    print("merging id to hdv")
    merge_hdv_id()


if __name__ == "__main__":
    main()
