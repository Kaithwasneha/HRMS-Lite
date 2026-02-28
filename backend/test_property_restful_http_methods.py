"""
Property-based test for RESTful HTTP methods.

**Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6**

This test verifies that all API endpoints use the correct HTTP methods
(POST for creation, GET for retrieval, DELETE for deletion) and return
appropriate status codes for success and error conditions.
"""
import pytest
from hypothesis import given, strategies as st, settings
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch
import sys
import os
from datetime import date, timedelta

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from database import Base, get_db
from models import Employee, Attendance


# Strategy for generating valid employee data
employee_id_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
    min_size=1,
    max_size=20
)

name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters=' '),
    min_size=2,
    max_size=50
).filter(lambda x: x.strip() != '')

# Generate valid email addresses
email_strategy = st.builds(
    lambda local, domain: f"{local}@{domain}",
    local=st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._%+-',
        min_size=1,
        max_size=20
    ).filter(lambda x: x and x[0].isalnum() and x[-1].isalnum()),
    domain=st.builds(
        lambda name, tld: f"{name}.{tld}",
        name=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
            min_size=1,
            max_size=20
        ).filter(lambda x: x and x[0].isalnum() and x[-1].isalnum()),
        tld=st.sampled_from(['com', 'org', 'net', 'edu', 'gov'])
    )
)

department_strategy = st.sampled_from([
    'Engineering', 'HR', 'Sales', 'Marketing', 'Finance', 'Operations'
])

# Strategy for attendance status
status_strategy = st.sampled_from(['Present', 'Absent'])

# Strategy for dates (within reasonable range)
date_strategy = st.dates(
    min_value=date.today() - timedelta(days=365),
    max_value=date.today() + timedelta(days=30)
)


