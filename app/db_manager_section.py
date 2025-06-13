import sqlite3
from datetime import datetime
from .config import DB_PATH

class DatabaseSectionManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_connection(self):
        """Create and return a new database connection."""
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def get_sections(self, program_filter=None, year_filter=None, academic_year=None, semester=None):
        """Get all sections with optional filters"""
        conn = self.db_manager.get_connection()
        try:
            query = """
                SELECT s.id, s.name, p.name as program_name, p.acronym as program_acronym,
                       COUNT(st.id) as student_count,
                       s.created_at, s.updated_at
                FROM sections s
                LEFT JOIN programs p ON s.program_id = p.id
                LEFT JOIN students st ON s.id = st.section AND st.user_id IN (
                    SELECT id FROM users WHERE isDeleted = 0
                )
            """
            
            # Add joins for academic year and semester filtering if needed
            if academic_year or semester:
                query += """
                    LEFT JOIN assigned_courses ac ON s.id = ac.section_id AND ac.isDeleted = 0
                """
            
            query += " WHERE s.isDeleted = 0"
            params = []
            
            if program_filter and program_filter != "All":
                query += " AND p.acronym = ?"
                params.append(program_filter)
            
            if year_filter and year_filter != "All":
                # Extract year number from filter like "1st Year"
                year_num = year_filter.split()[0].replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
                query += " AND s.name LIKE ?"
                params.append(f"{year_num}%")
            
            if academic_year:
                query += " AND ac.academic_year = ?"
                params.append(academic_year)
            
            if semester:
                query += " AND ac.semester = ?"
                params.append(semester)
            
            query += " GROUP BY s.id, s.name, p.name, p.acronym ORDER BY p.acronym, s.name"
            
            cursor = conn.execute(query, params)
            sections = cursor.fetchall()
            
            # Convert to list of dictionaries
            result = []
            for row in sections:
                # Determine year from section name (assuming format like "1-1", "2-3", etc.)
                year_num = row['name'].split('-')[0] if '-' in row['name'] else '1'
                year_display = f"{year_num}{'st' if year_num == '1' else 'nd' if year_num == '2' else 'rd' if year_num == '3' else 'th'} Year"
                
                result.append({
                    'id': row['id'],
                    'name': row['name'],
                    'program_name': row['program_name'],
                    'program_acronym': row['program_acronym'],
                    'year': year_display,
                    'student_count': row['student_count'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            
            return result
        finally:
            conn.close()

    def create_section(self, section_data):
        """Create a new section"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Validate required fields - handle both 'program_id' and 'program' keys
            if not section_data.get('name'):
                return False, "Section name is required"
            
            # Handle both program_id and program keys for backward compatibility
            program_id = section_data.get('program_id') or section_data.get('program')
            if not program_id:
                return False, "Program is required"
            
            # Check if section already exists for this program
            cursor.execute("""
                SELECT id FROM sections 
                WHERE name = ? AND program_id = ? AND isDeleted = 0
            """, (section_data['name'], program_id))
            
            if cursor.fetchone():
                return False, "Section already exists for this program"
            
            # Insert the new section
            cursor.execute("""
                INSERT INTO sections (name, program_id, isDeleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                section_data['name'],
                program_id,
                0,  # isDeleted = 0 (not deleted)
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            section_id = cursor.lastrowid
            return True, {"id": section_id, "message": "Section created successfully"}
            
        except Exception as e:
            conn.rollback()
            print(f"Error creating section: {e}")
            return False, str(e)
        finally:
            conn.close()

    def update_section(self, section_id, section_data):
        """Update an existing section"""
        conn = self.db_manager.get_connection()
        try:
            # Get program_id from program name
            program_cursor = conn.execute(
                "SELECT id FROM programs WHERE name = ? AND isDeleted = 0",
                (section_data['program'],)
            )
            program_row = program_cursor.fetchone()
            if not program_row:
                return False, "Program not found"
            
            program_id = program_row['id']
            
            # Check if section name already exists for this program (excluding current section)
            existing_cursor = conn.execute(
                "SELECT id FROM sections WHERE name = ? AND program_id = ? AND id != ? AND isDeleted = 0",
                (section_data['name'], program_id, section_id)
            )
            if existing_cursor.fetchone():
                return False, "Section name already exists for this program"
            
            # Update the section with proper datetime format
            current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
            conn.execute(
                """UPDATE sections SET name = ?, program_id = ?, updated_at = ?
                   WHERE id = ? AND isDeleted = 0""",
                (section_data['name'], program_id, current_time, section_id)
            )
            conn.commit()
            return True, "Section updated successfully"
        except Exception as e:
            conn.rollback()
            return False, f"Error updating section: {str(e)}"
        finally:
            conn.close()

    def delete_section(self, section_id):
        """Soft delete a section by setting isDeleted = 1"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Check if section exists and is not already deleted
            cursor.execute("""
                SELECT id, name FROM sections 
                WHERE id = ? AND isDeleted = 0
            """, (section_id,))
            
            section = cursor.fetchone()
            if not section:
                conn.close()
                return False, "Section not found or already deleted"
            
            # Soft delete by setting isDeleted = 1 with proper datetime format
            current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
            cursor.execute("""
                UPDATE sections 
                SET isDeleted = 1, updated_at = ?
                WHERE id = ?
            """, (current_time, section_id))
            
            if cursor.rowcount == 0:
                conn.close()
                return False, "Failed to delete section"
            
            conn.commit()
            conn.close()
            return True, "Section deleted successfully"
            
        except Exception as e:
            if 'conn' in locals():
                conn.close()
            print(f"Error in delete_section: {e}")
            return False, f"Database error: {str(e)}"

    def check_section_in_use(self, section_id):
        """Check if section is being used by students or assigned courses"""
        conn = self.db_manager.get_connection()
        try:
            # Check if any students are assigned to this section
            student_cursor = conn.execute(
                """SELECT COUNT(*) as count FROM students s
                   JOIN users u ON s.user_id = u.id
                   WHERE s.section = ? AND u.isDeleted = 0""",
                (section_id,)
            )
            student_count = student_cursor.fetchone()['count']
            
            # Check if any assigned courses use this section
            course_cursor = conn.execute(
                "SELECT COUNT(*) as count FROM assigned_courses WHERE section_id = ? AND isDeleted = 0",
                (section_id,)
            )
            course_count = course_cursor.fetchone()['count']
            
            return student_count > 0 or course_count > 0
        finally:
            conn.close()

    def get_section_details(self, section_id):
        """Get detailed information about a section"""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.execute(
                """SELECT s.id, s.name, p.name as program_name, p.acronym as program_acronym,
                          s.created_at, s.updated_at
                   FROM sections s
                   LEFT JOIN programs p ON s.program_id = p.id
                   WHERE s.id = ? AND s.isDeleted = 0""",
                (section_id,)
            )
            section = cursor.fetchone()
            if not section:
                return None
            
            return {
                'id': section['id'],
                'name': section['name'],
                'program_name': section['program_name'],
                'program_acronym': section['program_acronym'],
                'created_at': section['created_at'],
                'updated_at': section['updated_at']
            }
        finally:
            conn.close()

    def get_section_students(self, section_id, search_term="", status_filter=""):
        """Get students in a specific section"""
        conn = self.db_manager.get_connection()
        try:
            query = """
                SELECT u.id, u.first_name, u.last_name, u.email, st.student_number,
                       stat.name as status_name
                FROM students st
                JOIN users u ON st.user_id = u.id
                LEFT JOIN statuses stat ON u.status_id = stat.id
                WHERE st.section = ? AND u.isDeleted = 0
            """
            params = [section_id]
            
            if search_term:
                query += " AND (u.first_name LIKE ? OR u.last_name LIKE ? OR u.email LIKE ? OR st.student_number LIKE ?)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
            
            if status_filter and status_filter != "All":
                query += " AND stat.name = ?"
                params.append(status_filter)
            
            query += " ORDER BY u.last_name, u.first_name"
            
            cursor = conn.execute(query, params)
            students = cursor.fetchall()
            
            return [{
                'id': row['id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'email': row['email'],
                'student_number': row['student_number'],
                'status_name': row['status_name'] or 'Active'
            } for row in students]
        finally:
            conn.close()

    def get_section_statistics(self, section_id, academic_year=None, semester=None):
        """Get statistics for a specific section"""
        conn = self.db_manager.get_connection()
        try:
            # Get total students
            student_cursor = conn.execute(
                """SELECT COUNT(*) as count FROM students s
                   JOIN users u ON s.user_id = u.id
                   WHERE s.section = ? AND u.isDeleted = 0""",
                (section_id,)
            )
            total_students = student_cursor.fetchone()['count']
            
            # Get total courses
            course_query = """
                SELECT COUNT(*) as count FROM assigned_courses ac
                JOIN courses c ON ac.course_id = c.id
                WHERE ac.section_id = ? AND ac.isDeleted = 0 AND c.isDeleted = 0
            """
            course_params = [section_id]
            
            if academic_year:
                course_query += " AND ac.academic_year = ?"
                course_params.append(academic_year)
            
            if semester:
                course_query += " AND ac.semester = ?"
                course_params.append(semester)
            
            course_cursor = conn.execute(course_query, course_params)
            total_courses = course_cursor.fetchone()['count']
            
            # Get average attendance rate (placeholder - would need actual attendance data)
            avg_attendance = 85.5  # Placeholder
            
            return {
                'total_students': total_students,
                'total_courses': total_courses,
                'average_attendance': avg_attendance
            }
        finally:
            conn.close()

    def get_section_courses(self, section_id, academic_year=None, semester=None):
        """Get courses assigned to a specific section with complete assignment data"""
        conn = self.db_manager.get_connection()
        try:
            query = """
                SELECT c.id as course_id, c.name as course_name, c.code as course_code,
                       c.description, p.name as program_name, p.acronym as program_acronym,
                       ac.id as assignment_id, ac.section_id, ac.academic_year, ac.semester, ac.room,
                       u.first_name as faculty_first_name, u.last_name as faculty_last_name,
                       u.id as faculty_id, f.employee_number,
                       (SELECT COUNT(*) FROM schedules s WHERE s.assigned_course_id = ac.id) as schedule_count
                FROM assigned_courses ac
                JOIN courses c ON ac.course_id = c.id
                JOIN programs p ON c.program_id = p.id
                LEFT JOIN users u ON ac.faculty_id = u.id AND u.isDeleted = 0
                LEFT JOIN faculties f ON u.id = f.user_id
                WHERE ac.section_id = ? AND ac.isDeleted = 0 AND c.isDeleted = 0
            """
            params = [section_id]
            
            if academic_year:
                query += " AND ac.academic_year = ?"
                params.append(academic_year)
            
            if semester:
                query += " AND ac.semester = ?"
                params.append(semester)
            
            query += " ORDER BY c.name"
            
            cursor = conn.execute(query, params)
            courses = cursor.fetchall()
            
            if not courses:
                return True, []  # Return success with empty list
            
            # Convert to list of dictionaries with complete data
            result = []
            for row in courses:
                assignment_data = {
                    'course_id': row['course_id'],
                    'course_name': row['course_name'] or '',
                    'course_code': row['course_code'] or '',
                    'description': row['description'] or '',
                    'program_name': row['program_name'] or '',
                    'program_acronym': row['program_acronym'] or '',
                    'assignment_id': row['assignment_id'],
                    'section_id': row['section_id'],  # Added section_id to the returned data
                    'academic_year': row['academic_year'] or '',
                    'semester': row['semester'] or '',
                    'room': row['room'] or '',
                    'faculty_id': row['faculty_id'],
                    'faculty_first_name': row['faculty_first_name'] or '',
                    'faculty_last_name': row['faculty_last_name'] or '',
                    'employee_number': row['employee_number'] or '',
                    'faculty_name': f"{row['faculty_first_name']} {row['faculty_last_name']}" if row['faculty_first_name'] and row['faculty_last_name'] else "No Faculty Assigned",
                    'has_schedule': row['schedule_count'] > 0,
                    'schedule_count': row['schedule_count']
                }
                result.append(assignment_data)
            
            return True, result
            
        except Exception as e:
            print(f"Error getting section courses: {e}")
            return False, str(e)
        finally:
            conn.close()

    def get_section_courses_attendance_stats(self, section_id, academic_year=None, semester=None):
        """Get attendance statistics for all courses in a section with filters"""
        conn = self.db_manager.get_connection()
        try:
            query = """
                SELECT 
                    c.id as course_id,
                    c.name as course_name,
                    c.code as course_code,
                    ac.academic_year,
                    ac.semester,
                    COUNT(CASE WHEN al.status = 'present' THEN 1 END) as present_count,
                    COUNT(CASE WHEN al.status = 'absent' THEN 1 END) as absent_count,
                    COUNT(CASE WHEN al.status = 'late' THEN 1 END) as late_count,
                    COUNT(al.id) as total_logs,
                    COUNT(DISTINCT al.user_id) as student_count
                FROM assigned_courses ac
                JOIN courses c ON ac.course_id = c.id
                LEFT JOIN attendance_logs al ON ac.id = al.assigned_course_id
                LEFT JOIN users u ON al.user_id = u.id AND u.isDeleted = 0
                LEFT JOIN students s ON u.id = s.user_id AND s.section = ?
                WHERE ac.section_id = ? 
                  AND ac.isDeleted = 0 
                  AND c.isDeleted = 0
            """
            
            params = [section_id, section_id]
            
            if academic_year:
                query += " AND ac.academic_year = ?"
                params.append(academic_year)
            
            if semester:
                query += " AND ac.semester = ?"
                params.append(semester)
            
            query += """
                GROUP BY c.id, c.name, c.code, ac.academic_year, ac.semester
                ORDER BY c.name
            """
            
            cursor = conn.execute(query, params)
            results = cursor.fetchall()
            
            courses_stats = []
            for row in results:
                present_count = row['present_count'] or 0
                absent_count = row['absent_count'] or 0
                late_count = row['late_count'] or 0
                total_logs = row['total_logs'] or 0
                
                # Count late as present for attendance rate calculation
                effective_present = present_count + late_count
                
                if total_logs > 0:
                    present_rate = (effective_present / total_logs) * 100
                    absent_rate = (absent_count / total_logs) * 100
                else:
                    present_rate = 0.0
                    absent_rate = 0.0
                
                courses_stats.append({
                    'course_id': row['course_id'],
                    'course_name': row['course_name'] or 'Unknown Course',
                    'course_code': row['course_code'] or 'N/A',
                    'academic_year': row['academic_year'],
                    'semester': row['semester'],
                    'present_rate': round(present_rate, 1),
                    'absent_rate': round(absent_rate, 1),
                    'total_logs': total_logs,
                    'student_count': row['student_count'] or 0
                })
            
            return True, courses_stats
            
        except Exception as e:
            print(f"Error getting section courses attendance stats: {e}")
            return False, []
        finally:
            conn.close()

    def get_available_academic_years_for_section(self, section_id):
        """Get unique academic years from assigned courses for a specific section"""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.execute("""
                SELECT DISTINCT ac.academic_year
                FROM assigned_courses ac
                WHERE ac.section_id = ? AND ac.isDeleted = 0
                  AND ac.academic_year IS NOT NULL 
                  AND ac.academic_year != ''
                ORDER BY ac.academic_year DESC
            """, (section_id,))
            
            rows = cursor.fetchall()
            academic_years = [row['academic_year'] for row in rows]
            
            return True, academic_years
            
        except Exception as e:
            print(f"Error getting academic years for section: {e}")
            return False, []
        finally:
            conn.close()

    def get_available_academic_years_for_course_section(self, course_id, section_id):
        """Get unique academic years for a specific course and section combination"""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.execute("""
                SELECT DISTINCT ac.academic_year
                FROM assigned_courses ac
                WHERE ac.course_id = ? AND ac.section_id = ?
                  AND ac.isDeleted = 0 
                  AND ac.academic_year IS NOT NULL 
                  AND ac.academic_year != ''
                ORDER BY ac.academic_year DESC
            """, (course_id, section_id))
            
            rows = cursor.fetchall()
            academic_years = [row['academic_year'] for row in rows]
            
            return True, academic_years
            
        except Exception as e:
            print(f"Error getting academic years for course and section: {e}")
            return False, []
        finally:
            conn.close()
