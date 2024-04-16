import pandas as pd
from bs4 import BeautifulSoup

HTML_FILE_PATH = 'data/raw/a.html'


def parse_html_to_csv():

    # Open the HTML file
    with open(HTML_FILE_PATH, 'r') as f:
        html_content = f.read()

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table with ID 'scanTable'
    table = soup.find('table', id='scanTable')

    # Extract table headers (assuming they're in the first 'tr' element within 'thead')
    headers = [th.text.strip()
               for th in table.find('thead').find('tr').find_all('th')]

    # Extract table data (excluding header row)
    from concurrent.futures import ThreadPoolExecutor

    def extract_row_data(row):
        row_data = []
        for td in row.find_all('td'):
            text = td.text.strip() if td.text else None  # Handle empty cells
            if td.find('p'):
                # Extract text from nested paragraphs
                text = td.find('p').text.strip()
            row_data.append(text)
        return row_data

    data = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(extract_row_data, row) for row in table.find('tbody').find_all('tr')]
        for future in futures:
            data.append(future.result())

    # Create the DataFrame
    df = pd.DataFrame(data, columns=headers)
    df.dropna(axis=1, how='all', inplace=True)
    file_name= "data/bronze/no_id_hdv_prices.csv"
    df.rename(columns={'id': 'item_id'}, inplace=True)
    df.dropna(axis=1, how='all', inplace=True)
    df.to_csv(file_name, index=False)
    print(f"{file_name} saved , total rows : {df.shape}")

def merge_hdv_id():
    df1 = pd.read_csv("data/bronze/items.csv")
    df2 = pd.read_csv("data/bronze/no_id_hdv_prices.csv")

    # Merge the two dataframes on the "name" column
    merged_df = pd.merge(df1, df2, left_on="name",right_on="Nom de l'objet", how='inner')

   # Clean
    merged_df = merged_df.drop_duplicates()
    merged_df = merged_df[merged_df["item_id"] != 666]
    merged_df.dropna(axis=1, inplace=True)


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
