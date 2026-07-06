from datetime import date, datetime, time, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import and_, func

from database.database import get_db_session, hash_password
from database.models import Attendance, Employee, Settings


class AttendanceController:

    @staticmethod
    def calculate_hours(time_in: time, time_out: time) -> float:
        dummy_date = date.today()
        dt_in = datetime.combine(dummy_date, time_in)
        dt_out = datetime.combine(dummy_date, time_out)
        
        if dt_out < dt_in:
            dt_out += timedelta(days=1)
            
        delta = dt_out - dt_in
        total_hours = delta.total_seconds() / 3600.0

        # Lunch Break Deduction (12:00 PM to 1:00 PM)
        lunch_start = datetime.combine(dummy_date, time(12, 0))
        lunch_end = datetime.combine(dummy_date, time(13, 0))
        
        # Calculate overlap with the lunch break
        overlap_start = max(dt_in, lunch_start)
        overlap_end = min(dt_out, lunch_end)
        
        if overlap_start < overlap_end:
            overlap_hours = (overlap_end - overlap_start).total_seconds() / 3600.0
            total_hours -= overlap_hours

        return round(total_hours, 2)

    @staticmethod
    def time_in(employee_id: int, current_date: date, current_time: time) -> Tuple[bool, str]:
        with get_db_session() as db:
            try:
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

                if current_time < attendance.time_in:
                    return False, "Time Out cannot be earlier than Time In."

                attendance.time_out = current_time
                attendance.total_hours = AttendanceController.calculate_hours(attendance.time_in, current_time)
                
                return True, "Time Out recorded successfully."
            except Exception as e:
                return False, f"An unexpected error occurred: {str(e)}"

    @staticmethod
    def verify_admin_password(password: str) -> bool:
        with get_db_session() as db:
            settings = db.query(Settings).first()
            if not settings:
                return False
            return settings.admin_password_hash == hash_password(password)

    @staticmethod
    def update_attendance(record_id: int, admin_password: str, new_data: Dict[str, Any]) -> Tuple[bool, str]:
        if not AttendanceController.verify_admin_password(admin_password):
            return False, "Incorrect Administrator password. Editing denied."

        with get_db_session() as db:
            try:
                attendance = db.query(Attendance).filter(Attendance.id == record_id).first()
                if not attendance:
                    return False, "Attendance record not found."

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
    def delete_attendance(record_id: int) -> Tuple[bool, str]:
        with get_db_session() as db:
            try:
                attendance = db.query(Attendance).filter(Attendance.id == record_id).first()
                if not attendance:
                    return False, "Attendance record not found."
                
                db.delete(attendance)
                return True, "Attendance record deleted successfully."
            except Exception as e:
                return False, f"An unexpected error occurred: {str(e)}"

    @staticmethod
    def get_attendance_history(
        employee_id: Optional[int] = None, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[Any]:
        with get_db_session() as db:
            query = db.query(Attendance, Employee).join(Employee, Attendance.employee_id == Employee.id)
            
            if employee_id:
                query = query.filter(Attendance.employee_id == employee_id)
                
            if start_date:
                query = query.filter(Attendance.attendance_date >= start_date)
                
            if end_date:
                query = query.filter(Attendance.attendance_date <= end_date)
                
            return query.order_by(Attendance.attendance_date.desc()).all()