import sqlite3
import bcrypt
from datetime import datetime, timedelta
import os
from pathlib import Path
import logging
import random

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

def seed_assigned_courses_and_attendance():
    """Seed assigned courses and attendance logs"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        logger.info("Creating assigned courses and attendance logs...")
        
        # First, let's check the existing table structure
        cursor.execute("PRAGMA table_info(assigned_courses)")
        table_info = cursor.fetchall()
        logger.info(f"Assigned courses table structure: {table_info}")
        
        # Get all faculty and courses
        cursor.execute("""
            SELECT f.user_id, u.first_name, u.last_name
            FROM faculties f
            JOIN users u ON f.user_id = u.id
            WHERE u.role = 'Faculty' AND u.isDeleted = 0
        """)
        faculty_list = cursor.fetchall()
        
        cursor.execute("""
            SELECT c.id, c.name, p.name as program_name
            FROM courses c
            JOIN programs p ON c.program_id = p.id
        """)
        courses_list = cursor.fetchall()
        
        cursor.execute("""
            SELECT s.id, s.name, p.name as program_name
            FROM sections s
            JOIN programs p ON s.course_id = p.id
        """)
        sections_list = cursor.fetchall()
        
        logger.info(f"Found {len(faculty_list)} faculty, {len(courses_list)} courses, {len(sections_list)} sections")
        
        # Drop and recreate assigned_courses table with correct structure
        cursor.execute("DROP TABLE IF EXISTS assigned_courses")
        cursor.execute("DROP TABLE IF EXISTS attendance_logs")
        
        # Create assigned_courses table with correct structure
        cursor.execute("""
            CREATE TABLE assigned_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                section_id INTEGER NOT NULL,
                academic_year TEXT NOT NULL,
                semester TEXT NOT NULL,
                schedule_day TEXT,
                schedule_time TEXT,
                room TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
                FOREIGN KEY (section_id) REFERENCES sections (id) ON DELETE CASCADE
            )
        """)
        
        # Create attendance_logs table with correct structure
        cursor.execute("""
            CREATE TABLE attendance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                assigned_course_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                image BLOB,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (assigned_course_id) REFERENCES assigned_courses (id) ON DELETE CASCADE
            )
        """)
        
        current_time = datetime.now().isoformat()
        current_year = datetime.now().year
        academic_year = f"{current_year}-{current_year + 1}"
        
        # Sample assigned courses data
        assigned_course_ids = []
        
        # Ensure we have data to work with
        if not faculty_list:
            logger.warning("No faculty found to assign courses")
            conn.close()
            return False
            
        if not courses_list:
            logger.warning("No courses found to assign")
            conn.close()
            return False
            
        if not sections_list:
            logger.warning("No sections found to assign")
            conn.close()
            return False
        
        # Assign each faculty member to 2-3 courses
        for faculty_user_id, first_name, last_name in faculty_list:
            # Randomly select 2-3 courses for this faculty (ensure we don't exceed available courses)
            num_courses_to_assign = min(3, len(courses_list), random.randint(2, 3))
            selected_courses = random.sample(courses_list, num_courses_to_assign)
            
            for course_id, course_name, program_name in selected_courses:
                # Find matching sections for this program
                matching_sections = [s for s in sections_list if s[2] == program_name]
                
                if matching_sections:
                    # Select a random section
                    section_id, section_name, _ = random.choice(matching_sections)
                    
                    # Generate random schedule
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                    times = ['8:00-9:30', '9:30-11:00', '11:00-12:30', '1:30-3:00', '3:00-4:30']
                    rooms = ['Room 101', 'Room 102', 'Room 103', 'Lab 1', 'Lab 2', 'Conference Room']
                    
                    schedule_day = random.choice(days)
                    schedule_time = random.choice(times)
                    room = random.choice(rooms)
                    semester = random.choice(['1st Semester', '2nd Semester'])
                    
                    # Check if this assignment already exists
                    cursor.execute("""
                        SELECT id FROM assigned_courses 
                        WHERE user_id = ? AND course_id = ? AND section_id = ? AND academic_year = ?
                    """, (faculty_user_id, course_id, section_id, academic_year))
                    
                    existing = cursor.fetchone()
                    if existing:
                        assigned_course_ids.append(existing[0])
                        logger.info(f"Course assignment already exists for {first_name} {last_name} - {course_name}")
                        continue
                    
                    # Insert assigned course (using user_id instead of faculty_id)
                    cursor.execute("""
                        INSERT INTO assigned_courses 
                        (user_id, course_id, section_id, academic_year, semester, schedule_day, schedule_time, room, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (faculty_user_id, course_id, section_id, academic_year, semester, schedule_day, schedule_time, room, current_time, current_time))
                    
                    assigned_course_id = cursor.lastrowid
                    assigned_course_ids.append(assigned_course_id)
                    
                    logger.info(f"Assigned {first_name} {last_name} to teach {course_name} for section {section_name} (ID: {assigned_course_id})")
        
        logger.info(f"Created {len(assigned_course_ids)} course assignments")
        
        # Now seed attendance logs with realistic distributions
        if assigned_course_ids:
            # Get all students
            cursor.execute("""
                SELECT u.id, u.first_name, u.last_name, st.section
                FROM users u
                JOIN students st ON u.id = st.user_id
                WHERE u.role = 'Student' AND u.isDeleted = 0
            """)
            students_list = cursor.fetchall()
            
            logger.info(f"Found {len(students_list)} students for attendance logs")
            
            if not students_list:
                logger.warning("No students found to generate attendance logs")
                conn.commit()
                conn.close()
                return True
            
            # Define student performance categories with realistic distributions
            # Adjust to ensure more students have 90%+ attendance
            excellent_students = int(len(students_list) * 0.30)   # 30% excellent (95%+ attendance)
            very_good_students = int(len(students_list) * 0.25)   # 25% very good (90-94% attendance)
            good_students = int(len(students_list) * 0.25)        # 25% good (80-89% attendance)
            average_students = int(len(students_list) * 0.15)     # 15% average (70-79% attendance)
            poor_students = len(students_list) - excellent_students - very_good_students - good_students - average_students  # Remaining poor (<70% attendance)
            
            # Shuffle students and assign performance categories
            shuffled_students = students_list.copy()
            random.shuffle(shuffled_students)
            
            student_performance = {}
            idx = 0
            
            # Assign excellent students (95-99% attendance)
            for i in range(excellent_students):
                student_id = shuffled_students[idx][0]
                student_performance[student_id] = {
                    'category': 'excellent',
                    'attendance_rate': random.uniform(0.95, 0.99),
                    'consistency': random.uniform(0.9, 1.0)  # Very consistent
                }
                idx += 1
            
            # Assign very good students (90-94% attendance)
            for i in range(very_good_students):
                student_id = shuffled_students[idx][0]
                student_performance[student_id] = {
                    'category': 'very_good',
                    'attendance_rate': random.uniform(0.90, 0.94),
                    'consistency': random.uniform(0.85, 0.95)  # Very consistent
                }
                idx += 1
            
            # Assign good students (80-89% attendance)
            for i in range(good_students):
                student_id = shuffled_students[idx][0]
                student_performance[student_id] = {
                    'category': 'good',
                    'attendance_rate': random.uniform(0.80, 0.89),
                    'consistency': random.uniform(0.75, 0.85)  # Fairly consistent
                }
                idx += 1
            
            # Assign average students (70-79% attendance)
            for i in range(average_students):
                student_id = shuffled_students[idx][0]
                student_performance[student_id] = {
                    'category': 'average',
                    'attendance_rate': random.uniform(0.70, 0.79),
                    'consistency': random.uniform(0.6, 0.75)  # Moderately consistent
                }
                idx += 1
            
            # Assign poor students (<70% attendance)
            for i in range(poor_students):
                student_id = shuffled_students[idx][0]
                student_performance[student_id] = {
                    'category': 'poor',
                    'attendance_rate': random.uniform(0.40, 0.69),
                    'consistency': random.uniform(0.3, 0.6)  # Inconsistent
                }
                idx += 1
            
            logger.info(f"Student distribution: {excellent_students} excellent (95%+), {very_good_students} very good (90-94%), {good_students} good (80-89%), {average_students} average (70-79%), {poor_students} poor (<70%)")
            logger.info(f"Total students with 90%+ attendance: {excellent_students + very_good_students} ({((excellent_students + very_good_students) / len(students_list)) * 100:.1f}%)")
            
            # Generate attendance logs for the past 60 days (more data for better statistics)
            start_date = datetime.now() - timedelta(days=60)
            total_attendance_logs = 0
            
            for assigned_course_id in assigned_course_ids:
                # Get course and section info for this assignment
                cursor.execute("""
                    SELECT ac.section_id, c.name as course_name, s.name as section_name
                    FROM assigned_courses ac
                    JOIN courses c ON ac.course_id = c.id
                    JOIN sections s ON ac.section_id = s.id
                    WHERE ac.id = ?
                """, (assigned_course_id,))
                
                course_info = cursor.fetchone()
                if not course_info:
                    logger.warning(f"Could not find course info for assigned course {assigned_course_id}")
                    continue
                
                section_id, course_name, section_name = course_info
                
                # Find students in this section
                section_students = [s for s in students_list if s[3] == section_id]
                
                if not section_students:
                    logger.warning(f"No students found for section {section_name} (ID: {section_id})")
                    continue
                
                logger.info(f"Generating attendance for {len(section_students)} students in {course_name} - {section_name}")
                
                # Generate class schedule (3 times per week for each course)
                class_days = []
                for day_offset in range(60):
                    attendance_date = start_date + timedelta(days=day_offset)
                    
                    # Skip weekends
                    if attendance_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                        continue
                    
                    # Schedule classes 3 times per week (Monday, Wednesday, Friday pattern)
                    if attendance_date.weekday() in [0, 2, 4]:  # Monday, Wednesday, Friday
                        class_days.append(attendance_date)
                
                # Generate attendance for each class day
                for class_date in class_days:
                    # Generate attendance for each student in this section
                    for student_id, student_first, student_last, _ in section_students:
                        if student_id not in student_performance:
                            continue
                        
                        perf = student_performance[student_id]
                        
                        # Determine if student attends based on their profile
                        base_rate = perf['attendance_rate']
                        consistency = perf['consistency']
                        
                        # Add some randomness but weighted by consistency
                        attendance_probability = base_rate + (random.uniform(-0.1, 0.1) * (1 - consistency))
                        attendance_probability = max(0, min(1, attendance_probability))  # Clamp between 0 and 1
                        
                        # Determine attendance status
                        if random.random() < attendance_probability:
                            # Student attends - determine if present or late
                            if perf['category'] == 'excellent':
                                status = 'present' if random.random() < 0.96 else 'late'
                            elif perf['category'] == 'very_good':
                                status = 'present' if random.random() < 0.93 else 'late'
                            elif perf['category'] == 'good':
                                status = 'present' if random.random() < 0.88 else 'late'
                            elif perf['category'] == 'average':
                                status = 'present' if random.random() < 0.82 else 'late'
                            else:  # poor
                                status = 'present' if random.random() < 0.75 else 'late'
                        else:
                            status = 'absent'
                        
                        # Check if attendance already exists for this date/student/course
                        cursor.execute("""
                            SELECT id FROM attendance_logs 
                            WHERE user_id = ? AND assigned_course_id = ? AND date = ?
                        """, (student_id, assigned_course_id, class_date.strftime('%Y-%m-%d')))
                        
                        if cursor.fetchone():
                            continue  # Skip if already exists
                        
                        # Insert attendance log
                        cursor.execute("""
                            INSERT INTO attendance_logs 
                            (user_id, assigned_course_id, date, status, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            student_id, 
                            assigned_course_id, 
                            class_date.strftime('%Y-%m-%d'),
                            status, 
                            current_time, 
                            current_time
                        ))
                        
                        total_attendance_logs += 1
                
                logger.info(f"Generated attendance logs for course {course_name} - {section_name}")
        
        conn.commit()
        
        # Log final statistics with detailed breakdown
        cursor.execute("SELECT COUNT(*) FROM assigned_courses")
        course_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attendance_logs")
        attendance_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM attendance_logs 
            GROUP BY status
        """)
        status_counts = cursor.fetchall()
        
        # Calculate attendance statistics per student
        cursor.execute("""
            SELECT 
                u.first_name || ' ' || u.last_name as student_name,
                COUNT(al.id) as total_classes,
                SUM(CASE WHEN al.status = 'present' THEN 1 ELSE 0 END) as present_count,
                SUM(CASE WHEN al.status = 'late' THEN 1 ELSE 0 END) as late_count,
                SUM(CASE WHEN al.status = 'absent' THEN 1 ELSE 0 END) as absent_count,
                ROUND((SUM(CASE WHEN al.status = 'present' THEN 1 ELSE 0 END) * 100.0 / COUNT(al.id)), 2) as attendance_percentage
            FROM users u
            JOIN attendance_logs al ON u.id = al.user_id
            WHERE u.role = 'Student'
            GROUP BY u.id, u.first_name, u.last_name
            ORDER BY attendance_percentage DESC
        """)
        student_stats = cursor.fetchall()
        
        # Count students by attendance ranges
        excellent_count = len([s for s in student_stats if s[5] >= 95])
        very_good_count = len([s for s in student_stats if 90 <= s[5] < 95])
        good_count = len([s for s in student_stats if 80 <= s[5] < 90])
        average_count = len([s for s in student_stats if 70 <= s[5] < 80])
        poor_count = len([s for s in student_stats if s[5] < 70])
        
        logger.info(f"✓ Created {course_count} assigned courses")
        logger.info(f"✓ Created {attendance_count} attendance logs")
        
        if status_counts:
            logger.info("Overall attendance distribution:")
            total_logs = sum(count for _, count in status_counts)
            for status, count in status_counts:
                percentage = (count / total_logs) * 100 if total_logs > 0 else 0
                logger.info(f"  {status}: {count} ({percentage:.1f}%)")
        
        logger.info(f"\nStudent attendance distribution:")
        logger.info(f"  Excellent (95%+): {excellent_count} students")
        logger.info(f"  Very Good (90-94%): {very_good_count} students")
        logger.info(f"  Good (80-89%): {good_count} students")
        logger.info(f"  Average (70-79%): {average_count} students")
        logger.info(f"  Poor (<70%): {poor_count} students")
        
        # Calculate 90%+ and 80%+ totals
        ninety_plus = excellent_count + very_good_count
        eighty_plus = excellent_count + very_good_count + good_count
        total_students_with_attendance = len(student_stats)
        
        if total_students_with_attendance > 0:
            ninety_plus_percent = (ninety_plus / total_students_with_attendance) * 100
            eighty_plus_percent = (eighty_plus / total_students_with_attendance) * 100
            logger.info(f"\nSummary:")
            logger.info(f"  Students with 90%+ attendance: {ninety_plus} ({ninety_plus_percent:.1f}%)")
            logger.info(f"  Students with 80%+ attendance: {eighty_plus} ({eighty_plus_percent:.1f}%)")

        # Show top and bottom performers
        if student_stats:
            logger.info(f"\nTop 3 performers:")
            for i, (name, total, present, late, absent, percentage) in enumerate(student_stats[:3]):
                logger.info(f"  {i+1}. {name}: {percentage}% ({present}/{total} present)")
            
            logger.info(f"\nBottom 3 performers:")
            for i, (name, total, present, late, absent, percentage) in enumerate(student_stats[-3:]):
                logger.info(f"  {i+1}. {name}: {percentage}% ({present}/{total} present)")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error creating assigned courses and attendance logs: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()
        return False

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
        
        # Now seed assigned courses and attendance logs
        logger.info("\nSeeding assigned courses and attendance logs...")
        attendance_success = seed_assigned_courses_and_attendance()
        
        if attendance_success:
            logger.info("Successfully created assigned courses and attendance logs!")
        else:
            logger.warning("Failed to create assigned courses and attendance logs")
        
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
