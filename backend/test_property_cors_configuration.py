"""
Property-based test for CORS configuration.

**Validates: Requirements 13.4**

This test verifies that the backend accepts requests from configured frontend
origins (localhost:5173 and FRONTEND_URL environment variable) and properly
sets CORS headers in responses.
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


# Strategy for generating various origin URLs
allowed_origin_strategy = st.sampled_from([
    "http://localhost:5173",  # Default development origin
])

# Strategy for generating disallowed origins
disallowed_origin_strategy = st.sampled_from([
    "http://localhost:3000",
    "http://localhost:8080",
    "https://evil-site.com",
    "https://malicious.org",
    "http://random-domain.net",
])


@given(allowed_origin=allowed_origin_strategy)
@settings(max_examples=5, deadline=None)
def test_cors_allows_configured_origins(allowed_origin):
    """
    Property 8: CORS Configuration - Allowed Origins
    
    **Validates: Requirements 13.4**
    
    The backend must accept requests from configured frontend origins
    (localhost:5173 and FRONTEND_URL environment variable) and include
    proper CORS headers in responses.
    
    Test Strategy:
    1. Send request with allowed Origin header
    2. Verify response includes Access-Control-Allow-Origin header
    3. Verify Access-Control-Allow-Origin matches the request origin
    4. Verify other CORS headers are present (credentials, methods, headers)
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
            
            # Test with allowed origin
            headers = {"Origin": allowed_origin}
            response = client.get("/", headers=headers)
            
            # Verify CORS headers are present
            assert "access-control-allow-origin" in response.headers, \
                f"Response should include Access-Control-Allow-Origin header for allowed origin {allowed_origin}"
            
            assert response.headers["access-control-allow-origin"] == allowed_origin, \
                f"Access-Control-Allow-Origin should match request origin {allowed_origin}, " \
                f"got {response.headers.get('access-control-allow-origin')}"
            
            # Verify other CORS headers
            assert "access-control-allow-credentials" in response.headers, \
                "Response should include Access-Control-Allow-Credentials header"
            
            assert response.headers["access-control-allow-credentials"] == "true", \
                "Access-Control-Allow-Credentials should be 'true'"
        
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(bind=engine)
            engine.dispose()


@given(disallowed_origin=disallowed_origin_strategy)
@settings(max_examples=5, deadline=None)
def test_cors_rejects_unconfigured_origins(disallowed_origin):
    """
    Property 8: CORS Configuration - Disallowed Origins
    
    **Validates: Requirements 13.4**
    
    The backend must NOT include CORS headers for requests from origins
    that are not in the configured list.
    
    Test Strategy:
    1. Send request with disallowed Origin header
    2. Verify response does NOT include Access-Control-Allow-Origin header
       OR the header does not match the request origin
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
            
            # Test with disallowed origin
            headers = {"Origin": disallowed_origin}
            response = client.get("/", headers=headers)
            
            # Verify CORS headers are NOT present or do not match the disallowed origin
            if "access-control-allow-origin" in response.headers:
                assert response.headers["access-control-allow-origin"] != disallowed_origin, \
                    f"Access-Control-Allow-Origin should NOT match disallowed origin {disallowed_origin}"
        
        finally:
            app.dependency_overrides.clear()
            Base.metadata.drop_all(bind=engine)
            engine.dispose()


def test_cors_with_frontend_url_env_variable():
    """
    Property 8: CORS Configuration - Environment Variable
    
    **Validates: Requirements 13.4**
    
    The backend must accept requests from the FRONTEND_URL environment variable
    in addition to localhost:5173.
    
    Test Strategy:
    1. Set FRONTEND_URL environment variable
    2. Reload the app to pick up the new configuration
    3. Send request with FRONTEND_URL as Origin
    4. Verify CORS headers are present and correct
    """
    # Set environment variable
    test_frontend_url = "https://test-frontend.vercel.app"
    
    with patch.dict(os.environ, {"FRONTEND_URL": test_frontend_url}):
        # Need to reload the module to pick up the new environment variable
        import importlib
        import main as main_module
        importlib.reload(main_module)
        
        # Create a fresh test database
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
        
        main_module.app.dependency_overrides[get_db] = override_get_db
        
        # Mock init_db to prevent startup event from interfering
        with patch('main.init_db'):
            try:
                client = TestClient(main_module.app)
                
                # Test with FRONTEND_URL origin
                headers = {"Origin": test_frontend_url}
                response = client.get("/", headers=headers)
                
                # Verify CORS headers are present
                assert "access-control-allow-origin" in response.headers, \
                    f"Response should include Access-Control-Allow-Origin header for FRONTEND_URL {test_frontend_url}"
                
                assert response.headers["access-control-allow-origin"] == test_frontend_url, \
                    f"Access-Control-Allow-Origin should match FRONTEND_URL {test_frontend_url}, " \
                    f"got {response.headers.get('access-control-allow-origin')}"
            
            finally:
                main_module.app.dependency_overrides.clear()
                Base.metadata.drop_all(bind=engine)
                engine.dispose()
                
                # Reload main module again to restore original state
                importlib.reload(main_module)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
