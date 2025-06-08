import random
from datetime import datetime
from .base_seeder import BaseSeeder
from .config import SEEDER_CONFIG, get_current_semester, get_academic_year, get_academic_years_to_generate

class CourseAssignmentSeeder(BaseSeeder):
    """Seeder for course assignments and schedules"""
    
    def seed(self):
        """Seed course assignments and schedules"""
        try:
            conn = self.get_connection()
            self.logger.info("Seeding course assignments...")
            
            # Create comprehensive course structure first
            self._create_comprehensive_courses(conn)
            
            # Get faculty, courses, and sections
            faculty_list = self._get_faculty(conn)
            courses_list = self._get_courses(conn)
            sections_list = self._get_sections(conn)
            
            # Create assigned courses with proper year-level mapping
            assigned_course_ids = self._create_year_based_assignments(conn, faculty_list, courses_list, sections_list)
            
            # Create schedules for assigned courses
            self._create_schedules(conn, assigned_course_ids)
            
            conn.commit()
            
            # Log summary
            self.log_summary(conn, "assigned_courses", "Course assignments")
            self.log_summary(conn, "schedules", "Schedules")
            
            conn.close()
            return True, assigned_course_ids
            
        except Exception as e:
            self.logger.error(f"Error seeding course assignments: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False, []
    
    def _create_comprehensive_courses(self, conn):
        """Create a comprehensive set of courses for 2 programs with summer only in 3rd year"""
        current_time = self.get_current_time()
        
        # Get all programs
        cursor = self.execute_query(conn, "SELECT id, name, acronym FROM programs")
        programs = cursor.fetchall()
        
        # Define comprehensive course structure for 2 programs only
        course_structure = {
            'Bachelor of Science in Information Technology': {
                1: {
                    '1st Semester': [
                        {'name': 'Introduction to Computing', 'code': 'IT-1101', 'description': 'Fundamentals of computing and digital literacy'},
                        {'name': 'Programming Fundamentals', 'code': 'IT-1102', 'description': 'Basic programming concepts and logic'},
                        {'name': 'Computer Hardware Fundamentals', 'code': 'IT-1103', 'description': 'Computer components and assembly'},
                        {'name': 'Mathematics in the Modern World', 'code': 'GE-1101', 'description': 'Applied mathematics for IT'},
                        {'name': 'Understanding the Self', 'code': 'GE-1102', 'description': 'Personal development course'},
                        {'name': 'Readings in Philippine History', 'code': 'GE-1103', 'description': 'Philippine historical perspectives'}
                    ],
                    '2nd Semester': [
                        {'name': 'Object-Oriented Programming', 'code': 'IT-1201', 'description': 'Object-oriented programming principles'},
                        {'name': 'Discrete Mathematics', 'code': 'IT-1202', 'description': 'Mathematical foundations for computing'},
                        {'name': 'Web Systems and Technologies', 'code': 'IT-1203', 'description': 'Web development fundamentals'},
                        {'name': 'Purposive Communication', 'code': 'GE-1201', 'description': 'Communication skills development'},
                        {'name': 'Art Appreciation', 'code': 'GE-1202', 'description': 'Arts and culture appreciation'},
                        {'name': 'Physical Education 1', 'code': 'PE-1201', 'description': 'Physical fitness and wellness'}
                    ]
                },
                2: {
                    '1st Semester': [
                        {'name': 'Data Structures and Algorithms', 'code': 'IT-2101', 'description': 'Advanced programming concepts and algorithmic thinking'},
                        {'name': 'Database Management Systems', 'code': 'IT-2102', 'description': 'Database design and implementation'},
                        {'name': 'Computer Networks', 'code': 'IT-2103', 'description': 'Network fundamentals and protocols'},
                        {'name': 'Statistics and Probability', 'code': 'IT-2104', 'description': 'Statistical analysis for IT applications'},
                        {'name': 'Ethics', 'code': 'GE-2101', 'description': 'Moral and ethical foundations'},
                        {'name': 'National Service Training Program 1', 'code': 'NSTP-2101', 'description': 'Civic welfare training service'}
                    ],
                    '2nd Semester': [
                        {'name': 'Advanced Database Systems', 'code': 'IT-2201', 'description': 'Advanced database concepts and optimization'},
                        {'name': 'Software Engineering', 'code': 'IT-2202', 'description': 'Software development methodologies'},
                        {'name': 'Network Administration', 'code': 'IT-2203', 'description': 'Network management and security'},
                        {'name': 'Human Computer Interaction', 'code': 'IT-2204', 'description': 'User interface design principles'},
                        {'name': 'Science, Technology and Society', 'code': 'GE-2201', 'description': 'Impact of technology on society'},
                        {'name': 'Physical Education 2', 'code': 'PE-2201', 'description': 'Advanced physical fitness'}
                    ]
                },
                3: {
                    '1st Semester': [
                        {'name': 'Machine Learning', 'code': 'IT-3101', 'description': 'Introduction to machine learning algorithms and applications'},
                        {'name': 'System Analysis and Design', 'code': 'IT-3102', 'description': 'System development lifecycle and design patterns'},
                        {'name': 'Mobile Application Development', 'code': 'IT-3103', 'description': 'Mobile app development for Android and iOS'},
                        {'name': 'Information Security', 'code': 'IT-3104', 'description': 'Cybersecurity principles and practices'},
                        {'name': 'Life and Works of Rizal', 'code': 'GE-3101', 'description': 'Philippine national hero study'},
                        {'name': 'Technical Writing', 'code': 'IT-3105', 'description': 'Technical documentation and communication'}
                    ],
                    '2nd Semester': [
                        {'name': 'Advanced Web Development', 'code': 'IT-3201', 'description': 'Full-stack web development with modern frameworks'},
                        {'name': 'Cloud Computing', 'code': 'IT-3202', 'description': 'Cloud platforms and services'},
                        {'name': 'Data Mining and Analytics', 'code': 'IT-3203', 'description': 'Big data analysis and visualization'},
                        {'name': 'Project Management', 'code': 'IT-3204', 'description': 'IT project planning and execution'},
                        {'name': 'Contemporary World', 'code': 'GE-3201', 'description': 'Global issues and perspectives'},
                        {'name': 'Research Methods in IT', 'code': 'IT-3205', 'description': 'Research methodology for information technology'}
                    ],
                    'Summer': [
                        {'name': 'Internship/On-the-Job Training', 'code': 'IT-3301', 'description': 'Industry training and practical experience'},
                        {'name': 'IT Practicum', 'code': 'IT-3302', 'description': 'Hands-on IT practice and application'}
                    ]
                },
                4: {
                    '1st Semester': [
                        {'name': 'Capstone Project 1', 'code': 'IT-4101', 'description': 'Senior capstone project development and planning'},
                        {'name': 'IT Service Management', 'code': 'IT-4102', 'description': 'ITIL and service management frameworks'},
                        {'name': 'Enterprise Architecture', 'code': 'IT-4103', 'description': 'Enterprise-level system design and architecture'},
                        {'name': 'Advanced Database Administration', 'code': 'IT-4104', 'description': 'Database optimization and administration'},
                        {'name': 'IT Elective 1 - DevOps', 'code': 'IT-4105', 'description': 'Development and operations integration'},
                        {'name': 'Gender and Society', 'code': 'GE-4101', 'description': 'Gender studies and social awareness'}
                    ],
                    '2nd Semester': [
                        {'name': 'Capstone Project 2', 'code': 'IT-4201', 'description': 'Senior capstone project implementation and completion'},
                        {'name': 'IT Governance and Strategy', 'code': 'IT-4202', 'description': 'Strategic IT management and governance'},
                        {'name': 'Emerging Technologies', 'code': 'IT-4203', 'description': 'Latest trends and innovations in technology'},
                        {'name': 'Advanced Cybersecurity', 'code': 'IT-4204', 'description': 'Advanced information security and ethical hacking'},
                        {'name': 'IT Elective 2 - Blockchain Technology', 'code': 'IT-4205', 'description': 'Blockchain development and applications'},
                        {'name': 'Professional Development and Ethics', 'code': 'IT-4206', 'description': 'Professional skills and ethical practices in IT'}
                    ]
                }
            },
            'Bachelor of Science in Computer Science': {
                1: {
                    '1st Semester': [
                        {'name': 'Introduction to Programming', 'code': 'CS-1101', 'description': 'Basic programming fundamentals and problem solving'},
                        {'name': 'Calculus 1', 'code': 'CS-1102', 'description': 'Differential calculus for computer science'},
                        {'name': 'Discrete Mathematics 1', 'code': 'CS-1103', 'description': 'Logic, sets, and mathematical reasoning'},
                        {'name': 'Computer Fundamentals', 'code': 'CS-1104', 'description': 'Basic computer concepts and digital literacy'},
                        {'name': 'Understanding the Self', 'code': 'GE-1101', 'description': 'Personal development and self-awareness'},
                        {'name': 'Readings in Philippine History', 'code': 'GE-1103', 'description': 'Philippine historical perspectives'}
                    ],
                    '2nd Semester': [
                        {'name': 'Programming Languages', 'code': 'CS-1201', 'description': 'Multiple programming paradigms and languages'},
                        {'name': 'Calculus 2', 'code': 'CS-1202', 'description': 'Integral calculus and applications'},
                        {'name': 'Discrete Mathematics 2', 'code': 'CS-1203', 'description': 'Graph theory, combinatorics, and probability'},
                        {'name': 'Physics for Computer Science', 'code': 'CS-1204', 'description': 'Applied physics concepts for computing'},
                        {'name': 'Purposive Communication', 'code': 'GE-1201', 'description': 'Advanced communication skills'},
                        {'name': 'Physical Education 1', 'code': 'PE-1201', 'description': 'Physical fitness and wellness'}
                    ]
                },
                2: {
                    '1st Semester': [
                        {'name': 'Data Structures', 'code': 'CS-2101', 'description': 'Abstract data types and algorithmic structures'},
                        {'name': 'Computer Organization and Architecture', 'code': 'CS-2102', 'description': 'Computer hardware and system architecture'},
                        {'name': 'Linear Algebra', 'code': 'CS-2103', 'description': 'Mathematical foundations for computer graphics and ML'},
                        {'name': 'Statistics for Computer Science', 'code': 'CS-2104', 'description': 'Statistical methods and data analysis'},
                        {'name': 'Ethics in Computing', 'code': 'GE-2101', 'description': 'Computer ethics and professional responsibility'},
                        {'name': 'National Service Training Program 1', 'code': 'NSTP-2101', 'description': 'Civic welfare and community service'}
                    ],
                    '2nd Semester': [
                        {'name': 'Algorithms and Complexity', 'code': 'CS-2201', 'description': 'Algorithm design, analysis, and computational complexity'},
                        {'name': 'Operating Systems', 'code': 'CS-2202', 'description': 'OS concepts, processes, and system management'},
                        {'name': 'Database Systems', 'code': 'CS-2203', 'description': 'Database theory, design, and implementation'},
                        {'name': 'Software Engineering 1', 'code': 'CS-2204', 'description': 'Software development processes and methodologies'},
                        {'name': 'Science, Technology and Society', 'code': 'GE-2201', 'description': 'Impact of technology on society'},
                        {'name': 'Physical Education 2', 'code': 'PE-2201', 'description': 'Advanced physical fitness and sports'}
                    ]
                },
                3: {
                    '1st Semester': [
                        {'name': 'Machine Learning', 'code': 'CS-3101', 'description': 'ML algorithms, statistical learning, and data mining'},
                        {'name': 'Computer Networks', 'code': 'CS-3102', 'description': 'Network protocols, architecture, and security'},
                        {'name': 'Theory of Computation', 'code': 'CS-3103', 'description': 'Formal languages, automata, and computability'},
                        {'name': 'Computer Graphics', 'code': 'CS-3104', 'description': 'Graphics programming and 3D visualization'},
                        {'name': 'Life and Works of Rizal', 'code': 'GE-3101', 'description': 'Study of Philippine national hero'},
                        {'name': 'Software Engineering 2', 'code': 'CS-3105', 'description': 'Advanced software engineering and project management'}
                    ],
                    '2nd Semester': [
                        {'name': 'Artificial Intelligence', 'code': 'CS-3201', 'description': 'AI principles, search algorithms, and knowledge representation'},
                        {'name': 'Compiler Design', 'code': 'CS-3202', 'description': 'Language processors, parsers, and code generation'},
                        {'name': 'Human-Computer Interaction', 'code': 'CS-3203', 'description': 'UI/UX design principles and usability'},
                        {'name': 'Advanced Database Systems', 'code': 'CS-3204', 'description': 'Distributed databases and data warehousing'},
                        {'name': 'Contemporary World', 'code': 'GE-3201', 'description': 'Global perspectives and international relations'},
                        {'name': 'Research Methods in Computer Science', 'code': 'CS-3205', 'description': 'Scientific research methodology and technical writing'}
                    ],
                    'Summer': [
                        {'name': 'CS Practicum', 'code': 'CS-3301', 'description': 'Hands-on computer science practice and application'},
                        {'name': 'Industry Immersion', 'code': 'CS-3302', 'description': 'Real-world CS experience in industry settings'}
                    ]
                },
                4: {
                    '1st Semester': [
                        {'name': 'Thesis 1', 'code': 'CS-4101', 'description': 'Research thesis development and proposal'},
                        {'name': 'Parallel and Distributed Computing', 'code': 'CS-4102', 'description': 'Concurrent programming and distributed systems'},
                        {'name': 'Information Security and Cryptography', 'code': 'CS-4103', 'description': 'Advanced security and cryptographic algorithms'},
                        {'name': 'Advanced Algorithms', 'code': 'CS-4104', 'description': 'Complex algorithmic techniques and optimization'},
                        {'name': 'CS Elective 1 - Computer Vision', 'code': 'CS-4105', 'description': 'Image processing and computer vision algorithms'},
                        {'name': 'Gender and Society', 'code': 'GE-4101', 'description': 'Gender studies and social equality'}
                    ],
                    '2nd Semester': [
                        {'name': 'Thesis 2', 'code': 'CS-4201', 'description': 'Research thesis implementation and defense'},
                        {'name': 'Software Project Management', 'code': 'CS-4202', 'description': 'Managing large-scale software development projects'},
                        {'name': 'Natural Language Processing', 'code': 'CS-4203', 'description': 'Computational linguistics and text processing'},
                        {'name': 'Advanced Computer Architecture', 'code': 'CS-4204', 'description': 'High-performance computing and processor design'},
                        {'name': 'CS Elective 2 - Quantum Computing', 'code': 'CS-4205', 'description': 'Quantum algorithms and quantum programming'},
                        {'name': 'Professional Development in CS', 'code': 'CS-4206', 'description': 'Career preparation and professional ethics'}
                    ]
                }
            }
        }
        
        # Create courses for each program
        for program_id, program_name, program_acronym in programs:
            if program_name in course_structure:
                program_courses = course_structure[program_name]
                
                for year_level, semesters in program_courses.items():
                    for semester, courses in semesters.items():
                        for course_data in courses:
                            # Check if course already exists
                            existing = self.check_exists(conn, "courses", {
                                "code": course_data['code'],
                                "program_id": program_id
                            })
                            
                            if existing:
                                continue
                            
                            try:
                                self.execute_query(conn, """
                                    INSERT INTO courses (name, code, description, program_id, isDeleted, created_at, updated_at)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    course_data['name'], course_data['code'], course_data['description'],
                                    program_id, 0, current_time, current_time
                                ))
                                
                                self.logger.info(f"Created course: {course_data['name']} ({course_data['code']}) for {program_acronym}")
                                
                            except Exception as e:
                                self.logger.error(f"Failed to create course {course_data['name']}: {e}")
                                continue
    
    def _get_faculty(self, conn):
        """Get all faculty members"""
        cursor = self.execute_query(conn, """
            SELECT f.user_id, u.first_name, u.last_name
            FROM faculties f
            JOIN users u ON f.user_id = u.id
            WHERE u.role = 'Faculty' AND u.isDeleted = 0
        """)
        return cursor.fetchall()
    
    def _get_courses(self, conn):
        """Get all courses with program information"""
        cursor = self.execute_query(conn, """
            SELECT c.id, c.name, c.code, p.name as program_name, p.acronym
            FROM courses c
            JOIN programs p ON c.program_id = p.id
        """)
        return cursor.fetchall()
    
    def _get_sections(self, conn):
        """Get all sections with program and year level information"""
        cursor = self.execute_query(conn, """
            SELECT s.id, s.name, p.name as program_name, p.acronym
            FROM sections s
            JOIN programs p ON s.program_id = p.id
        """)
        return cursor.fetchall()
    
    def _create_year_based_assignments(self, conn, faculty_list, courses_list, sections_list):
        """Create course assignments for multiple academic years dynamically"""
        assigned_course_ids = []
        current_time = self.get_current_time()
        
        # Get academic years to generate from config
        academic_years_to_generate = get_academic_years_to_generate()
        
        self.logger.info(f"Creating course assignments for academic years: {', '.join(academic_years_to_generate)}")
        
        # Only 3rd year has summer semester
        semesters = ["1st Semester", "2nd Semester"]
        
        # Group sections by program and year level
        sections_by_program_year = {}
        for section_id, section_name, program_name, program_acronym in sections_list:
            # Extract year level from section name (e.g., "1-1" -> year 1)
            try:
                year_level = int(section_name.split('-')[0])
            except:
                year_level = 1  # Default to first year if parsing fails
            
            key = (program_name, year_level)
            if key not in sections_by_program_year:
                sections_by_program_year[key] = []
            sections_by_program_year[key].append((section_id, section_name))
        
        # Group courses by program and extract year level from course code
        courses_by_program_year = {}
        for course_id, course_name, course_code, program_name, program_acronym in courses_list:
            # Extract year level from course code (e.g., "IT-2101" -> year 2)
            try:
                year_level = int(course_code.split('-')[1][0])
            except:
                year_level = 1  # Default to first year if parsing fails
            
            key = (program_name, year_level)
            if key not in courses_by_program_year:
                courses_by_program_year[key] = []
            courses_by_program_year[key].append((course_id, course_name, course_code))
        
        self.logger.info(f"Found {len(sections_by_program_year)} program-year combinations")
        self.logger.info(f"Found {len(courses_by_program_year)} course groups by program-year")
        
        # Create assignments for each academic year
        for academic_year in academic_years_to_generate:
            self.logger.info(f"Processing academic year: {academic_year}")
            
            # For each semester, assign courses to sections
            for semester in semesters:
                self.logger.info(f"Processing assignments for {semester} {academic_year}")
                
                # For each program-year combination
                for (program_name, year_level), sections in sections_by_program_year.items():
                    # Get courses for this program and year level
                    matching_courses = courses_by_program_year.get((program_name, year_level), [])
                    
                    if not matching_courses:
                        continue
                    
                    # Filter courses by semester (based on course code pattern)
                    semester_courses = self._filter_courses_by_semester(matching_courses, semester)
                    
                    if not semester_courses:
                        continue
                    
                    self.logger.info(f"Assigning {len(semester_courses)} courses to {len(sections)} sections for {program_name} Year {year_level} - {semester} {academic_year}")
                    
                    # Assign each course to ALL sections in this year level
                    for course_id, course_name, course_code in semester_courses:
                        # Assign one faculty member to teach this course across all sections
                        faculty_user_id, first_name, last_name = random.choice(faculty_list)
                        
                        for section_id, section_name in sections:
                            room = random.choice(SEEDER_CONFIG['rooms'])
                            
                            # Check if assignment already exists
                            existing = self.check_exists(conn, "assigned_courses", {
                                "faculty_id": faculty_user_id,
                                "course_id": course_id,
                                "section_id": section_id,
                                "academic_year": academic_year,
                                "semester": semester
                            })
                            
                            if existing:
                                assigned_course_ids.append(existing[0])
                                continue
                            
                            # Insert assigned course
                            cursor = self.execute_query(conn, """
                                INSERT INTO assigned_courses 
                                (faculty_id, course_id, section_id, academic_year, semester, room, isDeleted, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (faculty_user_id, course_id, section_id, academic_year, semester, room, 0, current_time, current_time))
                            
                            assigned_course_id = cursor.lastrowid
                            assigned_course_ids.append(assigned_course_id)
                    
                    self.logger.info(f"✓ Assigned courses for {program_name} Year {year_level} Section(s): {', '.join([s[1] for s in sections])} - {semester} {academic_year}")
            
            # Handle summer semester only for 3rd year for each academic year
            self.logger.info(f"Processing Summer semester assignments for 3rd year only - {academic_year}")
            summer_config = SEEDER_CONFIG['academic_calendar']['semesters']['Summer']
            self.logger.info(f"Summer period: {summer_config['description']}")
            
            for (program_name, year_level), sections in sections_by_program_year.items():
                if year_level == 3:  # Only 3rd year has summer
                    matching_courses = courses_by_program_year.get((program_name, year_level), [])
                    if matching_courses:
                        summer_courses = self._filter_courses_by_semester(matching_courses, "Summer")
                        if summer_courses:
                            self.logger.info(f"Assigning {len(summer_courses)} summer courses ({summer_config['description']}) to {len(sections)} sections for {program_name} Year 3 - {academic_year}")
                            
                            for course_id, course_name, course_code in summer_courses:
                                faculty_user_id, first_name, last_name = random.choice(faculty_list)
                                
                                for section_id, section_name in sections:
                                    room = random.choice(SEEDER_CONFIG['rooms'])
                                    
                                    # Check if assignment already exists
                                    existing = self.check_exists(conn, "assigned_courses", {
                                        "faculty_id": faculty_user_id,
                                        "course_id": course_id,
                                        "section_id": section_id,
                                        "academic_year": academic_year,
                                        "semester": "Summer"
                                    })
                                    
                                    if existing:
                                        assigned_course_ids.append(existing[0])
                                        continue
                                    
                                    # Insert assigned course
                                    cursor = self.execute_query(conn, """
                                        INSERT INTO assigned_courses 
                                        (faculty_id, course_id, section_id, academic_year, semester, room, isDeleted, created_at, updated_at)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (faculty_user_id, course_id, section_id, academic_year, "Summer", room, 0, current_time, current_time))
                                    
                                    assigned_course_id = cursor.lastrowid
                                    assigned_course_ids.append(assigned_course_id)
        
        self.logger.info(f"Total course assignments created across all academic years: {len(assigned_course_ids)}")
        return assigned_course_ids
    
    def _filter_courses_by_semester(self, courses, semester):
        """Filter courses based on semester pattern in course codes"""
        filtered_courses = []
        
        for course_id, course_name, course_code in courses:
            # Extract semester from course code (e.g., "IT-2101" -> 1st sem, "IT-2201" -> 2nd sem, "IT-2301" -> summer)
            try:
                code_parts = course_code.split('-')
                if len(code_parts) >= 2:
                    semester_digit = code_parts[1][1]  # Second digit indicates semester
                    
                    if semester == "1st Semester" and semester_digit == '1':
                        filtered_courses.append((course_id, course_name, course_code))
                    elif semester == "2nd Semester" and semester_digit == '2':
                        filtered_courses.append((course_id, course_name, course_code))
                    elif semester == "Summer" and semester_digit == '3':
                        filtered_courses.append((course_id, course_name, course_code))
            except:
                # If parsing fails, include in 1st semester by default
                if semester == "1st Semester":
                    filtered_courses.append((course_id, course_name, course_code))
        
        return filtered_courses
    
    def _create_schedules(self, conn, assigned_course_ids):
        """Create schedules for assigned courses"""
        current_time = self.get_current_time()
        days_of_week = SEEDER_CONFIG['course_schedule']['days_of_week']
        time_slots = SEEDER_CONFIG['course_schedule']['time_slots']
        
        for assigned_course_id in assigned_course_ids:
            # Most courses meet 2-3 times per week
            num_meetings = random.choice([2, 3])
            selected_days = random.sample(days_of_week, num_meetings)
            
            for day in selected_days:
                start_time, end_time = random.choice(time_slots)
                
                # Convert to datetime for storage
                today = datetime.now().date()
                start_datetime = datetime.combine(today, datetime.strptime(start_time, '%H:%M:%S').time())
                end_datetime = datetime.combine(today, datetime.strptime(end_time, '%H:%M:%S').time())
                
                self.execute_query(conn, """
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
