from sqlalchemy import create_engine
from models import Base, User, Student, Faculty, Program, Course, Section, Status, OTP_Request, Assigned_Course, Schedule, AttendanceLog  # Import all model classes
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import sqlite3
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Use relative path from the current script location
SCRIPT_DIR = Path(__file__).parent  # Directory where create_db.py is located
DATA_DIR = SCRIPT_DIR / "data"  # data folder relative to script
DEFAULT_DB_PATH = DATA_DIR / "attendance_app.db"

# Get database path from environment variable or use default
DB_PATH = os.getenv("DB_PATH", str(DEFAULT_DB_PATH))

# Also define the remembered credentials file path
REMEMBERED_CREDENTIALS_PATH = DATA_DIR / "remembered_credentials.json"

def seed_statuses(db_path):
    """Seed status data directly into the database"""
    try:
        # Add a small delay to ensure database is fully created
        import time
        time.sleep(0.5)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        current_time = datetime.now().isoformat()
        
        # The statuses table should already exist from SQLAlchemy models
        # Just check if it exists first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='statuses'")
        if not cursor.fetchone():
            logger.error("Statuses table not found!")
            conn.close()
            return False
        
        # Student statuses
        student_statuses = [
            ('Enrolled', 'Currently enrolled student', 'student'),
            ('Graduated', 'Successfully graduated student', 'student'),
            ('Dropout', 'Student who dropped out', 'student'),
            ('On Leave', 'Student on temporary leave', 'student'),
            ('Suspended', 'Temporarily suspended student', 'student')
        ]
        
        # Faculty statuses
        faculty_statuses = [
            ('Active', 'Currently active faculty member', 'faculty'),
            ('Inactive', 'Inactive faculty member', 'faculty'),
            ('Retired', 'Retired faculty member', 'faculty'),
            ('On Leave', 'Faculty member on leave', 'faculty'),
            ('Probationary', 'Faculty member on probation', 'faculty'),
            ('Tenure Track', 'Faculty member on tenure track', 'faculty'),
            ('Tenured', 'Tenured faculty member', 'faculty')
        ]
        
        all_statuses = student_statuses + faculty_statuses
        
        # Use INSERT OR IGNORE to handle duplicates gracefully
        for name, description, user_type in all_statuses:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO statuses (name, description, user_type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, description, user_type, current_time, current_time))
            except sqlite3.IntegrityError:
                # Status already exists, skip it
                logger.info(f"Status '{name}' for {user_type} already exists, skipping")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info("Status data seeded successfully")
        print("Status data seeded successfully")
        
        # Show seeded statuses
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, user_type FROM statuses ORDER BY user_type, name")
        statuses = cursor.fetchall()
        conn.close()
        
        print("\nSeeded statuses:")
        current_type = None
        for name, user_type in statuses:
            if current_type != user_type:
                current_type = user_type
                print(f"\n{user_type.title()} Statuses:")
            print(f"  - {name}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error seeding statuses: {e}")
        print(f"Error seeding statuses: {e}")
        return False

def create_superadmin(db_path):
    """Create a superadmin user"""
    try:
        import bcrypt
        import time
        
        # Add delay to ensure previous operations are complete
        time.sleep(0.5)
        
        conn = sqlite3.connect(db_path, timeout=30)  # Increase timeout
        cursor = conn.cursor()
        
        current_time = datetime.now().isoformat()
        
        # Check if superadmin already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", ("admin@iskolarngbayan.pup.edu.ph",))
        if cursor.fetchone():
            print("Superadmin already exists")
            conn.close()
            return True
        
        # Get the "Active" status for faculty
        cursor.execute("SELECT id FROM statuses WHERE name = 'Active' AND user_type = 'faculty'")
        status_result = cursor.fetchone()
        status_id = status_result[0] if status_result else None
        
        if not status_id:
            logger.warning("No 'Active' status found for faculty, creating superadmin without status")
        
        # Create superadmin user
        admin_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, birthday, password_hash, contact_number, role, status_id, verified, isDeleted, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("System", "Administrator", "admin@iskolarngbayan.pup.edu.ph", "1990-01-01", admin_password.decode('utf-8'), "09123456789", "Admin", status_id, 1, 0, current_time, current_time))
        
        admin_id = cursor.lastrowid
        
        # Create faculty record for admin
        cursor.execute("""
            INSERT INTO faculties (user_id, employee_number)
            VALUES (?, ?)
        """, (admin_id, "EMP001"))
        
        conn.commit()
        conn.close()
        
        logger.info("Superadmin created successfully")
        print("Superadmin created successfully")
        print("  Email: admin@iskolarngbayan.pup.edu.ph")
        print("  Password: admin123")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating superadmin: {e}")
        print(f"Error creating superadmin: {e}")
        return False

# Delete the database file if it exists
if os.path.exists(DB_PATH):
    try:
        logger.info(f"Removing existing database at: {DB_PATH}")
        os.remove(DB_PATH)
        logger.info("Existing database removed successfully")
    except Exception as e:
        logger.error(f"Failed to remove existing database: {str(e)}")
        exit(1)  # Exit if we can't remove the existing database

# Delete the remembered credentials file if it exists
if os.path.exists(REMEMBERED_CREDENTIALS_PATH):
    try:
        logger.info(f"Removing remembered credentials file at: {REMEMBERED_CREDENTIALS_PATH}")
        os.remove(REMEMBERED_CREDENTIALS_PATH)
        logger.info("Remembered credentials file removed successfully")
    except Exception as e:
        logger.warning(f"Failed to remove remembered credentials file: {str(e)}")
        # Don't exit for this - it's not critical

# Ensure directory exists
DATA_DIR.mkdir(exist_ok=True)  # Create data directory if it doesn't exist

logger.info(f"Creating new database at: {DB_PATH}")

# Create SQLite engine
engine = create_engine(f"sqlite:///{DB_PATH}")

# Create all tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Tables in database: {tables}")
    
    if 'users' not in tables:
        logger.error("Users table not found after creation!")
        exit(1)  # Exit if users table wasn't created
    else:
        logger.info("Users table successfully created")
except Exception as e:
    logger.exception(f"Error creating database tables: {str(e)}")
    exit(1)  # Exit if table creation failed

print(f"Database successfully created at: {DB_PATH}")
print(f"Tables created: {', '.join(tables)}")
print("Remembered login credentials cleared")

# Add a delay to ensure all database operations are complete
import time
time.sleep(1)

# Check and add missing columns to existing tables
print("\nChecking for database schema updates...")
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if assigned_courses table has isDeleted column
    cursor.execute("PRAGMA table_info(assigned_courses)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'isDeleted' not in columns:
        cursor.execute("ALTER TABLE assigned_courses ADD COLUMN isDeleted INTEGER DEFAULT 0")
        print("✓ Added isDeleted column to assigned_courses table")
        conn.commit()
    else:
        print("✓ assigned_courses table already has isDeleted column")
    
    conn.close()
    
except Exception as e:
    print(f"Error checking database schema: {e}")

# Seed status data
print("\nSeeding status data...")
if seed_statuses(DB_PATH):
    print("Status seeding completed successfully")
else:
    print("Status seeding failed")

# Create superadmin
print("\nCreating superadmin...")
if create_superadmin(DB_PATH):
    print("Superadmin creation completed successfully")
else:
    print("Superadmin creation failed")

print("\nDatabase initialization completed!")
print("\nYour clean database is ready with:")
print("- Status tables for students and faculty")
print("- Superadmin account (admin@iskolarngbayan.pup.edu.ph / admin123)")
print("\nTo add sample data, run:")
print("python create_seed_users.py")