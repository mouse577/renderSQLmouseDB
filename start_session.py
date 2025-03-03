import pandas as pd
import sqlite3
import requests

def download_csv_from_github(url, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as f:
        f.write(response.content)

def initialize_database_from_github():
    mouse_list_url = "https://raw.githubusercontent.com/mouse577/renderSQLmouseDB/main/initial_mouse_list.csv"
    deceased_list_url = "https://raw.githubusercontent.com/mouse577/renderSQLmouseDB/main/initial_deceased_mouse_list.csv"

    download_csv_from_github(mouse_list_url, 'mouse_list.csv')
    download_csv_from_github(deceased_list_url, 'deceased_mouse_list.csv')

    conn = sqlite3.connect('mouse_database.db')
    pd.read_csv('mouse_list.csv').to_sql('mouse_list', conn, if_exists='replace', index=False)
    pd.read_csv('deceased_mouse_list.csv').to_sql('deceased_mouse_list', conn, if_exists='replace', index=False)
    conn.close()

if __name__ == "__main__":
    initialize_database_from_github()
    print("✅ Database initialized from GitHub CSV files.")
