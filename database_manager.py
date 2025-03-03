import sqlite3
import pandas as pd


# Database file paths
DB_FILE = "mouse_database.db"  # Primary database
TABLE_LIVE = "mouse_list"  # Secondary database
TABLE_DECEASED = "deceased_mouse_list"  # Table name

TABLE_NAME = TABLE_LIVE

# Column names (ensures consistency across functions)
COLUMN_NAMES = [
    "id", "cage_number", "mouseline", "genotype", "gender",
    "dob", "available", "health", "username", "user_manipulations", "status", "comments"
]

# ----------------- DATABASE INITIALIZATION -----------------
def initialize_database():
    """Creates the main database table if it does not exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            INDEX_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            id TEXT,
            cage_number INTEGER,
            mouseline TEXT,
            genotype TEXT,
            gender TEXT,
            dob TEXT,
            available TEXT,
            health TEXT,
            username TEXT,
            user_manipulations TEXT,
            status TEXT
            comments TEXT
        )
    """)

    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    columns = [column[1] for column in cursor.fetchall()]

    conn.commit()
    conn.close()

def create_empty_database():
    """Creates the secondary (deceased) database if it does not exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id TEXT PRIMARY KEY,
            cage_number TEXT,
            mouseline TEXT,
            genotype TEXT,
            gender TEXT,
            dob TEXT,
            available TEXT,
            health TEXT,
            username TEXT,
            user_manipulations TEXT,
            status TEXT,
            comments TEXT
        )
    """)
    conn.commit()
    conn.close()

# ----------------- DATA MANAGEMENT FUNCTIONS -----------------
def fetch_data(db_file, table_name):
    conn = sqlite3.connect(db_file)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df


def filter_records(db_file, column, value):
    """Filters records based on a column value in the specified database."""
    conn = sqlite3.connect(db_file)
    df = pd.read_sql(f"SELECT id, cage_number, mouseline, genotype, gender, dob, available, health, username, user_manipulations, status, comments FROM {TABLE_NAME} WHERE {column} = ?", conn, params=(value,))
    conn.close()
    return df

def export_to_csv(db_file, csv_filename):
    """Exports the table to a CSV file from the specified database, excluding INDEX_ID."""
    conn = sqlite3.connect(db_file)
    df = pd.read_sql(f"SELECT id, cage_number, mouseline, genotype, gender, dob,available, health, username, user_manipulations, status, comments FROM {TABLE_NAME}", conn)
    df.to_csv(csv_filename, index=False)
    conn.close()

# ----------------- RECORD OPERATIONS -----------------
def insert_record(db_file, table_name, record):
    """Inserts a new record into the specified database, including COMMENTS."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    columns = ', '.join(record.keys())
    placeholders = ', '.join(['?'] * len(record))
    
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    
    cursor.execute(sql, tuple(record.values()))
    
    conn.commit()
    conn.close()
    print(f"✅ New record inserted successfully into {table_name}.")


def update_record(db_file, id, cage_number, mouseline, genotype, gender, dob, available, health, username, user_manipulations, status, comments):
    """Updates an existing record using id as the unique identifier, including COMMENTS."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Retrieve INDEX_ID internally
    cursor.execute(f"SELECT INDEX_ID FROM {TABLE_NAME} WHERE id = ?", (id,))
    index_id = cursor.fetchone()

    if not index_id:
        conn.close()
        return False  # Record not found

    index_id = index_id[0]  # Extract INDEX_ID

    cursor.execute(f"""
        UPDATE {table_name} SET ... WHERE id = ?
        SET cage_number = ?, mouseline = ?, genotype = ?, gender = ?, dob = ?, 
            available = ?, health = ?, username = ?, user_manipulations = ?, status = ?, comments = ?
        WHERE id = ?
    """, (cage_num, mouseline, genotype, gender, dob, available, health, user_name, user_manipulations, status, comments, index_id))

    conn.commit()
    conn.close()
    return True


def delete_record(db_file, id_tatoo_nt):
    """Deletes a record from the database using id as the unique identifier."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # ✅ Ensure ID_TATOO_NT exists before trying to delete
    cursor.execute(f"SELECT 1 FROM {TABLE_NAME} WHERE id = ?", (id,))
    if cursor.fetchone() is None:
        conn.close()
        return False  # No record found, return failure

    # ✅ Delete the record
    cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return True  # ✅ Successfully deleted



# ----------------- ROW COPY FUNCTION -----------------
def copy_row_to_new_db(id):
    """Copies a specific row from the primary database to the secondary database using id."""
    conn_old = sqlite3.connect(DB_FILE)
    conn_new = sqlite3.connect(NEW_DB_FILE)

    cursor_old = conn_old.cursor()
    cursor_new = conn_new.cursor()

    cursor_old.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", (id,))
    row = cursor_old.fetchone()

    if row:
        cursor_new.execute(f"""
            INSERT INTO {TABLE_NAME} (id, cage_number, mouseline, genotype, gender, dob, available, health, username, user_manipulations, status, comments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row)

        conn_new.commit()

    conn_old.close()
    conn_new.close()








