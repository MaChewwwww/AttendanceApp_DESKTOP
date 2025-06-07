import sqlite3
import bcrypt
import base64
import os
import random
import string
from datetime import datetime, timedelta
from .config import DB_PATH, UPLOAD_DIR
from .email_service import EmailService
from .db_manager_auth import DatabaseAuthManager
from .db_manager_init import DatabaseInitManager
from .db_manager_user_management import DatabaseUserManager
from .db_manager_program import DatabaseProgramManager

class DatabaseManager:
    def __init__(self):
        self.email_service = EmailService()
        # Initialize auth manager with reference to this instance
        self.auth = DatabaseAuthManager(self)
        # Initialize database init manager with reference to this instance
        self.init = DatabaseInitManager(self)
        # Initialize user management manager with reference to this instance
        self.users = DatabaseUserManager(self)
        # Initialize program management manager with reference to this instance
        self.programs = DatabaseProgramManager(self)
        # Initialize database tables on first run
        self.init.initialize_database()
    
    def get_connection(self):
        """Create and return a new database connection."""
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn
    
    def close(self):
        """
        Dummy close method to maintain compatibility with application code.
        Since we're using per-operation connections now, this method doesn't need to do anything.
        """
        return
    
    # Delegate authentication methods to auth manager
    def check_email_exists(self, email):
        return self.auth.check_email_exists(email)
    
    def check_student_id_exists(self, student_id):
        return self.auth.check_student_id_exists(student_id)

    def check_employee_number_exists(self, employee_number):
        return self.auth.check_employee_number_exists(employee_number)
    
    def login(self, email, password):
        return self.auth.login(email, password)
    
    def generate_otp(self, length=6):
        return self.auth.generate_otp(length)
    
    def create_login_otp(self, email):
        return self.auth.create_login_otp(email)
    
    def check_otp_requirement(self, user_id):
        return self.auth.check_otp_requirement(user_id)

    def update_login_otp_verification(self, user_id):
        return self.auth.update_login_otp_verification(user_id)

    def verify_login_otp(self, email, otp_code):
        return self.auth.verify_login_otp(email, otp_code)

    def create_registration_otp(self, email, first_name):
        return self.auth.create_registration_otp(email, first_name)
    
    def verify_registration_otp_and_register(self, email, otp_code, registration_data):
        return self.auth.verify_registration_otp_and_register(email, otp_code, registration_data)

    def cleanup_expired_otps(self):
        return self.auth.cleanup_expired_otps()

    def create_password_reset_otp(self, email):
        return self.auth.create_password_reset_otp(email)

    def verify_password_reset_otp(self, email, otp_code):
        return self.auth.verify_password_reset_otp(email, otp_code)

    def reset_password_with_otp(self, email, otp_code, new_password):
        return self.auth.reset_password_with_otp(email, otp_code, new_password)

    # Delegate user management methods to user manager
    def get_all_users_simple(self):
        return self.users.get_all_users_simple()

    def filter_users_python(self, all_users, search_term="", role_filter="", year_filter="", section_filter="", program_filter="", status_filter=""):
        return self.users.filter_users_python(all_users, search_term, role_filter, year_filter, section_filter, program_filter, status_filter)

    def get_students_with_filters(self, search_term="", year_filter="", section_filter="", program_filter="", status_filter=""):
        return self.users.get_students_with_filters(search_term, year_filter, section_filter, program_filter, status_filter)

    def get_faculty_with_filters(self, search_term="", status_filter="", role_filter=""):
        return self.users.get_faculty_with_filters(search_term, status_filter, role_filter)

    def get_user_by_name(self, first_name, last_name, role=None):
        return self.users.get_user_by_name(first_name, last_name, role)

    def get_user_details(self, user_id):
        return self.users.get_user_details(user_id)

    def get_user_section_and_program_ids(self, user_id):
        return self.users.get_user_section_and_program_ids(user_id)

    def update_user(self, user_id, user_data):
        return self.users.update_user(user_id, user_data)

    def validate_section_assignment(self, program_abbreviation, section_name):
        return self.users.validate_section_assignment(program_abbreviation, section_name)

    def delete_user(self, user_id):
        return self.users.delete_user(user_id)

    def restore_user(self, user_id):
        return self.users.restore_user(user_id)

    def get_deleted_users(self):
        return self.users.get_deleted_users()

    def get_assigned_courses(self, faculty_id=None):
        return self.users.get_assigned_courses(faculty_id)

    def get_student_attendance_summary(self, user_id):
        return self.users.get_student_attendance_summary(user_id)

    def get_programs(self):
        return self.users.get_programs()

    def get_sections(self, program_id=None):
        return self.users.get_sections(program_id)

    def get_sections_all(self):
        return self.users.get_sections_all()

    def get_sections_by_program(self, program_name):
        return self.users.get_sections_by_program(program_name)

    def get_statuses(self, user_type=None):
        return self.users.get_statuses(user_type)

    def get_dropdown_options_for_user_type(self, user_type):
        return self.users.get_dropdown_options_for_user_type(user_type)

    def _get_program_abbreviation(self, program_name):
        return self.users._get_program_abbreviation(program_name)

    # Delegate program management methods to program manager
    def create_program(self, program_data):
        return self.programs.create_program(program_data)

    def update_program(self, program_id, program_data):
        return self.programs.update_program(program_id, program_data)

    def delete_program(self, program_id):
        return self.programs.delete_program(program_id)

    def check_program_in_use(self, program_id):
        return self.programs.check_program_in_use(program_id)

    def get_program_statistics(self, program_id, academic_year=None, semester=None):
        return self.programs.get_program_statistics(program_id, academic_year, semester)

    def get_available_academic_years(self):
        return self.programs.get_available_academic_years()

    def get_available_semesters(self):
        return self.programs.get_available_semesters()
