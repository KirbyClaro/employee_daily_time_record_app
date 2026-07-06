from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QLineEdit, QGroupBox, QFormLayout, 
    QMessageBox, QFileDialog, QCheckBox
)
from PySide6.QtCore import Qt, QSettings, Signal
from PySide6.QtGui import QFont

from controllers.settings_controller import SettingsController


class SettingsPage(QWidget):
    
    company_name_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.local_prefs = QSettings("ModernDTR", "Preferences")
        self._setup_ui()
        self._load_current_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        title = QLabel("System Settings")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #333333;")
        layout.addWidget(title)

        profile_group = QGroupBox("Company Profile")
        profile_group.setStyleSheet(self._groupbox_style())
        profile_layout = QFormLayout(profile_group)
        profile_layout.setContentsMargins(20, 30, 20, 20)
        
        self.company_name_input = QLineEdit()
        self.company_name_input.setStyleSheet(self._input_style())
        
        self.btn_save_profile = QPushButton("Save Profile")
        self.btn_save_profile.setStyleSheet(self._primary_btn_style())
        self.btn_save_profile.clicked.connect(self._save_company_profile)
        
        profile_layout.addRow(QLabel("Company Name:"), self.company_name_input)
        profile_layout.addRow("", self.btn_save_profile)
        layout.addWidget(profile_group)

        security_group = QGroupBox("Security & Access")
        security_group.setStyleSheet(self._groupbox_style())
        security_layout = QFormLayout(security_group)
        security_layout.setContentsMargins(20, 30, 20, 20)

        self.old_pass_input = QLineEdit()
        self.old_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_pass_input.setStyleSheet(self._input_style())
        
        self.new_pass_input = QLineEdit()
        self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass_input.setStyleSheet(self._input_style())

        self.btn_change_pass = QPushButton("Update Password")
        self.btn_change_pass.setStyleSheet(self._primary_btn_style())
        self.btn_change_pass.clicked.connect(self._change_password)

        security_layout.addRow(QLabel("Current Password:"), self.old_pass_input)
        security_layout.addRow(QLabel("New Password:"), self.new_pass_input)
        security_layout.addRow("", self.btn_change_pass)
        layout.addWidget(security_group)

        pref_group = QGroupBox("Attendance Rules")
        pref_group.setStyleSheet(self._groupbox_style())
        pref_layout = QVBoxLayout(pref_group)
        pref_layout.setContentsMargins(20, 30, 20, 20)

        self.lunch_toggle = QCheckBox("Automatically deduct 1-hour lunch break (12:00 PM - 1:00 PM)")
        self.lunch_toggle.setFont(QFont("Segoe UI", 11))
        self.lunch_toggle.stateChanged.connect(self._save_preferences)
        
        pref_layout.addWidget(self.lunch_toggle)
        layout.addWidget(pref_group)

        db_group = QGroupBox("Database Management")
        db_group.setStyleSheet(self._groupbox_style())
        db_layout = QVBoxLayout(db_group)
        db_layout.setContentsMargins(20, 30, 20, 20)

        self.btn_backup = QPushButton("Backup Database")
        self.btn_backup.setStyleSheet(self._secondary_btn_style())
        self.btn_backup.setFixedWidth(200)
        self.btn_backup.clicked.connect(self._backup_database)

        db_desc = QLabel("Creates a safe copy of your employee_dtr.db file.")
        db_desc.setStyleSheet("color: #757575; font-style: italic;")

        db_layout.addWidget(self.btn_backup)
        db_layout.addWidget(db_desc)
        layout.addWidget(db_group)

        layout.addStretch()

    def _groupbox_style(self):
        return """
            QGroupBox { font-weight: bold; font-size: 14px; border: 1px solid #E0E0E0; border-radius: 6px; margin-top: 10px; background-color: #FFFFFF; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #1976D2; }
        """
    def _input_style(self):
        return "padding: 8px; border: 1px solid #CCC; border-radius: 4px; font-size: 13px; max-width: 300px;"
    def _primary_btn_style(self):
        return "background-color: #1976D2; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; max-width: 150px;"
    def _secondary_btn_style(self):
        return "background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;"

    def _load_current_data(self):
        settings = SettingsController.get_current_settings()
        if settings:
            self.company_name_input.setText(settings.company_name)
        
        lunch_pref = self.local_prefs.value("auto_lunch_deduct", True, type=bool)
        self.lunch_toggle.setChecked(lunch_pref)

    def _save_company_profile(self):
        new_name = self.company_name_input.text().strip()
        if not new_name:
            QMessageBox.warning(self, "Invalid Input", "Company name cannot be empty.")
            return
            
        success, msg = SettingsController.update_company_name(new_name)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.company_name_changed.emit(new_name)
        else:
            QMessageBox.warning(self, "Error", msg)

    def _change_password(self):
        old_pass = self.old_pass_input.text()
        new_pass = self.new_pass_input.text()
        
        if len(new_pass) < 5:
            QMessageBox.warning(self, "Weak Password", "New password must be at least 5 characters.")
            return

        success, msg = SettingsController.update_admin_password(old_pass, new_pass)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.old_pass_input.clear()
            self.new_pass_input.clear()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _save_preferences(self):
        self.local_prefs.setValue("auto_lunch_deduct", self.lunch_toggle.isChecked())

    def _backup_database(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Database Backup", "employee_dtr_backup.db", "SQLite Database (*.db)")
        if filepath:
            success, msg = SettingsController.backup_database(filepath)
            if success:
                QMessageBox.information(self, "Backup Successful", msg)
            else:
                QMessageBox.critical(self, "Backup Failed", msg)