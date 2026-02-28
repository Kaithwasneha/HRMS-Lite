"""
Property-based test for email format validation.

**Validates: Requirements 3.1, 3.2**

This test verifies that the system rejects employee creation attempts
with invalid email formats and returns HTTP 422 status code.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import re
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from database import Base, get_db
from models import Employee


# Email regex pattern from design document
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


def is_valid_email(email: str) -> bool:
    """Check if email matches the required pattern."""
    return bool(re.match(EMAIL_PATTERN, email))


# Strategy for generating invalid emails
# We'll generate strings that don't match the email pattern
invalid_email_strategy = st.one_of(
    # Missing @ symbol
    st.text(alphabet=st.characters(blacklist_characters='@'), min_size=1, max_size=50),
    # Multiple @ symbols
    st.from_regex(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+$', fullmatch=True),
    # Missing domain
    st.from_regex(r'^[a-zA-Z0-9._%+-]+@$', fullmatch=True),
    # Missing local part
    st.from_regex(r'^@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', fullmatch=True),
    # Missing TLD
    st.from_regex(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+$', fullmatch=True),
    # TLD too short (only 1 character)
    st.from_regex(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]$', fullmatch=True),
    # Invalid characters in local part
    st.from_regex(r'^[a-zA-Z0-9._%+-]*[!#$&*()]+[a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', fullmatch=True),
    # Spaces in email
    st.from_regex(r'^[a-zA-Z0-9._%+-]+ [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', fullmatch=True),
    # Empty string
    st.just(''),
    # Just whitespace
    st.text(alphabet=' \t\n', min_size=1, max_size=10),
)


# Strategy for generating valid employee data (except email)
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

department_strategy = st.sampled_from([
    'Engineering', 'HR', 'Sales', 'Marketing', 'Finance', 'Operations'
])


@given(
    employee_id=employee_id_strategy,
    name=name_strategy,
    invalid_email=invalid_email_strategy,
    department=department_strategy
)
@settings(max_examples=10, deadline=None)
def test_email_format_validation(employee_id, name, invalid_email, department):
    """
    Property 2: Email Format Validation
    
    **Validates: Requirements 3.1, 3.2**
    
    For all employee creation attempts, if the email does not match the email 
    regex pattern, the system must reject the creation with HTTP 422.
    
    Test Strategy:
    1. Generate invalid email formats using various patterns
    2. Attempt to create an employee with the invalid email
    3. Verify the system rejects with HTTP 422 status code
    4. Verify the error message indicates email format is invalid
    """
    # Ensure the email is actually invalid according to our pattern
    assume(not is_valid_email(invalid_email))
    
    # Create a fresh test database for each test
    engine = create_engine("sqlite:///:memory:", echo=False)
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
        
        # Attempt to create employee with invalid email
        response = client.post(
            "/employees",
            json={
                "employee_id": employee_id,
                "name": name,
                "email": invalid_email,
                "department": department
            }
        )
        
        # Verify HTTP 422 status code
        assert response.status_code == 422, \
            f"Expected status code 422 for invalid email '{invalid_email}', got {response.status_code}"
        
        # Verify error response contains information about email validation
        response_data = response.json()
        assert "detail" in response_data, "Response should contain 'detail' field"
        
        # The error detail should mention email or validation
        detail_str = str(response_data["detail"]).lower()
        assert "email" in detail_str or "validation" in detail_str, \
            f"Error message should mention email validation, got: {response_data['detail']}"
        
        # Verify employee was NOT created in database
        test_db = TestingSessionLocal()
        try:
            employee_in_db = test_db.query(Employee).filter(
                Employee.employee_id == employee_id
            ).first()
            assert employee_in_db is None, \
                "Employee should not be created in database when email validation fails"
        finally:
            test_db.close()
    
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
