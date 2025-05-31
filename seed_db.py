from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Student, Faculty
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import bcrypt
from datetime import datetime, timezone, date

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Use relative path from the current script location
SCRIPT_DIR = Path(__file__).parent  # Directory where seed_db.py is located
DATA_DIR = SCRIPT_DIR / "data"  # data folder relative to script
DEFAULT_DB_PATH = DATA_DIR / "attendance_app.db"

# Get database path from environment variable or use default
DB_PATH = os.getenv("DB_PATH", str(DEFAULT_DB_PATH))

logger.info(f"Seeding database at: {DB_PATH}")

# Create SQLite engine and session
engine = create_engine(f"sqlite:///{DB_PATH}")
Session = sessionmaker(bind=engine)
session = Session()

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def seed_admin_users():
    """Seed admin users"""
    admin_users = [
        {
            "email": "admin@iskolarngbayan.pup.edu.ph",
            "password": "admin123",
            "first_name": "System",
            "last_name": "Administrator",
            "role": "admin",
            "birthday": date(1990, 1, 1),
            "contact_number": "+639123456789"
        }
    ]
    
    for admin_data in admin_users:
        # Check if admin already exists
        existing_admin = session.query(User).filter_by(email=admin_data["email"]).first()
        if existing_admin:
            logger.info(f"Admin {admin_data['email']} already exists, skipping...")
            continue
        
        # Create admin user
        admin_user = User(
            email=admin_data["email"],
            password_hash=hash_password(admin_data["password"]),
            first_name=admin_data["first_name"],
            last_name=admin_data["last_name"],
            role=admin_data["role"],
            birthday=admin_data["birthday"],
            contact_number=admin_data["contact_number"],
            status="active",
            verified=1  # 1 for True
        )
        
        session.add(admin_user)
        logger.info(f"Created admin user: {admin_data['email']}")
    
    session.commit()

def main():
    """Main seeding function"""
    try:
        logger.info("Starting database seeding...")
        
        # Seed admin users only
        logger.info("Seeding admin users...")
        seed_admin_users()
        
        logger.info("Database seeding completed successfully!")
        
        # Print summary
        admin_count = session.query(User).filter_by(role='admin').count()
        
        print(f"\nDatabase seeding completed!")
        print(f"Admin users: {admin_count}")
        
        print(f"\nLogin credentials:")
        print(f"Admin: admin@iskolarngbayan.pup.edu.ph / admin123")
        
    except Exception as e:
        logger.exception(f"Error during database seeding: {str(e)}")
        session.rollback()
        exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    main()
