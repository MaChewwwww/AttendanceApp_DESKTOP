import os
from pathlib import Path
from datetime import datetime

# Database configuration
SCRIPT_DIR = os.getenv('SCRIPT_DIR', Path(__file__).resolve().parent)
DATA_DIR = os.getenv('DATA_DIR', SCRIPT_DIR / 'data')
DB_PATH = os.getenv('DB_PATH', DATA_DIR / 'attendance.db')

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
    # Christmas break (during 1st semester)
    "12-20": "Start of Christmas Break",
    "12-21": "Christmas Break",
    "12-22": "Christmas Break",
    "12-23": "Christmas Break",
    "12-24": "Christmas Eve",
    "12-26": "Christmas Break",
    "12-27": "Christmas Break",
    "12-28": "Christmas Break",
    "12-29": "Christmas Break",
    
    # New Year extension (during 1st semester)
    "01-02": "New Year Break",
    "01-03": "New Year Break",
    
    # Semestral breaks
    "10-15": "Mid-semester Break (1st Semester)",
    "10-16": "Mid-semester Break (1st Semester)",
    "04-15": "Mid-semester Break (2nd Semester)",
    "04-16": "Mid-semester Break (2nd Semester)",
    
    # End of semester breaks
    "01-25": "End of 1st Semester Break",
    "01-26": "End of 1st Semester Break",
    "06-25": "End of 2nd Semester Break",
    "06-26": "End of 2nd Semester Break",
}

# Philippine Academic Calendar Configuration
ACADEMIC_CALENDAR = {
    'semesters': {
        '1st Semester': {
            'start_month': 9,    # September
            'end_month': 1,      # January
            'description': 'First Semester (September - January)'
        },
        '2nd Semester': {
            'start_month': 2,    # February  
            'end_month': 6,      # June
            'description': 'Second Semester (February - June)'
        },
        'Summer': {
            'start_month': 7,    # July
            'end_month': 8,      # August
            'description': 'Summer Semester (July - August)'
        }
    },
    'academic_year_start_month': 9,  # Academic year starts in September
}

