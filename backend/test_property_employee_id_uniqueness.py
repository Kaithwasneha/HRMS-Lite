"""
Property-based test for employee ID uniqueness.

**Validates: Requirements 2.1, 2.2**

This test verifies that the system rejects employee creation attempts
when an employee_id already exists in the database, and returns HTTP 409
status code with an appropriate error message.
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

# Generate valid email addresses that match the backend validation pattern
# Pattern: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
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


@given(
    employee_id=employee_id_strategy,
    name1=name_strategy,
    name2=name_strategy,
    email1=email_strategy,
    email2=email_strategy,
    department1=department_strategy,
    department2=department_strategy
)
@settings(max_examples=10, deadline=None)
def test_employee_id_uniqueness(employee_id, name1, name2, email1, email2, department1, department2):
    """
    Property 1: Employee ID Uniqueness
    
    **Validates: Requirements 2.1, 2.2**
    
    For all employee creation attempts, if an employee_id already exists in 
    the database, the system must reject the creation with HTTP 409.
    
    Test Strategy:
    1. Generate random employee data with a specific employee_id
    2. Create the first employee successfully
    3. Attempt to create a second employee with the same employee_id but different other fields
    4. Verify the system rejects with HTTP 409 status code
    5. Verify the error message indicates the employee_id is already in use
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
            
            # Create first employee with the employee_id
            first_employee_data = {
                "employee_id": employee_id,
                "name": name1,
                "email": email1,
                "department": department1
            }
            
            response1 = client.post("/employees", json=first_employee_data)
            
            # First creation should succeed with HTTP 201
            assert response1.status_code == 201, \
                f"First employee creation should succeed with 201, got {response1.status_code}. Response: {response1.json()}"
            
            # Verify first employee was created in database
            test_db = TestingSessionLocal()
            try:
                employee_in_db = test_db.query(Employee).filter(
                    Employee.employee_id == employee_id
                ).first()
                assert employee_in_db is not None, \
                    "First employee should be created in database"
                assert employee_in_db.employee_id == employee_id
            finally:
                test_db.close()
            
            # Attempt to create second employee with same employee_id but different other fields
            second_employee_data = {
                "employee_id": employee_id,  # Same employee_id
                "name": name2,  # Different name
                "email": email2,  # Different email
                "department": department2  # Different department
            }
            
            response2 = client.post("/employees", json=second_employee_data)
            
            # Second creation should fail with HTTP 409 (Conflict)
            assert response2.status_code == 409, \
                f"Expected status code 409 for duplicate employee_id '{employee_id}', got {response2.status_code}"
            
            # Verify error response contains information about the duplicate
            response_data = response2.json()
            assert "detail" in response_data, "Response should contain 'detail' field"
            
            # The error detail should mention the employee_id or that it already exists
            detail_str = str(response_data["detail"]).lower()
            assert (
                employee_id.lower() in detail_str or
                "already exists" in detail_str or
                "duplicate" in detail_str or
                "conflict" in detail_str
            ), f"Error message should indicate employee_id already exists, got: {response_data['detail']}"
            
            # Verify only ONE employee exists in database (second was not created)
            test_db = TestingSessionLocal()
            try:
                employee_count = test_db.query(Employee).filter(
                    Employee.employee_id == employee_id
                ).count()
                assert employee_count == 1, \
                    f"Only one employee with employee_id '{employee_id}' should exist, found {employee_count}"
            finally:
                test_db.close()
        
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(bind=engine)
            engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
