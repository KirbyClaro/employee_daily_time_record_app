"""
Employee Form Dialog.
A reusable dialog window for adding new employees or editing existing ones.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QMessageBox, QDateEdit, QFormLayout
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from controllers.employee_controller import EmployeeController


class EmployeeFormDialog(QDialog):
    """Dialog for creating and editing employee records."""

    def __init__(self, parent=None, employee_data=None):
        super().__init__(parent)
        self.employee_data = employee_data
        self.is_edit_mode = employee_data is not None
        
        title = "Edit Employee" if self.is_edit_mode else "Add New Employee"
        self.setWindowTitle(title)
        self.setFixedSize(450, 550)
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLineEdit, QComboBox, QDateEdit {
                padding: 4px 8px; 
                min-height: 24px;  
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                background-color: #F9F9F9;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #1976D2;
                background-color: #FFFFFF;
            }
            QLabel { font-weight: bold; color: #555555; }
        """)

        self._setup_ui()
        if self.is_edit_mode:
            self._populate_fields()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Header
        header_lbl = QLabel("Employee Details")
        header_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_lbl.setStyleSheet("color: #1976D2; border: none;")
        layout.addWidget(header_lbl)

        # Form Layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.emp_id_input = QLineEdit()
        self.emp_id_input.setPlaceholderText("e.g. EMP-001")
        
        self.first_name_input = QLineEdit()
        self.middle_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        
        self.department_input = QComboBox()
        self.department_input.addItems(["IT", "HR", "Finance", "Operations", "Marketing", "Sales", "Engineering"])
        self.department_input.setEditable(True) # Allow custom departments
        
        self.position_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.email_input = QLineEdit()
        
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())
        
        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "Inactive", "On Leave", "Terminated"])

        form_layout.addRow("Employee ID *", self.emp_id_input)
        form_layout.addRow("First Name *", self.first_name_input)
        form_layout.addRow("Middle Name", self.middle_name_input)
        form_layout.addRow("Last Name *", self.last_name_input)
        form_layout.addRow("Department", self.department_input)
        form_layout.addRow("Position", self.position_input)
        form_layout.addRow("Contact No.", self.contact_input)
        form_layout.addRow("Email Address", self.email_input)
        form_layout.addRow("Hire Date", self.hire_date_input)
        form_layout.addRow("Status", self.status_input)

        layout.addLayout(form_layout)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton { padding: 8px 16px; border: 1px solid #CCCCCC; border-radius: 4px; background: #FFFFFF; }
            QPushButton:hover { background: #F5F5F5; }
        """)
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Save Employee")
        self.save_btn.setStyleSheet("""
            QPushButton { padding: 8px 16px; border: none; border-radius: 4px; background: #1976D2; color: white; font-weight: bold; }
            QPushButton:hover { background: #1565C0; }
        """)
        self.save_btn.clicked.connect(self._save_employee)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

    def _populate_fields(self):
        """Fills the form with existing data if in edit mode."""
        if not self.employee_data:
            return
            
        self.emp_id_input.setText(self.employee_data.employee_id)
        self.emp_id_input.setReadOnly(True) # Usually shouldn't change ID after creation
        self.first_name_input.setText(self.employee_data.first_name)
        self.middle_name_input.setText(self.employee_data.middle_name or "")
        self.last_name_input.setText(self.employee_data.last_name)
        self.department_input.setCurrentText(self.employee_data.department or "")
        self.position_input.setText(self.employee_data.position or "")
        self.contact_input.setText(self.employee_data.contact_number or "")
        self.email_input.setText(self.employee_data.email or "")
        self.status_input.setCurrentText(self.employee_data.status)
        
        if self.employee_data.hire_date:
            qt_date = QDate(
                self.employee_data.hire_date.year,
                self.employee_data.hire_date.month,
                self.employee_data.hire_date.day
            )
            self.hire_date_input.setDate(qt_date)

    def _save_employee(self):
        """Validates and saves the data via the controller."""
        emp_id = self.emp_id_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()

        # Basic Validation
        if not emp_id or not first_name or not last_name:
            QMessageBox.warning(self, "Validation Error", "Employee ID, First Name, and Last Name are required.")
            return

        data = {
            "employee_id": emp_id,
            "first_name": first_name,
            "middle_name": self.middle_name_input.text().strip(),
            "last_name": last_name,
            "department": self.department_input.currentText().strip(),
            "position": self.position_input.text().strip(),
            "contact_number": self.contact_input.text().strip(),
            "email": self.email_input.text().strip(),
            "hire_date": self.hire_date_input.date().toPython(),
            "status": self.status_input.currentText().strip()
        }

        if self.is_edit_mode:
            success, message = EmployeeController.update_employee(self.employee_data.id, data)
        else:
            success, message = EmployeeController.add_employee(data)

        if success:
            QMessageBox.information(self, "Success", message)
            self.accept() # Closes the dialog and returns success
        else:
            QMessageBox.critical(self, "Error", message)