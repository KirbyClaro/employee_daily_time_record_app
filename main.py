"""
Main entry point for the Employee DTR Application.
Initializes the SQLite database, sets up the PySide6 QApplication, 
and applies global Material Design typography.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont
from database.database import init_db
from views.dashboard import DashboardWindow


def setup_global_styling(app: QApplication):
    """Applies global Material Design baseline styles and typography."""
    # Try to set a modern default font (Roboto, Segoe UI, or system default)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Global Material Design baseline QSS
    # #F5F5F5 is the standard Material Light Gray background
    # #333333 is standard dark gray text for readability
    app.setStyleSheet("""
        QWidget {
            background-color: #F5F5F5;
            color: #333333;
        }
        QScrollBar:vertical {
            border: none;
            background: #E0E0E0;
            width: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #BDBDBD;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover {
            background: #9E9E9E;
        }
    """)


def main():
    # 1. Initialize the Database (Creates tables and default admin settings)
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Critical Database Error: {e}")
        sys.exit(1)

    # 2. Create the PySide6 Application object
    app = QApplication(sys.argv)
    app.setApplicationName("Employee DTR")
    
    # 3. Apply global Material theme settings
    setup_global_styling(app)

    print("Application boot sequence complete. Ready for UI!")

    # 4. Launch the Main Dashboard (Commented out until we create views/dashboard.py)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()