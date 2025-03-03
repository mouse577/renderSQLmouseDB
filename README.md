# renderSQLmouseDB
SQLite with python gui for web-based mouse DB management on Render

# Mouse Database Manager - Render + GitHub Sync Edition

## How It Works
1. On app start, the latest `mouse_list.csv` and `deceased_mouse_list.csv` are downloaded from GitHub.
2. These files are loaded into a fresh SQLite database (`mouse_database.db`).
3. The existing Python GUI (`gui.py`) runs and allows users to edit the data.
4. When the user closes the GUI, all tables are automatically exported to CSV and pushed back to GitHub.

---

## Required Environment Variables (set in Render Dashboard)
| Variable | Description |
|---|---|
| GITHUB_USERNAME | Your GitHub username |
| GITHUB_TOKEN | Personal access token with `repo` permission |

---

## Required Files in Repo

