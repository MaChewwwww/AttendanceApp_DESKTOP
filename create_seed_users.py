import sqlite3
import bcrypt
from datetime import datetime
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use relative path from the current script location
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
DB_PATH = DATA_DIR / "attendance_app.db"

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_users():
    """Seed the database with sample users"""
    
    if not os.path.exists(DB_PATH):
        logger.error(f"Database not found at: {DB_PATH}")
        logger.error("Please run create_db.py first to create the database")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if users already exist
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            logger.info(f"Database already has {user_count} users. Skipping seeding.")
            conn.close()
            return True
        
        logger.info("Seeding database with sample users...")
        
        current_time = datetime.now().isoformat()
        
        # Sample users data
        users_data = [
            # Admin user
            {
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@school.edu',
                'birthday': '1990-01-01',
                'password': 'admin123',
                'contact_number': '+63912345678',
                'role': 'Admin',
                'verified': 1,
                'user_type': 'admin'
            },
            # Faculty users
            {
                'first_name': 'Dr. Maria',
                'last_name': 'Santos',
                'email': 'maria.santos@school.edu',
                'birthday': '1985-03-15',
                'password': 'faculty123',
                'contact_number': '+63912345679',
                'role': 'Faculty',
                'verified': 1,
                'user_type': 'faculty',
                'employee_number': 'EMP-2019-001'
            },
            {
                'first_name': 'Prof. John',
                'last_name': 'Doe',
                'email': 'john.doe@school.edu',
                'birthday': '1980-07-22',
                'password': 'faculty123',
                'contact_number': '+63912345680',
                'role': 'Faculty',
                'verified': 1,
                'user_type': 'faculty',
                'employee_number': 'EMP-2020-015'
            },
            {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane.smith@school.edu',
                'birthday': '1988-11-30',
                'password': 'faculty123',
                'contact_number': '+63912345681',
                'role': 'Faculty',
                'verified': 1,
                'user_type': 'faculty',
                'employee_number': 'EMP-2018-005'
            },
            # Student users
            {
                'first_name': 'Shadrack',
                'last_name': 'Castro',
                'email': 'shadrack.castro@student.edu',
                'birthday': '2002-05-10',
                'password': 'student123',
                'contact_number': '+63912345682',
                'role': 'Student',
                'verified': 1,
                'user_type': 'student',
                'student_number': '2024-00001',
                'section': 1
            },
            {
                'first_name': 'Jerlee',
                'last_name': 'Alipio',
                'email': 'jerlee.alipio@student.edu',
                'birthday': '2001-09-18',
                'password': 'student123',
                'contact_number': '+63912345683',
                'role': 'Student',
                'verified': 1,
                'user_type': 'student',
                'student_number': '2024-00002',
                'section': 2
            },
            {
                'first_name': 'Steven',
                'last_name': 'Masangcay',
                'email': 'steven.masangcay@student.edu',
                'birthday': '2000-12-25',
                'password': 'student123',
                'contact_number': '+63912345684',
                'role': 'Student',
                'verified': 1,
                'user_type': 'student',
                'student_number': '2024-00003',
                'section': 1
            },
            {
                'first_name': 'John Mathew',
                'last_name': 'Parocha',
                'email': 'john.parocha@student.edu',
                'birthday': '1999-08-14',
                'password': 'student123',
                'contact_number': '+63912345685',
                'role': 'Student',
                'verified': 1,
                'user_type': 'student',
                'student_number': '2024-00004',
                'section': 2
            }
        ]
        
        # Insert users
        for user_data in users_data:
            # Hash password
            hashed_password = hash_password(user_data['password'])
            
            # Insert into users table
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, birthday, password_hash, 
                                 contact_number, role, verified, isDeleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
            """, (
                user_data['first_name'],
                user_data['last_name'],
                user_data['email'],
                user_data['birthday'],
                hashed_password,
                user_data['contact_number'],
                user_data['role'],
                user_data['verified'],
                current_time,
                current_time
            ))
            
            user_id = cursor.lastrowid
            
            # Insert into role-specific tables
            if user_data['user_type'] == 'student':
                cursor.execute("""
                    INSERT INTO students (user_id, student_number, section)
                    VALUES (?, ?, ?)
                """, (user_id, user_data['student_number'], user_data.get('section')))
                
            elif user_data['user_type'] == 'faculty':
                cursor.execute("""
                    INSERT INTO faculties (user_id, employee_number)
                    VALUES (?, ?)
                """, (user_id, user_data['employee_number']))
            
            logger.info(f"Created {user_data['role']}: {user_data['first_name']} {user_data['last_name']} ({user_data['email']})")
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        logger.info("Successfully seeded database with sample users!")
        logger.info("\nLogin credentials:")
        logger.info("Admin: admin@school.edu / admin123")
        logger.info("Faculty: maria.santos@school.edu / faculty123")
        logger.info("Student: shadrack.castro@student.edu / student123")
        
        return True
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("Seeding database with sample users...")
    success = seed_users()
    if success:
        print("\n✅ Database seeded successfully!")
    else:
        print("\n❌ Failed to seed database!")
        exit(1)
