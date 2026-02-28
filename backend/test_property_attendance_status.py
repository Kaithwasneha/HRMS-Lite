"""
Property-based test for attendance status validation.

**Validates: Requirements 5.3, 5.4**

This test verifies that the system rejects attendance creation attempts
with invalid status values (anything other than "Present" or "Absent")
and returns HTTP 422 status code.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from database import Base, get_db
from models import Employee, Attendance


# Valid status values
VALID_STATUSES = {"Present", "Absent"}


# Strategy for generating invalid status values
# These are strings that are NOT exactly "Present" or "Absent"
invalid_status_strategy = st.one_of(
    # Case variations (should be rejected - must be exact match)
    st.sampled_from(['present', 'PRESENT', 'Absent', 'ABSENT', 'PrEsEnT', 'aBsEnT']),
    # Similar words
    st.sampled_from(['Presence', 'Absense', 'Attended', 'Missing', 'Here', 'Away']),
    # Empty or whitespace
    st.just(''),
    st.text(alphabet=' \t\n', min_size=1, max_size=10),
    # Random text
    st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters=' -_'),
        min_size=1,
        max_size=20
    ),
    # Numbers
    st.from_regex(r'^\d+$', fullmatch=True),
    # Special characters
    st.text(alphabet='!@#$%^&*()[]{}|;:,.<>?/', min_size=1, max_size=10),
    # Boolean-like values
    st.sampled_from(['true', 'false', 'True', 'False', 'yes', 'no', 'Yes', 'No']),
    # Status with extra spaces
    st.sampled_from([' Present', 'Present ', ' Absent', 'Absent ', '  Present  ']),
    # Null-like strings
    st.sampled_from(['null', 'None', 'undefined', 'N/A', 'NA']),
)


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
    max_value=date.today() + timedelta(days=30)
)


@given(
    employee_id=employee_id_strategy,
    name=name_strategy,
    email=email_strategy,
    attendance_date=date_strategy,
    invalid_status=invalid_status_strategy,
    department=department_strategy
)
@settings(max_examples=10, deadline=None)
def test_attendance_status_validation(
    employee_id,
    name,
    email,
    attendance_date,
    invalid_status,
    department
):
    """
    Property 4: Attendance Status Validation
    
    **Validates: Requirements 5.3, 5.4**
    
    For all attendance creation attempts, if the status is not exactly 
    "Present" or "Absent", the system must reject the creation with HTTP 422.
    
    Test Strategy:
    1. Create a valid employee first
    2. Generate invalid status values (case variations, similar words, random text, etc.)
    3. Attempt to create an attendance record with the invalid status
    4. Verify the system rejects with HTTP 422 status code
    5. Verify the error message indicates status validation failure
    """
    # Ensure the status is actually invalid
    assume(invalid_status not in VALID_STATUSES)
    
    # Create a fresh test database for each test
    # Use shared cache to ensure all connections see the same in-memory database
    engine = create_engine(
        "sqlite:///file:testdb?mode=memory&cache=shared&uri=true",
        echo=False,
        connect_args={"check_same_thread": False, "uri": True}
    )
    
    # Ensure models are loaded before creating tables
    import models  # Force module reload to ensure models are registered
    
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        client = TestClient(app)
        
        # Step 1: Create a valid employee first
        employee_response = client.post(
            "/employees",
            json={
                "employee_id": employee_id,
                "name": name,
                "email": email,
                "department": department
            }
        )
        
        # Skip test if employee creation fails (e.g., invalid email generated)
        if employee_response.status_code != 201:
            return
        
        # Step 2: Attempt to create attendance with invalid status
        response = client.post(
            "/attendance",
            json={
                "employee_id": employee_id,
                "date": attendance_date.isoformat(),
                "status": invalid_status
            }
        )
        
        # Step 3: Verify HTTP 422 status code
        assert response.status_code == 422, \
            f"Expected status code 422 for invalid status '{invalid_status}', got {response.status_code}"
        
        # Step 4: Verify error response contains information about status validation
        response_data = response.json()
        assert "detail" in response_data, "Response should contain 'detail' field"
        
        # The error detail should mention status or validation
        detail_str = str(response_data["detail"]).lower()
        assert (
            "status" in detail_str or
            "validation" in detail_str or
            "literal" in detail_str or
            "input" in detail_str
        ), f"Error message should mention status validation, got: {response_data['detail']}"
        
        # Step 5: Verify attendance was NOT created in database
        test_db = TestingSessionLocal()
        try:
            attendance_in_db = test_db.query(Attendance).filter(
                Attendance.employee_id == employee_id
            ).all()
            assert len(attendance_in_db) == 0, \
                "No attendance record should be created when status validation fails"
        finally:
            test_db.close()
    
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@given(
    employee_id=employee_id_strategy,
    name=name_strategy,
    email=email_strategy,
    attendance_date=date_strategy,
    department=department_strategy
)
@settings(max_examples=5, deadline=None)
def test_valid_status_present(employee_id, name, email, attendance_date, department):
    """
    Verify that "Present" (exact case) is accepted as valid status.
    
    **Validates: Requirement 5.3**
    """
    engine = create_engine(
        "sqlite:///file:testdb?mode=memory&cache=shared&uri=true",
        echo=False,
        connect_args={"check_same_thread": False, "uri": True}
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        client = TestClient(app)
        
        # Create employee
        employee_response = client.post(
            "/employees",
            json={
                "employee_id": employee_id,
                "name": name,
                "email": email,
                "department": department
            }
        )
        
        if employee_response.status_code != 201:
            return
        
        # Create attendance with "Present" status
        response = client.post(
            "/attendance",
            json={
                "employee_id": employee_id,
                "date": attendance_date.isoformat(),
                "status": "Present"
            }
        )
        
        assert response.status_code == 201, \
            f"Expected 201 for valid status 'Present', got {response.status_code}"
    
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@given(
    employee_id=employee_id_strategy,
    name=name_strategy,
    email=email_strategy,
    attendance_date=date_strategy,
    department=department_strategy
)
@settings(max_examples=5, deadline=None)
def test_valid_status_absent(employee_id, name, email, attendance_date, department):
    """
    Verify that "Absent" (exact case) is accepted as valid status.
    
    **Validates: Requirement 5.3**
    """
    engine = create_engine(
        "sqlite:///file:testdb?mode=memory&cache=shared&uri=true",
        echo=False,
        connect_args={"check_same_thread": False, "uri": True}
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        client = TestClient(app)
        
        # Create employee
        employee_response = client.post(
            "/employees",
            json={
                "employee_id": employee_id,
                "name": name,
                "email": email,
                "department": department
            }
        )
        
        if employee_response.status_code != 201:
            return
        
        # Create attendance with "Absent" status
        response = client.post(
            "/attendance",
            json={
                "employee_id": employee_id,
                "date": attendance_date.isoformat(),
                "status": "Absent"
            }
        )
        
        assert response.status_code == 201, \
            f"Expected 201 for valid status 'Absent', got {response.status_code}"
    
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
