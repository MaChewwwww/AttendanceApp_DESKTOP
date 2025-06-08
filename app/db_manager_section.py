import sqlite3
from datetime import datetime

class DatabaseSectionManager:
    def __init__(self, main_db_manager):
        self.main_db_manager = main_db_manager

    def get_sections(self, program_filter=None, year_filter=None):
        """Get all sections with optional filters"""
        conn = self.main_db_manager.get_connection()
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
                WHERE s.isDeleted = 0
            """
            params = []
            
            if program_filter and program_filter != "All":
                query += " AND p.acronym = ?"
                params.append(program_filter)
            
            if year_filter and year_filter != "All":
                # Extract year number from filter like "1st Year"
                year_num = year_filter.split()[0].replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
                query += " AND s.name LIKE ?"
                params.append(f"{year_num}%")
            
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
        conn = self.main_db_manager.get_connection()
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
            
            # Check if section already exists for this program
            existing_cursor = conn.execute(
                "SELECT id FROM sections WHERE name = ? AND program_id = ? AND isDeleted = 0",
                (section_data['name'], program_id)
            )
            if existing_cursor.fetchone():
                return False, "Section already exists for this program"
            
            # Create the section
            conn.execute(
                """INSERT INTO sections (name, program_id, created_at, updated_at)
                   VALUES (?, ?, ?, ?)""",
                (section_data['name'], program_id, datetime.now(), datetime.now())
            )
            conn.commit()
            return True, "Section created successfully"
        except Exception as e:
            conn.rollback()
            return False, f"Error creating section: {str(e)}"
        finally:
            conn.close()

    def update_section(self, section_id, section_data):
        """Update an existing section"""
        conn = self.main_db_manager.get_connection()
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
            
            # Update the section
            conn.execute(
                """UPDATE sections SET name = ?, program_id = ?, updated_at = ?
                   WHERE id = ? AND isDeleted = 0""",
                (section_data['name'], program_id, datetime.now(), section_id)
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
            conn = self.main_db_manager.get_connection()
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
            
            # Soft delete by setting isDeleted = 1
            cursor.execute("""
                UPDATE sections 
                SET isDeleted = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (section_id,))
            
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
        conn = self.main_db_manager.get_connection()
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
        conn = self.main_db_manager.get_connection()
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
        conn = self.main_db_manager.get_connection()
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
        conn = self.main_db_manager.get_connection()
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
