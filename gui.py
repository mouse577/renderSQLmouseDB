import sys
import sqlite3
import os
os.environ["DISPLAY"] = ":99"
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, \
    QLineEdit, QLabel, QFileDialog, QHBoxLayout, QMessageBox, QComboBox
from database_manager import fetch_data, filter_records, export_to_csv, insert_record, delete_record, \
    update_record, copy_row_to_new_db, create_empty_database, TABLE_NAME

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mouse Database Manager")

def run_gui():
    app = QApplication([])
    window = MyMainWindow()
    window.show()
    app.exec_()

# Database file paths
DB_FILE = "PPL_Scholl_428_MouseDatabase.db"
NEW_DB_FILE = "PPL_Scholl_428_Deceased_MouseDatabase.db"


class DatabaseApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mouse List Database Manager")
        self.setGeometry(100, 100, 900, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Database selection
        self.db_label = QLabel("Select Database:")
        self.layout.addWidget(self.db_label)

        self.db_selector = QComboBox()
        self.db_selector.addItems(["Primary Database", "Deceased Database"])
        self.db_selector.currentIndexChanged.connect(self.switch_database)
        self.layout.addWidget(self.db_selector)

        # Search Bar
        self.search_label = QLabel("Search by Mouseline:")
        self.layout.addWidget(self.search_label)

        self.search_input = QLineEdit()
        self.layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_data)
        self.layout.addWidget(self.search_button)

        # Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self.fill_update_fields)
        self.table.setSortingEnabled(True)  # ✅ ENABLE SORTING
        self.layout.addWidget(self.table)

        # Buttons Layout
        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.clicked.connect(self.load_data)
        button_layout.addWidget(self.refresh_button)

        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_data)
        button_layout.addWidget(self.export_button)

        self.copy_button = QPushButton("Copy Selected Row to New DB")
        self.copy_button.clicked.connect(self.copy_selected_row)
        button_layout.addWidget(self.copy_button)

        self.layout.addLayout(button_layout)

        # Add/Edit Record Inputs
        self.fields = {}
        labels = ["ID_TATOO_NT", "CAGE_NUM", "MOUSELINE", "GENOTYPE", "GENDER", "DOB", "AVAILABLE", "HEALTH",
                  "USER_NAME", "USER_MANIPULATIONS", "STATUS", "COMMENTS"]

        for label in labels:
            field_label = QLabel(f"Enter {label}:")
            self.layout.addWidget(field_label)

            field_input = QLineEdit()

            if label == "COMMENTS":
                field_input.setFixedWidth(400)

            self.layout.addWidget(field_input)

            self.fields[label] = field_input

        self.add_button = QPushButton("Add Record")
        self.add_button.clicked.connect(self.add_record)
        self.layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Selected Row")
        self.update_button.clicked.connect(self.update_selected_row)
        self.layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Selected Record")
        self.delete_button.clicked.connect(self.delete_selected_record)
        self.layout.addWidget(self.delete_button)

        # Load data on startup
        self.current_db = DB_FILE  # Default database
        self.load_data()

    def switch_database(self):
        """Switches between the primary and deceased databases and reloads data."""
        self.current_db = DB_FILE if self.db_selector.currentIndex() == 0 else NEW_DB_FILE
        self.load_data()

    def load_data(self):
        """Loads data from the selected SQLite database into the table."""
        self.table.setSortingEnabled(False)
        df = fetch_data(self.current_db)
        if df.empty:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
        else:
            self.populate_table(df)

        self.table.setSortingEnabled(True)
        return

        self.populate_table(df)

    def search_data(self):
        """Filters data based on search input in the selected database."""
        mouseline = self.search_input.text()
        df = filter_records(self.current_db, "MOUSELINE", mouseline)
        self.populate_table(df)

    def export_data(self):
        """Exports the table to a CSV file."""
        filename, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if filename:
            export_to_csv(self.current_db, filename)

    def populate_table(self, df):
        """Populates the table widget with DataFrame data (excluding INDEX_ID)."""
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])  # ✅ Exclude INDEX_ID
        self.table.setHorizontalHeaderLabels(df.columns)

        for row_idx, row in df.iterrows():
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                if col_idx == df.columns.get_loc("COMMENTS"):
                    item.setTextAlignment(1)
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            self.table.setColumnWidth(df.columns.get_loc("COMMENTS"), 400)

    def copy_selected_row(self):
        """Copies the selected row to the deceased database and updates UI."""
        selected = self.table.currentRow()
        if selected >= 0:
            record_id = self.table.item(selected, 0).text()
            copy_row_to_new_db(record_id)
            QMessageBox.information(self, "Success", f"Row {record_id} copied to the deceased database.")
            self.load_data()  # Refresh UI
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a row to copy.")

    def fill_update_fields(self):
        """Fills input fields with selected row's data for editing (adjusted for no INDEX_ID)."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return  # No row selected

        selected_row = selected_rows[0].row()

        for col_idx, label in enumerate(self.fields.keys()):
            item = self.table.item(selected_row, col_idx)  # ✅ No longer skipping INDEX_ID
            if item:
                self.fields[label].setText(item.text())

    def update_selected_row(self):
        """Updates the selected row with new values from the input fields."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a row to update.")
            return

        selected_row = selected_rows[0].row()

        # ✅ Fetch `INDEX_ID` from database using primary key fields (e.g., ID_TATOO_NT)
        id_tatoo_nt = self.table.item(selected_row, 0).text()
        conn = sqlite3.connect(self.current_db)
        cursor = conn.cursor()
        cursor.execute(f"SELECT INDEX_ID FROM {TABLE_NAME} WHERE ID_TATOO_NT = ?", (id_tatoo_nt,))
        index_id = cursor.fetchone()
        conn.close()

        if not index_id:
            QMessageBox.warning(self, "Error", "Could not find the record in the database.")
            return

        index_id = index_id[0]  # Extract INDEX_ID

        values = [self.fields[label].text() for label in self.fields]

        if len(values) < 12:
            values.append("")

        update_record(self.current_db, *values)
        self.load_data()
        QMessageBox.information(self, "Success", "Record updated successfully.")

    def add_record(self):
        """Adds a new record to the selected database and ensures COMMENTS is included."""
        values = [self.fields[label].text() for label in self.fields]

        # ✅ Ensure COMMENTS is included (if missing, add an empty string)
        if len(values) < 12:
            values.append("")  # Default empty COMMENTS field

        insert_record(self.current_db, *values)  # ✅ Now always passes 13 arguments
        self.load_data()
        QMessageBox.information(self, "Success", "New record added successfully.")

    def delete_selected_record(self):
        """Deletes the selected record using ID_TATOO_NT and refreshes the UI."""
        selected = self.table.currentRow()
        if selected >= 0:
            # ✅ Fetch ID_TATOO_NT directly from table (first column)
            id_tatoo_nt = self.table.item(selected, 0).text().strip()  # Ensure no trailing spaces

            # ✅ Call delete_record() with ID_TATOO_NT
            success = delete_record(self.current_db, id_tatoo_nt)

            if success:
                self.load_data()  # Refresh UI after deletion
                QMessageBox.information(self, "Success", f"Record {id_tatoo_nt} deleted successfully.")
            else:
                QMessageBox.warning(self, "Error", "Record not found or could not be deleted.")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a record to delete.")


def run_gui():
    create_empty_database()  # Ensure the new database is created before GUI starts
    app = QApplication(sys.argv)
    window = DatabaseApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_gui()








