import os
from pathlib import Path

# Database configuration
SCRIPT_DIR = Path(__file__).parent.parent
DATA_DIR = SCRIPT_DIR / "data"
DB_PATH = DATA_DIR / "attendance_app.db"

# Philippine holidays for 2024-2025
PHILIPPINE_HOLIDAYS = {
    2024: {
        "01-01": "New Year's Day",
        "02-10": "Chinese New Year",
        "02-25": "EDSA People Power Revolution Anniversary",
        "03-28": "Maundy Thursday",
        "03-29": "Good Friday",
        "04-09": "Araw ng Kagitingan (Day of Valor)",
        "05-01": "Labor Day",
        "06-12": "Independence Day",
        "08-21": "Ninoy Aquino Day",
        "08-26": "National Heroes Day",
        "11-01": "All Saints' Day",
        "11-02": "All Souls' Day",
        "11-30": "Bonifacio Day",
        "12-25": "Christmas Day",
        "12-30": "Rizal Day",
        "12-31": "New Year's Eve"
    },
    2025: {
        "01-01": "New Year's Day",
        "01-29": "Chinese New Year",
        "02-25": "EDSA People Power Revolution Anniversary",
        "04-17": "Maundy Thursday",
        "04-18": "Good Friday",
        "04-09": "Araw ng Kagitingan (Day of Valor)",
        "05-01": "Labor Day",
        "06-12": "Independence Day",
        "08-21": "Ninoy Aquino Day",
        "08-25": "National Heroes Day",
        "11-01": "All Saints' Day",
        "11-02": "All Souls' Day",
        "11-30": "Bonifacio Day",
        "12-25": "Christmas Day",
        "12-30": "Rizal Day",
        "12-31": "New Year's Eve"
    }
}

# Academic calendar specific suspensions
ACADEMIC_SUSPENSIONS = {
    # Christmas break
    "12-20": "Start of Christmas Break",
    "12-21": "Christmas Break",
    "12-22": "Christmas Break",
    "12-23": "Christmas Break",
    "12-24": "Christmas Eve",
    "12-26": "Christmas Break",
    "12-27": "Christmas Break",
    "12-28": "Christmas Break",
    "12-29": "Christmas Break",
    
    # New Year extension
    "01-02": "New Year Break",
    "01-03": "New Year Break",
    
    # Semestral breaks
    "10-15": "Mid-semester Break",
    "10-16": "Mid-semester Break",
    "03-15": "Mid-semester Break",
    "03-16": "Mid-semester Break",
}

# Seeder configuration
SEEDER_CONFIG = {
    'academic_years': {
        'generate_previous': True,
        'generate_current': True,
        'semesters': ["1st Semester", "2nd Semester", "Summer"]
    },
    
    'student_performance': {
        'excellent': {'percentage': 0.45, 'attendance_range': (0.95, 0.98), 'consistency_range': (0.95, 1.0)},
        'very_good': {'percentage': 0.30, 'attendance_range': (0.90, 0.94), 'consistency_range': (0.90, 0.95)},
        'good': {'percentage': 0.15, 'attendance_range': (0.85, 0.89), 'consistency_range': (0.85, 0.90)},
        'average': {'percentage': 0.07, 'attendance_range': (0.80, 0.84), 'consistency_range': (0.75, 0.85)},
        'poor': {'percentage': 0.03, 'attendance_range': (0.75, 0.79), 'consistency_range': (0.65, 0.75)}
    },
    
    'course_schedule': {
        'days_of_week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        'time_slots': [
            ('07:00:00', '08:30:00'),
            ('08:30:00', '10:00:00'),
            ('10:00:00', '11:30:00'),
            ('11:30:00', '13:00:00'),
            ('13:00:00', '14:30:00'),
            ('14:30:00', '16:00:00'),
            ('16:00:00', '17:30:00'),
            ('17:30:00', '19:00:00')
        ],
        'meetings_per_week': {
            'regular': [2, 3],
            'summer': [2, 3]
        }
    },
    
    'rooms': [
        'Room 101', 'Room 102', 'Room 103', 'Room 104', 'Room 105',
        'Room 201', 'Room 202', 'Room 203', 'Room 204', 'Room 205',
        'Lab 1', 'Lab 2', 'Lab 3', 'Lab 4', 'Lab 5',
        'Computer Lab A', 'Computer Lab B', 'Computer Lab C',
        'Conference Room A', 'Conference Room B', 'Conference Room C',
        'Lecture Hall 1', 'Lecture Hall 2', 'Auditorium'
    ]
}

