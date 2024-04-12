import pandas as pd
from bs4 import BeautifulSoup

HTML_FILE_PATH = 'data/bronze/a.html'


def parse_html():

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
    data = []
    for row in table.find('tbody').find_all('tr'):
        # Extract data from each cell (handling potential empty cells or nested elements)
        row_data = []
        for td in row.find_all('td'):
            text = td.text.strip() if td.text else None  # Handle empty cells
            if td.find('p'):
                # Extract text from nested paragraphs
                text = td.find('p').text.strip()
            row_data.append(text)
        data.append(row_data)

    # Create the DataFrame
    df = pd.DataFrame(data, columns=headers)
    df.dropna(axis=1, how='all', inplace=True)
    return df


def main():
    df = parse_html()
    print("html parsed")
    df.to_csv("data/silver/hdv_prices.csv", index=False)
    print("saved to csv")


if __name__ == "__main__":
    main()
