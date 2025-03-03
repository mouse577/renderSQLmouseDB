import pandas as pd
import sqlite3
import requests

def download_csv_from_github(url, filename):
    # headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as f:
        f.write(response.content)

def initialize_database_from_github():
    mouse_list_url = "https://raw.githubusercontent.com/mouse577/renderSQLmouseDB/main/initial_mouse_list.csv"
    deceased_list_url = "https://raw.githubusercontent.com/mouse577/renderSQLmouseDB/main/initial_deceased_list.csv"

    download_csv_from_github(mouse_list_url, 'mouse_list.csv')
    download_csv_from_github(deceased_list_url, 'deceased_mouse_list.csv')

    conn = sqlite3.connect(DB_FILE)
    pd.read_csv('mouse_list.csv').to_sql(TABLE_LIVE, conn, if_exists='replace', index=False)
    pd.read_csv('deceased_mouse_list.csv').to_sql(TABLE_DECEASED, conn, if_exists='replace', index=False)
    conn.close()

if __name__ == "__main__":
    initialize_database_from_github()
    print("✅ Database initialized from GitHub CSV files.")
