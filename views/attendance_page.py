from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
    QComboBox, QLabel, QDialog, QFormLayout, QDateEdit, QTimeEdit, 
    QLineEdit, QAbstractItemView, QInputDialog
)
from PySide6.QtCore import Qt, QDate, QTime
from datetime import date, datetime

from controllers.attendance_controller import AttendanceController
from controllers.employee_controller import EmployeeController


class ManualAttendanceDialog(QDialog):
    def __init__(self, parent=None, employee_id=None, employee_name=""):
        super().__init__(parent)
        self.employee_id = employee_id
        self.setWindowTitle("Manual Attendance Entry")
        self.setFixedSize(400, 350)
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLineEdit, QDateEdit, QTimeEdit {
                padding: 4px 8px; min-height: 24px; border: 1px solid #CCCCCC;
                border-radius: 4px; background-color: #F9F9F9; font-size: 13px;
                color: #333333;
            }
            QLabel { font-weight: bold; color: #555555; }
        """)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.emp_label = QLabel(employee_name)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.time_in_input = QTimeEdit()
        self.time_in_input.setTime(QTime(8, 0))
        
        self.time_out_input = QTimeEdit()
        self.time_out_input.setTime(QTime(17, 0))

        self.admin_pass_input = QLineEdit()
        self.admin_pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Employee:", self.emp_label)
        form_layout.addRow("Date:", self.date_input)
        form_layout.addRow("Time In:", self.time_in_input)
        form_layout.addRow("Time Out:", self.time_out_input)
        form_layout.addRow("Admin Password:", self.admin_pass_input)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Record")
        self.save_btn.setStyleSheet("background-color: #1976D2; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
        self.save_btn.clicked.connect(self._save_manual_record)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #9E9E9E; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

    def _save_manual_record(self):
        admin_pass = self.admin_pass_input.text()
        
        if not AttendanceController.verify_admin_password(admin_pass) and admin_pass not in ["admin", "DTR2026"]:
            QMessageBox.warning(self, "Access Denied", "Incorrect Admin Password. (Try 'admin' or 'DTR2026')")
            return

        selected_date = self.date_input.date().toPython()
        t_in = self.time_in_input.time().toPython()
        t_out = self.time_out_input.time().toPython()

        success_in, msg_in = AttendanceController.time_in(self.employee_id, selected_date, t_in)
        if not success_in:
            QMessageBox.warning(self, "Error", msg_in)
            return

        success_out, msg_out = AttendanceController.time_out(self.employee_id, selected_date, t_out)
        if not success_out:
            QMessageBox.warning(self, "Error", msg_out)
            return

        QMessageBox.information(self, "Success", "Manual attendance saved successfully.")
        self.accept()


class AttendancePage(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.load_employees_dropdown()
        self.load_history()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        toolbar_layout = QHBoxLayout()
        
        self.emp_combo = QComboBox()
        self.emp_combo.setMinimumWidth(250)
        self.emp_combo.setStyleSheet("padding: 8px; border: 1px solid #CCC; border-radius: 4px; font-size: 13px;")
        
        self.btn_time_in = QPushButton("Time In (Now)")
        self.btn_time_out = QPushButton("Time Out (Now)")
        self.btn_manual = QPushButton("Manual Entry (Past)")
        self.btn_delete = QPushButton("Delete Selected")
        self.btn_refresh = QPushButton("Refresh")

        self.btn_time_in.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #45A049; }")
        self.btn_time_out.setStyleSheet("QPushButton { background-color: #F44336; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #E53935; }")
        self.btn_manual.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #FB8C00; }")
        self.btn_delete.setStyleSheet("QPushButton { background-color: #D32F2F; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #B71C1C; }")
        self.btn_refresh.setStyleSheet("QPushButton { background-color: #9E9E9E; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #757575; }")

        self.btn_time_in.clicked.connect(self._auto_time_in)
        self.btn_time_out.clicked.connect(self._auto_time_out)
        self.btn_manual.clicked.connect(self._manual_entry)
        self.btn_delete.clicked.connect(self._delete_record)
        self.btn_refresh.clicked.connect(self.load_history)

        toolbar_layout.addWidget(QLabel("Select Employee:"))
        toolbar_layout.addWidget(self.emp_combo)
        toolbar_layout.addSpacing(20)
        toolbar_layout.addWidget(self.btn_time_in)
        toolbar_layout.addWidget(self.btn_time_out)
        toolbar_layout.addWidget(self.btn_manual)
        toolbar_layout.addWidget(self.btn_delete)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_refresh)

        layout.addLayout(toolbar_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Date", "Day", "Employee Name", "Time In", "Time Out", "Total Hours", "Status"])
        
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; gridline-color: #EEEEEE; font-size: 13px; }
            QHeaderView::section { background-color: #1976D2; color: white; padding: 10px; font-weight: bold; border: none; border-right: 1px solid #1565C0; }
            QTableWidget::item { padding: 5px; }
            QTableWidget::item:selected { background-color: #E3F2FD; color: #000000; }
        """)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        for i in [0, 1, 3, 4, 5, 6]:
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table)

    def load_employees_dropdown(self):
        self.emp_combo.clear()
        employees = EmployeeController.get_all_employees()
        for emp in employees:
            full_name = f"{emp.first_name} {emp.last_name}"
            self.emp_combo.addItem(f"{emp.employee_id} - {full_name}", emp.id)

    def load_history(self):
        self.table.setRowCount(0)
        history = AttendanceController.get_attendance_history()
        
        for row_idx, (att, emp) in enumerate(history):
            self.table.insertRow(row_idx)
            full_name = f"{emp.first_name} {emp.last_name}"
            
            t_in = att.time_in.strftime("%I:%M %p") if att.time_in else "--:--"
            t_out = att.time_out.strftime("%I:%M %p") if att.time_out else "--:--"
            hrs = str(att.total_hours) if att.total_hours else "--"
            
            date_item = QTableWidgetItem(att.attendance_date.strftime("%Y-%m-%d"))
            date_item.setData(Qt.ItemDataRole.UserRole, att.id)
            
            self.table.setItem(row_idx, 0, date_item)
            self.table.setItem(row_idx, 1, QTableWidgetItem(att.day))
            self.table.setItem(row_idx, 2, QTableWidgetItem(full_name))
            self.table.setItem(row_idx, 3, QTableWidgetItem(t_in))
            self.table.setItem(row_idx, 4, QTableWidgetItem(t_out))
            self.table.setItem(row_idx, 5, QTableWidgetItem(hrs))
            self.table.setItem(row_idx, 6, QTableWidgetItem(att.attendance_status))

    def _get_selected_emp_id(self):
        return self.emp_combo.currentData()

    def _auto_time_in(self):
        emp_id = self._get_selected_emp_id()
        if not emp_id: return
        now = datetime.now()
        success, msg = AttendanceController.time_in(emp_id, now.date(), now.time())
        if success:
            QMessageBox.information(self, "Success", msg)
            self.load_history()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _auto_time_out(self):
        emp_id = self._get_selected_emp_id()
        if not emp_id: return
        now = datetime.now()
        success, msg = AttendanceController.time_out(emp_id, now.date(), now.time())
        if success:
            QMessageBox.information(self, "Success", msg)
            self.load_history()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _manual_entry(self):
        emp_id = self._get_selected_emp_id()
        emp_name = self.emp_combo.currentText()
        if not emp_id: return
        
        dialog = ManualAttendanceDialog(self, emp_id, emp_name)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_history()

    def _delete_record(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Required", "Please select a record to delete.")
            return

        record_id = self.table.item(selected_rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)

        password, ok = QInputDialog.getText(
            self, 
            "Admin Authorization", 
            "Enter deletion password:", 
            QLineEdit.EchoMode.Password
        )

        if ok:
            if password == "DTR2026":
                reply = QMessageBox.question(
                    self, 
                    "Confirm Deletion", 
                    "Are you sure you want to delete this attendance record?", 
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    success, msg = AttendanceController.delete_attendance(record_id)
                    if success:
                        QMessageBox.information(self, "Success", msg)
                        self.load_history()
                    else:
                        QMessageBox.warning(self, "Error", msg)
            else:
                QMessageBox.warning(self, "Access Denied", "Incorrect password.")