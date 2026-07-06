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
from views.employee_list import EmployeeListPage
from views.attendance_page import AttendancePage
from views.report_page import ReportPage
from views.report_page import ReportPage
from views.settings_page import SettingsPage

class DashboardWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee DTR System")
        self.setMinimumSize(1200, 800)
        
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
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("""
            QFrame { background-color: #FFFFFF; border-right: 1px solid #E0E0E0; }
            QPushButton { text-align: left; padding: 15px 20px; border: none; font-size: 14px; font-weight: bold; color: #555555; background-color: transparent; }
            QPushButton:hover { background-color: #F0F7FF; color: #1976D2; border-left: 4px solid #1976D2; }
            QPushButton:checked { background-color: #E3F2FD; color: #1976D2; border-left: 4px solid #1976D2; }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(5)

        title_label = QLabel("Modern DTR")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1976D2; padding: 0 20px 20px 20px;")
        sidebar_layout.addWidget(title_label)

        self.nav_buttons = {}
        nav_items = ["Dashboard", "Employees", "Attendance", "Reports", "Settings"]
        
        for index, item in enumerate(nav_items):
            btn = QPushButton(f"  {item}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=index, name=item: self._switch_page(idx, name))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[item] = btn

        self.nav_buttons["Dashboard"].setChecked(True)

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sidebar_layout.addItem(spacer)

        self.main_layout.addWidget(self.sidebar)

    def _setup_main_content(self):
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

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
        refresh_btn.setStyleSheet("QPushButton { background-color: #1976D2; color: white; border-radius: 4px; padding: 8px 16px; font-weight: bold; border: none; } QPushButton:hover { background-color: #1565C0; }")
        refresh_btn.clicked.connect(self.refresh_statistics)

        top_bar_layout.addWidget(self.date_label)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.time_label)
        top_bar_layout.addSpacing(20)
        top_bar_layout.addWidget(refresh_btn)

        content_layout.addWidget(top_bar)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #F5F5F5;")
        
        self.dashboard_page = self._create_dashboard_page()
        self.stacked_widget.addWidget(self.dashboard_page)
        
        self.employees_page = EmployeeListPage()
        self.stacked_widget.addWidget(self.employees_page)
        
        self.attendance_page = AttendancePage()
        self.stacked_widget.addWidget(self.attendance_page)
        
        self.reports_page = ReportPage()
        self.stacked_widget.addWidget(self.reports_page)
        
        self.stacked_widget.addWidget(QLabel("Settings Page (Coming Soon)"))
        
        content_layout.addWidget(self.stacked_widget)
        self.main_layout.addWidget(content_container)

    def _switch_page(self, index: int, active_name: str):
        self.stacked_widget.setCurrentIndex(index)
        
        if active_name == "Attendance":
            self.attendance_page.load_employees_dropdown()
            self.attendance_page.load_history()
        elif active_name == "Employees":
            self.employees_page.load_employees()
        elif active_name == "Reports":
            self.reports_page.load_employees_dropdown()
            
        for name, btn in self.nav_buttons.items():
            if name != active_name:
                btn.setChecked(False)
            else:
                btn.setChecked(True)

    def _create_dashboard_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QLabel("Overview")
        header.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header.setStyleSheet("color: #333333;")
        layout.addWidget(header)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        self.card_total_emp = self._create_stat_card("Total Employees", "0", "#1976D2")
        self.card_present = self._create_stat_card("Present Today", "0", "#4CAF50")
        self.card_not_timed_in = self._create_stat_card("Not Timed In", "0", "#FF9800")
        self.card_not_timed_out = self._create_stat_card("Not Timed Out", "0", "#F44336")

        cards_layout.addWidget(self.card_total_emp)
        cards_layout.addWidget(self.card_present)
        cards_layout.addWidget(self.card_not_timed_in)
        cards_layout.addWidget(self.card_not_timed_out)

        layout.addLayout(cards_layout)
        layout.addStretch() 

        return page

    def _create_stat_card(self, title: str, value: str, accent_color: str) -> QFrame:
        card = QFrame()
        card.setFixedSize(220, 120)
        card.setStyleSheet(f"QFrame {{ background-color: white; border-radius: 8px; border-top: 4px solid {accent_color}; }}")
        
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

        card.value_lbl = QLabel(value)
        card.value_lbl.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        card.value_lbl.setStyleSheet("color: #333333; border: none;")

        layout.addWidget(title_lbl)
        layout.addWidget(card.value_lbl)

        return card

    def _start_clock(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_datetime)
        self.timer.start(1000) 
        self._update_datetime() 

    def _update_datetime(self):
        now = datetime.now()
        self.date_label.setText(now.strftime("%A, %B %d, %Y"))
        self.time_label.setText(now.strftime("%I:%M:%S %p"))

    def refresh_statistics(self):
        employees = EmployeeController.get_all_employees()
        total_emp = len(employees)
        
        history = AttendanceController.get_attendance_history(start_date=date.today(), end_date=date.today())
        
        present_count = len(history)
        not_timed_out = sum(1 for att, emp in history if not att.time_out)
        not_timed_in = total_emp - present_count

        self.card_total_emp.value_lbl.setText(str(total_emp))
        self.card_present.value_lbl.setText(str(present_count))
        self.card_not_timed_in.value_lbl.setText(str(not_timed_in))
        self.card_not_timed_out.value_lbl.setText(str(not_timed_out))