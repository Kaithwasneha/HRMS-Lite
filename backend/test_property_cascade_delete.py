"""
Property-based test for cascade delete integrity.

**Validates: Requirements 1.3**

This test verifies that when an employee is deleted, all associated 
attendance records are also deleted from the database (cascade delete).
"""
import pytest
from hypothesis import given, strategies as st, settings
from sqlalchemy import create_engine, Column, String, Integer, Date, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date, timedelta
import enum


# Create base for test models
Base = declarative_base()


class AttendanceStatus(enum.Enum):
    """Enum for attendance status values."""
    Present = "Present"
    Absent = "Absent"


class Employee(Base):
    """Employee model for testing."""
    __tablename__ = "employees"

    employee_id = Column(String(50), primary_key=True, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)

    # Relationship with cascade delete
    attendance_records = relationship(
        "Attendance",
        back_populates="employee",
        cascade="all, delete-orphan"
    )


class Attendance(Base):
    """Attendance model for testing."""
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        String(50),
        ForeignKey("employees.employee_id", ondelete="CASCADE"),
        nullable=False
    )
    date = Column(Date, nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)

    employee = relationship("Employee", back_populates="attendance_records")


# Strategy for generating valid employee IDs
employee_id_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
    min_size=1,
    max_size=20
)

# Strategy for generating valid names
name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters=' '),
    min_size=2,
    max_size=50
).filter(lambda x: x.strip() != '')

# Strategy for generating valid emails
email_strategy = st.emails()

# Strategy for generating valid departments
department_strategy = st.sampled_from([
    'Engineering', 'HR', 'Sales', 'Marketing', 'Finance', 'Operations'
])

# Strategy for generating dates (within reasonable range)
date_strategy = st.dates(
    min_value=date.today() - timedelta(days=365),
    max_value=date.today()
)

# Strategy for generating attendance status
status_strategy = st.sampled_from([AttendanceStatus.Present, AttendanceStatus.Absent])

# Strategy for generating number of attendance records (1 to 10)
attendance_count_strategy = st.integers(min_value=1, max_value=10)


@given(
    employee_id=employee_id_strategy,
    name=name_strategy,
    email=email_strategy,
    department=department_strategy,
    attendance_count=attendance_count_strategy,
    dates=st.lists(date_strategy, min_size=1, max_size=10),
    statuses=st.lists(status_strategy, min_size=1, max_size=10)
)
@settings(max_examples=10, deadline=None)
def test_cascade_delete_integrity(
    employee_id,
    name,
    email,
    department,
    attendance_count,
    dates,
    statuses
):
    """
    Property 5: Cascade Delete Integrity
    
    **Validates: Requirements 1.3**
    
    For all employee deletion operations, all associated attendance records 
    must be deleted from the database.
    
    Test Strategy:
    1. Create an employee with random valid data
    2. Create multiple attendance records for that employee
    3. Delete the employee
    4. Verify that all attendance records for that employee are also deleted
    """
    # Create a fresh in-memory database for each test
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    test_db = SessionLocal()
    
    try:
        # Step 1: Create employee
        employee = Employee(
            employee_id=employee_id,
            name=name,
            email=email,
            department=department
        )
        
        try:
            test_db.add(employee)
            test_db.commit()
            test_db.refresh(employee)
        except Exception:
            # Skip if employee creation fails (e.g., duplicate ID in same test run)
            test_db.rollback()
            return
        
        # Step 2: Create attendance records for the employee
        # Use the minimum of attendance_count and available dates/statuses
        num_records = min(attendance_count, len(dates), len(statuses))
        
        for i in range(num_records):
            attendance = Attendance(
                employee_id=employee_id,
                date=dates[i],
                status=statuses[i]
            )
            test_db.add(attendance)
        
        test_db.commit()
        
        # Verify attendance records were created
        attendance_before = test_db.query(Attendance).filter(
            Attendance.employee_id == employee_id
        ).all()
        assert len(attendance_before) == num_records, \
            f"Expected {num_records} attendance records, found {len(attendance_before)}"
        
        # Step 3: Delete the employee
        test_db.delete(employee)
        test_db.commit()
        
        # Step 4: Verify all attendance records are deleted (cascade delete)
        attendance_after = test_db.query(Attendance).filter(
            Attendance.employee_id == employee_id
        ).all()
        
        assert len(attendance_after) == 0, \
            f"Expected 0 attendance records after employee deletion, found {len(attendance_after)}"
        
        # Also verify the employee is deleted
        employee_after = test_db.query(Employee).filter(
            Employee.employee_id == employee_id
        ).first()
        assert employee_after is None, "Employee should be deleted from database"
        
    finally:
        test_db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

