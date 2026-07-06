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

DB_FILE = "employee_dtr.db"
DB_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(
    DB_URL, 
    echo=False, 
    connect_args={"check_same_thread": False}
)

# Added expire_on_commit=False to fix the DetachedInstanceError
SessionFactory = sessionmaker(
    bind=engine, 
    autoflush=False, 
    autocommit=False,
    expire_on_commit=False 
)

SessionLocal = scoped_session(SessionFactory)


def hash_password(password: str) -> str:
    """Hashes a password using SHA-256 for secure storage."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def init_db():
    """
    Creates all database tables if they don't exist.
    Seeds the initial Settings, including the default admin password.
    """
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        settings = session.query(Settings).first()
        if not settings:
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