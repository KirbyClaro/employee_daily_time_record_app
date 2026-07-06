# Employee Daily Time Record (DTR) Application

A modern, production-quality desktop application for managing employee attendance, built with Python. 

## Features
* **Modern Dashboard:** Material Design interface providing real-time statistics (Present, Not Timed In, Total Employees).
* **Employee Management:** Complete CRUD operations for employee records with profile picture support.
* **Attendance Tracking:** Automatic and manual Time In/Time Out capabilities.
* **Secure Editing:** Password-protected attendance modification for administrators.
* **Advanced Reporting:** Export data to Excel, CSV, and PDF formats.
* **Settings Management:** Dark/Light theme toggling, database backups, and customizable company profiles.

## Technology Stack
* **Language:** Python 3.12+
* **GUI Framework:** PySide6 (Qt for Python)
* **Database:** SQLite3
* **ORM:** SQLAlchemy
* **Data Manipulation:** Pandas
* **PDF Generation:** ReportLab / WeasyPrint

## Project Architecture (MVC)
```text
employee_dtr/
├── main.py
├── database/        # SQLite integration and SQLAlchemy models
├── controllers/     # Business logic and data flow bridging
├── views/           # PySide6 UI components and dialogs
├── ui/              # Qt Designer UI files (if applicable)
├── assets/          # Icons, images, and QSS stylesheets
├── reports/         # Generated PDF and Excel files
├── exports/         # Data exports
├── backups/         # Database backup files
├── utils/           # Helper functions and constants
└── requirements.txt