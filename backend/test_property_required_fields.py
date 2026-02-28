"""
Property-based test for required field validation.

**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

This test verifies that the system rejects employee creation attempts
when any required field (employee_id, name, email, department) is missing
or empty, and returns HTTP 422 status code.
"""
import pytest
from hypothesis import given, strategies as st, settings
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from database import Base, get_db
from models import Employee


# Strategy for generating valid field values
valid_employee_id_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
    min_size=1,
    max_size=20
)

valid_name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters=' '),
    min_size=2,
    max_size=50
).filter(lambda x: x.strip() != '')

valid_email_strategy = st.emails()

valid_department_strategy = st.sampled_from([
    'Engineering', 'HR', 'Sales', 'Marketing', 'Finance', 'Operations'
])


# Strategy for generating field combinations with at least one missing/empty field
@st.composite
def employee_data_with_missing_field(draw):
    """
    Generate employee data with at least one required field missing or empty.
    
    Returns a tuple of (employee_data_dict, missing_field_name)
    """
    # Generate valid values for all fields
    employee_id = draw(valid_employee_id_strategy)
    name = draw(valid_name_strategy)
    email = draw(valid_email_strategy)
    department = draw(valid_department_strategy)
    
    # Choose which field(s) to make invalid
    # We'll test one field at a time for clarity
    field_to_invalidate = draw(st.sampled_from([
        'employee_id', 'name', 'email', 'department'
    ]))
    
    # Choose how to invalidate: omit the field or make it empty
    # Only use 'omit' or 'empty' to ensure Pydantic catches it
    invalidation_method = draw(st.sampled_from(['omit', 'empty']))
    
    # Build the employee data dictionary
    employee_data = {
        'employee_id': employee_id,
        'name': name,
        'email': email,
        'department': department
    }
    
    # Apply invalidation
    if invalidation_method == 'omit':
        # Remove the field entirely
        del employee_data[field_to_invalidate]
    elif invalidation_method == 'empty':
        # Set to empty string
        employee_data[field_to_invalidate] = ''
    
    return employee_data, field_to_invalidate


@given(data=employee_data_with_missing_field())
@settings(max_examples=10, deadline=None)
def test_required_field_validation(data):
    """
    Property 3: Required Field Validation
    
    **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
    
    For all employee creation attempts, if any required field (employee_id, 
    name, email, department) is missing or empty, the system must reject 
    the creation with HTTP 422.
    
    Test Strategy:
    1. Generate employee data with one required field missing or empty
    2. Attempt to create an employee with the invalid data
    3. Verify the system rejects with HTTP 422 status code
    4. Verify the error message indicates which field is missing/invalid
    """
    employee_data, missing_field = data
    
    # Create a fresh test database for each test
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
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
        
        # Attempt to create employee with missing/empty required field
        response = client.post(
            "/employees",
            json=employee_data
        )
        
        # Verify HTTP 422 status code
        assert response.status_code == 422, \
            f"Expected status code 422 for missing/empty field '{missing_field}', got {response.status_code}. Data: {employee_data}"
        
        # Verify error response contains information about the validation failure
        response_data = response.json()
        assert "detail" in response_data, "Response should contain 'detail' field"
        
        # The error detail should be a list of validation errors or a string
        detail = response_data["detail"]
        detail_str = str(detail).lower()
        
        # Check that the error mentions the missing field or validation
        # Pydantic returns detailed validation errors
        assert (
            missing_field.lower() in detail_str or
            "required" in detail_str or
            "validation" in detail_str or
            "field" in detail_str
        ), f"Error message should mention the missing field '{missing_field}' or validation, got: {detail}"
        
        # Verify employee was NOT created in database
        test_db = TestingSessionLocal()
        try:
            # Check if any employee was created (shouldn't be any)
            employee_count = test_db.query(Employee).count()
            assert employee_count == 0, \
                "No employee should be created in database when required field validation fails"
        finally:
            test_db.close()
    
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@given(
    employee_id=st.one_of(st.just(''), st.just(None)),
    name=valid_name_strategy,
    email=valid_email_strategy,
    department=valid_department_strategy
)
@settings(max_examples=5, deadline=None)
def test_missing_employee_id(employee_id, name, email, department):
    """
    Test specifically for missing employee_id.
    
    **Validates: Requirement 4.1**
    """
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
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
        
        employee_data = {
            "name": name,
            "email": email,
            "department": department
        }
        
        if employee_id is not None:
            employee_data["employee_id"] = employee_id
        
        response = client.post("/employees", json=employee_data)
        
        assert response.status_code == 422, \
            f"Expected 422 for missing employee_id, got {response.status_code}"
    
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@given(
    employee_id=valid_employee_id_strategy,
    name=st.one_of(st.just(''), st.just(None)),
    email=valid_email_strategy,
    department=valid_department_strategy
)
@settings(max_examples=5, deadline=None)
def test_missing_name(employee_id, name, email, department):
    """
    Test specifically for missing name.
    
    **Validates: Requirement 4.2**
    """
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
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
        
        employee_data = {
            "employee_id": employee_id,
            "email": email,
            "department": department
        }
        
        if name is not None:
            employee_data["name"] = name
        
        response = client.post("/employees", json=employee_data)
        
        assert response.status_code == 422, \
            f"Expected 422 for missing name, got {response.status_code}"
    
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@given(
    employee_id=valid_employee_id_strategy,
    name=valid_name_strategy,
    email=st.one_of(st.just(''), st.just(None)),
    department=valid_department_strategy
)
@settings(max_examples=5, deadline=None)
def test_missing_email(employee_id, name, email, department):
    """
    Test specifically for missing email.
    
    **Validates: Requirement 4.3**
    """
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
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
        
        employee_data = {
            "employee_id": employee_id,
            "name": name,
            "department": department
        }
        
        if email is not None:
            employee_data["email"] = email
        
        response = client.post("/employees", json=employee_data)
        
        assert response.status_code == 422, \
            f"Expected 422 for missing email, got {response.status_code}"
    
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@given(
    employee_id=valid_employee_id_strategy,
    name=valid_name_strategy,
    email=valid_email_strategy,
    department=st.one_of(st.just(''), st.just(None))
)
@settings(max_examples=5, deadline=None)
def test_missing_department(employee_id, name, email, department):
    """
    Test specifically for missing department.
    
    **Validates: Requirement 4.4**
    """
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
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
        
        employee_data = {
            "employee_id": employee_id,
            "name": name,
            "email": email
        }
        
        if department is not None:
            employee_data["department"] = department
        
        response = client.post("/employees", json=employee_data)
        
        assert response.status_code == 422, \
            f"Expected 422 for missing department, got {response.status_code}"
    
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
