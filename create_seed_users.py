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

def seed_programs_and_courses():
    """Seed programs, courses, and sections"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        logger.info("Creating programs, courses, and sections...")
        
        # Programs data
        programs_data = [
            {
                'name': 'Bachelor of Science in Information Technology',
                'description': 'BSIT - A comprehensive program focusing on information technology and computer systems'
            },
            {
                'name': 'Bachelor of Science in Computer Science',
                'description': 'BSCS - A program emphasizing theoretical foundations of computation and practical software engineering'
            },
            {
                'name': 'Bachelor of Science in Information Systems',
                'description': 'BSIS - A program combining business processes with information technology solutions'
            }
        ]
        
        # Insert programs
        program_ids = {}
        for program_data in programs_data:
            cursor.execute("SELECT id FROM programs WHERE name = ?", (program_data['name'],))
            existing = cursor.fetchone()
            
            if existing:
                program_ids[program_data['name']] = existing[0]
                logger.info(f"Program {program_data['name']} already exists")
                continue
            
            current_time = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO programs (name, description, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (program_data['name'], program_data['description'], current_time, current_time))
            
            program_id = cursor.lastrowid
            program_ids[program_data['name']] = program_id
            logger.info(f"Created program: {program_data['name']} (ID: {program_id})")
        
        # Courses data for each program
        courses_data = [
            # BSIT Courses
            {'name': 'Programming Fundamentals', 'description': 'Introduction to programming concepts', 'program': 'Bachelor of Science in Information Technology'},
            {'name': 'Data Structures and Algorithms', 'description': 'Advanced programming and algorithms', 'program': 'Bachelor of Science in Information Technology'},
            {'name': 'Database Management Systems', 'description': 'Database design and management', 'program': 'Bachelor of Science in Information Technology'},
            {'name': 'Web Development', 'description': 'Frontend and backend web technologies', 'program': 'Bachelor of Science in Information Technology'},
            {'name': 'Network Administration', 'description': 'Computer networking and administration', 'program': 'Bachelor of Science in Information Technology'},
            
            # BSCS Courses
            {'name': 'Computer Programming', 'description': 'Core programming principles', 'program': 'Bachelor of Science in Computer Science'},
            {'name': 'Software Engineering', 'description': 'Software development methodologies', 'program': 'Bachelor of Science in Computer Science'},
            {'name': 'Machine Learning', 'description': 'AI and machine learning fundamentals', 'program': 'Bachelor of Science in Computer Science'},
            {'name': 'Computer Graphics', 'description': 'Graphics programming and visualization', 'program': 'Bachelor of Science in Computer Science'},
            {'name': 'Operating Systems', 'description': 'System software and OS concepts', 'program': 'Bachelor of Science in Computer Science'},
            
            # BSIS Courses
            {'name': 'Business Process Analysis', 'description': 'Analyzing business workflows', 'program': 'Bachelor of Science in Information Systems'},
            {'name': 'Systems Analysis and Design', 'description': 'System development lifecycle', 'program': 'Bachelor of Science in Information Systems'},
            {'name': 'Enterprise Resource Planning', 'description': 'ERP systems implementation', 'program': 'Bachelor of Science in Information Systems'},
            {'name': 'IT Project Management', 'description': 'Managing technology projects', 'program': 'Bachelor of Science in Information Systems'},
            {'name': 'Business Intelligence', 'description': 'Data analytics for business', 'program': 'Bachelor of Science in Information Systems'}
        ]
        
        # Insert courses
        course_ids = {}
        for course_data in courses_data:
            program_id = program_ids[course_data['program']]
            
            cursor.execute("SELECT id FROM courses WHERE name = ? AND program_id = ?", 
                         (course_data['name'], program_id))
            existing = cursor.fetchone()
            
            if existing:
                course_ids[course_data['name']] = existing[0]
                continue
            
            current_time = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO courses (name, description, program_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (course_data['name'], course_data['description'], program_id, current_time, current_time))
            
            course_id = cursor.lastrowid
            course_ids[course_data['name']] = course_id
            logger.info(f"Created course: {course_data['name']} (ID: {course_id})")
        
        # Sections data
        sections_data = [
            # Year 1 sections for each program
            {'name': '1-1', 'program': 'Bachelor of Science in Information Technology'},
            {'name': '1-2', 'program': 'Bachelor of Science in Information Technology'},
            {'name': '1-1', 'program': 'Bachelor of Science in Computer Science'},
            {'name': '1-2', 'program': 'Bachelor of Science in Computer Science'},
            {'name': '1-1', 'program': 'Bachelor of Science in Information Systems'},
            
            # Year 2 sections
            {'name': '2-1', 'program': 'Bachelor of Science in Information Technology'},
            {'name': '2-2', 'program': 'Bachelor of Science in Information Technology'},
            {'name': '2-1', 'program': 'Bachelor of Science in Computer Science'},
            {'name': '2-1', 'program': 'Bachelor of Science in Information Systems'},
            
            # Year 3 sections
            {'name': '3-1', 'program': 'Bachelor of Science in Information Technology'},
            {'name': '3-2', 'program': 'Bachelor of Science in Information Technology'},
            {'name': '3-1', 'program': 'Bachelor of Science in Computer Science'},
            
            # Year 4 sections
            {'name': '4-1', 'program': 'Bachelor of Science in Information Technology'},
            {'name': '4-1', 'program': 'Bachelor of Science in Information Systems'}
        ]
        
        # Insert sections
        section_ids = {}
        for section_data in sections_data:
            program_id = program_ids[section_data['program']]
            section_key = f"{section_data['name']}-{section_data['program']}"
            
            cursor.execute("SELECT id FROM sections WHERE name = ? AND course_id = ?", 
                         (section_data['name'], program_id))
            existing = cursor.fetchone()
            
            if existing:
                section_ids[section_key] = existing[0]
                continue
            
            current_time = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO sections (name, course_id, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (section_data['name'], program_id, current_time, current_time))
            
            section_id = cursor.lastrowid
            section_ids[section_key] = section_id
            logger.info(f"Created section: {section_data['name']} for {section_data['program']} (ID: {section_id})")
        
        conn.commit()
        conn.close()
        
        return True, program_ids, section_ids
        
    except Exception as e:
        logger.error(f"Error creating programs and courses: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False, {}, {}

def seed_users():
    """Seed the database with sample users"""
    
    if not os.path.exists(DB_PATH):
        logger.error(f"Database not found at: {DB_PATH}")
        logger.error("Please run create_db.py first to create the database")
        return False
    
    try:
        # First seed programs, courses, and sections
        success, program_ids, section_ids = seed_programs_and_courses()
        if not success:
            return False
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        logger.info("Creating seed users...")
        
        # Get status IDs for assignments
        cursor.execute("SELECT id, name, user_type FROM statuses")
        statuses = cursor.fetchall()
        
        student_statuses = {s[1]: s[0] for s in statuses if s[2] == 'student'}
        faculty_statuses = {s[1]: s[0] for s in statuses if s[2] == 'faculty'}
        
        logger.info(f"Found statuses - Students: {list(student_statuses.keys())}, Faculty: {list(faculty_statuses.keys())}")
        
        # Sample users data with proper section assignments and status
        users_data = [
            # Admin user 
            {
                'first_name': 'Super',
                'last_name': 'Admin',
                'email': 'admin@admin.com',
                'birthday': '1990-01-01',
                'password': 'admin',
                'contact_number': '+63912345678',
                'role': 'Admin',
                'verified': 1,
                'user_type': 'faculty',
                'employee_number': 'EMP-2024-001',
                'status': 'Active'
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
                'employee_number': 'EMP-2019-001',
                'status': 'Tenured'
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
                'employee_number': 'EMP-2020-015',
                'status': 'Active'
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
                'employee_number': 'EMP-2018-005',
                'status': 'Tenure Track'
            },
            # Student users with program and section assignments
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
                'program': 'Bachelor of Science in Information Technology',
                'section': '1-1',
                'year': '1st Year',
                'status': 'Enrolled'
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
                'program': 'Bachelor of Science in Computer Science',
                'section': '2-1',
                'year': '2nd Year',
                'status': 'Enrolled'
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
                'program': 'Bachelor of Science in Information Technology',
                'section': '3-2',
                'year': '3rd Year',
                'status': 'Enrolled'
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
                'program': 'Bachelor of Science in Information Systems',
                'section': '4-1',
                'year': '4th Year',
                'status': 'Graduated'
            },
            # More students for pagination testing
            {
                'first_name': 'Maria',
                'last_name': 'Garcia',
                'email': 'maria.garcia@student.edu',
                'birthday': '2001-03-12',
                'password': 'student123',
                'contact_number': '+63912345686',
                'role': 'Student',
                'verified': 1,
                'user_type': 'student',
                'student_number': '2024-00005',
                'program': 'Bachelor of Science in Information Technology',
                'section': '1-2',
                'year': '1st Year',
                'status': 'Enrolled'
            },
            {
                'first_name': 'Carlos',
                'last_name': 'Rodriguez',
                'email': 'carlos.rodriguez@student.edu',
                'birthday': '2002-07-20',
                'password': 'student123',
                'contact_number': '+63912345687',
                'role': 'Student',
                'verified': 1,
                'user_type': 'student',
                'student_number': '2024-00006',
                'program': 'Bachelor of Science in Computer Science',
                'section': '1-1',
                'year': '1st Year',
                'status': 'On Leave'
            },
            {
                'first_name': 'Anna',
                'last_name': 'Cruz',
                'email': 'anna.cruz@student.edu',
                'birthday': '2000-11-08',
                'password': 'student123',
                'contact_number': '+63912345688',
                'role': 'Student',
                'verified': 1,
                'user_type': 'student',
                'student_number': '2024-00007',
                'program': 'Bachelor of Science in Information Systems',
                'section': '1-1',
                'year': '1st Year',
                'status': 'Enrolled'
            },
            # Additional students with different statuses for variety
            {
                'first_name': 'Roberto',
                'last_name': 'Fernandez',
                'email': 'roberto.fernandez@student.edu',
                'birthday': '2001-04-15',
                'password': 'student123',
                'contact_number': '+63912345689',
                'role': 'Student',
                'verified': 1,
                'user_type': 'student',
                'student_number': '2024-00008',
                'program': 'Bachelor of Science in Information Technology',
                'section': '2-1',
                'year': '2nd Year',
                'status': 'Suspended'
            },
            {
                'first_name': 'Lisa',
                'last_name': 'Mendoza',
                'email': 'lisa.mendoza@student.edu',
                'birthday': '1999-06-03',
                'password': 'student123',
                'contact_number': '+63912345690',
                'role': 'Student',
                'verified': 1,
                'user_type': 'student',
                'student_number': '2024-00009',
                'program': 'Bachelor of Science in Computer Science',
                'section': '3-1',
                'year': '3rd Year',
                'status': 'Dropout'
            },
            # Additional faculty with different statuses
            {
                'first_name': 'Dr. Patricia',
                'last_name': 'Reyes',
                'email': 'patricia.reyes@school.edu',
                'birthday': '1975-09-12',
                'password': 'faculty123',
                'contact_number': '+63912345691',
                'role': 'Faculty',
                'verified': 1,
                'user_type': 'faculty',
                'employee_number': 'EMP-2015-008',
                'status': 'Retired'
            },
            {
                'first_name': 'Prof. Michael',
                'last_name': 'Torres',
                'email': 'michael.torres@school.edu',
                'birthday': '1982-01-28',
                'password': 'faculty123',
                'contact_number': '+63912345692',
                'role': 'Faculty',
                'verified': 1,
                'user_type': 'faculty',
                'employee_number': 'EMP-2021-012',
                'status': 'Probationary'
            },
            {
                'first_name': 'Dr. Sarah',
                'last_name': 'Villanueva',
                'email': 'sarah.villanueva@school.edu',
                'birthday': '1987-12-05',
                'password': 'faculty123',
                'contact_number': '+63912345693',
                'role': 'Faculty',
                'verified': 1,
                'user_type': 'faculty',
                'employee_number': 'EMP-2022-003',
                'status': 'On Leave'
            }
        ]
        
        # Begin transaction
        conn.execute("BEGIN TRANSACTION")
        
        for user_data in users_data:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (user_data['email'],))
            existing_user = cursor.fetchone()
            
            if existing_user:
                logger.info(f"User {user_data['email']} already exists, skipping...")
                continue
            
            # Hash password
            hashed_pw = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
            
            # Get status ID based on user type and status name
            status_id = None
            if user_data['user_type'] == 'student':
                status_id = student_statuses.get(user_data['status'])
            elif user_data['user_type'] == 'faculty':
                status_id = faculty_statuses.get(user_data['status'])
            
            if not status_id:
                logger.warning(f"Status '{user_data['status']}' not found for {user_data['user_type']}, using default")
                # Use first available status as fallback
                if user_data['user_type'] == 'student' and student_statuses:
                    status_id = list(student_statuses.values())[0]
                elif user_data['user_type'] == 'faculty' and faculty_statuses:
                    status_id = list(faculty_statuses.values())[0]
            
            # Insert user with status
            current_time = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, birthday, password_hash, contact_number, role, status_id, verified, isDeleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data['first_name'],
                user_data['last_name'],
                user_data['email'],
                user_data['birthday'],
                hashed_pw.decode('utf-8'),
                user_data['contact_number'],
                user_data['role'],
                status_id,
                user_data['verified'],
                0,  # isDeleted = 0 (False)
                current_time,
                current_time
            ))
            
            user_id = cursor.lastrowid
            logger.info(f"Created user: {user_data['email']} (ID: {user_id}) with status: {user_data['status']}")
            
            # Insert into role-specific tables
            if user_data['user_type'] == 'student':
                # Get section ID for this student
                section_key = f"{user_data['section']}-{user_data['program']}"
                section_id = section_ids.get(section_key)
                
                cursor.execute("""
                    INSERT INTO students (user_id, student_number, section)
                    VALUES (?, ?, ?)
                """, (user_id, user_data['student_number'], section_id))
                logger.info(f"  -> Added student record: {user_data['student_number']} in section {user_data['section']} ({user_data['program'][:5]})")
                
            elif user_data['user_type'] == 'faculty':
                cursor.execute("""
                    INSERT INTO faculties (user_id, employee_number)
                    VALUES (?, ?)
                """, (user_id, user_data['employee_number']))
                logger.info(f"  -> Added faculty record with employee number: {user_data['employee_number']}")
        
        # Commit transaction
        conn.commit()
        logger.info("Successfully created seed users!")
        
        # Verify what was created
        cursor.execute("""
            SELECT COUNT(*) as total_users,
                   SUM(CASE WHEN role = 'Student' THEN 1 ELSE 0 END) as students,
                   SUM(CASE WHEN role IN ('Faculty', 'Admin') THEN 1 ELSE 0 END) as faculty_admin
            FROM users WHERE isDeleted = 0
        """)
        counts = cursor.fetchone()
        logger.info(f"Database now has: {counts[0]} total users, {counts[1]} students, {counts[2]} faculty/admin")
        
        # Show status distribution
        cursor.execute("""
            SELECT s.name as status_name, s.user_type, COUNT(u.id) as count
            FROM statuses s
            LEFT JOIN users u ON s.id = u.status_id AND u.isDeleted = 0
            GROUP BY s.id, s.name, s.user_type
            ORDER BY s.user_type, s.name
        """)
        status_counts = cursor.fetchall()
        
        logger.info("Status distribution:")
        for status_name, user_type, count in status_counts:
            logger.info(f"  {user_type.title()}: {status_name} = {count} users")
        
        # Show programs and sections created
        cursor.execute("SELECT COUNT(*) FROM programs")
        program_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM sections")
        section_count = cursor.fetchone()[0]
        
        logger.info(f"Database also has: {program_count} programs, {course_count} courses, {section_count} sections")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error creating seed users: {e}")
        if conn:
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
