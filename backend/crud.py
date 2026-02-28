"""
CRUD operations for HRMS Lite.
Handles database operations for employees and attendance records.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Employee, Attendance, AttendanceStatus
from schemas import EmployeeCreate, AttendanceCreate
from datetime import date
from typing import List, Optional


class DuplicateEmployeeError(Exception):
    """Raised when attempting to create an employee with duplicate employee_id."""
    pass


class EmployeeNotFoundError(Exception):
    """Raised when employee is not found in database."""
    pass


def create_employee(db: Session, employee: EmployeeCreate) -> Employee:
    """
    Create a new employee record.
    
    Args:
        db: Database session
        employee: Employee data to create
        
    Returns:
        Created employee record
        
    Raises:
        DuplicateEmployeeError: If employee_id already exists
    """
    # Check if employee_id already exists
    existing = db.query(Employee).filter(Employee.employee_id == employee.employee_id).first()
    if existing:
        raise DuplicateEmployeeError(f"Employee with ID {employee.employee_id} already exists")
    
    # Create new employee
    db_employee = Employee(
        employee_id=employee.employee_id,
        name=employee.name,
        email=employee.email,
        department=employee.department
    )
    
    try:
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee
    except IntegrityError:
        db.rollback()
        raise DuplicateEmployeeError(f"Employee with ID {employee.employee_id} already exists")


def get_all_employees(db: Session) -> List[Employee]:
    """
    Retrieve all employee records.
    
    Args:
        db: Database session
        
    Returns:
        List of all employees
    """
    return db.query(Employee).all()


def delete_employee(db: Session, employee_id: str) -> bool:
    """
    Delete an employee and all associated attendance records (cascade delete).
    
    Args:
        db: Database session
        employee_id: ID of employee to delete
        
    Returns:
        True if employee was deleted, False if not found
    """
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        return False
    
    db.delete(employee)
    db.commit()
    return True


def create_attendance(db: Session, attendance: AttendanceCreate) -> Attendance:
    """
    Create an attendance record.
    
    Args:
        db: Database session
        attendance: Attendance data to create
        
    Returns:
        Created attendance record
        
    Raises:
        EmployeeNotFoundError: If employee does not exist
    """
    # Verify employee exists
    employee = db.query(Employee).filter(Employee.employee_id == attendance.employee_id).first()
    if not employee:
        raise EmployeeNotFoundError(f"Employee with ID {attendance.employee_id} not found")
    
    # Convert status string to enum
    status_enum = AttendanceStatus.Present if attendance.status == "Present" else AttendanceStatus.Absent
    
    # Create attendance record
    db_attendance = Attendance(
        employee_id=attendance.employee_id,
        date=attendance.date,
        status=status_enum
    )
    
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


def get_attendance_by_employee(db: Session, employee_id: str) -> List[Attendance]:
    """
    Retrieve all attendance records for a specific employee, sorted by date descending.
    
    Args:
        db: Database session
        employee_id: ID of employee
        
    Returns:
        List of attendance records sorted by date (newest first)
        
    Raises:
        EmployeeNotFoundError: If employee does not exist
    """
    # Verify employee exists
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise EmployeeNotFoundError(f"Employee with ID {employee_id} not found")
    
    # Get attendance records sorted by date descending
    return db.query(Attendance).filter(
        Attendance.employee_id == employee_id
    ).order_by(Attendance.date.desc()).all()
