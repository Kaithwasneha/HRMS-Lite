"""
FastAPI application for HRMS Lite backend.
Provides REST API endpoints for employee and attendance management.
"""
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from database import get_db, init_db
from models import Employee, Attendance, AttendanceStatus
from schemas import EmployeeCreate, EmployeeResponse, AttendanceCreate, AttendanceResponse
from crud import (
    create_employee,
    get_all_employees,
    delete_employee,
    create_attendance,
    get_attendance_by_employee,
    DuplicateEmployeeError,
    EmployeeNotFoundError
)

# Initialize FastAPI app
app = FastAPI(
    title="HRMS Lite API",
    description="REST API for Human Resource Management System",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:5173",  # Local development frontend
    os.getenv("FRONTEND_URL", ""),  # Production frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize database on application startup."""
    init_db()


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"status": "ok", "message": "HRMS Lite API is running"}


@app.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee_endpoint(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """
    Create a new employee record.
    
    Returns:
        201: Employee created successfully
        409: Employee ID already exists
        422: Validation error (invalid email, missing fields)
    """
    try:
        db_employee = create_employee(db, employee)
        return db_employee
    except DuplicateEmployeeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@app.get("/employees", response_model=List[EmployeeResponse])
def get_employees_endpoint(db: Session = Depends(get_db)):
    """
    Retrieve all employee records.
    
    Returns:
        200: List of all employees
    """
    employees = get_all_employees(db)
    return employees


@app.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_endpoint(employee_id: str, db: Session = Depends(get_db)):
    """
    Delete an employee and all associated attendance records.
    
    Returns:
        204: Employee deleted successfully
        404: Employee not found
    """
    deleted = delete_employee(db, employee_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )


@app.post("/attendance", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance_endpoint(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    """
    Create an attendance record.
    
    Returns:
        201: Attendance recorded successfully
        404: Employee not found
        422: Validation error (invalid status or date format)
    """
    try:
        db_attendance = create_attendance(db, attendance)
        return AttendanceResponse.from_orm(db_attendance)
    except EmployeeNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.get("/attendance/{employee_id}", response_model=List[AttendanceResponse])
def get_attendance_endpoint(employee_id: str, db: Session = Depends(get_db)):
    """
    Retrieve all attendance records for a specific employee.
    
    Returns:
        200: List of attendance records sorted by date (newest first)
        404: Employee not found
    """
    try:
        attendance_records = get_attendance_by_employee(db, employee_id)
        return [AttendanceResponse.from_orm(record) for record in attendance_records]
    except EmployeeNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get aggregated dashboard statistics in a single call.
    
    Returns:
        200: Dashboard statistics including employee count, attendance summary, etc.
    """
    from sqlalchemy import func
    from datetime import date
    
    # Get total employees
    total_employees = db.query(Employee).count()
    
    # Get total attendance records
    total_attendance = db.query(Attendance).count()
    
    # Get today's attendance
    today = date.today()
    today_present = db.query(Attendance).filter(
        Attendance.date == today,
        Attendance.status == AttendanceStatus.Present
    ).count()
    
    today_absent = db.query(Attendance).filter(
        Attendance.date == today,
        Attendance.status == AttendanceStatus.Absent
    ).count()
    
    # Get department distribution
    dept_distribution = db.query(
        Employee.department,
        func.count(Employee.employee_id).label('count')
    ).group_by(Employee.department).all()
    
    departments = [{"name": dept, "count": count} for dept, count in dept_distribution]
    
    # Get recent attendance (last 5 records)
    recent_attendance = db.query(Attendance).join(Employee).order_by(
        Attendance.date.desc()
    ).limit(5).all()
    
    recent = [{
        "employee_id": record.employee_id,
        "employee_name": record.employee.name,
        "date": str(record.date),
        "status": record.status.value
    } for record in recent_attendance]
    
    return {
        "total_employees": total_employees,
        "total_attendance": total_attendance,
        "present_today": today_present,
        "absent_today": today_absent,
        "departments": departments,
        "recent_attendance": recent
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    
    Returns:
        500: Internal server error
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred"}
    )
