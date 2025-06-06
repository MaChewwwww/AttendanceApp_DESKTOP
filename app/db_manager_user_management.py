import sqlite3
import bcrypt
import re
from datetime import datetime

class DatabaseUserManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_all_users_simple(self):
        """Get all users with basic joins - simple query"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Simple query to get all user data with basic joins
            query = """
            SELECT 
                u.*,
                s.name as status_name,
                st.student_number,
                st.section as section_id,
                f.employee_number,
                sec.name as section_name,
                p.name as program_name
            FROM users u
            LEFT JOIN statuses s ON u.status_id = s.id
            LEFT JOIN students st ON u.id = st.user_id
            LEFT JOIN faculties f ON u.id = f.user_id
            LEFT JOIN sections sec ON st.section = sec.id
            LEFT JOIN programs p ON sec.program_id = p.id
            WHERE u.isDeleted = 0
            ORDER BY u.role, u.last_name, u.first_name
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            users = []
            for row in results:
                user_dict = dict(row)
                # Add full_name for convenience
                user_dict['full_name'] = f"{user_dict['first_name']} {user_dict['last_name']}"
                users.append(user_dict)
            
            conn.close()
            return True, users
            
        except Exception as e:
            print(f"Error getting all users: {e}")
            return False, str(e)

    def filter_users_python(self, all_users, search_term="", role_filter="", year_filter="", section_filter="", program_filter="", status_filter=""):
        """Filter users using Python instead of SQL"""
        filtered_users = []
        
        for user in all_users:
            # Apply role filter first
            if role_filter and role_filter != "All":
                if user['role'] != role_filter:
                    continue
            
            # Apply status filter
            if status_filter and status_filter != "All":
                if user.get('status_name') != status_filter:
                    continue
            
            # Apply search term (search in multiple fields)
            if search_term:
                search_fields = [
                    user.get('first_name', ''),
                    user.get('last_name', ''),
                    user.get('email', ''),
                    user.get('student_number', ''),
                    user.get('employee_number', ''),
                    user.get('full_name', '')
                ]
                
                # Check if search term exists in any field
                search_found = False
                for field in search_fields:
                    if field and search_term.lower() in str(field).lower():
                        search_found = True
                        break
                
                if not search_found:
                    continue
            
            # Apply year filter (for students only)
            if year_filter and year_filter != "All" and user['role'] == 'Student':
                section_name = user.get('section_name', '')
                if section_name:
                    # Extract year from section name (e.g., "1-1" -> "1")
                    section_year = section_name.split('-')[0] if '-' in section_name else ''
                    year_mapping = {'1': '1st Year', '2': '2nd Year', '3': '3rd Year', '4': '4th Year'}
                    user_year = year_mapping.get(section_year, '')
                    
                    if user_year != year_filter:
                        continue
                else:
                    # If no section, skip this user for year filter
                    continue
            
            # Apply section filter (for students only)
            if section_filter and section_filter != "All" and user['role'] == 'Student':
                if user.get('section_name') != section_filter:
                    continue
            
            # Apply program filter (for students only)
            if program_filter and program_filter != "All" and user['role'] == 'Student':
                program_name = user.get('program_name', '')
                
                # Handle both full names and abbreviations
                program_matches = False
                if program_filter == 'BSIT' and 'Information Technology' in program_name:
                    program_matches = True
                elif program_filter == 'BSCS' and 'Computer Science' in program_name:
                    program_matches = True
                elif program_filter == 'BSIS' and 'Information Systems' in program_name:
                    program_matches = True
                elif program_name == program_filter:
                    program_matches = True
                
                if not program_matches:
                    continue
            
            # If we reach here, user passes all filters
            filtered_users.append(user)
        
        return filtered_users

    def get_students_with_filters(self, search_term="", year_filter="", section_filter="", program_filter="", status_filter=""):
        """Get filtered students using Python filtering"""
        try:
            # Get all users first
            success, all_users = self.get_all_users_simple()
            if not success:
                return False, all_users
            
            # Filter to only students
            students = [user for user in all_users if user['role'] == 'Student']
            
            # Apply filters using Python
            filtered_students = self.filter_users_python(
                students,
                search_term=search_term,
                role_filter="Student",
                year_filter=year_filter,
                section_filter=section_filter,
                program_filter=program_filter,
                status_filter=status_filter
            )
            
            return True, filtered_students
            
        except Exception as e:
            print(f"Error getting filtered students: {e}")
            return False, str(e)

    def get_faculty_with_filters(self, search_term="", status_filter="", role_filter=""):
        """Get filtered faculty using Python filtering"""
        try:
            # Get all users first
            success, all_users = self.get_all_users_simple()
            if not success:
                return False, all_users
            
            # Filter to only faculty and admin
            faculty = [user for user in all_users if user['role'] in ['Faculty', 'Admin']]
            
            # Apply filters using Python
            filtered_faculty = self.filter_users_python(
                faculty,
                search_term=search_term,
                role_filter=role_filter if role_filter and role_filter != "All" else "",
                status_filter=status_filter
            )
            
            return True, filtered_faculty
            
        except Exception as e:
            print(f"Error getting filtered faculty: {e}")
            return False, str(e)

    def get_user_by_name(self, first_name, last_name, role=None):
        """Get user details by name"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT u.*, s.student_number, f.employee_number, st.name as status_name
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id
            LEFT JOIN faculties f ON u.id = f.user_id
            LEFT JOIN statuses st ON u.status_id = st.id
            WHERE u.first_name = ? AND u.last_name = ?
            """
            
            params = [first_name, last_name]
            
            if role:
                query += " AND u.role = ?"
                params.append(role)
            
            query += " AND u.isDeleted = 0 LIMIT 1"
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return True, dict(result)
            else:
                return False, "User not found"
                
        except Exception as e:
            print(f"Error getting user by name: {e}")
            return False, str(e)

    def get_user_details(self, user_id):
        """Get detailed user information from database for a specific user"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get comprehensive user data with joins - handle null sections/programs
            query = """
            SELECT 
                u.id, u.first_name, u.last_name, u.email, u.birthday, 
                u.contact_number, u.role, u.face_image, u.status_id, 
                u.verified, u.isDeleted, u.created_at, u.updated_at,
                s.name as status_name,
                st.student_number, st.section as section_id,
                f.employee_number,
                COALESCE(sec.name, '') as section_name,
                COALESCE(p.name, '') as program_name
            FROM users u
            LEFT JOIN statuses s ON u.status_id = s.id
            LEFT JOIN students st ON u.id = st.user_id
            LEFT JOIN faculties f ON u.id = f.user_id
            LEFT JOIN sections sec ON st.section = sec.id
            LEFT JOIN programs p ON sec.program_id = p.id
            WHERE u.id = ? AND u.isDeleted = 0
            """
            
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return (False, "User not found")
            
            # Convert row to dictionary - handle null values properly
            user_data = {
                'id': result['id'],
                'first_name': result['first_name'],
                'last_name': result['last_name'],
                'email': result['email'],
                'birthday': result['birthday'],
                'contact_number': result['contact_number'] or '',
                'role': result['role'],
                'face_image': result['face_image'],
                'status_id': result['status_id'],
                'status_name': result['status_name'] or 'No Status',
                'verified': result['verified'],
                'created_at': result['created_at'],
                'updated_at': result['updated_at'],
                'student_number': result['student_number'] if result['student_number'] else '',
                'section_id': result['section_id'],
                'section_name': result['section_name'] if result['section_name'] else '',
                'employee_number': result['employee_number'] if result['employee_number'] else '',
                'program_name': result['program_name'] if result['program_name'] else ''
            }
            
            conn.close()
            return (True, user_data)
            
        except Exception as e:
            print(f"Error getting user details: {e}")
            return (False, f"Database error: {str(e)}")

    def get_user_section_and_program_ids(self, user_id):
        """Get the current section_id and program_id for a user"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT st.section as section_id, s.program_id
                FROM students st
                JOIN sections s ON st.section = s.id
                WHERE st.user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return True, {'section_id': result['section_id'], 'program_id': result['program_id']}
            else:
                return False, "User section/program not found"
                
        except Exception as e:
            print(f"Error getting user section/program: {e}")
            return False, str(e)

    def update_user(self, user_id, user_data):
        """Update user information with comprehensive validations"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Begin transaction
            conn.execute("BEGIN TRANSACTION")
            
            # Validate required fields
            if not user_data.get('first_name') or not user_data.get('first_name').strip():
                conn.rollback()
                conn.close()
                return False, "First name is required"
            
            if not user_data.get('last_name') or not user_data.get('last_name').strip():
                conn.rollback()
                conn.close()
                return False, "Last name is required"
            
            if not user_data.get('email') or not user_data.get('email').strip():
                conn.rollback()
                conn.close()
                return False, "Email is required"
            
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, user_data['email'].strip()):
                conn.rollback()
                conn.close()
                return False, "Invalid email format"
            
            # Check if user exists
            cursor.execute("SELECT role FROM users WHERE id = ? AND isDeleted = 0", (user_id,))
            user_result = cursor.fetchone()
            if not user_result:
                conn.rollback()
                conn.close()
                return False, "User not found"
            
            user_role = user_result['role']
            
            # Check if email is already used by another user
            cursor.execute("SELECT id FROM users WHERE email = ? AND id != ? AND isDeleted = 0", 
                          (user_data['email'].strip(), user_id))
            if cursor.fetchone():
                conn.rollback()
                conn.close()
                return False, "Email is already in use by another user"
            
            # Validate contact number if provided
            contact_number = user_data.get('contact_number', '').strip()
            if contact_number:
                # Basic phone number validation (digits, spaces, dashes, parentheses, plus)
                phone_pattern = r'^[\d\s\-\(\)\+]+$'
                if not re.match(phone_pattern, contact_number) or len(contact_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')) < 10:
                    conn.rollback()
                    conn.close()
                    return False, "Invalid contact number format"
            
            # Get status ID if status is provided
            status_id = None
            if user_data.get('status'):
                cursor.execute("SELECT id FROM statuses WHERE name = ?", (user_data['status'],))
                status_result = cursor.fetchone()
                if status_result:
                    status_id = status_result['id']
                else:
                    conn.rollback()
                    conn.close()
                    return False, f"Invalid status: {user_data['status']}"
            
            # Prepare update data
            current_time = datetime.now().isoformat()
            
            # Build update query dynamically based on provided fields
            update_fields = []
            update_values = []
            
            # Always update these basic fields
            update_fields.extend(['first_name', 'last_name', 'email', 'contact_number', 'updated_at'])
            update_values.extend([
                user_data['first_name'].strip(),
                user_data['last_name'].strip(), 
                user_data['email'].strip(),
                contact_number,
                current_time
            ])
            
            # Update status if provided
            if status_id:
                update_fields.append('status_id')
                update_values.append(status_id)
            
            # Update password if provided
            if user_data.get('password'):
                # Validate password strength
                password = user_data['password']
                if len(password) < 6:
                    conn.rollback()
                    conn.close()
                    return False, "Password must be at least 6 characters long"
                
                # Hash the new password
                hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                update_fields.append('password_hash')
                update_values.append(hashed_pw.decode('utf-8'))
            
            # Update face image if provided
            if user_data.get('face_image'):
                # Validate face image size (max 5MB)
                if len(user_data['face_image']) > 5 * 1024 * 1024:
                    conn.rollback()
                    conn.close()
                    return False, "Face image size exceeds 5MB limit"
                
                update_fields.append('face_image')
                update_values.append(user_data['face_image'])
            
            # Update users table
            update_query = f"UPDATE users SET {', '.join([f'{field} = ?' for field in update_fields])} WHERE id = ?"
            update_values.append(user_id)
            
            cursor.execute(update_query, update_values)
            
            # Handle role-specific updates
            if user_role == 'Student':
                self._handle_student_updates(cursor, user_id, user_data, conn)
            elif user_role in ['Faculty', 'Admin']:
                self._handle_faculty_updates(cursor, user_id, user_data, conn)
            
            # Commit transaction
            conn.commit()
            conn.close()
            
            print(f"Successfully updated user {user_id}: {user_data['first_name']} {user_data['last_name']}")
            
            return True, {
                "message": "User updated successfully",
                "user_id": user_id,
                "name": f"{user_data['first_name']} {user_data['last_name']}",
                "email": user_data['email']
            }
            
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
                conn.close()
            print(f"Database error during user update: {e}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            print(f"Unexpected error during user update: {e}")
            return False, f"Update failed: {str(e)}"

    def _handle_student_updates(self, cursor, user_id, user_data, conn):
        """Handle student-specific updates"""
        # Handle program and section updates for students
        program_name = user_data.get('program')
        section_name = user_data.get('section')
        
        # Get current student record
        cursor.execute("SELECT section FROM students WHERE user_id = ?", (user_id,))
        student_result = cursor.fetchone()
        
        if student_result:
            new_section_id = None
            
            # Handle program and section assignment
            if program_name and section_name:
                # Validate section assignment using database directly
                success, section_id_or_error = self._validate_section_assignment_direct(cursor, program_name, section_name)
                if success:
                    new_section_id = section_id_or_error
                else:
                    conn.rollback()
                    conn.close()
                    raise ValueError(section_id_or_error)
            
            # Update student section (None if not assigned)
            cursor.execute("UPDATE students SET section = ? WHERE user_id = ?", 
                         (new_section_id, user_id))
        else:
            conn.rollback()
            conn.close()
            raise ValueError("Student record not found")

    def _handle_faculty_updates(self, cursor, user_id, user_data, conn):
        """Handle faculty-specific updates"""
        employee_number = user_data.get('employee_number')
        if employee_number:
            # Check if employee number already exists for another user
            cursor.execute("SELECT user_id FROM faculties WHERE employee_number = ? AND user_id != ?", 
                         (employee_number, user_id))
            if cursor.fetchone():
                conn.rollback()
                conn.close()
                raise ValueError("Employee number is already in use by another faculty member")
        
        # Check if faculty record exists
        cursor.execute("SELECT user_id FROM faculties WHERE user_id = ?", (user_id,))
        faculty_result = cursor.fetchone()
        
        if faculty_result:
            # Update existing faculty record
            if employee_number:
                cursor.execute("UPDATE faculties SET employee_number = ? WHERE user_id = ?", 
                             (employee_number, user_id))
        else:
            # Create faculty record if it doesn't exist
            cursor.execute("INSERT INTO faculties (user_id, employee_number) VALUES (?, ?)", 
                         (user_id, employee_number))

    def _validate_section_assignment_direct(self, cursor, program_abbreviation, section_name):
        """Validate section assignment using database cursor directly"""
        try:
            # Find program by abbreviation - check multiple ways
            program_id = None
            
            # Try direct name match first
            cursor.execute("SELECT id FROM programs WHERE name = ?", (program_abbreviation,))
            result = cursor.fetchone()
            if result:
                program_id = result['id']
            else:
                # Try partial match for common abbreviations
                if program_abbreviation == 'BSIT':
                    cursor.execute("SELECT id FROM programs WHERE name LIKE '%Information Technology%'")
                elif program_abbreviation == 'BSCS':
                    cursor.execute("SELECT id FROM programs WHERE name LIKE '%Computer Science%'")
                elif program_abbreviation == 'BSIS':
                    cursor.execute("SELECT id FROM programs WHERE name LIKE '%Information Systems%'")
                else:
                    cursor.execute("SELECT id FROM programs WHERE name LIKE ?", (f"%{program_abbreviation}%",))
                
                result = cursor.fetchone()
                if result:
                    program_id = result['id']
            
            if not program_id:
                return False, f"Program '{program_abbreviation}' not found"
            
            # Check if section exists in this program
            cursor.execute("SELECT id FROM sections WHERE name = ? AND program_id = ?", 
                         (section_name, program_id))
            section_result = cursor.fetchone()
            
            if section_result:
                return True, section_result['id']
            else:
                return False, f"Section '{section_name}' does not belong to program '{program_abbreviation}'"
                
        except Exception as e:
            return False, f"Error validating section assignment: {str(e)}"

    def validate_section_assignment(self, program_abbreviation, section_name):
        """Validate that a section belongs to the specified program"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            success, result = self._validate_section_assignment_direct(cursor, program_abbreviation, section_name)
            conn.close()
            
            return success, result
                
        except Exception as e:
            print(f"Error validating section assignment: {e}")
            return False, str(e)

    def delete_user(self, user_id):
        """Soft delete a user by setting isDeleted flag"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id, first_name, last_name FROM users WHERE id = ? AND isDeleted = 0", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False, "User not found"
            
            # Soft delete the user
            current_time = datetime.now().isoformat()
            cursor.execute("""
                UPDATE users 
                SET isDeleted = 1, updated_at = ? 
                WHERE id = ?
            """, (current_time, user_id))
            
            conn.commit()
            conn.close()
            
            print(f"Successfully deleted user {user_id}: {user['first_name']} {user['last_name']}")
            return True, "User deleted successfully"
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False, str(e)

    def restore_user(self, user_id):
        """Restore a soft-deleted user"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Check if user exists and is deleted
            cursor.execute("SELECT id, first_name, last_name FROM users WHERE id = ? AND isDeleted = 1", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False, "Deleted user not found"
            
            # Restore the user
            current_time = datetime.now().isoformat()
            cursor.execute("""
                UPDATE users 
                SET isDeleted = 0, updated_at = ? 
                WHERE id = ?
            """, (current_time, user_id))
            
            conn.commit()
            conn.close()
            
            print(f"Successfully restored user {user_id}: {user['first_name']} {user['last_name']}")
            return True, "User restored successfully"
            
        except Exception as e:
            print(f"Error restoring user: {e}")
            return False, str(e)

    def get_deleted_users(self):
        """Get all soft-deleted users"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT 
                u.id, u.first_name, u.last_name, u.email, u.role,
                u.created_at, u.updated_at,
                s.name as status_name,
                st.student_number,
                f.employee_number
            FROM users u
            LEFT JOIN statuses s ON u.status_id = s.id
            LEFT JOIN students st ON u.id = st.user_id
            LEFT JOIN faculties f ON u.id = f.user_id
            WHERE u.isDeleted = 1
            ORDER BY u.updated_at DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            users = [dict(row) for row in results]
            conn.close()
            
            return True, users
            
        except Exception as e:
            print(f"Error getting deleted users: {e}")
            return False, str(e)

    def get_assigned_courses(self, faculty_id=None):
        """Get assigned courses with optional faculty filter"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT 
                ac.id,
                ac.user_id as faculty_id,
                ac.course_id,
                ac.section_id,
                ac.academic_year,
                ac.semester,
                ac.schedule_day,
                ac.schedule_time,
                ac.room,
                c.name as course_name,
                c.description as course_description,
                s.name as section_name,
                p.name as program_name,
                u.first_name || ' ' || u.last_name as faculty_name
            FROM assigned_courses ac
            JOIN courses c ON ac.course_id = c.id
            JOIN sections s ON ac.section_id = s.id
            JOIN programs p ON s.program_id = p.id
            JOIN users u ON ac.user_id = u.id
            WHERE u.isDeleted = 0
            """
            
            params = []
            if faculty_id:
                query += " AND ac.user_id = ?"
                params.append(faculty_id)
            
            query += " ORDER BY c.name, s.name"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            courses = []
            for row in results:
                course_dict = dict(row)
                courses.append(course_dict)
            
            conn.close()
            return True, courses
            
        except Exception as e:
            print(f"Error getting assigned courses: {e}")
            return False, str(e)

    def get_student_attendance_summary(self, user_id):
        """Get attendance summary for a specific student"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get attendance summary grouped by course
            query = """
            SELECT 
                c.name as course_name,
                s.name as section_name,
                p.name as program_name,
                COUNT(al.id) as total_classes,
                SUM(CASE WHEN al.status = 'present' THEN 1 ELSE 0 END) as present_count,
                SUM(CASE WHEN al.status = 'absent' THEN 1 ELSE 0 END) as absent_count,
                SUM(CASE WHEN al.status = 'late' THEN 1 ELSE 0 END) as late_count,
                ac.id as assigned_course_id,
                ac.schedule_day,
                ac.schedule_time,
                ac.room,
                ac.semester,
                ac.academic_year
            FROM attendance_logs al
            JOIN assigned_courses ac ON al.assigned_course_id = ac.id
            JOIN courses c ON ac.course_id = c.id
            JOIN sections sec ON ac.section_id = sec.id
            JOIN programs p ON sec.program_id = p.id
            LEFT JOIN sections s ON ac.section_id = s.id
            WHERE al.user_id = ?
            GROUP BY ac.id, c.name, s.name, p.name
            ORDER BY c.name, s.name
            """
            
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            
            summary = []
            for row in results:
                summary_dict = dict(row)
                summary.append(summary_dict)
            
            conn.close()
            return True, summary
            
        except Exception as e:
            print(f"Error getting student attendance summary: {e}")
            return False, str(e)

    def get_programs(self):
        """Get all available programs"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description, acronym, color
                FROM programs 
                WHERE isDeleted = 0
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
            conn = self.db_manager.get_connection()
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

    def get_sections_all(self):
        """Get all sections from all programs"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.id, s.name, s.created_at, s.updated_at, p.name as program_name
                FROM sections s
                JOIN programs p ON s.program_id = p.id
                WHERE p.isDeleted = 0
                ORDER BY p.name ASC, s.name ASC
            """)
            
            sections = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            section_list = []
            for section in sections:
                section_dict = {
                    'id': section[0],
                    'name': section[1],
                    'created_at': section[2],
                    'updated_at': section[3],
                    'program_name': section[4]
                }
                section_list.append(section_dict)
            
            return True, section_list
            
        except Exception as e:
            print(f"Exception in get_sections_all: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)

    def get_sections_by_program(self, program_name):
        """Get all sections for a specific program by program name"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Check if the program exists
            cursor.execute("SELECT id FROM programs WHERE name = ? AND isDeleted = 0", (program_name,))
            program_result = cursor.fetchone()
            
            if not program_result:
                conn.close()
                return True, []  # Return empty list but success=True
            
            program_id = program_result[0]
            
            # Now get sections for this program
            cursor.execute("""
                SELECT s.id, s.name, s.created_at, s.updated_at, p.name as program_name
                FROM sections s
                JOIN programs p ON s.program_id = p.id
                WHERE s.program_id = ? 
                ORDER BY s.name ASC
            """, (program_id,))
            
            sections = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            section_list = []
            for section in sections:
                section_dict = {
                    'id': section[0],
                    'name': section[1],
                    'created_at': section[2],
                    'updated_at': section[3],
                    'program_name': section[4]
                }
                section_list.append(section_dict)
            
            return True, section_list
            
        except Exception as e:
            print(f"Exception in get_sections_by_program: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)

    def get_statuses(self, user_type=None):
        """Get all statuses, optionally filtered by user type"""
        try:
            conn = self.db_manager.get_connection()
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
