"""
Database models for the Employee DTR Application.
Defines the schema for Employees, Attendance, and Settings using SQLAlchemy 2.0.
"""

from datetime import date, time
from typing import List, Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""
    pass


class Employee(Base):
    """Model representing an employee in the company."""
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100))
    position: Mapped[Optional[str]] = mapped_column(String(100))
    contact_number: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    hire_date: Mapped[Optional[date]]
    status: Mapped[str] = mapped_column(String(20), default="Active")
    profile_picture: Mapped[Optional[str]] = mapped_column(String(255))

    # One-to-Many relationship with Attendance
    attendance_records: Mapped[List["Attendance"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )


class Attendance(Base):
    """Model representing a daily time record entry for an employee."""
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    attendance_date: Mapped[date] = mapped_column(nullable=False)
    day: Mapped[str] = mapped_column(String(20), nullable=False)
    time_in: Mapped[time] = mapped_column(nullable=False)
    time_out: Mapped[Optional[time]]
    total_hours: Mapped[Optional[float]]
    attendance_status: Mapped[Optional[str]] = mapped_column(String(50))

    # Many-to-One relationship back to Employee
    employee: Mapped["Employee"] = relationship(back_populates="attendance_records")


class Settings(Base):
    """Model representing the application configuration."""
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    admin_password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(100), default="My Company")
    theme: Mapped[str] = mapped_column(String(20), default="Light")