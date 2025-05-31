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

        # Create admin users
        admin_users = [
            {
                "first_name": "System",
                "last_name": "Administrator",
                "email": "admin@pup.edu.ph",
                "birthday": date(1990, 1, 1),
                "password_hash": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "contact_number": "09123456789",
                "role": "Admin",
                "verified": 1,  # Admin is automatically verified
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "first_name": "Super",
                "last_name": "Admin",
                "email": "superadmin@pup.edu.ph",
                "birthday": date(1985, 5, 15),
                "password_hash": bcrypt.hashpw("superadmin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                "contact_number": "09987654321",
                "role": "Admin",
                "verified": 1,  # Admin is automatically verified
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]

        for admin_data in admin_users:
            admin_user = User(
                first_name=admin_data["first_name"],
                last_name=admin_data["last_name"],
                email=admin_data["email"],
                birthday=admin_data["birthday"],
                password_hash=admin_data["password_hash"],
                contact_number=admin_data["contact_number"],
                role=admin_data["role"],
                verified=admin_data["verified"],
                created_at=admin_data["created_at"],
                updated_at=admin_data["updated_at"]
            )
            session.add(admin_user)

        session.commit()
        logger.info("Admin users seeded successfully")

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
