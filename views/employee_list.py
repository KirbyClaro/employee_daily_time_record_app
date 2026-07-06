"""
Employee List View.
Displays a professional Material Design table of all employees with instant search,
and toolbar actions for Add, Edit, Delete, and Refresh.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QMessageBox, QAbstractItemView, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from controllers.employee_controller import EmployeeController
from views.employee_form import EmployeeFormDialog


class EmployeeListPage(QWidget):
    """Widget representing the Employees management tab."""

    # Signal emitted when an employee is double-clicked (for opening Employee Profile later)
    employee_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.load_employees()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header Title
        header = QLabel("Employee Management")
        header.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header.setStyleSheet("color: #333333;")
        layout.addWidget(header)

        # Toolbar Card (Search & Buttons)
        toolbar_frame = QFrame()
        toolbar_frame.setStyleSheet("""
            QFrame { background-color: white; border-radius: 8px; border: 1px solid #E0E0E0; }
            QLineEdit { padding: 8px 12px; border: 1px solid #CCCCCC; border-radius: 4px; font-size: 13px; min-width: 250px; }
            QLineEdit:focus { border: 2px solid #1976D2; }
        """)
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(15, 15, 15, 15)

        # Instant Search Input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID, Name, Department...")
        self.search_input.textChanged.connect(self._handle_search)
        toolbar_layout.addWidget(self.search_input)

        toolbar_layout.addStretch()

        # Action Buttons
        self.btn_add = QPushButton(" + Add Employee ")
        self.btn_add.setStyleSheet("""
            QPushButton { background-color: #1976D2; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #1565C0; }
        """)
        self.btn_add.clicked.connect(self._open_add_dialog)

        self.btn_edit = QPushButton(" Edit ")
        self.btn_edit.setStyleSheet("""
            QPushButton { background-color: #FF9800; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #F57C00; }
        """)
        self.btn_edit.clicked.connect(self._open_edit_dialog)

        self.btn_delete = QPushButton(" Delete ")
        self.btn_delete.setStyleSheet("""
            QPushButton { background-color: #F44336; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #D32F2F; }
        """)
        self.btn_delete.clicked.connect(self._delete_employee)

        self.btn_refresh = QPushButton(" Refresh ")
        self.btn_refresh.setStyleSheet("""
            QPushButton { background-color: #E0E0E0; color: #333333; font-weight: bold; padding: 8px 16px; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #D5D5D5; }
        """)
        self.btn_refresh.clicked.connect(self.load_employees)

        toolbar_layout.addWidget(self.btn_add)
        toolbar_layout.addWidget(self.btn_edit)
        toolbar_layout.addWidget(self.btn_delete)
        toolbar_layout.addWidget(self.btn_refresh)

        layout.addWidget(toolbar_frame)

        # Employee Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["DB ID", "Employee ID", "Full Name", "Department", "Position", "Status"])
        self.table.setColumnHidden(0, True) # Hide internal DB ID from user
        
        # Table Styling & Behavior
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                gridline-color: #F0F0F0;
                font-size: 13px;
            }
            QTableWidget::item { padding: 10px; }
            QTableWidget::item:selected { background-color: #E3F2FD; color: #1976D2; font-weight: bold; }
            QHeaderView::section {
                background-color: #FAFAFA;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #E0E0E0;
                color: #555555;
            }
        """)
        self.table.doubleClicked.connect(self._handle_double_click)

        layout.addWidget(self.table)

    def load_employees(self, search_query: str = None):
        """Fetches employees from DB and populates the table."""
        self.table.setRowCount(0)
        
        if search_query and search_query.strip():
            employees = EmployeeController.search_employees(search_query.strip())
        else:
            employees = EmployeeController.get_all_employees()

        self.table.setRowCount(len(employees))

        for row_idx, emp in enumerate(employees):
            # DB ID (Hidden col 0)
            item_id = QTableWidgetItem(str(emp.id))
            # Employee ID
            item_empid = QTableWidgetItem(emp.employee_id)
            # Full Name
            full_name = f"{emp.first_name} {emp.last_name}"
            item_name = QTableWidgetItem(full_name)
            # Department
            item_dept = QTableWidgetItem(emp.department or "N/A")
            # Position
            item_pos = QTableWidgetItem(emp.position or "N/A")
            # Status
            item_status = QTableWidgetItem(emp.status)
            if emp.status == "Active":
                item_status.setForeground(QColor("#4CAF50")) # Green
            else:
                item_status.setForeground(QColor("#F44336")) # Red

            # Center align ID and Status
            item_empid.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(row_idx, 0, item_id)
            self.table.setItem(row_idx, 1, item_empid)
            self.table.setItem(row_idx, 2, item_name)
            self.table.setItem(row_idx, 3, item_dept)
            self.table.setItem(row_idx, 4, item_pos)
            self.table.setItem(row_idx, 5, item_status)

    def _handle_search(self, text: str):
        """Instant search triggered as the user types."""
        self.load_employees(text)

    def _get_selected_employee_id(self) -> int:
        pass

    def _get_selected_db_id(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None
        row = selected_items[0].row()
        return int(self.table.item(row, 0).text())

    def _open_add_dialog(self):
        """Opens the EmployeeFormDialog in add mode."""
        dialog = EmployeeFormDialog(self)
        if dialog.exec():
            self.load_employees()

    def _open_edit_dialog(self):
        """Opens the EmployeeFormDialog for the selected employee."""
        db_id = self._get_selected_db_id()
        if not db_id:
            QMessageBox.warning(self, "Selection Required", "Please select an employee from the table to edit.")
            return

        employee = EmployeeController.get_employee_by_id(db_id)
        if employee:
            dialog = EmployeeFormDialog(self, employee_data=employee)
            if dialog.exec():
                self.load_employees()

    def _delete_employee(self):
        """Deletes the selected employee after confirmation."""
        db_id = self._get_selected_db_id()
        if not db_id:
            QMessageBox.warning(self, "Selection Required", "Please select an employee to delete.")
            return

        # Get name for the confirmation prompt
        row = self.table.selectedItems()[0].row()
        emp_name = self.table.item(row, 2).text()

        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to permanently delete employee: '{emp_name}'?\nThis will also delete all their attendance records.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            success, message = EmployeeController.delete_employee(db_id)
            if success:
                QMessageBox.information(self, "Deleted", message)
                self.load_employees()
            else:
                QMessageBox.critical(self, "Error", message)

    def _handle_double_click(self):
        """Emits signal with the selected employee DB ID when double clicked."""
        db_id = self._get_selected_db_id()
        if db_id:
            self.employee_selected.emit(db_id)
            # Once we build employee_profile.py in the next step, double clicking 
            # will open their full attendance profile where you can add the 3 days!
            print(f"Employee DB ID {db_id} double clicked. Ready to open profile.")