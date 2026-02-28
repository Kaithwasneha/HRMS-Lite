"""
Database configuration and session management for HRMS Lite.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_database_url():
    # Option 1: Try building from individual Railway variables (most reliable)
    host = os.getenv("MYSQLHOST")
    port = os.getenv("MYSQLPORT", "3306")
    user = os.getenv("MYSQLUSER")
    password = os.getenv("MYSQLPASSWORD")
    database = os.getenv("MYSQLDATABASE")

    if all([host, user, password, database]):
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    # Option 2: Try DATABASE_URL env var
    url = os.getenv("DATABASE_URL")
    if url:
        if url.startswith("mysql://"):
            url = url.replace("mysql://", "mysql+pymysql://", 1)
        return url

    # Option 3: Try MYSQL_URL env var
    url = os.getenv("MYSQL_URL")
    if url:
        if url.startswith("mysql://"):
            url = url.replace("mysql://", "mysql+pymysql://", 1)
        return url

    # Fallback: local development
    return "mysql+pymysql://root:password@localhost:3306/hrms_lite"

DATABASE_URL = get_database_url()

print(f"[DB] Connecting to: {DATABASE_URL}")  # helpful for debugging in Railway logs

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    Should be called on application startup.
    """
    Base.metadata.create_all(bind=engine)