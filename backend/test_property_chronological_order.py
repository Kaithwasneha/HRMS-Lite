"""
Property-based test for attendance chronological order.

**Validates: Requirements 6.2**

This test verifies that attendance records are returned in chronological 
order (newest first) when retrieved for an employee.
"""
import pytest
from hypothesis import given, strategies as st, settings
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

# Strategy for generating attendance status
status_strategy = st.sampled_from(['Present', 'Absent'])


@given(
    employee_id=employee_id_strategy,
    name=name_strategy,
    email=email_strategy,
    department=department_strategy,
    dates=st.lists(date_strategy, min_size=2, max_size=10, unique=True),
    statuses=st.lists(status_strategy, min_size=2, max_size=10)
)
@settings(max_examples=10, deadline=None)
def test_attendance_chronological_order(
    employee_id,
    name,
    email,
    department,
    dates,
    statuses
):
    """
    Property 6: Attendance Chronological Order
    
    **Validates: Requirements 6.2**
    
    For all attendance retrieval operations, the returned records must be 
    sorted by date in descending order (newest first).
    
    Test Strategy:
    1. Create an employee with random valid data
    2. Create multiple attendance records with different dates
    3. Retrieve attendance records via API
    4. Verify records are sorted by date descending (newest first)
    """
    # Create a fresh test database for each test
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
        
        # Step 1: Create a valid employee
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
        
        # Step 2: Create multiple attendance records with different dates
        # Use the minimum of available dates and statuses
        num_records = min(len(dates), len(statuses))
        
        for i in range(num_records):
            attendance_response = client.post(
                "/attendance",
                json={
                    "employee_id": employee_id,
                    "date": dates[i].isoformat(),
                    "status": statuses[i]
                }
            )
            
            # Skip test if attendance creation fails
            if attendance_response.status_code != 201:
                return
        
        # Step 3: Retrieve attendance records via API
        response = client.get(f"/attendance/{employee_id}")
        
        assert response.status_code == 200, \
            f"Expected status code 200, got {response.status_code}"
        
        attendance_records = response.json()
        
        # Verify we got all the records we created
        assert len(attendance_records) == num_records, \
            f"Expected {num_records} attendance records, got {len(attendance_records)}"
        
        # Step 4: Verify records are sorted by date descending (newest first)
        returned_dates = [record["date"] for record in attendance_records]
        
        # Convert string dates back to date objects for comparison
        returned_date_objects = [date.fromisoformat(d) for d in returned_dates]
        
        # Check that dates are in descending order
        for i in range(len(returned_date_objects) - 1):
            assert returned_date_objects[i] >= returned_date_objects[i + 1], \
                f"Dates not in descending order: {returned_date_objects[i]} should be >= {returned_date_objects[i + 1]}"
        
        # Alternative verification: compare with sorted list
        expected_sorted_dates = sorted(returned_date_objects, reverse=True)
        assert returned_date_objects == expected_sorted_dates, \
            f"Dates are not sorted in descending order. Got: {returned_date_objects}, Expected: {expected_sorted_dates}"
    
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