# Programs data
PROGRAMS_DATA = [
    {
        'name': 'Bachelor of Science in Information Technology',
        'acronym': 'BSIT',
        'code': 'PROG-001',
        'description': 'A comprehensive program focusing on information technology and computer systems, preparing students for careers in software development, network administration, and IT management.',
        'color': '#3B82F6'
    },
    {
        'name': 'Bachelor of Science in Computer Science',
        'acronym': 'BSCS', 
        'code': 'PROG-002',
        'description': 'A program emphasizing theoretical foundations of computation and practical software engineering, covering algorithms, data structures, and advanced computing concepts.',
        'color': '#10B981'
    },
    {
        'name': 'Bachelor of Science in Information Systems',
        'acronym': 'BSIS',
        'code': 'PROG-003',
        'description': 'A program combining business processes with information technology solutions, focusing on systems analysis, database management, and enterprise applications.',
        'color': '#F59E0B'
    },
    {
        'name': 'Bachelor of Science in Computer Engineering',
        'acronym': 'BSCpE',
        'code': 'PROG-004',
        'description': 'A program integrating computer science and electrical engineering principles, covering hardware design, embedded systems, and computer architecture.',
        'color': '#8B5CF6'
    },
    {
        'name': 'Bachelor of Science in Software Engineering',
        'acronym': 'BSSE',
        'code': 'PROG-005',
        'description': 'A specialized program focused on software development methodologies, project management, and large-scale system design and implementation.',
        'color': '#EF4444'
    }
]

# Enhanced courses data for each program
COURSES_DATA = [
    # BSIT Courses
    {'name': 'Programming Fundamentals', 'code': 'IT-101', 'description': 'Introduction to programming concepts using modern languages', 'program': 'Bachelor of Science in Information Technology'},
    {'name': 'Data Structures and Algorithms', 'code': 'IT-201', 'description': 'Advanced programming concepts and algorithmic thinking', 'program': 'Bachelor of Science in Information Technology'},
    {'name': 'Database Management Systems', 'code': 'IT-301', 'description': 'Database design, implementation, and management', 'program': 'Bachelor of Science in Information Technology'},
    {'name': 'Web Development Technologies', 'code': 'IT-302', 'description': 'Frontend and backend web development frameworks', 'program': 'Bachelor of Science in Information Technology'},
    {'name': 'Network Administration', 'code': 'IT-401', 'description': 'Computer networking and system administration', 'program': 'Bachelor of Science in Information Technology'},
    
    # BSCS Courses
    {'name': 'Computer Programming', 'code': 'CS-101', 'description': 'Core programming principles and paradigms', 'program': 'Bachelor of Science in Computer Science'},
    {'name': 'Software Engineering', 'code': 'CS-301', 'description': 'Software development methodologies and practices', 'program': 'Bachelor of Science in Computer Science'},
    {'name': 'Machine Learning', 'code': 'CS-401', 'description': 'AI and machine learning fundamentals and applications', 'program': 'Bachelor of Science in Computer Science'},
    {'name': 'Computer Graphics', 'code': 'CS-302', 'description': 'Graphics programming and visualization techniques', 'program': 'Bachelor of Science in Computer Science'},
    {'name': 'Operating Systems', 'code': 'CS-201', 'description': 'System software and operating system concepts', 'program': 'Bachelor of Science in Computer Science'},
    
    # ...existing course data...
]

# Section distributions
SECTION_DISTRIBUTIONS = {
    'Bachelor of Science in Information Technology': ['1-1', '1-2', '1-3', '2-1', '2-2', '3-1', '3-2', '4-1'],
    'Bachelor of Science in Computer Science': ['1-1', '1-2', '2-1', '2-2', '3-1', '4-1'],
    'Bachelor of Science in Information Systems': ['1-1', '2-1', '3-1', '4-1'],
    'Bachelor of Science in Computer Engineering': ['1-1', '2-1', '3-1'],
    'Bachelor of Science in Software Engineering': ['1-1', '2-1']
}

def get_philippine_holidays(year):
    """Get Philippine holidays for a given year"""
    return PHILIPPINE_HOLIDAYS.get(year, {})

def is_class_suspended(date, semester):
    """Check if classes are typically suspended on this date"""
    date_str = date.strftime('%m-%d')
    year = date.year
    
    # Check Philippine holidays
    holidays = get_philippine_holidays(year)
    if date_str in holidays:
        return True, holidays[date_str]
    
    # Check academic suspensions
    if date_str in ACADEMIC_SUSPENSIONS:
        return True, ACADEMIC_SUSPENSIONS[date_str]
    
    # Typhoon season random suspensions (June to November)
    if date.month in [6, 7, 8, 9, 10, 11]:
        import random
        if random.random() < 0.03:  # 3% chance during typhoon season
            return True, "Weather Suspension (Typhoon/Heavy Rain)"
    
    return False, None
