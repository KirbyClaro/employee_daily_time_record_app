"""
Employee Controller.
Handles all business logic and CRUD operations related to employees.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from database.database import get_db_session
from database.models import Employee


class EmployeeController:
    """Controller class for managing Employee data."""

    @staticmethod
    def add_employee(data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Adds a new employee to the database.
        
        Args:
            data: A dictionary containing employee details.
            
        Returns:
            A tuple (success: bool, message: str)
        """
        with get_db_session() as db:
            try:
                new_employee = Employee(
                    employee_id=data.get("employee_id"),
                    first_name=data.get("first_name"),
                    middle_name=data.get("middle_name"),
                    last_name=data.get("last_name"),
                    department=data.get("department"),
                    position=data.get("position"),
                    contact_number=data.get("contact_number"),
                    email=data.get("email"),
                    hire_date=data.get("hire_date"),
                    status=data.get("status", "Active"),
                    profile_picture=data.get("profile_picture")
                )
                db.add(new_employee)
                return True, "Employee added successfully."
            except IntegrityError:
                return False, f"Error: Employee ID '{data.get('employee_id')}' already exists."
            except Exception as e:
                return False, f"An unexpected error occurred: {str(e)}"

    @staticmethod
    def get_all_employees() -> List[Employee]:
        """Retrieves all employees from the database."""
        with get_db_session() as db:
            return db.query(Employee).all()

    @staticmethod
    def get_employee_by_id(db_id: int) -> Optional[Employee]:
        """Retrieves a single employee by their database primary key (id)."""
        with get_db_session() as db:
            return db.query(Employee).filter(Employee.id == db_id).first()
            
    @staticmethod
    def get_employee_by_emp_id(emp_id: str) -> Optional[Employee]:
        """Retrieves a single employee by their company Employee ID."""
        with get_db_session() as db:
            return db.query(Employee).filter(Employee.employee_id == emp_id).first()

    @staticmethod
    def update_employee(db_id: int, data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Updates an existing employee's information.
        
        Args:
            db_id: The primary key of the employee to update.
            data: A dictionary containing updated employee details.
            
        Returns:
            A tuple (success: bool, message: str)
        """
        with get_db_session() as db:
            try:
                employee = db.query(Employee).filter(Employee.id == db_id).first()
                if not employee:
                    return False, "Employee not found."

                # Update attributes if they are present in the data dictionary
                for key, value in data.items():
                    if hasattr(employee, key):
                        setattr(employee, key, value)

                return True, "Employee updated successfully."
            except IntegrityError:
                return False, "Error: Employee ID is already in use by another record."
            except Exception as e:
                return False, f"An unexpected error occurred: {str(e)}"

    @staticmethod
    def delete_employee(db_id: int) -> tuple[bool, str]:
        """
        Deletes an employee from the database.
        
        Args:
            db_id: The primary key of the employee to delete.
            
        Returns:
            A tuple (success: bool, message: str)
        """
        with get_db_session() as db:
            try:
                employee = db.query(Employee).filter(Employee.id == db_id).first()
                if not employee:
                    return False, "Employee not found."
                
                db.delete(employee)
                return True, "Employee deleted successfully."
            except Exception as e:
                return False, f"An unexpected error occurred: {str(e)}"

    @staticmethod
    def search_employees(query_str: str) -> List[Employee]:
        """
        Searches employees by ID, First Name, Last Name, Department, or Position.
        """
        with get_db_session() as db:
            search_term = f"%{query_str}%"
            return db.query(Employee).filter(
                or_(
                    Employee.employee_id.ilike(search_term),
                    Employee.first_name.ilike(search_term),
                    Employee.last_name.ilike(search_term),
                    Employee.department.ilike(search_term),
                    Employee.position.ilike(search_term)
                )
            ).all()