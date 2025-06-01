import sqlite3
import bcrypt
import random
from datetime import datetime, timedelta

# Database path
DB_PATH = "database.db"

def get_connection():
    """Create and return a new database connection."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def seed_statuses():
    """Seed status data"""
    conn = get_connection()
    cursor = conn.cursor()
    
    current_time = datetime.now().isoformat()
    
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
    
    try:
        for name, description, user_type in all_statuses:
            # Check if status already exists
            cursor.execute("SELECT id FROM statuses WHERE name = ? AND user_type = ?", (name, user_type))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO statuses (name, description, user_type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, description, user_type, current_time, current_time))
        
        conn.commit()
        print("✓ Status data seeded successfully")
        
    except Exception as e:
        print(f"✗ Error seeding statuses: {e}")
        conn.rollback()
    finally:
        conn.close()

def seed_programs_and_sections():
    """Seed programs and sections"""
    conn = get_connection()
    cursor = conn.cursor()
    
    current_time = datetime.now().isoformat()
    
    try:
        # Programs
        programs = [
            ("Bachelor of Science in Information Technology", "BSIT Program"),
            ("Bachelor of Science in Computer Science", "BSCS Program"),
            ("Bachelor of Science in Information Systems", "BSIS Program")
        ]
        
        program_ids = {}
        for name, description in programs:
            cursor.execute("SELECT id FROM programs WHERE name = ?", (name,))
            existing = cursor.fetchone()
            if not existing:
                cursor.execute("""
                    INSERT INTO programs (name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (name, description, current_time, current_time))
                program_ids[name] = cursor.lastrowid
            else:
                program_ids[name] = existing['id']
        
        # Sections for each program and year level
        sections = []
        for program_name, program_id in program_ids.items():
            for year in range(1, 5):  # Years 1-4
                for section_num in range(1, 3):  # Sections 1-2
                    section_name = f"{year}-{section_num}"
                    sections.append((section_name, program_id))
        
        for section_name, program_id in sections:
            cursor.execute("SELECT id FROM sections WHERE name = ? AND course_id = ?", (section_name, program_id))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO sections (name, course_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (section_name, program_id, current_time, current_time))
        
        conn.commit()
        print("✓ Programs and sections seeded successfully")
        
    except Exception as e:
        print(f"✗ Error seeding programs and sections: {e}")
        conn.rollback()
    finally:
        conn.close()

