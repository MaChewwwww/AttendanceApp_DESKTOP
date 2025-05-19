from sqlalchemy import create_engine
from models import Base
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define absolute path for the database file (same as in db.py)
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "attendance_app.db")

# Get database path from environment variable or use default
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB_PATH)

# Ensure directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Create SQLite engine
engine = create_engine(f"sqlite:///{DB_PATH}")

# Create all tables
Base.metadata.create_all(bind=engine)

print(f"Database created at: {DB_PATH}")