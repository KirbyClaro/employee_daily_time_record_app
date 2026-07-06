"""
Main Dashboard View.
Provides the main application shell, sidebar navigation, top bar with real-time clock,
and the home dashboard with Material Design statistics cards.
"""

from datetime import date, datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QStackedWidget, QFrame, QGraphicsDropShadowEffect,
    QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QColor

from controllers.employee_controller import EmployeeController
from controllers.attendance_controller import AttendanceController


class DashboardWindow(QMainWindow):
    """The main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee DTR System")
        self.setMinimumSize(1200, 800)
        
        # Main central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self._setup_sidebar()
        self._setup_main_content()
        self._start_clock()
        self.refresh_statistics()

    def _setup_sidebar(self):
        """Creates the left navigation sidebar."""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-right: 1px solid #E0E0E0;
            }
            QPushButton {
                text-align: left;
                padding: 15px 20px;
                border: none;
                font-size: 14px;
                font-weight: bold;
                color: #555555;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #F0F7FF;
                color: #1976D2;
                border-left: 4px solid #1976D2;
            }
            QPushButton:checked {
                background-color: #E3F2FD;
                color: #1976D2;
                border-left: 4px solid #1976D2;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(5)

        # App Logo/Title placeholder
        title_label = QLabel("Modern DTR")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1976D2; padding: 0 20px 20px 20px;")
        sidebar_layout.addWidget(title_label)

        # Navigation Buttons
        self.nav_buttons = {}
        nav_items = ["Dashboard", "Employees", "Attendance", "Reports", "Settings"]
        
        for item in nav_items:
            btn = QPushButton(f"  {item}")
            btn.setCheckable(True)
            sidebar_layout.addWidget(btn)
            self.nav_buttons[item] = btn

        # Set default active button
        self.nav_buttons["Dashboard"].setChecked(True)

        # Spacer to push items up
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sidebar_layout.addItem(spacer)

        self.main_layout.addWidget(self.sidebar)

    def _setup_main_content(self):
        """Creates the top bar and the central stacked widget area."""
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # --- Top Bar ---
        top_bar = QFrame()
        top_bar.setFixedHeight(70)
        top_bar.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #E0E0E0;")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(20, 0, 20, 0)

        self.date_label = QLabel()
        self.date_label.setFont(QFont("Segoe UI", 12))
        self.date_label.setStyleSheet("color: #757575; border: none;")
        
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: #333333; border: none;")

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2; color: white; border-radius: 4px;
                padding: 8px 16px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #1565C0; }
        """)
        refresh_btn.clicked.connect(self.refresh_statistics)

        top_bar_layout.addWidget(self.date_label)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.time_label)
        top_bar_layout.addSpacing(20)
        top_bar_layout.addWidget(refresh_btn)

        content_layout.addWidget(top_bar)

        # --- Stacked Widget (Page Area) ---
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #F5F5F5;")
        
        # Initialize Dashboard Home Page
        self.dashboard_page = self._create_dashboard_page()
        self.stacked_widget.addWidget(self.dashboard_page)
        
        # Placeholders for future pages
        self.stacked_widget.addWidget(QLabel("Employees Page (Coming Soon)"))
        self.stacked_widget.addWidget(QLabel("Attendance Page (Coming Soon)"))
        
        content_layout.addWidget(self.stacked_widget)
        self.main_layout.addWidget(content_container)

    def _create_dashboard_page(self) -> QWidget:
        """Builds the main dashboard page with statistics cards."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QLabel("Overview")
        header.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header.setStyleSheet("color: #333333;")
        layout.addWidget(header)

        # Cards Layout (Grid-like using HBox)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # Initialize Stat Cards
        self.card_total_emp = self._create_stat_card("Total Employees", "0", "#1976D2")
        self.card_present = self._create_stat_card("Present Today", "0", "#4CAF50")
        self.card_not_timed_in = self._create_stat_card("Not Timed In", "0", "#FF9800")
        self.card_not_timed_out = self._create_stat_card("Not Timed Out", "0", "#F44336")

        cards_layout.addWidget(self.card_total_emp)
        cards_layout.addWidget(self.card_present)
        cards_layout.addWidget(self.card_not_timed_in)
        cards_layout.addWidget(self.card_not_timed_out)

        layout.addLayout(cards_layout)
        layout.addStretch() # Push everything to the top

        return page

    def _create_stat_card(self, title: str, value: str, accent_color: str) -> QFrame:
        """Creates a Material Design styled card."""
        card = QFrame()
        card.setFixedSize(220, 120)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border-top: 4px solid {accent_color};
            }}
        """)
        
        # Add soft shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 11))
        title_lbl.setStyleSheet(f"color: #757575; border: none;")

        # Store the value label as an attribute of the card so we can update it later
        card.value_lbl = QLabel(value)
        card.value_lbl.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        card.value_lbl.setStyleSheet("color: #333333; border: none;")

        layout.addWidget(title_lbl)
        layout.addWidget(card.value_lbl)

        return card

    def _start_clock(self):
        """Initializes and starts the real-time clock timer."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_datetime)
        self.timer.start(1000) # Update every 1000ms (1 second)
        self._update_datetime() # Set initial time immediately

    def _update_datetime(self):
        """Updates the top bar labels with the current date and time."""
        now = datetime.now()
        self.date_label.setText(now.strftime("%A, %B %d, %Y"))
        self.time_label.setText(now.strftime("%I:%M:%S %p"))

    def refresh_statistics(self):
        """Fetches data from controllers and updates the dashboard cards."""
        # Note: We will implement the actual calculation logic here once 
        # we have some dummy data. For now, we will query total employees.
        employees = EmployeeController.get_all_employees()
        total_emp = len(employees)
        
        history = AttendanceController.get_attendance_history(start_date=date.today(), end_date=date.today())
        
        present_count = len(history)
        not_timed_out = sum(1 for att, emp in history if not att.time_out)
        not_timed_in = total_emp - present_count

        # Update Card UI
        self.card_total_emp.value_lbl.setText(str(total_emp))
        self.card_present.value_lbl.setText(str(present_count))
        self.card_not_timed_in.value_lbl.setText(str(not_timed_in))
        self.card_not_timed_out.value_lbl.setText(str(not_timed_out))