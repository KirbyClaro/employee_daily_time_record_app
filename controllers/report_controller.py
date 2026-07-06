"""
Report Controller.
Handles data formatting and export capabilities (CSV, Excel, PDF).
"""

import os
import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import datetime

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


class ReportController:
    """Controller class for generating and exporting reports."""

    @staticmethod
    def format_attendance_data(history_records: List[Any]) -> List[Dict[str, Any]]:
        """
        Converts the raw SQLAlchemy join results (Attendance, Employee) 
        into a clean list of dictionaries for easier exporting.
        """
        formatted_data = []
        for attendance, employee in history_records:
            formatted_data.append({
                "Date": attendance.attendance_date.strftime("%Y-%m-%d"),
                "Day": attendance.day,
                "Employee ID": employee.employee_id,
                "Name": f"{employee.first_name} {employee.last_name}",
                "Department": employee.department or "N/A",
                "Time In": attendance.time_in.strftime("%I:%M %p") if attendance.time_in else "--:--",
                "Time Out": attendance.time_out.strftime("%I:%M %p") if attendance.time_out else "--:--",
                "Hours Worked": attendance.total_hours if attendance.total_hours else 0.0,
                "Status": attendance.attendance_status or "Unknown"
            })
        return formatted_data

    @staticmethod
    def _ensure_directory_exists(filepath: str):
        """Creates the directory for the file if it does not exist."""
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def export_csv(data: List[Dict[str, Any]], filepath: str) -> Tuple[bool, str]:
        """Exports data to a CSV file."""
        try:
            ReportController._ensure_directory_exists(filepath)
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            return True, f"Successfully exported CSV to {filepath}"
        except Exception as e:
            return False, f"Failed to export CSV: {str(e)}"

    @staticmethod
    def export_excel(data: List[Dict[str, Any]], filepath: str) -> Tuple[bool, str]:
        """Exports data to an Excel (.xlsx) file."""
        try:
            ReportController._ensure_directory_exists(filepath)
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False, engine='openpyxl')
            return True, f"Successfully exported Excel to {filepath}"
        except Exception as e:
            return False, f"Failed to export Excel: {str(e)}"

    @staticmethod
    def export_pdf(data: List[Dict[str, Any]], filepath: str, title: str = "Attendance Report") -> Tuple[bool, str]:
        """Exports data to a styled PDF document using ReportLab."""
        try:
            ReportController._ensure_directory_exists(filepath)
            
            # Setup the PDF Document (Landscape for wide tables)
            doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
            elements = []
            styles = getSampleStyleSheet()

            # Add Title and generation timestamp
            elements.append(Paragraph(title, styles['Title']))
            timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            elements.append(Paragraph(f"Generated on: {timestamp}", styles['Normal']))
            elements.append(Spacer(1, 12))

            if not data:
                elements.append(Paragraph("No records found for the selected criteria.", styles['Normal']))
                doc.build(elements)
                return True, f"Successfully exported empty PDF to {filepath}"

            # Prepare Data for Table
            headers = list(data[0].keys())
            table_data = [headers]
            for row in data:
                table_data.append([str(row.get(h, "")) for h in headers])

            # Create Table and apply Material Design inspired styling
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1976D2")),  # Material Blue Header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F5F5F5")), # Light Gray Background
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),  # Soft Borders
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(table)
            doc.build(elements)
            return True, f"Successfully exported PDF to {filepath}"
            
        except Exception as e:
            return False, f"Failed to export PDF: {str(e)}"