"""
Database connection and session management.
Handles engine creation, session factory, and database initialization.
"""

import os
import hashlib
import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database.models import Base, Settings

# Define the SQLite database file path
DB_FILE = "employee_dtr.db"
DB_URL = f"sqlite:///{DB_FILE}"

# Create the SQLAlchemy Engine
# connect_args={"check_same_thread": False} is required for SQLite in GUI apps (PySide6)
engine = create_engine(
    DB_URL, 
    echo=False, 
    connect_args={"check_same_thread": False}
)

# Create a configured "Session" factory
SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Use scoped_session for thread safety across the UI
SessionLocal = scoped_session(SessionFactory)


def hash_password(password: str) -> str:
    """Hashes a password using SHA-256 for secure storage."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def init_db():
    """
    Creates all database tables if they don't exist.
    Seeds the initial Settings, including the default admin password.
    """
    # Create tables based on the models
    Base.metadata.create_all(bind=engine)
    
    # Initialize default settings if the table is empty
    session = SessionLocal()
    try:
        settings = session.query(Settings).first()
        if not settings:
            # The default password will be 'admin'
            default_password_hash = hash_password("admin")
            default_settings = Settings(
                admin_password_hash=default_password_hash,
                company_name="Modern Enterprise DTR",
                theme="Light"
            )
            session.add(default_settings)
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error initializing database: {e}")
    finally:
        session.close()


@contextlib.contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    Ensures sessions are automatically committed or rolled back on error, and safely closed.
    
    Usage:
        with get_db_session() as db:
            employees = db.query(Employee).all()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()