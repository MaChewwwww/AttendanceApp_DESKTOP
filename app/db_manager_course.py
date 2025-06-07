import sqlite3
from datetime import datetime
from .config import DB_PATH

class DatabaseCourseManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_connection(self):
        """Create and return a new database connection."""
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def get_courses(self, program_filter=None, year_filter=None, section_filter=None):
        """
        Get all courses with optional filtering
        
        Args:
            program_filter (str): Optional program filter
            year_filter (str): Optional year filter  
            section_filter (str): Optional section filter
        
        Returns:
            tuple: (success: bool, result: list/str)
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Base query to get courses with program and section info
            query = """
            SELECT 
                c.id,
                c.name as course_name,
                c.description,
                c.code,
                p.name as program_name,
                p.acronym as program_acronym,
                c.created_at,
                c.updated_at
            FROM courses c
            LEFT JOIN programs p ON c.program_id = p.id
            WHERE c.isDeleted = 0 AND (p.isDeleted = 0 OR p.isDeleted IS NULL)
            ORDER BY c.name, p.name
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            courses = []
            for row in results:
                course_dict = {
                    'id': row['id'],
                    'name': row['course_name'],
                    'description': row['description'] or '',
                    'code': row['code'] or '',
                    'program_name': row['program_name'] or 'No Program',
                    'program_acronym': row['program_acronym'] or 'N/A',
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                courses.append(course_dict)
            
            conn.close()
            return True, courses
            
        except Exception as e:
            print(f"Error getting courses: {e}")
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def create_course(self, course_data):
        """Create a new course"""
        # TODO: Implement course creation
        return False, "Course creation not implemented yet"

    def update_course(self, course_id, course_data):
        """Update an existing course"""
        # TODO: Implement course update
        return False, "Course update not implemented yet"

    def delete_course(self, course_id):
        """Soft delete a course"""
        # TODO: Implement course deletion
        return False, "Course deletion not implemented yet"

    def check_course_in_use(self, course_id):
        """Check if a course is being used in assigned_courses"""
        # TODO: Implement usage check
        return True, {'in_use': False, 'assignment_count': 0}

    def get_course_statistics(self, course_id, academic_year=None, semester=None):
        """Get comprehensive statistics for a specific course"""
        # TODO: Implement course statistics
        return True, {
            'total_students': 0,
            'total_classes': 0,
            'attendance_rate': '0%',
            'total_absents': 0,
            'total_present': 0,
            'total_late': 0
        }

    def get_available_programs_for_courses(self):
        """Get list of available programs for course assignment"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, acronym 
                FROM programs 
                WHERE isDeleted = 0
                ORDER BY name
            """)
            programs = [dict(row) for row in cursor.fetchall()]
            return True, programs
        except Exception as e:
            print(f"Error getting programs for courses: {e}")
            return False, str(e)
        finally:
            conn.close()
