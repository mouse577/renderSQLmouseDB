import pandas as pd
import sqlite3
import subprocess
import os

def save_database_to_github():
    conn = sqlite3.connect('mouse_database.db')
    df_mouse = pd.read_sql('SELECT * FROM mouse_list', conn)
    df_deceased = pd.read_sql('SELECT * FROM deceased_mouse_list', conn)
    conn.close()

    df_mouse.to_csv('mouse_list.csv', index=False)
    df_deceased.to_csv('deceased_mouse_list.csv', index=False)

    github_username = os.getenv('GITHUB_USERNAME')
    github_token = os.getenv('GITHUB_TOKEN')
    repo_url = f"https://{mouse577}:{ghp_5z7y0odqUnqVCBwgTzpTM87q1tgG503ySHif}@https://github.com/mouse577/renderSQLmouseDB.git"

    subprocess.run(["git", "config", "--global", "user.email", "automation@example.com"])
    subprocess.run(["git", "config", "--global", "user.name", "Render Automation Bot"])

    subprocess.run(["git", "add", "mouse_list.csv", "deceased_mouse_list.csv"])
    subprocess.run(["git", "commit", "-m", "Automated backup of mouse database tables"])
    subprocess.run(["git", "push", repo_url])

if __name__ == "__main__":
    save_database_to_github()
    print("✅ Database changes saved to GitHub.")
