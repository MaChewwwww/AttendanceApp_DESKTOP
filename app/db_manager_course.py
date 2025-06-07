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
                c.code as course_code,
                c.description,
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
                    'code': row['course_code'] or '',
                    'description': row['description'] or '',
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
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Validate required fields
            if not course_data.get('name'):
                return False, "Course name is required"
            
            if not course_data.get('program_id'):
                return False, "Program is required"
            
            # Check if course code already exists (if provided)
            if course_data.get('code'):
                cursor.execute("SELECT id FROM courses WHERE code = ? AND isDeleted = 0", (course_data['code'],))
                if cursor.fetchone():
                    return False, "Course code already exists"
            
            # Insert the new course
            cursor.execute("""
                INSERT INTO courses (name, code, description, program_id, isDeleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                course_data['name'],
                course_data.get('code'),
                course_data.get('description'),
                course_data['program_id'],
                0,  # isDeleted = 0 (not deleted)
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            course_id = cursor.lastrowid
            return True, {"id": course_id, "message": "Course created successfully"}
            
        except Exception as e:
            conn.rollback()
            print(f"Error creating course: {e}")
            return False, str(e)
        finally:
            conn.close()

    def update_course(self, course_id, course_data):
        """Update an existing course"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Validate required fields
            if not course_data.get('name'):
                return False, "Course name is required"
            
            if not course_data.get('program_id'):
                return False, "Program is required"
            
            # Check if course exists
            cursor.execute("SELECT id FROM courses WHERE id = ? AND isDeleted = 0", (course_id,))
            if not cursor.fetchone():
                return False, "Course not found"
            
            # Check if course code already exists for other courses (if provided)
            if course_data.get('code'):
                cursor.execute("SELECT id FROM courses WHERE code = ? AND id != ? AND isDeleted = 0", 
                             (course_data['code'], course_id))
                if cursor.fetchone():
                    return False, "Course code already exists"
            
            # Update the course
            cursor.execute("""
                UPDATE courses 
                SET name = ?, code = ?, description = ?, program_id = ?, updated_at = ?
                WHERE id = ? AND isDeleted = 0
            """, (
                course_data['name'],
                course_data.get('code'),
                course_data.get('description'),
                course_data['program_id'],
                datetime.now().isoformat(),
                course_id
            ))
            
            conn.commit()
            
            if cursor.rowcount == 0:
                return False, "No rows were updated"
            
            return True, {"message": "Course updated successfully"}
            
        except Exception as e:
            conn.rollback()
            print(f"Error updating course: {e}")
            return False, str(e)
        finally:
            conn.close()

    def delete_course(self, course_id):
        """Soft delete a course"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if course exists
            cursor.execute("SELECT id FROM courses WHERE id = ? AND isDeleted = 0", (course_id,))
            if not cursor.fetchone():
                return False, "Course not found"
            
            # Check if course is being used
            usage_check = self.check_course_in_use(course_id)
            if usage_check[0] and usage_check[1]['in_use']:
                return False, f"Cannot delete course. It is currently assigned to {usage_check[1]['assignment_count']} classes."
            
            # Soft delete the course
            cursor.execute("""
                UPDATE courses 
                SET isDeleted = 1, updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), course_id))
            
            conn.commit()
            return True, {"message": "Course deleted successfully"}
            
        except Exception as e:
            conn.rollback()
            print(f"Error deleting course: {e}")
            return False, str(e)
        finally:
            conn.close()

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

    def get_courses_by_year(self, year_number):
        """Get courses assigned to sections matching a specific year level"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get courses assigned to sections that match the year (first character of section name)
            query = """
            SELECT DISTINCT ac.course_id
            FROM assigned_courses ac
            JOIN sections s ON ac.section_id = s.id
            WHERE ac.isDeleted = 0 
            AND s.isDeleted = 0 
            AND SUBSTR(s.name, 1, 1) = ?
            """
            
            cursor.execute(query, (str(year_number),))
            results = cursor.fetchall()
            
            assigned_courses = [{'course_id': row['course_id']} for row in results]
            
            return True, assigned_courses
            
        except Exception as e:
            print(f"Error getting courses by year: {e}")
            return False, str(e)
        finally:
            conn.close()

    def get_courses_by_section(self, section_name):
        """Get courses assigned to a specific section"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get courses assigned to the specific section
            query = """
            SELECT DISTINCT ac.course_id
            FROM assigned_courses ac
            JOIN sections s ON ac.section_id = s.id
            WHERE ac.isDeleted = 0 
            AND s.isDeleted = 0 
            AND s.name = ?
            """
            
            cursor.execute(query, (section_name,))
            results = cursor.fetchall()
            
            assigned_courses = [{'course_id': row['course_id']} for row in results]
            
            return True, assigned_courses
            
        except Exception as e:
            print(f"Error getting courses by section: {e}")
            return False, str(e)
        finally:
            conn.close()

    def check_course_in_use(self, course_id):
        """Check if a course is being used in assigned_courses"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if course is assigned to any classes
            cursor.execute("""
                SELECT COUNT(*) as assignment_count
                FROM assigned_courses 
                WHERE course_id = ? AND isDeleted = 0
            """, (course_id,))
            
            result = cursor.fetchone()
            assignment_count = result['assignment_count'] if result else 0
            
            return True, {
                'in_use': assignment_count > 0,
                'assignment_count': assignment_count
            }
            
        except Exception as e:
            print(f"Error checking course usage: {e}")
            return False, str(e)
        finally:
            conn.close()

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

    def get_courses_by_year(self, year_number):
        """Get courses assigned to sections matching a specific year level"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get courses assigned to sections that match the year (first character of section name)
            query = """
            SELECT DISTINCT ac.course_id
            FROM assigned_courses ac
            JOIN sections s ON ac.section_id = s.id
            WHERE ac.isDeleted = 0 
            AND s.isDeleted = 0 
            AND SUBSTR(s.name, 1, 1) = ?
            """
            
            cursor.execute(query, (str(year_number),))
            results = cursor.fetchall()
            
            assigned_courses = [{'course_id': row['course_id']} for row in results]
            
            return True, assigned_courses
            
        except Exception as e:
            print(f"Error getting courses by year: {e}")
            return False, str(e)
        finally:
            conn.close()

    def get_courses_by_section(self, section_name):
        """Get courses assigned to a specific section"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get courses assigned to the specific section
            query = """
            SELECT DISTINCT ac.course_id
            FROM assigned_courses ac
            JOIN sections s ON ac.section_id = s.id
            WHERE ac.isDeleted = 0 
            AND s.isDeleted = 0 
            AND s.name = ?
            """
            
            cursor.execute(query, (section_name,))
            results = cursor.fetchall()
            
            assigned_courses = [{'course_id': row['course_id']} for row in results]
            
            return True, assigned_courses
            
        except Exception as e:
            print(f"Error getting courses by section: {e}")
            return False, str(e)
        finally:
            conn.close()

    def check_course_in_use(self, course_id):
        """Check if a course is being used in assigned_courses"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if course is assigned to any classes
            cursor.execute("""
                SELECT COUNT(*) as assignment_count
                FROM assigned_courses 
                WHERE course_id = ? AND isDeleted = 0
            """, (course_id,))
            
            result = cursor.fetchone()
            assignment_count = result['assignment_count'] if result else 0
            
            return True, {
                'in_use': assignment_count > 0,
                'assignment_count': assignment_count
            }
            
        except Exception as e:
            print(f"Error checking course usage: {e}")
            return False, str(e)
        finally:
            conn.close()

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

    def get_courses_by_year(self, year_number):
        """Get courses assigned to sections matching a specific year level"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get courses assigned to sections that match the year (first character of section name)
            query = """
            SELECT DISTINCT ac.course_id
            FROM assigned_courses ac
            JOIN sections s ON ac.section_id = s.id
            WHERE ac.isDeleted = 0 
            AND s.isDeleted = 0 
            AND SUBSTR(s.name, 1, 1) = ?
            """
            
            cursor.execute(query, (str(year_number),))
            results = cursor.fetchall()
            
            assigned_courses = [{'course_id': row['course_id']} for row in results]
            
            return True, assigned_courses
            
        except Exception as e:
            print(f"Error getting courses by year: {e}")
            return False, str(e)
        finally:
            conn.close()

    def get_courses_by_section(self, section_name):
        """Get courses assigned to a specific section"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get courses assigned to the specific section
            query = """
            SELECT DISTINCT ac.course_id
            FROM assigned_courses ac
            JOIN sections s ON ac.section_id = s.id
            WHERE ac.isDeleted = 0 
            AND s.isDeleted = 0 
            AND s.name = ?
            """
            
            cursor.execute(query, (section_name,))
            results = cursor.fetchall()
            
            assigned_courses = [{'course_id': row['course_id']} for row in results]
            
            return True, assigned_courses
            
        except Exception as e:
            print(f"Error getting courses by section: {e}")
            return False, str(e)
        finally:
            conn.close()

    def check_course_in_use(self, course_id):
        """Check if a course is being used in assigned_courses"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if course is assigned to any classes
            cursor.execute("""
                SELECT COUNT(*) as assignment_count
                FROM assigned_courses 
                WHERE course_id = ? AND isDeleted = 0
            """, (course_id,))
            
            result = cursor.fetchone()
            assignment_count = result['assignment_count'] if result else 0
            
            return True, {
                'in_use': assignment_count > 0,
                'assignment_count': assignment_count
            }
            
        except Exception as e:
            print(f"Error checking course usage: {e}")
            return False, str(e)
        finally:
            conn.close()