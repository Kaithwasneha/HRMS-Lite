"""
Pydantic schemas for request/response validation in HRMS Lite.
Handles validation for employee and attendance data.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date as date_type
from typing import Literal
import re


class EmployeeCreate(BaseModel):
    """Schema for creating a new employee."""
    employee_id: str = Field(..., min_length=1, description="Unique employee identifier")
    name: str = Field(..., min_length=1, description="Employee name")
    email: EmailStr = Field(..., description="Employee email address")
    department: str = Field(..., min_length=1, description="Employee department")

    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate email format using regex pattern."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v


class EmployeeResponse(BaseModel):
    """Schema for employee response."""
    employee_id: str
    name: str
    email: str
    department: str

    class Config:
        from_attributes = True


class AttendanceCreate(BaseModel):
    """Schema for creating an attendance record."""
    employee_id: str = Field(..., min_length=1, description="Employee identifier")
    date: date_type = Field(..., description="Attendance date")
    status: Literal["Present", "Absent"] = Field(..., description="Attendance status")


class AttendanceResponse(BaseModel):
    """Schema for attendance response."""
    id: int
    employee_id: str
    date: date_type
    status: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to response, handling enum status."""
        return cls(
            id=obj.id,
            employee_id=obj.employee_id,
            date=obj.date,
            status=obj.status.value if hasattr(obj.status, 'value') else obj.status
        )
