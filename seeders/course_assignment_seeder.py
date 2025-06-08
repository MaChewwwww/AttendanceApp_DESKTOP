import random
from datetime import datetime
from .base_seeder import BaseSeeder
from .config import SEEDER_CONFIG

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
        """Create a comprehensive set of courses for all programs and year levels"""
        current_time = self.get_current_time()
        
        # Get all programs
        cursor = self.execute_query(conn, "SELECT id, name, acronym FROM programs")
        programs = cursor.fetchall()
        
        # Define comprehensive course structure for all programs
        course_structure = {
            'Bachelor of Science in Information Technology': {
                1: {
                    '1st Semester': [
                        {'name': 'Introduction to Computing', 'code': 'IT-1101', 'description': 'Fundamentals of computing and digital literacy'},
                        {'name': 'Programming Fundamentals', 'code': 'IT-1102', 'description': 'Basic programming concepts and logic'},
                        {'name': 'Computer Hardware Fundamentals', 'code': 'IT-1103', 'description': 'Computer components and assembly'},
                        {'name': 'Mathematics in the Modern World', 'code': 'GE-1101', 'description': 'Applied mathematics for IT'},
                        {'name': 'Understanding the Self', 'code': 'GE-1102', 'description': 'Personal development course'}
                    ],
                    '2nd Semester': [
                        {'name': 'Object-Oriented Programming', 'code': 'IT-1201', 'description': 'Object-oriented programming principles'},
                        {'name': 'Discrete Mathematics', 'code': 'IT-1202', 'description': 'Mathematical foundations for computing'},
                        {'name': 'Web Systems and Technologies', 'code': 'IT-1203', 'description': 'Web development fundamentals'},
                        {'name': 'Purposive Communication', 'code': 'GE-1201', 'description': 'Communication skills development'},
                        {'name': 'Art Appreciation', 'code': 'GE-1202', 'description': 'Arts and culture appreciation'}
                    ],
                    'Summer': [
                        {'name': 'National Service Training Program', 'code': 'NSTP-1', 'description': 'Civic welfare training service'},
                        {'name': 'Physical Education 1', 'code': 'PE-1', 'description': 'Physical fitness and wellness'}
                    ]
                },
                2: {
                    '1st Semester': [
                        {'name': 'Data Structures and Algorithms', 'code': 'IT-2101', 'description': 'Advanced programming concepts and algorithmic thinking'},
                        {'name': 'Database Management Systems', 'code': 'IT-2102', 'description': 'Database design and implementation'},
                        {'name': 'Computer Networks', 'code': 'IT-2103', 'description': 'Network fundamentals and protocols'},
                        {'name': 'Statistics and Probability', 'code': 'IT-2104', 'description': 'Statistical analysis for IT applications'},
                        {'name': 'Ethics', 'code': 'GE-2101', 'description': 'Moral and ethical foundations'}
                    ],
                    '2nd Semester': [
                        {'name': 'Advanced Database Systems', 'code': 'IT-2201', 'description': 'Advanced database concepts and optimization'},
                        {'name': 'Software Engineering', 'code': 'IT-2202', 'description': 'Software development methodologies'},
                        {'name': 'Network Administration', 'code': 'IT-2203', 'description': 'Network management and security'},
                        {'name': 'Human Computer Interaction', 'code': 'IT-2204', 'description': 'User interface design principles'},
                        {'name': 'Science, Technology and Society', 'code': 'GE-2201', 'description': 'Impact of technology on society'}
                    ],
                    'Summer': [
                        {'name': 'Physical Education 2', 'code': 'PE-2', 'description': 'Advanced physical fitness'},
                        {'name': 'Technical Writing', 'code': 'IT-2301', 'description': 'Technical documentation skills'}
                    ]
                },
                3: {
                    '1st Semester': [
                        {'name': 'Machine Learning', 'code': 'IT-3101', 'description': 'Introduction to machine learning algorithms and applications'},
                        {'name': 'System Analysis and Design', 'code': 'IT-3102', 'description': 'System development lifecycle and design patterns'},
                        {'name': 'Mobile Application Development', 'code': 'IT-3103', 'description': 'Mobile app development for Android and iOS'},
                        {'name': 'Information Security', 'code': 'IT-3104', 'description': 'Cybersecurity principles and practices'},
                        {'name': 'Life and Works of Rizal', 'code': 'GE-3101', 'description': 'Philippine national hero study'}
                    ],
                    '2nd Semester': [
                        {'name': 'Advanced Web Development', 'code': 'IT-3201', 'description': 'Full-stack web development with modern frameworks'},
                        {'name': 'Cloud Computing', 'code': 'IT-3202', 'description': 'Cloud platforms and services'},
                        {'name': 'Data Mining and Analytics', 'code': 'IT-3203', 'description': 'Big data analysis and visualization'},
                        {'name': 'Project Management', 'code': 'IT-3204', 'description': 'IT project planning and execution'},
                        {'name': 'Contemporary World', 'code': 'GE-3201', 'description': 'Global issues and perspectives'}
                    ],
                    'Summer': [
                        {'name': 'Internship/OJT', 'code': 'IT-3301', 'description': 'Industry training and experience'},
                        {'name': 'Research Methods', 'code': 'IT-3302', 'description': 'Research methodology for IT'}
                    ]
                },
                4: {
                    '1st Semester': [
                        {'name': 'Capstone Project 1', 'code': 'IT-4101', 'description': 'Senior capstone project development'},
                        {'name': 'IT Service Management', 'code': 'IT-4102', 'description': 'ITIL and service management frameworks'},
                        {'name': 'Enterprise Architecture', 'code': 'IT-4103', 'description': 'Enterprise-level system design'},
                        {'name': 'IT Elective 1', 'code': 'IT-4104', 'description': 'Specialized IT track course'},
                        {'name': 'Reading in Philippine History', 'code': 'GE-4101', 'description': 'Philippine historical perspectives'}
                    ],
                    '2nd Semester': [
                        {'name': 'Capstone Project 2', 'code': 'IT-4201', 'description': 'Senior capstone project completion'},
                        {'name': 'IT Governance and Strategy', 'code': 'IT-4202', 'description': 'Strategic IT management'},
                        {'name': 'Emerging Technologies', 'code': 'IT-4203', 'description': 'Latest trends in technology'},
                        {'name': 'IT Elective 2', 'code': 'IT-4204', 'description': 'Advanced specialized IT course'},
                        {'name': 'Gender and Society', 'code': 'GE-4201', 'description': 'Gender studies and social issues'}
                    ]
                }
            },
            'Bachelor of Science in Computer Science': {
                1: {
                    '1st Semester': [
                        {'name': 'Introduction to Programming', 'code': 'CS-1101', 'description': 'Basic programming fundamentals'},
                        {'name': 'Calculus 1', 'code': 'CS-1102', 'description': 'Differential calculus'},
                        {'name': 'Discrete Mathematics 1', 'code': 'CS-1103', 'description': 'Logic and set theory'},
                        {'name': 'Computer Fundamentals', 'code': 'CS-1104', 'description': 'Basic computer systems'},
                        {'name': 'Understanding the Self', 'code': 'GE-1101', 'description': 'Personal development'}
                    ],
                    '2nd Semester': [
                        {'name': 'Programming Languages', 'code': 'CS-1201', 'description': 'Multiple programming paradigms'},
                        {'name': 'Calculus 2', 'code': 'CS-1202', 'description': 'Integral calculus'},
                        {'name': 'Discrete Mathematics 2', 'code': 'CS-1203', 'description': 'Graph theory and combinatorics'},
                        {'name': 'Physics for Computer Science', 'code': 'CS-1204', 'description': 'Applied physics concepts'},
                        {'name': 'Purposive Communication', 'code': 'GE-1201', 'description': 'Advanced communication skills'}
                    ]
                },
                2: {
                    '1st Semester': [
                        {'name': 'Data Structures', 'code': 'CS-2101', 'description': 'Abstract data types and structures'},
                        {'name': 'Computer Organization', 'code': 'CS-2102', 'description': 'Computer architecture fundamentals'},
                        {'name': 'Linear Algebra', 'code': 'CS-2103', 'description': 'Mathematical foundations for CS'},
                        {'name': 'Statistics for Computer Science', 'code': 'CS-2104', 'description': 'Statistical methods in computing'},
                        {'name': 'Ethics', 'code': 'GE-2101', 'description': 'Computer ethics and morality'}
                    ],
                    '2nd Semester': [
                        {'name': 'Algorithms', 'code': 'CS-2201', 'description': 'Algorithm design and analysis'},
                        {'name': 'Operating Systems', 'code': 'CS-2202', 'description': 'OS concepts and implementation'},
                        {'name': 'Database Systems', 'code': 'CS-2203', 'description': 'Database theory and implementation'},
                        {'name': 'Software Engineering 1', 'code': 'CS-2204', 'description': 'Software development processes'},
                        {'name': 'Science, Technology and Society', 'code': 'GE-2201', 'description': 'Technology impact on society'}
                    ]
                },
                3: {
                    '1st Semester': [
                        {'name': 'Machine Learning', 'code': 'CS-3101', 'description': 'ML algorithms and statistical learning'},
                        {'name': 'Computer Networks', 'code': 'CS-3102', 'description': 'Network protocols and architecture'},
                        {'name': 'Theory of Computation', 'code': 'CS-3103', 'description': 'Formal languages and automata'},
                        {'name': 'Computer Graphics', 'code': 'CS-3104', 'description': 'Graphics programming and visualization'},
                        {'name': 'Life and Works of Rizal', 'code': 'GE-3101', 'description': 'Philippine national hero'}
                    ],
                    '2nd Semester': [
                        {'name': 'Artificial Intelligence', 'code': 'CS-3201', 'description': 'AI principles and applications'},
                        {'name': 'Software Engineering 2', 'code': 'CS-3202', 'description': 'Advanced software engineering'},
                        {'name': 'Compiler Design', 'code': 'CS-3203', 'description': 'Language processors and compilers'},
                        {'name': 'Human-Computer Interaction', 'code': 'CS-3204', 'description': 'UI/UX design principles'},
                        {'name': 'Contemporary World', 'code': 'GE-3201', 'description': 'Global perspectives'}
                    ]
                },
                4: {
                    '1st Semester': [
                        {'name': 'Thesis 1', 'code': 'CS-4101', 'description': 'Research thesis development'},
                        {'name': 'Parallel and Distributed Computing', 'code': 'CS-4102', 'description': 'Concurrent programming'},
                        {'name': 'Information Security', 'code': 'CS-4103', 'description': 'Cryptography and security'},
                        {'name': 'CS Elective 1', 'code': 'CS-4104', 'description': 'Specialized CS track'},
                        {'name': 'Reading in Philippine History', 'code': 'GE-4101', 'description': 'Philippine history'}
                    ],
                    '2nd Semester': [
                        {'name': 'Thesis 2', 'code': 'CS-4201', 'description': 'Research thesis completion'},
                        {'name': 'Software Project Management', 'code': 'CS-4202', 'description': 'Managing software projects'},
                        {'name': 'Advanced Algorithms', 'code': 'CS-4203', 'description': 'Complex algorithmic techniques'},
                        {'name': 'CS Elective 2', 'code': 'CS-4204', 'description': 'Advanced specialized course'},
                        {'name': 'Gender and Society', 'code': 'GE-4201', 'description': 'Gender studies'}
                    ]
                }
            },
            'Bachelor of Science in Information Systems': {
                1: {
                    '1st Semester': [
                        {'name': 'Introduction to Information Systems', 'code': 'IS-1101', 'description': 'Fundamentals of information systems'},
                        {'name': 'Business Mathematics', 'code': 'IS-1102', 'description': 'Mathematical foundations for business'},
                        {'name': 'Computer Fundamentals', 'code': 'IS-1103', 'description': 'Basic computer concepts'},
                        {'name': 'Accounting Principles', 'code': 'IS-1104', 'description': 'Basic accounting concepts'},
                        {'name': 'Understanding the Self', 'code': 'GE-1101', 'description': 'Personal development'}
                    ],
                    '2nd Semester': [
                        {'name': 'Programming for Business', 'code': 'IS-1201', 'description': 'Business-oriented programming'},
                        {'name': 'Microeconomics', 'code': 'IS-1202', 'description': 'Economic principles'},
                        {'name': 'Statistics for Business', 'code': 'IS-1203', 'description': 'Business statistics'},
                        {'name': 'Management Concepts', 'code': 'IS-1204', 'description': 'Basic management principles'},
                        {'name': 'Purposive Communication', 'code': 'GE-1201', 'description': 'Communication skills'}
                    ]
                },
                2: {
                    '1st Semester': [
                        {'name': 'Database Systems', 'code': 'IS-2101', 'description': 'Database design and management'},
                        {'name': 'Systems Analysis and Design', 'code': 'IS-2102', 'description': 'System development lifecycle'},
                        {'name': 'Business Process Management', 'code': 'IS-2103', 'description': 'Process optimization'},
                        {'name': 'Financial Management', 'code': 'IS-2104', 'description': 'Corporate finance'},
                        {'name': 'Ethics', 'code': 'GE-2101', 'description': 'Business ethics'}
                    ],
                    '2nd Semester': [
                        {'name': 'Enterprise Resource Planning', 'code': 'IS-2201', 'description': 'ERP systems'},
                        {'name': 'Web Development for Business', 'code': 'IS-2202', 'description': 'Business web applications'},
                        {'name': 'Operations Management', 'code': 'IS-2203', 'description': 'Business operations'},
                        {'name': 'Marketing Management', 'code': 'IS-2204', 'description': 'Marketing principles'},
                        {'name': 'Science, Technology and Society', 'code': 'GE-2201', 'description': 'Technology impact'}
                    ]
                },
                3: {
                    '1st Semester': [
                        {'name': 'Business Intelligence', 'code': 'IS-3101', 'description': 'Data analytics for business'},
                        {'name': 'IT Project Management', 'code': 'IS-3102', 'description': 'Managing IT projects'},
                        {'name': 'E-Commerce Systems', 'code': 'IS-3103', 'description': 'Online business systems'},
                        {'name': 'Strategic Management', 'code': 'IS-3104', 'description': 'Business strategy'},
                        {'name': 'Life and Works of Rizal', 'code': 'GE-3101', 'description': 'Philippine history'}
                    ],
                    '2nd Semester': [
                        {'name': 'Information Security Management', 'code': 'IS-3201', 'description': 'Security in business'},
                        {'name': 'Supply Chain Management', 'code': 'IS-3202', 'description': 'Supply chain optimization'},
                        {'name': 'Customer Relationship Management', 'code': 'IS-3203', 'description': 'CRM systems'},
                        {'name': 'Quality Management', 'code': 'IS-3204', 'description': 'Quality assurance'},
                        {'name': 'Contemporary World', 'code': 'GE-3201', 'description': 'Global perspectives'}
                    ]
                },
                4: {
                    '1st Semester': [
                        {'name': 'Capstone Project 1', 'code': 'IS-4101', 'description': 'Senior project development'},
                        {'name': 'IT Governance', 'code': 'IS-4102', 'description': 'IT governance frameworks'},
                        {'name': 'Business Analytics', 'code': 'IS-4103', 'description': 'Advanced analytics'},
                        {'name': 'IS Elective 1', 'code': 'IS-4104', 'description': 'Specialized IS course'},
                        {'name': 'Reading in Philippine History', 'code': 'GE-4101', 'description': 'Philippine history'}
                    ],
                    '2nd Semester': [
                        {'name': 'Capstone Project 2', 'code': 'IS-4201', 'description': 'Senior project completion'},
                        {'name': 'Enterprise Architecture', 'code': 'IS-4202', 'description': 'Enterprise system design'},
                        {'name': 'Digital Transformation', 'code': 'IS-4203', 'description': 'Business digitalization'},
                        {'name': 'IS Elective 2', 'code': 'IS-4204', 'description': 'Advanced specialized course'},
                        {'name': 'Gender and Society', 'code': 'GE-4201', 'description': 'Gender studies'}
                    ]
                }
            },
            'Bachelor of Science in Computer Engineering': {
                1: {
                    '1st Semester': [
                        {'name': 'Engineering Drawing', 'code': 'CPE-1101', 'description': 'Technical drawing fundamentals'},
                        {'name': 'Engineering Mathematics 1', 'code': 'CPE-1102', 'description': 'Advanced mathematics'},
                        {'name': 'Physics 1', 'code': 'CPE-1103', 'description': 'Mechanics and thermodynamics'},
                        {'name': 'Chemistry for Engineers', 'code': 'CPE-1104', 'description': 'Applied chemistry'},
                        {'name': 'Understanding the Self', 'code': 'GE-1101', 'description': 'Personal development'}
                    ],
                    '2nd Semester': [
                        {'name': 'Computer Programming 1', 'code': 'CPE-1201', 'description': 'Programming fundamentals'},
                        {'name': 'Engineering Mathematics 2', 'code': 'CPE-1202', 'description': 'Differential equations'},
                        {'name': 'Physics 2', 'code': 'CPE-1203', 'description': 'Electricity and magnetism'},
                        {'name': 'Materials Science', 'code': 'CPE-1204', 'description': 'Engineering materials'},
                        {'name': 'Purposive Communication', 'code': 'GE-1201', 'description': 'Communication skills'}
                    ]
                },
                2: {
                    '1st Semester': [
                        {'name': 'Digital Logic Design', 'code': 'CPE-2101', 'description': 'Digital circuits and logic'},
                        {'name': 'Circuit Analysis', 'code': 'CPE-2102', 'description': 'Electrical circuit fundamentals'},
                        {'name': 'Data Structures and Algorithms', 'code': 'CPE-2103', 'description': 'Programming data structures'},
                        {'name': 'Engineering Statistics', 'code': 'CPE-2104', 'description': 'Statistical analysis'},
                        {'name': 'Ethics', 'code': 'GE-2101', 'description': 'Engineering ethics'}
                    ],
                    '2nd Semester': [
                        {'name': 'Microprocessors and Microcontrollers', 'code': 'CPE-2201', 'description': 'Embedded systems'},
                        {'name': 'Electronics Circuits', 'code': 'CPE-2202', 'description': 'Electronic circuit design'},
                        {'name': 'Object-Oriented Programming', 'code': 'CPE-2203', 'description': 'OOP concepts'},
                        {'name': 'Signals and Systems', 'code': 'CPE-2204', 'description': 'Signal processing'},
                        {'name': 'Science, Technology and Society', 'code': 'GE-2201', 'description': 'Technology impact'}
                    ]
                },
                3: {
                    '1st Semester': [
                        {'name': 'Computer Architecture', 'code': 'CPE-3101', 'description': 'Computer system design'},
                        {'name': 'Operating Systems', 'code': 'CPE-3102', 'description': 'OS concepts'},
                        {'name': 'Communication Systems', 'code': 'CPE-3103', 'description': 'Data communication'},
                        {'name': 'Control Systems', 'code': 'CPE-3104', 'description': 'Automatic control'},
                        {'name': 'Life and Works of Rizal', 'code': 'GE-3101', 'description': 'Philippine history'}
                    ],
                    '2nd Semester': [
                        {'name': 'VLSI Design', 'code': 'CPE-3201', 'description': 'VLSI circuit design'},
                        {'name': 'Computer Networks', 'code': 'CPE-3202', 'description': 'Network systems'},
                        {'name': 'Digital Signal Processing', 'code': 'CPE-3203', 'description': 'Signal processing'},
                        {'name': 'Software Engineering', 'code': 'CPE-3204', 'description': 'Software development'},
                        {'name': 'Contemporary World', 'code': 'GE-3201', 'description': 'Global perspectives'}
                    ]
                },
                4: {
                    '1st Semester': [
                        {'name': 'Design Project 1', 'code': 'CPE-4101', 'description': 'Senior design project'},
                        {'name': 'Embedded Systems Design', 'code': 'CPE-4102', 'description': 'Advanced embedded systems'},
                        {'name': 'Computer Engineering Elective 1', 'code': 'CPE-4103', 'description': 'Specialized CPE course'},
                        {'name': 'Engineering Management', 'code': 'CPE-4104', 'description': 'Engineering leadership'},
                        {'name': 'Reading in Philippine History', 'code': 'GE-4101', 'description': 'Philippine history'}
                    ],
                    '2nd Semester': [
                        {'name': 'Design Project 2', 'code': 'CPE-4201', 'description': 'Senior design completion'},
                        {'name': 'Computer Engineering Elective 2', 'code': 'CPE-4202', 'description': 'Advanced specialized course'},
                        {'name': 'Professional Ethics and Law', 'code': 'CPE-4203', 'description': 'Professional ethics'},
                        {'name': 'Technopreneurship', 'code': 'CPE-4204', 'description': 'Technology entrepreneurship'},
                        {'name': 'Gender and Society', 'code': 'GE-4201', 'description': 'Gender studies'}
                    ]
                }
            },
            'Bachelor of Science in Software Engineering': {
                1: {
                    '1st Semester': [
                        {'name': 'Introduction to Software Engineering', 'code': 'SE-1101', 'description': 'Software engineering fundamentals'},
                        {'name': 'Programming Fundamentals', 'code': 'SE-1102', 'description': 'Basic programming'},
                        {'name': 'Discrete Mathematics', 'code': 'SE-1103', 'description': 'Mathematical foundations'},
                        {'name': 'Technical Communication', 'code': 'SE-1104', 'description': 'Technical writing'},
                        {'name': 'Understanding the Self', 'code': 'GE-1101', 'description': 'Personal development'}
                    ],
                    '2nd Semester': [
                        {'name': 'Object-Oriented Programming', 'code': 'SE-1201', 'description': 'OOP principles'},
                        {'name': 'Calculus for Software Engineers', 'code': 'SE-1202', 'description': 'Applied calculus'},
                        {'name': 'Computer Systems Fundamentals', 'code': 'SE-1203', 'description': 'Computer systems'},
                        {'name': 'Software Engineering Tools', 'code': 'SE-1204', 'description': 'Development tools'},
                        {'name': 'Purposive Communication', 'code': 'GE-1201', 'description': 'Communication skills'}
                    ]
                },
                2: {
                    '1st Semester': [
                        {'name': 'Data Structures and Algorithms', 'code': 'SE-2101', 'description': 'Programming data structures'},
                        {'name': 'Software Requirements Engineering', 'code': 'SE-2102', 'description': 'Requirements analysis'},
                        {'name': 'Database Systems', 'code': 'SE-2103', 'description': 'Database management'},
                        {'name': 'Statistics and Probability', 'code': 'SE-2104', 'description': 'Statistical methods'},
                        {'name': 'Ethics', 'code': 'GE-2101', 'description': 'Software ethics'}
                    ],
                    '2nd Semester': [
                        {'name': 'Software Design and Architecture', 'code': 'SE-2201', 'description': 'Software architecture'},
                        {'name': 'Web Development', 'code': 'SE-2202', 'description': 'Web application development'},
                        {'name': 'Software Testing', 'code': 'SE-2203', 'description': 'Testing methodologies'},
                        {'name': 'Human-Computer Interaction', 'code': 'SE-2204', 'description': 'UI/UX design'},
                        {'name': 'Science, Technology and Society', 'code': 'GE-2201', 'description': 'Technology impact'}
                    ]
                },
                3: {
                    '1st Semester': [
                        {'name': 'Software Project Management', 'code': 'SE-3101', 'description': 'Project management'},
                        {'name': 'Mobile Application Development', 'code': 'SE-3102', 'description': 'Mobile app development'},
                        {'name': 'Software Quality Assurance', 'code': 'SE-3103', 'description': 'Quality management'},
                        {'name': 'Advanced Algorithms', 'code': 'SE-3104', 'description': 'Complex algorithms'},
                        {'name': 'Life and Works of Rizal', 'code': 'GE-3101', 'description': 'Philippine history'}
                    ],
                    '2nd Semester': [
                        {'name': 'DevOps and Deployment', 'code': 'SE-3201', 'description': 'DevOps practices'},
                        {'name': 'Software Maintenance', 'code': 'SE-3202', 'description': 'Software maintenance'},
                        {'name': 'Agile Development', 'code': 'SE-3203', 'description': 'Agile methodologies'},
                        {'name': 'Cloud Computing', 'code': 'SE-3204', 'description': 'Cloud platforms'},
                        {'name': 'Contemporary World', 'code': 'GE-3201', 'description': 'Global perspectives'}
                    ]
                },
                4: {
                    '1st Semester': [
                        {'name': 'Capstone Project 1', 'code': 'SE-4101', 'description': 'Senior project development'},
                        {'name': 'Software Engineering Research', 'code': 'SE-4102', 'description': 'Research methods'},
                        {'name': 'SE Elective 1', 'code': 'SE-4103', 'description': 'Specialized SE course'},
                        {'name': 'Professional Practice', 'code': 'SE-4104', 'description': 'Professional skills'},
                        {'name': 'Reading in Philippine History', 'code': 'GE-4101', 'description': 'Philippine history'}
                    ],
                    '2nd Semester': [
                        {'name': 'Capstone Project 2', 'code': 'SE-4201', 'description': 'Senior project completion'},
                        {'name': 'Emerging Technologies', 'code': 'SE-4202', 'description': 'Latest technologies'},
                        {'name': 'SE Elective 2', 'code': 'SE-4203', 'description': 'Advanced specialized course'},
                        {'name': 'Software Engineering Ethics', 'code': 'SE-4204', 'description': 'Professional ethics'},
                        {'name': 'Gender and Society', 'code': 'GE-4201', 'description': 'Gender studies'}
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
        """Create course assignments based on year levels"""
        assigned_course_ids = []
        current_time = self.get_current_time()
        current_date = datetime.now()
        
        # Generate current academic year
        if current_date.month >= 9:
            academic_year = f"{current_date.year}-{current_date.year + 1}"
        else:
            academic_year = f"{current_date.year - 1}-{current_date.year}"
        
        semesters = ["1st Semester", "2nd Semester", "Summer"]
        
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
        
        # For each semester, assign courses to sections
        for semester in semesters:
            self.logger.info(f"Processing assignments for {semester}")
            
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
                
                self.logger.info(f"Assigning {len(semester_courses)} courses to {len(sections)} sections for {program_name} Year {year_level} - {semester}")
                
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
                
                self.logger.info(f"✓ Assigned courses for {program_name} Year {year_level} Section(s): {', '.join([s[1] for s in sections])}")
        
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