# Seeder configuration
SEEDER_CONFIG = {
    'academic_years': {
        'generate_previous': True,
        'generate_current': True,
        'years_to_generate': ['2023-2024'],  # Can add more years as needed
        'semesters': ["1st Semester", "2nd Semester", "Summer"]
    },
    
    'academic_calendar': ACADEMIC_CALENDAR,
    
    'student_performance': {
        'excellent': {'percentage': 0.40, 'attendance_range': (0.95, 0.98), 'consistency_range': (0.95, 1.0)},
        'very_good': {'percentage': 0.30, 'attendance_range': (0.88, 0.94), 'consistency_range': (0.90, 0.95)},
        'good': {'percentage': 0.18, 'attendance_range': (0.82, 0.87), 'consistency_range': (0.85, 0.90)},
        'average': {'percentage': 0.09, 'attendance_range': (0.75, 0.81), 'consistency_range': (0.75, 0.85)},
        'poor': {'percentage': 0.03, 'attendance_range': (0.65, 0.74), 'consistency_range': (0.60, 0.75)}
    },
    
    # Status-specific attendance requirements
    'status_attendance_requirements': {
        'Suspended': {'max_attendance': 0.70, 'min_attendance': 0.40},
        'Dropout': {'max_attendance': 0.60, 'min_attendance': 0.30},
        'Graduated': {'min_attendance': 0.80, 'max_attendance': 0.98},
        'On Leave': {'min_attendance': 0.70, 'max_attendance': 0.85},
        'Enrolled': {'min_attendance': 0.65, 'max_attendance': 0.98}
    },
    
    # Section size configuration
    'section_size': {
        'min_students': 5,
        'max_students': 10
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
            'regular': [1, 2],
            'summer': [1, 2]
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

# Programs data - Only 2 programs
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
]

# Section distributions - 2 sections per year level
SECTION_DISTRIBUTIONS = {
    'Bachelor of Science in Information Technology': ['1-1', '1-2', '2-1', '2-2', '3-1', '3-2', '4-1', '4-2'],
    'Bachelor of Science in Computer Science': ['1-1', '1-2', '2-1', '2-2', '3-1', '3-2', '4-1', '4-2']
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

def get_current_semester(date=None):
    """Get the current semester based on date"""
    from datetime import datetime
    
    if date is None:
        date = datetime.now()
    
    month = date.month
    
    # 1st Semester: September - January
    if month >= 9 or month == 1:
        return "1st Semester"
    # 2nd Semester: February - June
    elif 2 <= month <= 6:
        return "2nd Semester"
    # Summer: July - August
    else:
        return "Summer"

def get_academic_year(date=None):
    """Get the academic year based on date (e.g., '2024-2025')"""
    from datetime import datetime
    
    if date is None:
        date = datetime.now()
    
    # Academic year starts in September
    if date.month >= ACADEMIC_CALENDAR['academic_year_start_month']:
        return f"{date.year}-{date.year + 1}"
    else:
        return f"{date.year - 1}-{date.year}"

def is_semester_month(month, semester):
    """Check if a given month belongs to a specific semester"""
    semester_config = ACADEMIC_CALENDAR['semesters'].get(semester)
    if not semester_config:
        return False
    
    start_month = semester_config['start_month']
    end_month = semester_config['end_month']
    
    # Handle semester that spans across year boundary (1st Semester: Sep-Jan)
    if start_month > end_month:
        return month >= start_month or month <= end_month
    else:
        return start_month <= month <= end_month

def get_semester_months(semester):
    """Get list of months for a specific semester"""
    semester_config = ACADEMIC_CALENDAR['semesters'].get(semester)
    if not semester_config:
        return []
    
    start_month = semester_config['start_month']
    end_month = semester_config['end_month']
    
    months = []
    
    # Handle semester that spans across year boundary
    if start_month > end_month:
        # Add months from start_month to 12
        months.extend(range(start_month, 13))
        # Add months from 1 to end_month
        months.extend(range(1, end_month + 1))
    else:
        months.extend(range(start_month, end_month + 1))
    
    return months

def get_semester_attendance_modifier(date, semester=None):
    """Get attendance rate modifier based on semester timing"""
    if semester is None:
        semester = get_current_semester(date)
    
    month = date.month
    
    # 1st Semester modifiers (September - January)
    if semester == "1st Semester":
        if month == 9:  # September - start of school year
            return 1.02
        elif month == 12:  # December - Christmas break approaching
            return 0.88
        elif month == 1:  # January - finals period
            return 0.92
        elif month in [10, 11]:  # October-November - stable period
            return 1.0
    
    # 2nd Semester modifiers (February - June)
    elif semester == "2nd Semester":
        if month == 2:  # February - start of 2nd semester
            return 1.01
        elif month == 6:  # June - end of school year
            return 0.85
        elif month == 5:  # May - finals period
            return 0.90
        elif month in [3, 4]:  # March-April - stable period
            return 1.0
    
    # Summer modifiers (July - August)
    elif semester == "Summer":
        return 0.82  # Generally lower attendance due to heat and vacation mindset
    
    return 1.0  # Default modifier

def get_academic_years_to_generate():
    """Get list of academic years that should have data generated"""
    return SEEDER_CONFIG['academic_years']['years_to_generate']

def get_semester_date_ranges_for_academic_year(academic_year):
    """Get semester date ranges for a specific academic year"""
    # Parse academic year (e.g., '2023-2024' -> start_year=2023, end_year=2024)
    start_year, end_year = map(int, academic_year.split('-'))
    
    periods = []
    academic_calendar = SEEDER_CONFIG['academic_calendar']['semesters']
    
    # 1st Semester: September (start_year) - January (end_year)
    first_sem_config = academic_calendar['1st Semester']
    start_1st = datetime(start_year, first_sem_config['start_month'], 1)
    end_1st = datetime(end_year, first_sem_config['end_month'], 31)
    periods.append(("1st Semester", start_1st, end_1st))
    
    # 2nd Semester: February (end_year) - June (end_year)
    second_sem_config = academic_calendar['2nd Semester']
    start_2nd = datetime(end_year, second_sem_config['start_month'], 1)
    end_2nd = datetime(end_year, second_sem_config['end_month'], 30)
    periods.append(("2nd Semester", start_2nd, end_2nd))
    
    # Summer: July (end_year) - August (end_year)
    summer_config = academic_calendar['Summer']
    start_summer = datetime(end_year, summer_config['start_month'], 1)
    end_summer = datetime(end_year, summer_config['end_month'], 31)
    periods.append(("Summer", start_summer, end_summer))
    
    return periods
