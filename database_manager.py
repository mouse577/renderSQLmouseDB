import sqlite3
import pandas as pd

# Database file paths
DB_FILE = "PPL_Scholl_428_MouseDatabase.db"  # Primary database
NEW_DB_FILE = "PPL_Scholl_428_Deceased_MouseDatabase.db"  # Secondary database
TABLE_NAME = "mouse_list"  # Table name

# Column names (ensures consistency across functions)
COLUMN_NAMES = [
    "ID_TATOO_NT", "CAGE_NUM", "MOUSELINE", "GENOTYPE", "GENDER",
    "DOB", "AVAILABLE", "HEALTH", "USER_NAME", "USER_MANIPULATIONS", "STATUS", "COMMENTS"
]

# ----------------- DATABASE INITIALIZATION -----------------
def initialize_database():
    """Creates the main database table if it does not exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            INDEX_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_TATOO_NT TEXT,
            CAGE_NUM INTEGER,
            MOUSELINE TEXT,
            GENOTYPE TEXT,
            GENDER TEXT,
            DOB TEXT,
            AVAILABLE TEXT,
            HEALTH TEXT,
            USER_NAME TEXT,
            USER_MANIPULATIONS TEXT,
            STATUS TEXT
            COMMENTS TEXT DEFAULT ''
        )
    """)

    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    columns = [column[1] for column in cursor.fetchall()]

    conn.commit()
    conn.close()

def create_empty_database():
    """Creates the secondary (deceased) database if it does not exist."""
    conn = sqlite3.connect(NEW_DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            INDEX_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_TATOO_NT TEXT,
            CAGE_NUM INTEGER,
            MOUSELINE TEXT,
            GENOTYPE TEXT,
            GENDER TEXT,
            DOB TEXT,
            AVAILABLE TEXT,
            HEALTH TEXT,
            USER_NAME TEXT,
            USER_MANIPULATIONS TEXT,
            STATUS TEXT
        )
    """)
    conn.commit()
    conn.close()

# ----------------- DATA MANAGEMENT FUNCTIONS -----------------
def fetch_data(db_file):
    """Fetches all data from the specified SQLite database, excluding INDEX_ID."""
    conn = sqlite3.connect(db_file)
    df = pd.read_sql(f"SELECT ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, AVAILABLE, HEALTH, USER_NAME, USER_MANIPULATIONS, STATUS, COMMENTS FROM {TABLE_NAME}", conn)
    conn.close()
    return df

def filter_records(db_file, column, value):
    """Filters records based on a column value in the specified database."""
    conn = sqlite3.connect(db_file)
    df = pd.read_sql(f"SELECT ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, AVAILABLE, HEALTH, USER_NAME, USER_MANIPULATIONS, STATUS FROM {TABLE_NAME} WHERE {column} = ?", conn, params=(value,))
    conn.close()
    return df

def export_to_csv(db_file, csv_filename):
    """Exports the table to a CSV file from the specified database, excluding INDEX_ID."""
    conn = sqlite3.connect(db_file)
    df = pd.read_sql(f"SELECT ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, AVAILABLE, HEALTH, USER_NAME, USER_MANIPULATIONS, STATUS FROM {TABLE_NAME}", conn)
    df.to_csv(csv_filename, index=False)
    conn.close()

# ----------------- RECORD OPERATIONS -----------------
def insert_record(db_file, id_tatoo_nt, cage_num, mouseline, genotype, gender, dob, available, health, user_name, user_manipulations, status, comments):
    """Inserts a new record into the specified database, including COMMENTS."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute(f"""
        INSERT INTO {TABLE_NAME} (ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, 
                                  AVAILABLE, HEALTH, USER_NAME, USER_MANIPULATIONS, STATUS, COMMENTS)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (id_tatoo_nt, cage_num, mouseline, genotype, gender, dob, available, health, user_name, user_manipulations, status, comments))

    conn.commit()
    conn.close()
    print("✅ New record inserted successfully.")


def update_record(db_file, id_tatoo_nt, cage_num, mouseline, genotype, gender, dob, available, health, user_name, user_manipulations, status, comments):
    """Updates an existing record using ID_TATOO_NT as the unique identifier, including COMMENTS."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Retrieve INDEX_ID internally
    cursor.execute(f"SELECT INDEX_ID FROM {TABLE_NAME} WHERE ID_TATOO_NT = ?", (id_tatoo_nt,))
    index_id = cursor.fetchone()

    if not index_id:
        conn.close()
        return False  # Record not found

    index_id = index_id[0]  # Extract INDEX_ID

    cursor.execute(f"""
        UPDATE {TABLE_NAME}
        SET CAGE_NUM = ?, MOUSELINE = ?, GENOTYPE = ?, GENDER = ?, DOB = ?, 
            AVAILABLE = ?, HEALTH = ?, USER_NAME = ?, USER_MANIPULATIONS = ?, STATUS = ?, COMMENTS = ?
        WHERE INDEX_ID = ?
    """, (cage_num, mouseline, genotype, gender, dob, available, health, user_name, user_manipulations, status, comments, index_id))

    conn.commit()
    conn.close()
    return True


def delete_record(db_file, id_tatoo_nt):
    """Deletes a record from the database using ID_TATOO_NT as the unique identifier."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # ✅ Ensure ID_TATOO_NT exists before trying to delete
    cursor.execute(f"SELECT 1 FROM {TABLE_NAME} WHERE ID_TATOO_NT = ?", (id_tatoo_nt,))
    if cursor.fetchone() is None:
        conn.close()
        return False  # No record found, return failure

    # ✅ Delete the record
    cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE ID_TATOO_NT = ?", (id_tatoo_nt,))
    conn.commit()
    conn.close()

    return True  # ✅ Successfully deleted



# ----------------- ROW COPY FUNCTION -----------------
def copy_row_to_new_db(id_tatoo_nt):
    """Copies a specific row from the primary database to the secondary database using ID_TATOO_NT."""
    conn_old = sqlite3.connect(DB_FILE)
    conn_new = sqlite3.connect(NEW_DB_FILE)

    cursor_old = conn_old.cursor()
    cursor_new = conn_new.cursor()

    cursor_old.execute(f"SELECT ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, AVAILABLE, HEALTH, USER_NAME, USER_MANIPULATIONS, STATUS FROM {TABLE_NAME} WHERE ID_TATOO_NT = ?", (id_tatoo_nt,))
    row = cursor_old.fetchone()

    if row:
        cursor_new.execute(f"""
            INSERT INTO {TABLE_NAME} (ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, 
                                      AVAILABLE, HEALTH, USER_NAME, USER_MANIPULATIONS, STATUS)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row)

        conn_new.commit()

    conn_old.close()
    conn_new.close()








