"""
Employee List View.
Displays a professional Material Design table of all employees with instant search,
and toolbar actions for Add, Edit, Delete, and Refresh.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
    QAbstractItemView, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from controllers.employee_controller import EmployeeController
from views.employee_form import EmployeeFormDialog


class EmployeeListPage(QWidget):

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.load_employees()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        toolbar_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("+ Add Employee")
        self.btn_edit = QPushButton("Edit Selected")
        self.btn_delete = QPushButton("Delete Selected")
        self.btn_refresh = QPushButton("Refresh")

        self.btn_add.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #45A049; }")
        self.btn_edit.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #FB8C00; }")
        self.btn_delete.setStyleSheet("QPushButton { background-color: #F44336; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #E53935; }")
        self.btn_refresh.setStyleSheet("QPushButton { background-color: #9E9E9E; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #757575; }")

        self.btn_add.clicked.connect(self._add_employee)
        self.btn_edit.clicked.connect(self._edit_employee)
        self.btn_delete.clicked.connect(self._delete_employee)
        self.btn_refresh.clicked.connect(self.load_employees)

        toolbar_layout.addWidget(self.btn_add)
        toolbar_layout.addWidget(self.btn_edit)
        toolbar_layout.addWidget(self.btn_delete)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_refresh)

        layout.addLayout(toolbar_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Employee ID", "Full Name", "Department", "Position", "Status"])
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                gridline-color: #EEEEEE;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #1976D2;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-right: 1px solid #1565C0;
            }
            QTableWidget::item { padding: 5px; }
            QTableWidget::item:selected { background-color: #E3F2FD; color: #000000; }
        """)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) 
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.table.itemDoubleClicked.connect(self._edit_employee)

        layout.addWidget(self.table)

    def load_employees(self):
        self.table.setRowCount(0)
        employees = EmployeeController.get_all_employees()
        
        print(f"DEBUG: Loaded {len(employees)} employees from database.")
        
        for row_idx, emp in enumerate(employees):
            self.table.insertRow(row_idx)
            
            full_name = f"{emp.first_name} {emp.middle_name or ''} {emp.last_name}".replace("  ", " ").strip()
            
            id_item = QTableWidgetItem(emp.employee_id)
            id_item.setData(Qt.ItemDataRole.UserRole, emp.id) 
            
            self.table.setItem(row_idx, 0, id_item)
            self.table.setItem(row_idx, 1, QTableWidgetItem(full_name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(emp.department or "N/A"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(emp.position or "N/A"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(emp.status))

    def _get_selected_employee_id(self) -> int:
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return None
        return self.table.item(selected_rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)

    def _add_employee(self):
        dialog = EmployeeFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_employees()

    def _edit_employee(self):
        emp_db_id = self._get_selected_employee_id()
        if not emp_db_id:
            QMessageBox.warning(self, "Selection Required", "Please select an employee to edit.")
            return

        employee = EmployeeController.get_employee_by_id(emp_db_id)
        if employee:
            dialog = EmployeeFormDialog(self, employee_data=employee)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_employees()

    def _delete_employee(self):
        emp_db_id = self._get_selected_employee_id()
        if not emp_db_id:
            QMessageBox.warning(self, "Selection Required", "Please select an employee to delete.")
            return

        reply = QMessageBox.question(
            self, "Confirm Deletion", 
            "Are you sure you want to delete this employee? This will also delete their attendance history.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = EmployeeController.delete_employee(emp_db_id)
            if success:
                QMessageBox.information(self, "Deleted", message)
                self.load_employees()
            else:
                QMessageBox.critical(self, "Error", message)