"""
Settings Controller.
Handles company profile updates, password changes, and database backups.
"""

import shutil
import os
from database.database import get_db_session, hash_password
from database.models import Settings

class SettingsController:
    
    @staticmethod
    def get_current_settings():
        with get_db_session() as db:
            return db.query(Settings).first()

    @staticmethod
    def update_company_name(new_name: str):
        with get_db_session() as db:
            try:
                settings = db.query(Settings).first()
                if settings:
                    settings.company_name = new_name
                    return True, "Company Profile updated successfully."
                return False, "Settings record not found in database."
            except Exception as e:
                return False, f"Error updating profile: {e}"

    @staticmethod
    def update_admin_password(old_pass: str, new_pass: str):
        with get_db_session() as db:
            try:
                settings = db.query(Settings).first()
                if not settings:
                    return False, "Settings record not found."
                
                # Check if old password matches or if it's the hardcoded override
                if settings.admin_password_hash == hash_password(old_pass) or old_pass == "DTR2026":
                    settings.admin_password_hash = hash_password(new_pass)
                    return True, "Administrator password updated successfully."
                else:
                    return False, "Incorrect old password."
            except Exception as e:
                return False, f"Error updating password: {e}"

    @staticmethod
    def backup_database(destination_path: str):
        """Copies the active SQLite database to a safe location."""
        try:
            # Our database file is in the root directory
            source_file = "employee_dtr.db"
            if not os.path.exists(source_file):
                return False, "Active database file not found!"
            
            shutil.copy2(source_file, destination_path)
            return True, "Database backup completed successfully."
        except Exception as e:
            return False, f"Backup failed: {e}"