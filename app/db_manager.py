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

class DatabaseManager:
    def __init__(self):
        self.email_service = EmailService()
        # Initialize auth manager with reference to this instance
        self.auth = DatabaseAuthManager(self)
        # Initialize database init manager with reference to this instance
        self.init = DatabaseInitManager(self)
        # Initialize user management manager with reference to this instance
        self.users = DatabaseUserManager(self)
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
        """Get all available programs"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description, acronym, color
                FROM programs 
                ORDER BY name
            """)
            
            results = cursor.fetchall()
            programs = [dict(row) for row in results]
            
            conn.close()
            return True, programs
            
        except Exception as e:
            print(f"Error getting programs: {e}")
            return False, str(e)

    def get_sections(self, program_id=None):
        """Get all sections, optionally filtered by program"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if program_id:
                cursor.execute("""
                    SELECT id, name, program_id 
                    FROM sections 
                    WHERE program_id = ?
                    ORDER BY name
                """, (program_id,))
            else:
                cursor.execute("""
                    SELECT s.id, s.name, s.program_id, p.name as program_name
                    FROM sections s
                    JOIN programs p ON s.program_id = p.id
                    ORDER BY p.name, s.name
                """)
            
            results = cursor.fetchall()
            sections = [dict(row) for row in results]
            
            conn.close()
            return True, sections
            
        except Exception as e:
            print(f"Error getting sections: {e}")
            return False, str(e)

    def get_sections_by_program(self, program_id):
        """Get sections filtered by program ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, program_id 
                FROM sections 
                WHERE program_id = ?
                ORDER BY name
            """, (program_id,))
            
            results = cursor.fetchall()
            sections = [dict(row) for row in results]
            
            conn.close()
            return True, sections
            
        except Exception as e:
            print(f"Error getting sections by program: {e}")
            return False, str(e)

    def get_statuses(self, user_type=None):
        """Get all statuses, optionally filtered by user type"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if user_type:
                cursor.execute("""
                    SELECT id, name, description, user_type 
                    FROM statuses 
                    WHERE user_type = ?
                    ORDER BY name
                """, (user_type,))
            else:
                cursor.execute("""
                    SELECT id, name, description, user_type 
                    FROM statuses 
                    ORDER BY user_type, name
                """)
            
            results = cursor.fetchall()
            statuses = [dict(row) for row in results]
            
            conn.close()
            return True, statuses
            
        except Exception as e:
            print(f"Error getting statuses: {e}")
            return False, str(e)

    def get_dropdown_options_for_user_type(self, user_type):
        """Get all dropdown options for a specific user type (student/faculty)"""
        try:
            # Get programs
            success_programs, programs = self.get_programs()
            if not success_programs:
                return False, f"Error fetching programs: {programs}"
            
            # Get sections  
            success_sections, sections = self.get_sections()
            if not success_sections:
                return False, f"Error fetching sections: {sections}"
            
            # Get statuses for this user type
            success_statuses, statuses = self.get_statuses(user_type)
            if not success_statuses:
                return False, f"Error fetching statuses: {statuses}"
            
            # Format for dropdown usage
            dropdown_options = {
                'programs': [{'id': p['id'], 'name': p['name'], 'abbreviation': self._get_program_abbreviation(p['name'])} for p in programs],
                'sections': [{'id': s['id'], 'name': s['name'], 'program_id': s.get('program_id')} for s in sections],
                'statuses': [{'id': s['id'], 'name': s['name']} for s in statuses]
            }
            
            return True, dropdown_options
            
        except Exception as e:
            print(f"Error getting dropdown options: {e}")
            return False, str(e)

    def _get_program_abbreviation(self, program_name):
        """Convert program name to abbreviation"""
        if not program_name:
            return "N/A"
        
        if "Information Technology" in program_name:
            return "BSIT"
        elif "Computer Science" in program_name:
            return "BSCS"  
        elif "Information Systems" in program_name:
            return "BSIS"
        else:
            # Extract abbreviation from name if possible, or return first letters
            words = program_name.split()
            if len(words) >= 2:
                return ''.join([word[0].upper() for word in words])
            return program_name[:4].upper()