def seed_users():
    """Seed sample users with realistic data and status assignments"""
    conn = get_connection()
    cursor = conn.cursor()
    
    current_time = datetime.now().isoformat()
    
    try:
        # Get status IDs
        cursor.execute("SELECT id, name, user_type FROM statuses")
        statuses = cursor.fetchall()
        student_statuses = [s for s in statuses if s['user_type'] == 'student']
        faculty_statuses = [s for s in statuses if s['user_type'] == 'faculty']
        
        # Get section IDs
        cursor.execute("SELECT id, name FROM sections")
        sections = cursor.fetchall()
        
        # Create admin user first
        admin_email = "admin@university.edu"
        cursor.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
        if not cursor.fetchone():
            admin_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            admin_status = random.choice([s for s in faculty_statuses if s['name'] == 'Active'])
            
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, birthday, password_hash, contact_number, role, status_id, verified, isDeleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("System", "Administrator", admin_email, "1990-01-01", admin_password.decode('utf-8'), "+1234567890", "admin", admin_status['id'], 1, 0, current_time, current_time))
            
            admin_id = cursor.lastrowid
            
            # Create faculty record for admin
            cursor.execute("""
                INSERT INTO faculties (user_id, employee_number)
                VALUES (?, ?)
            """, (admin_id, "EMP001"))
            
            print("✓ Admin user created (admin@university.edu / admin123)")
        
        # Sample student data
        student_names = [
            ("John", "Doe"), ("Jane", "Smith"), ("Michael", "Johnson"), ("Emily", "Brown"),
            ("David", "Wilson"), ("Sarah", "Davis"), ("Robert", "Miller"), ("Lisa", "Garcia"),
            ("James", "Martinez"), ("Maria", "Rodriguez"), ("William", "Lopez"), ("Jennifer", "Gonzalez"),
            ("Richard", "Anderson"), ("Linda", "Taylor"), ("Charles", "Thomas"), ("Patricia", "Moore"),
            ("Christopher", "Jackson"), ("Barbara", "Martin"), ("Daniel", "Lee"), ("Nancy", "Perez")
        ]
        
        # Create students
        student_counter = 1
        for i, (first_name, last_name) in enumerate(student_names):
            email = f"{first_name.lower()}.{last_name.lower()}@student.university.edu"
            
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                continue
                
            password = bcrypt.hashpw("student123".encode('utf-8'), bcrypt.gensalt())
            birthday = (datetime.now() - timedelta(days=random.randint(6570, 10950))).strftime("%Y-%m-%d")  # Age 18-30
            contact = f"+639{random.randint(100000000, 999999999)}"
            
            # Assign status with realistic distribution
            status_weights = {
                'Enrolled': 0.75,  # 75% enrolled
                'Graduated': 0.15,  # 15% graduated
                'Dropout': 0.05,   # 5% dropout
                'On Leave': 0.03,  # 3% on leave
                'Suspended': 0.02  # 2% suspended
            }
            
            status_choice = random.choices(
                student_statuses,
                weights=[status_weights.get(s['name'], 0.01) for s in student_statuses],
                k=1
            )[0]
            
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, birthday, password_hash, contact_number, role, status_id, verified, isDeleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (first_name, last_name, email, birthday, password.decode('utf-8'), contact, "student", status_choice['id'], 1, 0, current_time, current_time))
            
            user_id = cursor.lastrowid
            student_number = f"2024{str(student_counter).zfill(4)}"
            section = random.choice(sections)
            
            cursor.execute("""
                INSERT INTO students (user_id, student_number, section)
                VALUES (?, ?, ?)
            """, (user_id, student_number, section['id']))
            
            student_counter += 1
        
        # Sample faculty data
        faculty_names = [
            ("Dr. Alice", "Johnson"), ("Prof. Robert", "Williams"), ("Dr. Carol", "Brown"),
            ("Prof. Michael", "Davis"), ("Dr. Susan", "Miller"), ("Prof. James", "Wilson"),
            ("Dr. Linda", "Moore"), ("Prof. David", "Taylor")
        ]
        
        # Create faculty
        faculty_counter = 2  # Start from 2 since admin is EMP001
        for first_name, last_name in faculty_names:
            email = f"{first_name.lower().replace('dr. ', '').replace('prof. ', '')}.{last_name.lower()}@faculty.university.edu"
            
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                continue
                
            password = bcrypt.hashpw("faculty123".encode('utf-8'), bcrypt.gensalt())
            birthday = (datetime.now() - timedelta(days=random.randint(10950, 21900))).strftime("%Y-%m-%d")  # Age 30-60
            contact = f"+639{random.randint(100000000, 999999999)}"
            
            # Assign status with realistic distribution for faculty
            status_weights = {
                'Active': 0.70,      # 70% active
                'Tenured': 0.15,     # 15% tenured
                'Tenure Track': 0.10, # 10% tenure track
                'Probationary': 0.03, # 3% probationary
                'On Leave': 0.02     # 2% on leave
            }
            
            status_choice = random.choices(
                faculty_statuses,
                weights=[status_weights.get(s['name'], 0.01) for s in faculty_statuses],
                k=1
            )[0]
            
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, birthday, password_hash, contact_number, role, status_id, verified, isDeleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (first_name, last_name, email, birthday, password.decode('utf-8'), contact, "faculty", status_choice['id'], 1, 0, current_time, current_time))
            
            user_id = cursor.lastrowid
            employee_number = f"EMP{str(faculty_counter).zfill(3)}"
            
            cursor.execute("""
                INSERT INTO faculties (user_id, employee_number)
                VALUES (?, ?)
            """, (user_id, employee_number))
            
            faculty_counter += 1
        
        conn.commit()
        print(f"✓ Users seeded successfully")
        print(f"  - Students: {len(student_names)} (Password: student123)")
        print(f"  - Faculty: {len(faculty_names)} (Password: faculty123)")
        
    except Exception as e:
        print(f"✗ Error seeding users: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """Run all seeders"""
    print("🌱 Starting database seeding...")
    
    seed_statuses()
    seed_programs_and_sections()
    seed_users()
    
    print("\n🎉 Database seeding completed!")
    print("\nLogin credentials:")
    print("Admin: admin@university.edu / admin123")
    print("Students: [firstname].[lastname]@student.university.edu / student123")
    print("Faculty: [firstname].[lastname]@faculty.university.edu / faculty123")

if __name__ == "__main__":
    main()
