"""
Attendance Controller.
Handles Time In, Time Out, attendance rules, and history retrieval.
"""

from datetime import date, datetime, time, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import and_, func

from database.database import get_db_session, hash_password
from database.models import Attendance, Employee, Settings


class AttendanceController:
    """Controller class for managing Attendance records."""

    @staticmethod
    def calculate_hours(time_in: time, time_out: time) -> float:
        """Calculates total hours worked between two time objects."""
        # Use a dummy date to perform datetime math
        dummy_date = date.today()
        dt_in = datetime.combine(dummy_date, time_in)
        dt_out = datetime.combine(dummy_date, time_out)
        
        # If time_out is somehow strictly before time_in, assume it crossed midnight
        if dt_out < dt_in:
            dt_out += timedelta(days=1)
            
        delta = dt_out - dt_in
        return round(delta.total_seconds() / 3600.0, 2)

    @staticmethod
    def time_in(employee_id: int, current_date: date, current_time: time) -> Tuple[bool, str]:
        """
        Records a Time In for an employee.
        Ensures only one attendance record per employee per day.
        """
        with get_db_session() as db:
            try:
                # Check if a record already exists for today
                existing = db.query(Attendance).filter(
                    and_(
                        Attendance.employee_id == employee_id,
                        Attendance.attendance_date == current_date
                    )
                ).first()

                if existing:
                    return False, f"Employee already timed in on {current_date.strftime('%Y-%m-%d')}."

                day_of_week = current_date.strftime("%A")
                
                new_attendance = Attendance(
                    employee_id=employee_id,
                    attendance_date=current_date,
                    day=day_of_week,
                    time_in=current_time,
                    attendance_status="Present"
                )
                db.add(new_attendance)
                return True, "Time In recorded successfully."
            except Exception as e:
                return False, f"An unexpected error occurred: {str(e)}"

    @staticmethod
    def time_out(employee_id: int, current_date: date, current_time: time) -> Tuple[bool, str]:
        """
        Records a Time Out for an employee.
        Ensures Time In exists and calculates total hours worked.
        """
        with get_db_session() as db:
            try:
                attendance = db.query(Attendance).filter(
                    and_(
                        Attendance.employee_id == employee_id,
                        Attendance.attendance_date == current_date
                    )
                ).first()

                if not attendance:
                    return False, "No Time In record found for this date. Cannot Time Out."

                if attendance.time_out:
                    return False, "Employee has already timed out for this date."

                # Prevent Time Out before Time In on the same day
                if current_time < attendance.time_in:
                    return False, "Time Out cannot be earlier than Time In."

                attendance.time_out = current_time
                attendance.total_hours = AttendanceController.calculate_hours(attendance.time_in, current_time)
                
                return True, "Time Out recorded successfully."
            except Exception as e:
                return False, f"An unexpected error occurred: {str(e)}"

    @staticmethod
    def verify_admin_password(password: str) -> bool:
        """Verifies the provided password against the stored hash in Settings."""
        with get_db_session() as db:
            settings = db.query(Settings).first()
            if not settings:
                return False
            return settings.admin_password_hash == hash_password(password)

    @staticmethod
    def update_attendance(record_id: int, admin_password: str, new_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Securely updates an existing attendance record.
        Requires correct admin password.
        """
        if not AttendanceController.verify_admin_password(admin_password):
            return False, "Incorrect Administrator password. Editing denied."

        with get_db_session() as db:
            try:
                attendance = db.query(Attendance).filter(Attendance.id == record_id).first()
                if not attendance:
                    return False, "Attendance record not found."

                # Update fields
                if "attendance_date" in new_data:
                    new_date = new_data["attendance_date"]
                    attendance.attendance_date = new_date
                    attendance.day = new_date.strftime("%A")
                
                if "time_in" in new_data:
                    attendance.time_in = new_data["time_in"]
                
                if "time_out" in new_data:
                    attendance.time_out = new_data["time_out"]

                if "attendance_status" in new_data:
                    attendance.attendance_status = new_data["attendance_status"]

                # Recalculate hours if both times exist
                if attendance.time_in and attendance.time_out:
                    if attendance.time_out >= attendance.time_in:
                        attendance.total_hours = AttendanceController.calculate_hours(
                            attendance.time_in, attendance.time_out
                        )
                    else:
                        return False, "Time Out cannot be earlier than Time In."
                else:
                    attendance.total_hours = None

                return True, "Attendance record updated successfully."
            except Exception as e:
                return False, f"An unexpected error occurred: {str(e)}"

    @staticmethod
    def get_attendance_history(
        employee_id: Optional[int] = None, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[Any]:
        """
        Retrieves attendance history, optionally filtered by employee and date range.
        Returns a list of tuples containing (Attendance, Employee).
        """
        with get_db_session() as db:
            query = db.query(Attendance, Employee).join(Employee, Attendance.employee_id == Employee.id)
            
            if employee_id:
                query = query.filter(Attendance.employee_id == employee_id)
                
            if start_date:
                query = query.filter(Attendance.attendance_date >= start_date)
                
            if end_date:
                query = query.filter(Attendance.attendance_date <= end_date)
                
            return query.order_by(Attendance.attendance_date.desc()).all()