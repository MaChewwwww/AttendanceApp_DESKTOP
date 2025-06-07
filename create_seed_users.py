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
        
        # Programs data with proper unique constraints
        programs_data = [
            {
                'name': 'Bachelor of Science in Information Technology',
                'acronym': 'BSIT',
                'code': 'PROG-001',  # Updated to ensure uniqueness
                'description': 'A comprehensive program focusing on information technology and computer systems, preparing students for careers in software development, network administration, and IT management.',
                'color': '#3B82F6'  # Blue
            },
            {
                'name': 'Bachelor of Science in Computer Science',
                'acronym': 'BSCS',
                'code': 'PROG-002',  # Updated to ensure uniqueness
                'description': 'A program emphasizing theoretical foundations of computation and practical software engineering, covering algorithms, data structures, and advanced computing concepts.',
                'color': '#10B981'  # Green
            },
            {
                'name': 'Bachelor of Science in Information Systems',
                'acronym': 'BSIS',
                'code': 'PROG-003',  # Updated to ensure uniqueness
                'description': 'A program combining business processes with information technology solutions, focusing on systems analysis, database management, and enterprise applications.',
                'color': '#F59E0B'  # Orange
            },
            {
                'name': 'Bachelor of Science in Computer Engineering',
                'acronym': 'BSCpE',
                'code': 'PROG-004',  # Additional program
                'description': 'A program integrating computer science and electrical engineering principles, covering hardware design, embedded systems, and computer architecture.',
                'color': '#8B5CF6'  # Purple
            },
            {
                'name': 'Bachelor of Science in Software Engineering',
                'acronym': 'BSSE',
                'code': 'PROG-005',  # Additional program
                'description': 'A specialized program focused on software development methodologies, project management, and large-scale system design and implementation.',
                'color': '#EF4444'  # Red
            }
        ]
        
        # Insert programs with proper error handling for unique constraints
        program_ids = {}
        for program_data in programs_data:
            # Check if program with same name, acronym, or code already exists
            cursor.execute("""
                SELECT id, name, acronym, code FROM programs 
                WHERE (name = ? OR acronym = ? OR code = ?) AND isDeleted = 0
            """, (program_data['name'], program_data['acronym'], program_data['code']))
            existing = cursor.fetchone()
            
            if existing:
                program_ids[program_data['name']] = existing[0]
                logger.info(f"Program already exists: {existing[1]} (ID: {existing[0]}, Acronym: {existing[2]}, Code: {existing[3]})")
                continue
            
            try:
                current_time = datetime.now().isoformat()
                cursor.execute("""
                    INSERT INTO programs (name, acronym, code, description, color, isDeleted, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    program_data['name'], 
                    program_data['acronym'], 
                    program_data['code'], 
                    program_data['description'], 
                    program_data['color'], 
                    0, 
                    current_time, 
                    current_time
                ))
                
                program_id = cursor.lastrowid
                program_ids[program_data['name']] = program_id
                logger.info(f"✓ Created program: {program_data['name']}")
                logger.info(f"  - Acronym: {program_data['acronym']}")
                logger.info(f"  - Code: {program_data['code']}")
                logger.info(f"  - Color: {program_data['color']}")
                logger.info(f"  - ID: {program_id}")
                
            except sqlite3.IntegrityError as e:
                logger.error(f"Failed to create program {program_data['name']}: {e}")
                # Try to find existing program by name only as fallback
                cursor.execute("SELECT id FROM programs WHERE name = ? AND isDeleted = 0", (program_data['name'],))
                fallback = cursor.fetchone()
                if fallback:
                    program_ids[program_data['name']] = fallback[0]
                    logger.info(f"Using existing program {program_data['name']} (ID: {fallback[0]})")
                continue
        
        # Enhanced courses data for each program
        courses_data = [
            # BSIT Courses (5 core courses)
            {'name': 'Programming Fundamentals', 'code': 'IT-101', 'description': 'Introduction to programming concepts using modern languages', 'program': 'Bachelor of Science in Information Technology'},
            {'name': 'Data Structures and Algorithms', 'code': 'IT-201', 'description': 'Advanced programming concepts and algorithmic thinking', 'program': 'Bachelor of Science in Information Technology'},
            {'name': 'Database Management Systems', 'code': 'IT-301', 'description': 'Database design, implementation, and management', 'program': 'Bachelor of Science in Information Technology'},
            {'name': 'Web Development Technologies', 'code': 'IT-302', 'description': 'Frontend and backend web development frameworks', 'program': 'Bachelor of Science in Information Technology'},
            {'name': 'Network Administration', 'code': 'IT-401', 'description': 'Computer networking and system administration', 'program': 'Bachelor of Science in Information Technology'},
            
            # BSCS Courses (5 core courses)
            {'name': 'Computer Programming', 'code': 'CS-101', 'description': 'Core programming principles and paradigms', 'program': 'Bachelor of Science in Computer Science'},
            {'name': 'Software Engineering', 'code': 'CS-301', 'description': 'Software development methodologies and practices', 'program': 'Bachelor of Science in Computer Science'},
            {'name': 'Machine Learning', 'code': 'CS-401', 'description': 'AI and machine learning fundamentals and applications', 'program': 'Bachelor of Science in Computer Science'},
            {'name': 'Computer Graphics', 'code': 'CS-302', 'description': 'Graphics programming and visualization techniques', 'program': 'Bachelor of Science in Computer Science'},
            {'name': 'Operating Systems', 'code': 'CS-201', 'description': 'System software and operating system concepts', 'program': 'Bachelor of Science in Computer Science'},
            
            # BSIS Courses (5 core courses)
            {'name': 'Business Process Analysis', 'code': 'IS-101', 'description': 'Analyzing and optimizing business workflows', 'program': 'Bachelor of Science in Information Systems'},
            {'name': 'Systems Analysis and Design', 'code': 'IS-201', 'description': 'System development lifecycle and design patterns', 'program': 'Bachelor of Science in Information Systems'},
            {'name': 'Enterprise Resource Planning', 'code': 'IS-301', 'description': 'ERP systems implementation and management', 'program': 'Bachelor of Science in Information Systems'},
            {'name': 'IT Project Management', 'code': 'IS-302', 'description': 'Managing technology projects and teams', 'program': 'Bachelor of Science in Information Systems'},
            {'name': 'Business Intelligence', 'code': 'IS-401', 'description': 'Data analytics and business intelligence tools', 'program': 'Bachelor of Science in Information Systems'},
            
            # BSCpE Courses (4 core courses)
            {'name': 'Digital Logic Design', 'code': 'CPE-101', 'description': 'Digital circuits and logic design principles', 'program': 'Bachelor of Science in Computer Engineering'},
            {'name': 'Microprocessors and Microcontrollers', 'code': 'CPE-201', 'description': 'Embedded systems and processor architecture', 'program': 'Bachelor of Science in Computer Engineering'},
            {'name': 'Computer Architecture', 'code': 'CPE-301', 'description': 'Hardware design and computer organization', 'program': 'Bachelor of Science in Computer Engineering'},
            {'name': 'VLSI Design', 'code': 'CPE-401', 'description': 'Very Large Scale Integration circuit design', 'program': 'Bachelor of Science in Computer Engineering'},
            
            # BSSE Courses (4 core courses)
            {'name': 'Software Architecture', 'code': 'SE-301', 'description': 'Large-scale software system design patterns', 'program': 'Bachelor of Science in Software Engineering'},
            {'name': 'Software Testing and Quality Assurance', 'code': 'SE-302', 'description': 'Testing methodologies and quality control', 'program': 'Bachelor of Science in Software Engineering'},
            {'name': 'DevOps and Deployment', 'code': 'SE-401', 'description': 'Continuous integration and deployment practices', 'program': 'Bachelor of Science in Software Engineering'},
            {'name': 'Agile Development Methodologies', 'code': 'SE-201', 'description': 'Agile and Scrum development practices', 'program': 'Bachelor of Science in Software Engineering'}
        ]
        
        # Insert courses with proper error handling
        course_ids = {}
        for course_data in courses_data:
            # Skip if program doesn't exist
            if course_data['program'] not in program_ids:
                logger.warning(f"Program {course_data['program']} not found, skipping course {course_data['name']}")
                continue
                
            program_id = program_ids[course_data['program']]
            
            # Check if course already exists for this program (by name or code)
            cursor.execute("SELECT id FROM courses WHERE (name = ? OR code = ?) AND program_id = ?", 
                         (course_data['name'], course_data['code'], program_id))
            existing = cursor.fetchone()
            
            if existing:
                course_ids[course_data['name']] = existing[0]
                continue
            
            try:
                current_time = datetime.now().isoformat()
                cursor.execute("""
                    INSERT INTO courses (name, code, description, program_id, isDeleted, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (course_data['name'], course_data['code'], course_data['description'], program_id, 0, current_time, current_time))
                
                course_id = cursor.lastrowid
                course_ids[course_data['name']] = course_id
                program_acronym = next((p['acronym'] for p in programs_data if p['name'] == course_data['program']), 'Unknown')
                logger.info(f"✓ Created course: {course_data['name']} ({course_data['code']}) - {program_acronym} - ID: {course_id}")
                
            except sqlite3.Error as e:
                logger.error(f"Failed to create course {course_data['name']} ({course_data['code']}): {e}")
                continue
        
        # Enhanced sections data with more realistic distribution
        sections_data = [
            # BSIT sections (most popular program)
            {'name': '1-1', 'program': 'Bachelor of Science in Information Technology'},
            {'name': '1-2', 'program': 'Bachelor of Science in Information Technology'},
            {'name': '1-3', 'program': 'Bachelor of Science in Information Technology'},
            {'name': '2-1', 'program': 'Bachelor of Science in Information Technology'},
            {'name': '2-2', 'program': 'Bachelor of Science in Information Technology'},
            {'name': '3-1', 'program': 'Bachelor of Science in Information Technology'},
            {'name': '3-2', 'program': 'Bachelor of Science in Information Technology'},
            {'name': '4-1', 'program': 'Bachelor of Science in Information Technology'},
            
            # BSCS sections (second most popular)
            {'name': '1-1', 'program': 'Bachelor of Science in Computer Science'},
            {'name': '1-2', 'program': 'Bachelor of Science in Computer Science'},
            {'name': '2-1', 'program': 'Bachelor of Science in Computer Science'},
            {'name': '2-2', 'program': 'Bachelor of Science in Computer Science'},
            {'name': '3-1', 'program': 'Bachelor of Science in Computer Science'},
            {'name': '4-1', 'program': 'Bachelor of Science in Computer Science'},
            
            # BSIS sections (moderate popularity)
            {'name': '1-1', 'program': 'Bachelor of Science in Information Systems'},
            {'name': '2-1', 'program': 'Bachelor of Science in Information Systems'},
            {'name': '3-1', 'program': 'Bachelor of Science in Information Systems'},
            {'name': '4-1', 'program': 'Bachelor of Science in Information Systems'},
            
            # BSCpE sections (smaller program)
            {'name': '1-1', 'program': 'Bachelor of Science in Computer Engineering'},
            {'name': '2-1', 'program': 'Bachelor of Science in Computer Engineering'},
            {'name': '3-1', 'program': 'Bachelor of Science in Computer Engineering'},
            
            # BSSE sections (newer/smaller program)
            {'name': '1-1', 'program': 'Bachelor of Science in Software Engineering'},
            {'name': '2-1', 'program': 'Bachelor of Science in Software Engineering'}
        ]
        
        # Insert sections with proper error handling
        section_ids = {}
        for section_data in sections_data:
            # Skip if program doesn't exist
            if section_data['program'] not in program_ids:
                logger.warning(f"Program {section_data['program']} not found, skipping section {section_data['name']}")
                continue
                
            program_id = program_ids[section_data['program']]
            section_key = f"{section_data['name']}-{section_data['program']}"
            
            # Check if section already exists for this program
            cursor.execute("SELECT id FROM sections WHERE name = ? AND program_id = ?", 
                         (section_data['name'], program_id))
            existing = cursor.fetchone()
            
            if existing:
                section_ids[section_key] = existing[0]
                continue
            
            try:
                current_time = datetime.now().isoformat()
                cursor.execute("""
                    INSERT INTO sections (name, program_id, isDeleted, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (section_data['name'], program_id, 0, current_time, current_time))
                
                section_id = cursor.lastrowid
                section_ids[section_key] = section_id
                program_acronym = next((p['acronym'] for p in programs_data if p['name'] == section_data['program']), 'Unknown')
                logger.info(f"✓ Created section: {section_data['name']} ({program_acronym}) - ID: {section_id}")
                
            except sqlite3.Error as e:
                logger.error(f"Failed to create section {section_data['name']} for {section_data['program']}: {e}")
                continue
        
        conn.commit()
        
        # Log summary statistics
        cursor.execute("SELECT COUNT(*) FROM programs WHERE isDeleted = 0")
        program_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM sections")
        section_count = cursor.fetchone()[0]
        
        logger.info(f"\n✓ Database seeding summary:")
        logger.info(f"  - Programs: {program_count}")
        logger.info(f"  - Courses: {course_count}")
        logger.info(f"  - Sections: {section_count}")
        
        # Show program details
        cursor.execute("""
            SELECT p.name, p.acronym, p.code, p.color, COUNT(s.id) as section_count
            FROM programs p
            LEFT JOIN sections s ON p.id = s.program_id
            WHERE p.isDeleted = 0
            GROUP BY p.id, p.name, p.acronym, p.code, p.color
            ORDER BY p.acronym
        """)
        program_details = cursor.fetchall()
        
        logger.info(f"\nProgram details:")
        for name, acronym, code, color, sections in program_details:
            logger.info(f"  {acronym} ({code}): {sections} sections - {color}")
        
        conn.close()
        
        return True, program_ids, section_ids
        
    except Exception as e:
        logger.error(f"Error creating programs and courses: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()
        return False, {}, {}

def get_philippine_holidays(year):
    """Get Philippine holidays for a given year"""
    holidays = set()
    
    # Fixed holidays
    holidays.add(f"{year}-01-01")  # New Year's Day
    holidays.add(f"{year}-04-09")  # Araw ng Kagitingan (Day of Valor)
    holidays.add(f"{year}-05-01")  # Labor Day
    holidays.add(f"{year}-06-12")  # Independence Day
    holidays.add(f"{year}-08-21")  # Ninoy Aquino Day
    holidays.add(f"{year}-08-29")  # National Heroes Day (last Monday of August)
    holidays.add(f"{year}-11-30")  # Bonifacio Day
    holidays.add(f"{year}-12-25")  # Christmas Day
    holidays.add(f"{year}-12-30")  # Rizal Day
    holidays.add(f"{year}-12-31")  # New Year's Eve
    
    # Movable holidays (approximate dates - these vary by year)
    # Holy Week holidays (usually March/April)
    holidays.add(f"{year}-04-06")  # Maundy Thursday (example)
    holidays.add(f"{year}-04-07")  # Good Friday (example)
    holidays.add(f"{year}-04-08")  # Black Saturday (example)
    
    # Additional common school holidays
    holidays.add(f"{year}-11-01")  # All Saints' Day
    holidays.add(f"{year}-11-02")  # All Souls' Day
    
    # Chinese New Year (varies by year)
    if year == 2024:
        holidays.add("2024-02-10")
    elif year == 2023:
        holidays.add("2023-01-22")
    elif year == 2025:
        holidays.add("2025-01-29")
    
    return holidays

def is_class_suspended(date, semester):
    """Check if classes are typically suspended on this date"""
    # Get Philippine holidays for this year
    holidays = get_philippine_holidays(date.year)
    
    # Check if date is a holiday
    date_str = date.strftime('%Y-%m-%d')
    if date_str in holidays:
        return True
    
    # Check for common suspension periods
    month = date.month
    day = date.day
    
    # Christmas break (December 20-31)
    if month == 12 and day >= 20:
        return True
    
    # New Year extension (January 2-7)
    if month == 1 and day <= 7:
        return True
    
    # Holy Week (usually March/April - broader range)
    if month == 4 and 6 <= day <= 10:
        return True
    
    # Semestral break periods
    if semester == "1st Semester":
        # Mid-semester break (October)
        if month == 10 and 15 <= day <= 17:
            return True
    elif semester == "2nd Semester":
        # Mid-semester break (March)
        if month == 3 and 15 <= day <= 17:
            return True
    
    # Extreme weather suspensions (randomly for realism - typhoon season)
    if month in [7, 8, 9, 10, 11]:  # Typhoon season
        # 5% chance of suspension during typhoon season
        if random.random() < 0.05:
            return True
    
    return False

def seed_assigned_courses_and_attendance():
    """Seed assigned courses and attendance logs"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        logger.info("Creating assigned courses, schedules, and attendance logs...")
        
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
            JOIN programs p ON s.program_id = p.id
        """)
        sections_list = cursor.fetchall()
        
        logger.info(f"Found {len(faculty_list)} faculty, {len(courses_list)} courses, {len(sections_list)} sections")
        
        # Drop and recreate tables with correct structure
        cursor.execute("DROP TABLE IF EXISTS schedules")
        cursor.execute("DROP TABLE IF EXISTS attendance_logs")
        cursor.execute("DROP TABLE IF EXISTS assigned_courses")
        
        # Create assigned_courses table (note: using faculty_id to match model)
        cursor.execute("""
            CREATE TABLE assigned_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                faculty_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                section_id INTEGER NOT NULL,
                academic_year TEXT,
                semester TEXT,
                schedule_time TEXT,
                room TEXT,
                isDeleted INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (faculty_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE,
                FOREIGN KEY (section_id) REFERENCES sections (id) ON DELETE CASCADE
            )
        """)
        
        # Create schedules table to match the Schedule model
        cursor.execute("""
            CREATE TABLE schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assigned_course_id INTEGER NOT NULL,
                day_of_week TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (assigned_course_id) REFERENCES assigned_courses (id) ON DELETE CASCADE
            )
        """)
        
        # Create attendance_logs table
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
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # Generate data for multiple academic years and semesters
        academic_years_to_generate = []
        
        # Generate current academic year
        if current_month >= 9:  # September onwards = new academic year
            current_academic_year = f"{current_year}-{current_year + 1}"
        else:  # January to August = previous academic year
            current_academic_year = f"{current_year - 1}-{current_year}"
        
        # Generate previous academic year for historical data
        if current_month >= 9:
            previous_academic_year = f"{current_year - 1}-{current_year}"
        else:
            previous_academic_year = f"{current_year - 2}-{current_year - 1}"
        
        academic_years_to_generate = [previous_academic_year, current_academic_year]
        
        # Define all semesters
        all_semesters = ["1st Semester", "2nd Semester", "Summer"]
        
        logger.info(f"Generating data for academic years: {academic_years_to_generate}")
        
        assigned_course_ids = []
        
        # Ensure we have data to work with
        if not faculty_list or not courses_list or not sections_list:
            logger.warning("Missing required data for course assignments")
            conn.close()
            return False
        
        # Track faculty course assignments to prevent repetition across semesters
        faculty_course_assignments = {}  # faculty_id -> set of (course_id, section_id) tuples
        
        # Generate course assignments for each academic year and semester
        for academic_year in academic_years_to_generate:
            for semester in all_semesters:
                logger.info(f"Creating assignments for {academic_year} - {semester}")
                
                # Assign each faculty member to 2-3 courses per semester
                for faculty_user_id, first_name, last_name in faculty_list:
                    # Initialize faculty assignment tracking if not exists
                    if faculty_user_id not in faculty_course_assignments:
                        faculty_course_assignments[faculty_user_id] = set()
                    
                    # Vary the number of courses per semester
                    if semester == "Summer":
                        num_courses_to_assign = min(2, len(courses_list), random.randint(1, 2))  # Fewer courses in summer
                    else:
                        num_courses_to_assign = min(3, len(courses_list), random.randint(2, 3))  # Regular semester load
                    
                    # Get available courses that haven't been assigned to this faculty yet
                    available_course_section_pairs = []
                    for course_id, course_name, program_name in courses_list:
                        # Find matching sections for this program
                        matching_sections = [s for s in sections_list if s[2] == program_name]
                        for section_id, section_name, _ in matching_sections:
                            pair = (course_id, section_id)
                            if pair not in faculty_course_assignments[faculty_user_id]:
                                available_course_section_pairs.append((course_id, course_name, program_name, section_id, section_name))
                    
                    # If we don't have enough unique combinations, allow some repetition but prefer new ones
                    if len(available_course_section_pairs) < num_courses_to_assign:
                        # Add all possible combinations, giving priority to new ones
                        all_possible_pairs = []
                        for course_id, course_name, program_name in courses_list:
                            matching_sections = [s for s in sections_list if s[2] == program_name]
                            for section_id, section_name, _ in matching_sections:
                                all_possible_pairs.append((course_id, course_name, program_name, section_id, section_name))
                        
                        # Shuffle and use all available combinations
                        random.shuffle(all_possible_pairs)
                        selected_assignments = all_possible_pairs[:num_courses_to_assign]
                    else:
                        # We have enough unique combinations
                        selected_assignments = random.sample(available_course_section_pairs, num_courses_to_assign)
                    
                    for course_id, course_name, program_name, section_id, section_name in selected_assignments:
                        rooms = ['Room 101', 'Room 102', 'Room 103', 'Lab 1', 'Lab 2', 'Conference Room']
                        room = random.choice(rooms)
                        
                        # Check if this exact assignment already exists for this semester
                        cursor.execute("""
                            SELECT id FROM assigned_courses 
                            WHERE faculty_id = ? AND course_id = ? AND section_id = ? AND academic_year = ? AND semester = ?
                        """, (faculty_user_id, course_id, section_id, academic_year, semester))
                        
                        existing = cursor.fetchone()
                        if existing:
                            assigned_course_ids.append(existing[0])
                            continue
                        
                        # Insert assigned course (using faculty_id to match model)
                        cursor.execute("""
                            INSERT INTO assigned_courses 
                            (faculty_id, course_id, section_id, academic_year, semester, room, isDeleted, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (faculty_user_id, course_id, section_id, academic_year, semester, room, 0, current_time, current_time))
                        
                        assigned_course_id = cursor.lastrowid
                        assigned_course_ids.append(assigned_course_id)
                        
                        # Track this assignment to prevent future repetition
                        faculty_course_assignments[faculty_user_id].add((course_id, section_id))
                        
                        # Create schedule entries for this assigned course
                        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                        time_slots = [
                            ('08:00:00', '09:30:00'),
                            ('09:30:00', '11:00:00'),
                            ('11:00:00', '12:30:00'),
                            ('13:30:00', '15:00:00'),
                            ('15:00:00', '16:30:00'),
                            ('16:30:00', '18:00:00')
                        ]
                        
                        # Most courses meet 2-3 times per week
                        if semester == "Summer":
                            num_meetings = random.choice([2, 3])  # Summer courses may be more intensive
                        else:
                            num_meetings = random.choice([2, 3])
                        
                        selected_days = random.sample(days_of_week, num_meetings)
                        
                        for day in selected_days:
                            start_time, end_time = random.choice(time_slots)
                            
                            # Convert time strings to datetime objects for storage
                            today = datetime.now().date()
                            start_datetime = datetime.combine(today, datetime.strptime(start_time, '%H:%M:%S').time())
                            end_datetime = datetime.combine(today, datetime.strptime(end_time, '%H:%M:%S').time())
                            
                            cursor.execute("""
                                INSERT INTO schedules 
                                (assigned_course_id, day_of_week, start_time, end_time, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                                assigned_course_id,
                                day,
                                start_datetime.isoformat(),
                                end_datetime.isoformat(),
                                current_time,
                                current_time
                            ))
                        
                        logger.info(f"Assigned {first_name} {last_name} to teach {course_name} for section {section_name} in {academic_year} {semester} with {num_meetings} weekly meetings")
        
        logger.info(f"Created {len(assigned_course_ids)} course assignments across all semesters")
        
        # Log faculty assignment distribution
        for faculty_id, assignments in faculty_course_assignments.items():
            cursor.execute("SELECT first_name, last_name FROM users WHERE id = ?", (faculty_id,))
            faculty_name = cursor.fetchone()
            if faculty_name:
                logger.info(f"Faculty {faculty_name[0]} {faculty_name[1]} assigned to {len(assignments)} unique course-section combinations")
        
        # Get total schedule count
        cursor.execute("SELECT COUNT(*) FROM schedules")
        schedule_count = cursor.fetchone()[0]
        logger.info(f"Created {schedule_count} schedule entries")
        
        # Now seed attendance logs with realistic academic calendar data for each semester
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
            
            # Define student performance categories with top university standards
            # Higher baseline attendance rates reflecting top university standards
            excellent_students = int(len(students_list) * 0.45)   # 45% excellent (95-98% attendance)
            very_good_students = int(len(students_list) * 0.30)   # 30% very good (90-94% attendance)
            good_students = int(len(students_list) * 0.15)        # 15% good (85-89% attendance)
            average_students = int(len(students_list) * 0.07)     # 7% average (80-84% attendance)
            poor_students = len(students_list) - excellent_students - very_good_students - good_students - average_students  # 3% struggling (75-79% attendance)
            
            # Shuffle students and assign performance categories
            shuffled_students = students_list.copy()
            random.shuffle(shuffled_students)
            
            student_performance = {}
            idx = 0
            
            # Assign performance categories with higher baseline rates
            categories = [
                ('excellent', excellent_students, (0.95, 0.98), (0.95, 1.0)),      # Top performers
                ('very_good', very_good_students, (0.90, 0.94), (0.90, 0.95)),    # Strong performers
                ('good', good_students, (0.85, 0.89), (0.85, 0.90)),              # Good performers
                ('average', average_students, (0.80, 0.84), (0.75, 0.85)),        # Average performers
                ('poor', poor_students, (0.75, 0.79), (0.65, 0.75))               # Struggling students (for demo)
            ]
            
            for category, count, attendance_range, consistency_range in categories:
                for i in range(count):
                    if idx < len(shuffled_students):
                        student_id = shuffled_students[idx][0]
                        student_performance[student_id] = {
                            'category': category,
                            'attendance_rate': random.uniform(*attendance_range),
                            'consistency': random.uniform(*consistency_range)
                        }
                        idx += 1
            
            logger.info(f"Top university student distribution: {excellent_students} excellent (95-98%), {very_good_students} very good (90-94%), {good_students} good (85-89%), {average_students} average (80-84%), {poor_students} struggling (75-79%)")
            
            # Generate attendance for each assigned course
            total_class_days_generated = 0
            total_suspensions = 0
            
            # Track student-course combinations to prevent duplicates
            student_course_tracking = {}  # student_id -> set of course_ids they've attended
            
            for assigned_course_id in assigned_course_ids:
                # Get course assignment details
                cursor.execute("""
                    SELECT ac.section_id, ac.course_id, c.name as course_name, s.name as section_name, 
                           ac.academic_year, ac.semester
                    FROM assigned_courses ac
                    JOIN courses c ON ac.course_id = c.id
                    JOIN sections s ON ac.section_id = s.id
                    WHERE ac.id = ?
                """, (assigned_course_id,))
                
                course_info = cursor.fetchone()
                if not course_info:
                    continue
                
                section_id, course_id, course_name, section_name, academic_year, semester = course_info
                
                # Find students in this section
                section_students = [s for s in students_list if s[3] == section_id]
                
                if not section_students:
                    continue
                
                # Filter students who haven't taken this course before
                eligible_students = []
                for student_id, student_first, student_last, student_section in section_students:
                    if student_id not in student_course_tracking:
                        student_course_tracking[student_id] = set()
                    
                    # Only add students who haven't taken this specific course before
                    if course_id not in student_course_tracking[student_id]:
                        eligible_students.append((student_id, student_first, student_last, student_section))
                        # Mark this course as taken by this student
                        student_course_tracking[student_id].add(course_id)
                
                if not eligible_students:
                    logger.info(f"No eligible students for course {course_name} section {section_name} - all students have already taken this course")
                    continue
                
                logger.info(f"Course {course_name} section {section_name}: {len(eligible_students)} eligible students (filtered from {len(section_students)} total section students)")
                
                # Determine semester date ranges
                year_parts = academic_year.split('-')
                start_year = int(year_parts[0])
                end_year = int(year_parts[1])
                
                if semester == "1st Semester":
                    # September to January
                    start_date = datetime(start_year, 9, 1)
                    end_date = datetime(end_year, 1, 31)
                elif semester == "2nd Semester":
                    # February to June
                    start_date = datetime(end_year, 2, 1)
                    end_date = datetime(end_year, 6, 30)
                else:  # Summer
                    # July to August
                    start_date = datetime(end_year, 7, 1)
                    end_date = datetime(end_year, 8, 31)
                
                # Only generate data for completed semesters or up to current date for current semester
                if start_date > current_date:
                    continue  # Skip future semesters
                    
                # Limit end date to current date for ongoing semesters
                if end_date > current_date:
                    end_date = current_date
                
                # Get the schedule for this course to determine class days
                cursor.execute("""
                    SELECT day_of_week FROM schedules 
                    WHERE assigned_course_id = ?
                """, (assigned_course_id,))
                schedule_days = [row[0] for row in cursor.fetchall()]
                
                if not schedule_days:
                    continue
                
                # Map day names to weekday numbers
                day_mapping = {
                    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
                    'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
                }
                class_weekdays = [day_mapping[day] for day in schedule_days if day in day_mapping]
                
                # Generate class schedule based on actual academic calendar and Philippine holidays
                class_days = []
                suspended_days = []
                current_check_date = start_date
                
                while current_check_date <= end_date:
                    # Check if this date falls on a scheduled class day
                    if current_check_date.weekday() in class_weekdays:
                        # Check if classes are suspended (holidays, etc.)
                        if is_class_suspended(current_check_date, semester):
                            suspended_days.append(current_check_date)
                            total_suspensions += 1
                        else:
                            class_days.append(current_check_date)
                            total_class_days_generated += 1
                    current_check_date += timedelta(days=1)
                
                if suspended_days:
                    logger.info(f"Course {course_name} section {section_name} ({academic_year} {semester}): {len(suspended_days)} days suspended due to holidays/events")
                
                logger.info(f"Course {course_name} section {section_name} ({academic_year} {semester}): {len(class_days)} class days from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                
                # Generate attendance for each class day using only eligible students
                for class_date in class_days:
                    for student_id, student_first, student_last, _ in eligible_students:
                        if student_id not in student_performance:
                            continue
                        
                        perf = student_performance[student_id]
                        
                        # Determine attendance based on student profile
                        base_rate = perf['attendance_rate']
                        consistency = perf['consistency']
                        
                        # Add seasonal variations (more nuanced for top university)
                        month = class_date.month
                        seasonal_modifier = 1.0
                        
                        # Academic calendar considerations
                        if month == 12:  # December - pre-Christmas stress, lower attendance
                            seasonal_modifier = 0.92
                        elif month == 6:  # June - end of semester fatigue
                            seasonal_modifier = 0.94
                        elif month in [1, 2]:  # January-February - post-holiday motivation
                            seasonal_modifier = 1.03
                        elif month in [9, 10]:  # September-October - start of semester enthusiasm
                            seasonal_modifier = 1.05
                        elif month in [7, 8]:  # July-August - summer semester (more focused students)
                            seasonal_modifier = 1.02
                        elif month in [3, 4]:  # March-April - midterm period stress
                            seasonal_modifier = 0.96
                        elif month == 5:  # May - finals preparation, high attendance
                            seasonal_modifier = 1.04
                        elif month == 11:  # November - good academic momentum
                            seasonal_modifier = 1.02
                        
                        # Day of week effect (Monday blues, Friday fatigue)
                        day_of_week = class_date.weekday()
                        day_modifier = 1.0
                        if day_of_week == 0:  # Monday
                            day_modifier = 0.97
                        elif day_of_week == 4:  # Friday
                            day_modifier = 0.98
                        elif day_of_week in [1, 2, 3]:  # Tuesday, Wednesday, Thursday
                            day_modifier = 1.01
                        
                        # Weather/calamity considerations (rainy season in PH)
                        weather_modifier = 1.0
                        if month in [6, 7, 8, 9]:  # Rainy season
                            if random.random() < 0.15:  # 15% chance of bad weather affecting attendance
                                weather_modifier = 0.85
                        
                        attendance_probability = base_rate * seasonal_modifier * day_modifier * weather_modifier
                        
                        # Add small random variation based on consistency
                        random_variation = (random.uniform(-0.05, 0.05) * (1 - consistency))
                        attendance_probability += random_variation
                        
                        # Ensure probability stays within bounds
                        attendance_probability = max(0.1, min(0.99, attendance_probability))
                        
                        # Determine attendance status
                        if random.random() < attendance_probability:
                            # Student attends - determine if present or late
                            # Top university students are generally more punctual
                            late_probability = {
                                'excellent': 0.02,    # 2% late rate for excellent students
                                'very_good': 0.04,    # 4% late rate
                                'good': 0.07,         # 7% late rate
                                'average': 0.12,      # 12% late rate
                                'poor': 0.18          # 18% late rate
                            }
                            status = 'late' if random.random() < late_probability[perf['category']] else 'present'
                        else:
                            status = 'absent'
                        
                        # Check if attendance already exists
                        cursor.execute("""
                            SELECT id FROM attendance_logs 
                            WHERE user_id = ? AND assigned_course_id = ? AND date = ?
                        """, (student_id, assigned_course_id, class_date.strftime('%Y-%m-%d')))
                        
                        if cursor.fetchone():
                            continue
                        
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
        
        # Log student course distribution
        total_unique_enrollments = 0
        for student_id, courses_taken in student_course_tracking.items():
            total_unique_enrollments += len(courses_taken)
            cursor.execute("SELECT first_name, last_name FROM users WHERE id = ?", (student_id,))
            student_name = cursor.fetchone()
            if student_name and len(courses_taken) > 0:
                logger.info(f"Student {student_name[0]} {student_name[1]} enrolled in {len(courses_taken)} unique courses")
        
        logger.info(f"Total unique student-course enrollments: {total_unique_enrollments}")
        
        conn.commit()
        
        # Log final statistics with holiday information
        cursor.execute("SELECT COUNT(*) FROM assigned_courses")
        course_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM schedules")
        schedule_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attendance_logs")
        attendance_count = cursor.fetchone()[0]
        
        # Calculate overall attendance statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present,
                SUM(CASE WHEN status = 'late' THEN 1 ELSE 0 END) as late,
                SUM(CASE WHEN status = 'absent' THEN 1 ELSE 0 END) as absent
            FROM attendance_logs
        """)
        overall_stats = cursor.fetchone()
        
        if overall_stats and overall_stats[0] > 0:
            total_records = overall_stats[0]
            present = overall_stats[1]
            late = overall_stats[2]
            absent = overall_stats[3]
            
            overall_attendance_rate = ((present + late) / total_records) * 100
            present_rate = (present / total_records) * 100
            late_rate = (late / total_records) * 100
            absent_rate = (absent / total_records) * 100
            
            logger.info(f"✓ Overall attendance statistics:")
            logger.info(f"  - Total records: {total_records}")
            logger.info(f"  - Overall attendance rate: {overall_attendance_rate:.1f}%")
            logger.info(f"  - Present: {present} ({present_rate:.1f}%)")
            logger.info(f"  - Late: {late} ({late_rate:.1f}%)")
            logger.info(f"  - Absent: {absent} ({absent_rate:.1f}%)")
        
        # Show attendance by academic year, semester, and month
        cursor.execute("""
            SELECT 
                ac.academic_year,
                ac.semester,
                substr(al.date, 1, 7) as month,
                COUNT(*) as total_records,
                SUM(CASE WHEN al.status = 'present' THEN 1 ELSE 0 END) as present,
                SUM(CASE WHEN al.status = 'late' THEN 1 ELSE 0 END) as late,
                SUM(CASE WHEN al.status = 'absent' THEN 1 ELSE 0 END) as absent
            FROM attendance_logs al
            JOIN assigned_courses ac ON al.assigned_course_id = ac.id
            GROUP BY ac.academic_year, ac.semester, month 
            ORDER BY ac.academic_year, ac.semester, month
        """)
        detailed_stats = cursor.fetchall()
        
        logger.info(f"✓ Created {course_count} assigned courses across all semesters")
        logger.info(f"✓ Created {schedule_count} schedule entries")
        logger.info(f"✓ Created {attendance_count} attendance logs")
        logger.info(f"✓ Total class days generated: {total_class_days_generated}")
        logger.info(f"✓ Total days suspended (holidays): {total_suspensions}")
        
        logger.info("Detailed attendance distribution by semester (including holiday effects):")
        current_ay = None
        current_sem = None
        for academic_year, semester, month, total, present, late, absent in detailed_stats:
            if academic_year != current_ay or semester != current_sem:
                logger.info(f"\n{academic_year} - {semester}:")
                current_ay = academic_year
                current_sem = semester
            
            attendance_rate = ((present + late) / total * 100) if total > 0 else 0
            present_rate = (present / total * 100) if total > 0 else 0
            logger.info(f"  {month}: {total} records, {present} present ({present_rate:.1f}%), {late} late, {absent} absent, overall rate: {attendance_rate:.1f}%")
        
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
        
        logger.info("Creating comprehensive seed users...")
        
        # Get status IDs for assignments
        cursor.execute("SELECT id, name, user_type FROM statuses")
        statuses = cursor.fetchall()
        
        student_statuses = {s[1]: s[0] for s in statuses if s[2] == 'student'}
        faculty_statuses = {s[1]: s[0] for s in statuses if s[2] == 'faculty'}
        
        logger.info(f"Found statuses - Students: {list(student_statuses.keys())}, Faculty: {list(faculty_statuses.keys())}")
        
        # Enhanced faculty data (30 faculty members)
        faculty_data = [
            # Department Heads and Senior Faculty
            {'first_name': 'Dr. Maria', 'last_name': 'Santos', 'email': 'maria.santos@pup.edu.ph', 'birthday': '1975-03-15', 'password': 'faculty123', 'contact_number': '09123456789', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2015-001', 'status': 'Tenured'},
            {'first_name': 'Prof. John', 'last_name': 'Doe', 'email': 'john.doe@pup.edu.ph', 'birthday': '1978-07-22', 'password': 'faculty123', 'contact_number': '09234567890', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2016-002', 'status': 'Tenured'},
            {'first_name': 'Dr. Jane', 'last_name': 'Smith', 'email': 'jane.smith@pup.edu.ph', 'birthday': '1980-11-30', 'password': 'faculty123', 'contact_number': '09345678901', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2017-003', 'status': 'Tenured'},
            {'first_name': 'Dr. Patricia', 'last_name': 'Reyes', 'email': 'patricia.reyes@pup.edu.ph', 'birthday': '1973-09-12', 'password': 'faculty123', 'contact_number': '09456789012', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2014-004', 'status': 'Tenured'},
            {'first_name': 'Prof. Michael', 'last_name': 'Torres', 'email': 'michael.torres@pup.edu.ph', 'birthday': '1979-01-28', 'password': 'faculty123', 'contact_number': '09567890123', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2018-005', 'status': 'Tenure Track'},
            
            # Associate Professors
            {'first_name': 'Dr. Sarah', 'last_name': 'Villanueva', 'email': 'sarah.villanueva@pup.edu.ph', 'birthday': '1982-12-05', 'password': 'faculty123', 'contact_number': '09678901234', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2019-006', 'status': 'Tenure Track'},
            {'first_name': 'Prof. Robert', 'last_name': 'Garcia', 'email': 'robert.garcia@pup.edu.ph', 'birthday': '1981-04-18', 'password': 'faculty123', 'contact_number': '09789012345', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2020-007', 'status': 'Active'},
            {'first_name': 'Dr. Anna', 'last_name': 'Martinez', 'email': 'anna.martinez@pup.edu.ph', 'birthday': '1984-08-25', 'password': 'faculty123', 'contact_number': '09890123456', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2020-008', 'status': 'Active'},
            {'first_name': 'Prof. David', 'last_name': 'Lopez', 'email': 'david.lopez@pup.edu.ph', 'birthday': '1983-06-14', 'password': 'faculty123', 'contact_number': '09901234567', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2021-009', 'status': 'Active'},
            {'first_name': 'Dr. Elena', 'last_name': 'Cruz', 'email': 'elena.cruz@pup.edu.ph', 'birthday': '1985-10-03', 'password': 'faculty123', 'contact_number': '09012345678', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2021-010', 'status': 'Active'},
            
            # Assistant Professors
            {'first_name': 'Prof. James', 'last_name': 'Rodriguez', 'email': 'james.rodriguez@pup.edu.ph', 'birthday': '1986-02-20', 'password': 'faculty123', 'contact_number': '09123456780', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2022-011', 'status': 'Probationary'},
            {'first_name': 'Dr. Lisa', 'last_name': 'Fernandez', 'email': 'lisa.fernandez@pup.edu.ph', 'birthday': '1987-05-17', 'password': 'faculty123', 'contact_number': '09234567891', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2022-012', 'status': 'Probationary'},
            {'first_name': 'Prof. Carlos', 'last_name': 'Mendoza', 'email': 'carlos.mendoza@pup.edu.ph', 'birthday': '1988-09-11', 'password': 'faculty123', 'contact_number': '09345678902', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2023-013', 'status': 'Probationary'},
            {'first_name': 'Dr. Michelle', 'last_name': 'Perez', 'email': 'michelle.perez@pup.edu.ph', 'birthday': '1989-12-08', 'password': 'faculty123', 'contact_number': '09456789013', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2023-014', 'status': 'Active'},
            {'first_name': 'Prof. Kevin', 'last_name': 'Gonzales', 'email': 'kevin.gonzales@pup.edu.ph', 'birthday': '1990-03-22', 'password': 'faculty123', 'contact_number': '09567890124', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2024-015', 'status': 'Active'},
            
            # Additional Faculty (15 more for comprehensive coverage)
            {'first_name': 'Dr. Rachel', 'last_name': 'Rivera', 'email': 'rachel.rivera@pup.edu.ph', 'birthday': '1981-07-30', 'password': 'faculty123', 'contact_number': '09678901235', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2019-016', 'status': 'Tenure Track'},
            {'first_name': 'Prof. Mark', 'last_name': 'Diaz', 'email': 'mark.diaz@pup.edu.ph', 'birthday': '1985-11-15', 'password': 'faculty123', 'contact_number': '09789012346', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2021-017', 'status': 'Active'},
            {'first_name': 'Dr. Catherine', 'last_name': 'Morales', 'email': 'catherine.morales@pup.edu.ph', 'birthday': '1983-04-12', 'password': 'faculty123', 'contact_number': '09890123457', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2020-018', 'status': 'Active'},
            {'first_name': 'Prof. Steven', 'last_name': 'Castillo', 'email': 'steven.castillo@pup.edu.ph', 'birthday': '1987-08-07', 'password': 'faculty123', 'contact_number': '09901234568', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2022-019', 'status': 'Probationary'},
            {'first_name': 'Dr. Amanda', 'last_name': 'Ramos', 'email': 'amanda.ramos@pup.edu.ph', 'birthday': '1986-01-25', 'password': 'faculty123', 'contact_number': '09012345679', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2022-020', 'status': 'Active'},
            {'first_name': 'Prof. Daniel', 'last_name': 'Herrera', 'email': 'daniel.herrera@pup.edu.ph', 'birthday': '1988-06-18', 'password': 'faculty123', 'contact_number': '09123456781', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2023-021', 'status': 'Active'},
            {'first_name': 'Dr. Nicole', 'last_name': 'Flores', 'email': 'nicole.flores@pup.edu.ph', 'birthday': '1984-09-03', 'password': 'faculty123', 'contact_number': '09234567892', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2021-022', 'status': 'Active'},
            {'first_name': 'Prof. Anthony', 'last_name': 'Valdez', 'email': 'anthony.valdez@pup.edu.ph', 'birthday': '1989-12-14', 'password': 'faculty123', 'contact_number': '09345678903', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2023-023', 'status': 'Probationary'},
            {'first_name': 'Dr. Stephanie', 'last_name': 'Jimenez', 'email': 'stephanie.jimenez@pup.edu.ph', 'birthday': '1987-05-09', 'password': 'faculty123', 'contact_number': '09456789014', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2022-024', 'status': 'Active'},
            {'first_name': 'Prof. Jason', 'last_name': 'Aguilar', 'email': 'jason.aguilar@pup.edu.ph', 'birthday': '1990-02-28', 'password': 'faculty123', 'contact_number': '09567890125', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2024-025', 'status': 'Active'},
            {'first_name': 'Dr. Jennifer', 'last_name': 'Vargas', 'email': 'jennifer.vargas@pup.edu.ph', 'birthday': '1985-10-21', 'password': 'faculty123', 'contact_number': '09678901236', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2021-026', 'status': 'Active'},
            {'first_name': 'Prof. Ryan', 'last_name': 'Ortega', 'email': 'ryan.ortega@pup.edu.ph', 'birthday': '1988-07-16', 'password': 'faculty123', 'contact_number': '09789012347', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2023-027', 'status': 'Probationary'},
            {'first_name': 'Dr. Melissa', 'last_name': 'Gutierrez', 'email': 'melissa.gutierrez@pup.edu.ph', 'birthday': '1986-11-05', 'password': 'faculty123', 'contact_number': '09890123458', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2022-028', 'status': 'Active'},
            {'first_name': 'Prof. Brian', 'last_name': 'Medina', 'email': 'brian.medina@pup.edu.ph', 'birthday': '1991-04-13', 'password': 'faculty123', 'contact_number': '09901234569', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2024-029', 'status': 'Active'},
            {'first_name': 'Dr. Laura', 'last_name': 'Sandoval', 'email': 'laura.sandoval@pup.edu.ph', 'birthday': '1984-08-27', 'password': 'faculty123', 'contact_number': '09012345680', 'role': 'Faculty', 'verified': 1, 'user_type': 'faculty', 'employee_number': 'EMP-2021-030', 'status': 'Active'}
        ]
        
        # Generate 50 comprehensive student data
        programs = [
            'Bachelor of Science in Information Technology',
            'Bachelor of Science in Computer Science', 
            'Bachelor of Science in Information Systems',
            'Bachelor of Science in Computer Engineering',
            'Bachelor of Science in Software Engineering'
        ]
        
        # Define realistic section distributions per program (adjusted for 50 students total)
        program_sections = {
            'Bachelor of Science in Information Technology': ['1-1', '1-2', '2-1', '2-2', '3-1', '4-1'],  # Most popular - 15 students
            'Bachelor of Science in Computer Science': ['1-1', '2-1', '3-1', '4-1'],  # Second most popular - 12 students
            'Bachelor of Science in Information Systems': ['1-1', '2-1', '3-1'],  # Moderate - 10 students
            'Bachelor of Science in Computer Engineering': ['1-1', '2-1'],  # Smaller - 8 students
            'Bachelor of Science in Software Engineering': ['1-1']  # Newest/smallest - 5 students
        }
        
        # Define realistic student name pools
        first_names = [
            # Common male first names
            'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Charles', 'Thomas', 'Daniel',
            'Matthew', 'Anthony', 'Mark', 'Donald', 'Steven', 'Paul', 'Andrew', 'Joshua', 'Ryan', 'Kevin',
            'Brian', 'George', 'Timothy', 'Ronald', 'Jason', 'Jeffrey', 'Jacob', 'Nicholas', 'Christian', 'Jordan',
            'Eric', 'Aaron', 'Charles', 'Austin', 'Dylan', 'Jesse', 'Ethan', 'Adam', 'Gavin', 'Rafael',
            'Luis', 'Miguel', 'Diego', 'Fernando', 'Antonio', 'Sebastian', 'Adrian', 'Gabriel', 'Oscar', 'Julian',
            
            # Common female first names
            'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen',
            'Nancy', 'Lisa', 'Betty', 'Helen', 'Sandra', 'Donna', 'Carol', 'Ruth', 'Sharon', 'Michelle',
            'Laura', 'Kimberly', 'Deborah', 'Dorothy', 'Nancy', 'Helen', 'Maria', 'Ana', 'Carmen', 'Rosa',
            'Teresa', 'Luz', 'Esperanza', 'Concepcion', 'Remedios', 'Pilar', 'Angela', 'Cristina', 'Veronica', 'Monica',
            'Claudia', 'Adriana', 'Beatriz', 'Cecilia', 'Diana', 'Elena', 'Joy', 'Rose', 'Iris', 'Lily'
        ]
        
        last_names = [
            'Santos', 'Reyes', 'Cruz', 'Bautista', 'Ocampo', 'Garcia', 'Mendoza', 'Torres', 'Tomas', 'Andres',
            'Marquez', 'Romualdez', 'Mercado', 'Agbayani', 'Tolentino', 'Castillo', 'Villanueva', 'Soriano', 'Abad', 'Hernandez',
            'Morales', 'Castro', 'Ramos', 'Gutierrez', 'Gonzales', 'Rodriguez', 'Perez', 'Sanchez', 'Ramirez', 'Flores',
            'Rivera', 'Martinez', 'Gomez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore',
            'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris', 'Clark', 'Lewis', 'Robinson', 'Walker',
            'Dela Cruz', 'De Leon', 'Del Rosario', 'Fernandez', 'Aguilar', 'Jimenez', 'Vargas', 'Herrera', 'Medina', 'Ruiz'
        ]
        
        student_data = []
        student_number = 1
        
        # Define exact student counts per program to total 50
        program_student_counts = {
            'Bachelor of Science in Information Technology': 15,
            'Bachelor of Science in Computer Science': 12,
            'Bachelor of Science in Information Systems': 10,
            'Bachelor of Science in Computer Engineering': 8,
            'Bachelor of Science in Software Engineering': 5
        }
        
        # Generate students for each program
        for program in programs:
            sections = program_sections[program]
            total_students_for_program = program_student_counts[program]
            
            # Distribute students evenly across sections
            students_per_section = total_students_for_program // len(sections)
            remaining_students = total_students_for_program % len(sections)
            
            for section_idx, section in enumerate(sections):
                # Add remaining students to first sections
                actual_students = students_per_section + (1 if section_idx < remaining_students else 0)
                
                for i in range(actual_students):
                    first_name = random.choice(first_names)
                    last_name = random.choice(last_names)
                    
                    # Generate realistic birth years based on year level
                    year_level = section.split('-')[0]
                    if year_level == '1':
                        birth_year = random.randint(2003, 2005)  # 1st year: 19-21 years old
                    elif year_level == '2':
                        birth_year = random.randint(2002, 2004)  # 2nd year: 20-22 years old  
                    elif year_level == '3':
                        birth_year = random.randint(2001, 2003)  # 3rd year: 21-23 years old
                    else:  # 4th year
                        birth_year = random.randint(2000, 2002)  # 4th year: 22-24 years old
                    
                    birth_month = random.randint(1, 12)
                    birth_day = random.randint(1, 28)
                    birthday = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
                    
                    # Generate contact number
                    contact_number = f"09{random.randint(100000000, 999999999)}"
                    
                    # Generate student number with year and sequence
                    student_number_str = f"2024-{student_number:03d}"
                    
                    # Determine year level text
                    year_levels = {'1': '1st Year', '2': '2nd Year', '3': '3rd Year', '4': '4th Year'}
                    year_text = year_levels[year_level]
                    
                    # Realistic status distribution
                    status_weights = [
                        ('Enrolled', 90),     # 90% enrolled
                        ('On Leave', 5),      # 5% on leave
                        ('Suspended', 2),     # 2% suspended
                        ('Graduated', 2),     # 2% graduated (mostly 4th years)
                        ('Dropout', 1)        # 1% dropout
                    ]
                    
                    # Adjust status based on year level
                    if year_level == '4':
                        status_weights = [('Enrolled', 75), ('Graduated', 20), ('On Leave', 3), ('Suspended', 1), ('Dropout', 1)]
                    elif year_level == '1':
                        status_weights = [('Enrolled', 95), ('On Leave', 3), ('Suspended', 1), ('Graduated', 0), ('Dropout', 1)]
                    
                    # Select status based on weights
                    statuses_list, weights = zip(*status_weights)
                    status = random.choices(statuses_list, weights=weights)[0]
                    
                    student_data.append({
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': f"{first_name.lower()}.{last_name.lower().replace(' ', '')}@iskolarngbayan.pup.edu.ph",
                        'birthday': birthday,
                        'password': 'student123',
                        'contact_number': contact_number,
                        'role': 'Student',
                        'verified': 1,
                        'user_type': 'student',
                        'student_number': student_number_str,
                        'program': program,
                        'section': section,
                        'year': year_text,
                        'status': status
                    })
                    
                    student_number += 1
        
        # Add original key students
        key_students = [
            {'first_name': 'Shadrack', 'last_name': 'Castro', 'email': 'shadrack.castro@iskolarngbayan.pup.edu.ph', 'birthday': '2002-05-10', 'password': 'student123', 'contact_number': '09456789012', 'role': 'Student', 'verified': 1, 'user_type': 'student', 'student_number': '2024-KEY001', 'program': 'Bachelor of Science in Information Technology', 'section': '3-1', 'year': '3rd Year', 'status': 'Enrolled'},
            {'first_name': 'Jerlee', 'last_name': 'Alipio', 'email': 'jerlee.alipio@iskolarngbayan.pup.edu.ph', 'birthday': '2001-09-18', 'password': 'student123', 'contact_number': '09567890123', 'role': 'Student', 'verified': 1, 'user_type': 'student', 'student_number': '2024-KEY002', 'program': 'Bachelor of Science in Computer Science', 'section': '3-1', 'year': '3rd Year', 'status': 'Enrolled'},
            {'first_name': 'Steven', 'last_name': 'Masangcay', 'email': 'steven.masangcay@iskolarngbayan.pup.edu.ph', 'birthday': '2000-12-25', 'password': 'student123', 'contact_number': '09678901234', 'role': 'Student', 'verified': 1, 'user_type': 'student', 'student_number': '2024-KEY003', 'program': 'Bachelor of Science in Information Technology', 'section': '4-1', 'year': '4th Year', 'status': 'Enrolled'},
            {'first_name': 'John Mathew', 'last_name': 'Parocha', 'email': 'john.parocha@iskolarngbayan.pup.edu.ph', 'birthday': '1999-08-14', 'password': 'student123', 'contact_number': '09789012345', 'role': 'Student', 'verified': 1, 'user_type': 'student', 'student_number': '2024-KEY004', 'program': 'Bachelor of Science in Information Systems', 'section': '4-1', 'year': '4th Year', 'status': 'Graduated'}
        ]
        
        # Combine all user data
        all_users_data = faculty_data + student_data + key_students
        
        logger.info(f"Total users to create: {len(all_users_data)} ({len(faculty_data)} faculty + {len(student_data)} students + {len(key_students)} key students)")
        
        # Begin transaction
        conn.execute("BEGIN TRANSACTION")
        
        for user_data in all_users_data:
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
            
            # Insert into role-specific tables
            if user_data['user_type'] == 'student':
                # Get section ID for this student
                section_key = f"{user_data['section']}-{user_data['program']}"
                section_id = section_ids.get(section_key)
                
                cursor.execute("""
                    INSERT INTO students (user_id, student_number, section)
                    VALUES (?, ?, ?)
                """, (user_id, user_data['student_number'], section_id))
                
            elif user_data['user_type'] == 'faculty':
                cursor.execute("""
                    INSERT INTO faculties (user_id, employee_number)
                    VALUES (?, ?)
                """, (user_id, user_data['employee_number']))
        
        # Commit transaction
        conn.commit()
        logger.info("Successfully created comprehensive seed users!")
        
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
        print("\nDatabase seeded successfully!")
    else:
        print("\nFailed to seed database!")
        exit(1)