@given(
    employee_id=employee_id_strategy,
    name=name_strategy,
    email=email_strategy,
    department=department_strategy,
    attendance_status=status_strategy,
    attendance_date=date_strategy
)
@settings(max_examples=10, deadline=None)
def test_restful_http_methods(employee_id, name, email, department, attendance_status, attendance_date):
    """
    Property 7: RESTful HTTP Methods
    
    **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6**
    
    All API endpoints must use the correct HTTP methods (POST for creation,
    GET for retrieval, DELETE for deletion) and return appropriate status codes.
    
    Test Strategy:
    1. Verify POST /employees creates employee and returns 201
    2. Verify GET /employees retrieves employees and returns 200
    3. Verify POST /attendance creates attendance and returns 201
    4. Verify GET /attendance/{employee_id} retrieves attendance and returns 200
    5. Verify DELETE /employees/{employee_id} deletes employee and returns 204
    6. Verify appropriate error codes (404, 409, 422) for error conditions
    """
    # Create a fresh test database for each test
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
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
    
    # Mock init_db to prevent startup event from interfering
    with patch('main.init_db'):
        try:
            client = TestClient(app)
            
            # Test 1: POST /employees should create employee and return 201 (Requirement 7.1)
            employee_data = {
                "employee_id": employee_id,
                "name": name,
                "email": email,
                "department": department
            }
            
            response = client.post("/employees", json=employee_data)
            assert response.status_code == 201, \
                f"POST /employees should return 201 Created, got {response.status_code}"
            
            response_data = response.json()
            assert response_data["employee_id"] == employee_id, \
                "Response should contain created employee data"
            
            # Test 2: GET /employees should retrieve employees and return 200 (Requirement 7.2)
            response = client.get("/employees")
            assert response.status_code == 200, \
                f"GET /employees should return 200 OK, got {response.status_code}"
            
            employees = response.json()
            assert isinstance(employees, list), "GET /employees should return a list"
            assert len(employees) >= 1, "Should have at least one employee"
            assert any(emp["employee_id"] == employee_id for emp in employees), \
                "Created employee should be in the list"
            
            # Test 3: POST /attendance should create attendance and return 201 (Requirement 7.4)
            attendance_data = {
                "employee_id": employee_id,
                "date": attendance_date.isoformat(),
                "status": attendance_status
            }
            
            response = client.post("/attendance", json=attendance_data)
            assert response.status_code == 201, \
                f"POST /attendance should return 201 Created, got {response.status_code}"
            
            response_data = response.json()
            assert response_data["employee_id"] == employee_id, \
                "Response should contain created attendance data"
            assert response_data["status"] == attendance_status, \
                "Response should contain correct status"
            
            # Test 4: GET /attendance/{employee_id} should retrieve attendance and return 200 (Requirement 7.5)
            response = client.get(f"/attendance/{employee_id}")
            assert response.status_code == 200, \
                f"GET /attendance/{{employee_id}} should return 200 OK, got {response.status_code}"
            
            attendance_records = response.json()
            assert isinstance(attendance_records, list), \
                "GET /attendance/{employee_id} should return a list"
            assert len(attendance_records) >= 1, "Should have at least one attendance record"
            assert any(
                att["employee_id"] == employee_id and att["status"] == attendance_status
                for att in attendance_records
            ), "Created attendance should be in the list"
            
            # Test 5: DELETE /employees/{employee_id} should delete employee and return 204 (Requirement 7.3)
            response = client.delete(f"/employees/{employee_id}")
            assert response.status_code == 204, \
                f"DELETE /employees/{{employee_id}} should return 204 No Content, got {response.status_code}"
            
            # Verify employee is deleted
            response = client.get("/employees")
            employees = response.json()
            assert not any(emp["employee_id"] == employee_id for emp in employees), \
                "Deleted employee should not be in the list"
            
            # Test 6: Error conditions should return appropriate status codes (Requirement 7.6)
            
            # 6a: GET /attendance/{employee_id} for non-existent employee should return 404
            response = client.get(f"/attendance/{employee_id}")
            assert response.status_code == 404, \
                f"GET /attendance/{{employee_id}} for non-existent employee should return 404, got {response.status_code}"
            
            # 6b: DELETE /employees/{employee_id} for non-existent employee should return 404
            response = client.delete(f"/employees/{employee_id}")
            assert response.status_code == 404, \
                f"DELETE /employees/{{employee_id}} for non-existent employee should return 404, got {response.status_code}"
            
            # 6c: POST /employees with duplicate employee_id should return 409
            # First create an employee
            response = client.post("/employees", json=employee_data)
            assert response.status_code == 201, "First employee creation should succeed"
            
            # Try to create duplicate
            response = client.post("/employees", json=employee_data)
            assert response.status_code == 409, \
                f"POST /employees with duplicate employee_id should return 409 Conflict, got {response.status_code}"
            
            # 6d: POST /employees with invalid email should return 422
            invalid_employee_data = {
                "employee_id": employee_id + "_invalid",
                "name": name,
                "email": "invalid-email",  # Invalid email format
                "department": department
            }
            response = client.post("/employees", json=invalid_employee_data)
            assert response.status_code == 422, \
                f"POST /employees with invalid email should return 422 Unprocessable Entity, got {response.status_code}"
            
            # 6e: POST /attendance with invalid status should return 422
            invalid_attendance_data = {
                "employee_id": employee_id,
                "date": attendance_date.isoformat(),
                "status": "InvalidStatus"  # Invalid status
            }
            response = client.post("/attendance", json=invalid_attendance_data)
            assert response.status_code == 422, \
                f"POST /attendance with invalid status should return 422 Unprocessable Entity, got {response.status_code}"
            
            # 6f: POST /attendance for non-existent employee should return 404
            non_existent_attendance_data = {
                "employee_id": employee_id + "_nonexistent",
                "date": attendance_date.isoformat(),
                "status": attendance_status
            }
            response = client.post("/attendance", json=non_existent_attendance_data)
            assert response.status_code == 404, \
                f"POST /attendance for non-existent employee should return 404, got {response.status_code}"
        
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(bind=engine)
            engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
