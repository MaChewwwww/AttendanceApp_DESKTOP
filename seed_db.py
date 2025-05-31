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
    try:
        # Check if admin users already exist
        existing_admin = session.query(User).filter_by(role="Admin").first()
        if existing_admin:
            logger.info("Admin users already exist, skipping...")
            return

        # Create admin user
        admin_user_data = {
            "first_name": "Super",
            "last_name": "Admin",
            "email": "admin@iskolarngbayan.pup.edu.ph",
            "birthday": date(1985, 5, 15),
            "password_hash": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "contact_number": "admin123",
            "role": "Admin",
            "verified": 1,  # Admin is automatically verified
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        admin_user = User(
            first_name=admin_user_data["first_name"],
            last_name=admin_user_data["last_name"],
            email=admin_user_data["email"],
            birthday=admin_user_data["birthday"],
            password_hash=admin_user_data["password_hash"],
            contact_number=admin_user_data["contact_number"],
            role=admin_user_data["role"],
            verified=admin_user_data["verified"],
            created_at=admin_user_data["created_at"],
            updated_at=admin_user_data["updated_at"]
        )
        session.add(admin_user)

        session.commit()
        logger.info("Admin user seeded successfully")

    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding admin users: {str(e)}")
        raise

def main():
    """Main seeding function"""
    try:
        logger.info("Starting database seeding...")
        
        # Seed admin users only
        logger.info("Seeding admin users...")
        seed_admin_users()
        
        logger.info("Database seeding completed successfully!")
        
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
