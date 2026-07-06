import os
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
    QComboBox, QLabel, QDateEdit, QAbstractItemView, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from controllers.attendance_controller import AttendanceController
from controllers.employee_controller import EmployeeController
from controllers.report_controller import ReportController


class ReportPage(QWidget):
    def __init__(self):
        super().__init__()
        self.current_data = []
        self._setup_ui()
        self.load_employees_dropdown()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Top Section: Filters
        filter_layout = QHBoxLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setStyleSheet("padding: 8px; border: 1px solid #CCC; border-radius: 4px;")

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setStyleSheet("padding: 8px; border: 1px solid #CCC; border-radius: 4px;")

        self.emp_combo = QComboBox()
        self.emp_combo.setMinimumWidth(250)
        self.emp_combo.setStyleSheet("padding: 8px; border: 1px solid #CCC; border-radius: 4px;")

        self.btn_generate = QPushButton("Generate Preview")
        self.btn_generate.setStyleSheet("background-color: #1976D2; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
        self.btn_generate.clicked.connect(self._generate_preview)

        filter_layout.addWidget(QLabel("Start Date:"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addSpacing(10)
        filter_layout.addWidget(QLabel("End Date:"))
        filter_layout.addWidget(self.end_date)
        filter_layout.addSpacing(10)
        filter_layout.addWidget(QLabel("Employee:"))
        filter_layout.addWidget(self.emp_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(self.btn_generate)

        layout.addLayout(filter_layout)

        # Middle Section: Preview Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["Date", "Day", "Employee ID", "Name", "Department", "Time In", "Time Out", "Hours", "Status"])
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; gridline-color: #EEEEEE; font-size: 13px; }
            QHeaderView::section { background-color: #1976D2; color: white; padding: 10px; font-weight: bold; border: none; border-right: 1px solid #1565C0; }
            QTableWidget::item { padding: 5px; }
        """)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        for i in [0, 1, 2, 4, 5, 6, 7, 8]:
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table)

        # Bottom Section: Exports
        export_layout = QHBoxLayout()
        
        self.summary_label = QLabel("Showing 0 records.")
        self.summary_label.setStyleSheet("color: #757575; font-weight: bold;")

        self.btn_pdf = QPushButton("Export PDF")
        self.btn_excel = QPushButton("Export Excel")
        self.btn_csv = QPushButton("Export CSV")

        btn_style = "color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;"
        self.btn_pdf.setStyleSheet(f"background-color: #D32F2F; {btn_style}")
        self.btn_excel.setStyleSheet(f"background-color: #388E3C; {btn_style}")
        self.btn_csv.setStyleSheet(f"background-color: #F57C00; {btn_style}")

        self.btn_pdf.clicked.connect(self._export_pdf)
        self.btn_excel.clicked.connect(self._export_excel)
        self.btn_csv.clicked.connect(self._export_csv)

        export_layout.addWidget(self.summary_label)
        export_layout.addStretch()
        export_layout.addWidget(self.btn_csv)
        export_layout.addWidget(self.btn_excel)
        export_layout.addWidget(self.btn_pdf)

        layout.addLayout(export_layout)

    def load_employees_dropdown(self):
        self.emp_combo.clear()
        self.emp_combo.addItem("All Employees", None)
        employees = EmployeeController.get_all_employees()
        for emp in employees:
            self.emp_combo.addItem(f"{emp.employee_id} - {emp.first_name} {emp.last_name}", emp.id)

    def _generate_preview(self):
        start = self.start_date.date().toPython()
        end = self.end_date.date().toPython()
        emp_id = self.emp_combo.currentData()

        if start > end:
            QMessageBox.warning(self, "Invalid Date", "Start Date cannot be after End Date.")
            return

        history_records = AttendanceController.get_attendance_history(emp_id, start, end)
        self.current_data = ReportController.format_attendance_data(history_records)

        self.table.setRowCount(0)
        total_hours_sum = 0.0

        for row_idx, record in enumerate(self.current_data):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(record.get("Date", ""))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(record.get("Day", ""))))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(record.get("Employee ID", ""))))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(record.get("Name", ""))))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(record.get("Department", ""))))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(record.get("Time In", ""))))
            self.table.setItem(row_idx, 6, QTableWidgetItem(str(record.get("Time Out", ""))))
            
            hours_str = str(record.get("Hours Worked", ""))
            self.table.setItem(row_idx, 7, QTableWidgetItem(hours_str))
            self.table.setItem(row_idx, 8, QTableWidgetItem(str(record.get("Status", ""))))

            # Accumulate total hours
            if hours_str and hours_str not in ["--", "None"]:
                try:
                    total_hours_sum += float(hours_str)
                except ValueError:
                    pass

        # Append a visual-only Total row to the bottom of the table
        if self.current_data:
            total_row_idx = self.table.rowCount()
            self.table.insertRow(total_row_idx)
            
            total_label = QTableWidgetItem("TOTAL HOURS:")
            total_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            total_label.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            total_value = QTableWidgetItem(f"{total_hours_sum:.2f}")
            total_value.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            
            # Disable selection on empty cells in the total row
            for col in range(9):
                if col not in [6, 7]:
                    empty_item = QTableWidgetItem("")
                    empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
                    self.table.setItem(total_row_idx, col, empty_item)
            
            self.table.setItem(total_row_idx, 6, total_label)
            self.table.setItem(total_row_idx, 7, total_value)

        # Update the summary text at the bottom left
        self.summary_label.setText(f"Showing {len(self.current_data)} records from {start} to {end}.  |  Total Hours: {total_hours_sum:.2f}")

    def _export_pdf(self):
        if not self.current_data:
            QMessageBox.warning(self, "No Data", "Please generate a preview with data first.")
            return
        filepath, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "", "PDF Files (*.pdf)")
        if filepath:
            success, msg = ReportController.export_pdf(self.current_data, filepath)
            self._show_export_result(success, msg)

    def _export_excel(self):
        if not self.current_data:
            QMessageBox.warning(self, "No Data", "Please generate a preview with data first.")
            return
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Excel Report", "", "Excel Files (*.xlsx)")
        if filepath:
            success, msg = ReportController.export_excel(self.current_data, filepath)
            self._show_export_result(success, msg)

    def _export_csv(self):
        if not self.current_data:
            QMessageBox.warning(self, "No Data", "Please generate a preview with data first.")
            return
        filepath, _ = QFileDialog.getSaveFileName(self, "Save CSV Report", "", "CSV Files (*.csv)")
        if filepath:
            success, msg = ReportController.export_csv(self.current_data, filepath)
            self._show_export_result(success, msg)

    def _show_export_result(self, success: bool, msg: str):
        if success:
            QMessageBox.information(self, "Export Success", msg)
        else:
            QMessageBox.critical(self, "Export Failed", msg)