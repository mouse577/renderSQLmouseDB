import sys
import sqlite3
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, \
    QLineEdit, QLabel, QFileDialog, QHBoxLayout, QMessageBox, QComboBox
from database_manager import fetch_data, filter_records, export_to_csv, insert_record, delete_record, \
    update_record, copy_row_to_new_db, create_empty_database, TABLE_NAME

# Database file paths
DB_FILE = "mouse_database.db"
TABLE_LIVE = "mouse_list"
TABLE_DECEASED = "deceased_mouse_list"

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mouse Database Manager")

def run_gui():
    app = QApplication([])
    window = MyMainWindow()
    window.show()
    app.exec_()


class DatabaseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mouse List Database Manager")
        self.setGeometry(100, 100, 900, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.db_label = QLabel("Select Database Table:")
        self.layout.addWidget(self.db_label)

        self.db_selector = QComboBox()
        self.db_selector.addItems(["Live Mice", "Deceased Mice"])
        self.db_selector.currentIndexChanged.connect(self.load_data)
        self.layout.addWidget(self.db_selector)

        self.search_label = QLabel("Search by Mouseline:")
        self.layout.addWidget(self.search_label)

        self.search_input = QLineEdit()
        self.layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_data)
        self.layout.addWidget(self.search_button)

        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self.fill_update_fields)
        self.table.setSortingEnabled(True)
        self.layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.clicked.connect(self.load_data)
        button_layout.addWidget(self.refresh_button)

        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_data)
        button_layout.addWidget(self.export_button)

        self.copy_button = QPushButton("Copy Selected Row to Deceased")
        self.copy_button.clicked.connect(self.copy_selected_row)
        button_layout.addWidget(self.copy_button)

        self.layout.addLayout(button_layout)

        self.fields = {}
        labels = ["id", "cage_number", "mouseline", "genotype", "gender", "dob", "available", "health",
                  "username", "user_manipulations", "status", "comments"]
        for label in labels:
            field_label = QLabel(f"Enter {label}:")
            self.layout.addWidget(field_label)

            field_input = QLineEdit()
            self.layout.addWidget(field_input)
            self.fields[label] = field_input

        self.add_button = QPushButton("Add Record")
        self.add_button.clicked.connect(self.add_record)
        self.layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Selected Record")
        self.update_button.clicked.connect(self.update_selected_record)
        self.layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Selected Record")
        self.delete_button.clicked.connect(self.delete_selected_record)
        self.layout.addWidget(self.delete_button)

        self.load_data()

    def get_selected_table(self):
        return TABLE_LIVE if self.db_selector.currentIndex() == 0 else TABLE_DECEASED

    def load_data(self):
        table_name = self.get_selected_table()
        df = fetch_data(DB_FILE, table_name)
        self.populate_table(df)

    def search_data(self):
        table_name = self.get_selected_table()
        mouseline = self.search_input.text()
        df = filter_records(DB_FILE, table_name, "mouseline", mouseline)
        self.populate_table(df)

    def export_data(self):
        table_name = self.get_selected_table()
        filename, _ = QFileDialog.getSaveFileName(self, "Save CSV", f"{table_name}.csv", "CSV Files (*.csv)")
        if filename:
            export_to_csv(DB_FILE, table_name, filename)

    def populate_table(self, df):
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])
        self.table.setHorizontalHeaderLabels(df.columns)

        for row_idx, row in df.iterrows():
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)

    def fill_update_fields(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        selected_row = selected_rows[0].row()
        for col_idx, label in enumerate(self.fields.keys()):
            item = self.table.item(selected_row, col_idx)
            self.fields[label].setText(item.text() if item else "")

    def add_record(self):
        table_name = self.get_selected_table()
        record = {label: self.fields[label].text() for label in self.fields}
        insert_record(DB_FILE, table_name, record)
        self.load_data()
        QMessageBox.information(self, "Success", "Record added successfully.")

    def update_selected_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Error", "No record selected.")
            return
        table_name = self.get_selected_table()
        record_id = self.table.item(selected, 0).text()
        record = {label: self.fields[label].text() for label in self.fields}
        update_record(DB_FILE, table_name, record_id, record)
        self.load_data()
        QMessageBox.information(self, "Success", "Record updated successfully.")

    def delete_selected_record(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Error", "No record selected.")
            return
        table_name = self.get_selected_table()
        record_id = self.table.item(selected, 0).text()
        if delete_record(DB_FILE, table_name, record_id):
            self.load_data()
            QMessageBox.information(self, "Success", f"Record {record_id} deleted successfully.")
        else:
            QMessageBox.warning(self, "Error", "Record could not be found or deleted.")

    def copy_selected_row(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Error", "No record selected.")
            return
        record_id = self.table.item(selected, 0).text()
        copy_row_to_new_db(DB_FILE, record_id)
        QMessageBox.information(self, "Success", f"Row {record_id} copied to deceased list.")
        self.load_data()

def run_gui():
    create_empty_database()  # Ensure database/tables exist before GUI starts
    app = QApplication(sys.argv)
    window = DatabaseApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_gui()








