"""
SQLAlchemy models for HRMS Lite.
Defines Employee and Attendance database tables with proper constraints and indexes.
"""
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from database import Base
import enum


class AttendanceStatus(enum.Enum):
    """Enum for attendance status values."""
    Present = "Present"
    Absent = "Absent"


class Employee(Base):
    """
    Employee model representing employee records.
    
    Attributes:
        employee_id: Unique identifier for the employee (Primary Key)
        name: Employee's full name (Required)
        email: Employee's email address (Required, must be valid format)
        department: Employee's department (Required)
        attendance_records: Relationship to attendance records (cascade delete)
    
    Indexes:
        - Primary key index on employee_id (automatic)
        - Index on email for faster email lookups
        - Index on department for department-based queries
    """
    __tablename__ = "employees"

    employee_id = Column(String(50), primary_key=True, unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(100), nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)

    # Relationship with cascade delete - when employee is deleted, all attendance records are deleted
    attendance_records = relationship(
        "Attendance",
        back_populates="employee",
        cascade="all, delete-orphan"
    )

    # Composite index for common query patterns
    __table_args__ = (
        Index('idx_employee_dept_name', 'department', 'name'),
    )


class Attendance(Base):
    """
    Attendance model representing daily attendance records.
    
    Attributes:
        id: Auto-incrementing primary key
        employee_id: Foreign key reference to Employee (Required)
        date: Date of attendance (Required)
        status: Attendance status - Present or Absent (Required)
        employee: Relationship to Employee model
    
    Indexes:
        - Primary key index on id (automatic)
        - Index on employee_id for faster employee lookups
        - Index on date for date-based queries
        - Composite index on (employee_id, date) for common query patterns
        - Index on status for filtering by attendance status
    """
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        String(50),
        ForeignKey("employees.employee_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    date = Column(Date, nullable=False, index=True)
    status = Column(Enum(AttendanceStatus), nullable=False, index=True)

    # Relationship back to employee
    employee = relationship("Employee", back_populates="attendance_records")

    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_attendance_emp_date', 'employee_id', 'date'),
        Index('idx_attendance_date_status', 'date', 'status'),
    )
