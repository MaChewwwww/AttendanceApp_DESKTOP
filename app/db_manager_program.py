from .config import DB_PATH
import sqlite3

class DatabaseProgramManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_connection(self):
        """Create and return a new database connection."""
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def create_program(self, program_data):
        """
        Create a new program
        
        Args:
            program_data (dict): Dictionary containing program information
                - name (str): Program name
                - acronym (str): Program acronym
                - code (str): Program code
                - description (str): Program description (optional)
                - color (str): Hex color code (optional)
        
        Returns:
            tuple: (success: bool, result: dict/str)
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if acronym already exists
            cursor.execute("""
                SELECT id FROM programs 
                WHERE acronym = ? AND isDeleted = 0
            """, (program_data['acronym'],))
            
            if cursor.fetchone():
                return False, "A program with this acronym already exists."
            
            # Check if code already exists
            cursor.execute("""
                SELECT id FROM programs 
                WHERE code = ? AND isDeleted = 0
            """, (program_data['code'],))
            
            if cursor.fetchone():
                return False, "A program with this code already exists."
            
            # Create new program
            cursor.execute("""
                INSERT INTO programs (name, acronym, code, description, color, isDeleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 0, datetime('now'), datetime('now'))
            """, (
                program_data['name'],
                program_data['acronym'],
                program_data['code'],
                program_data.get('description', ''),
                program_data.get('color', '#3B82F6')
            ))
            
            program_id = cursor.lastrowid
            conn.commit()
            
            # Return the created program data
            cursor.execute("""
                SELECT id, name, acronym, code, description, color, created_at, updated_at
                FROM programs WHERE id = ?
            """, (program_id,))
            
            program = cursor.fetchone()
            if program:
                program_dict = {
                    'id': program['id'],
                    'name': program['name'],
                    'acronym': program['acronym'],
                    'code': program['code'],
                    'description': program['description'],
                    'color': program['color'],
                    'created_at': program['created_at'],
                    'updated_at': program['updated_at']
                }
                return True, program_dict
            else:
                return False, "Failed to retrieve created program."
            
        except Exception as e:
            conn.rollback()
            print(f"Error creating program: {e}")
            return False, f"Failed to create program: {str(e)}"
        finally:
            conn.close()

    def update_program(self, program_id, program_data):
        """
        Update an existing program
        
        Args:
            program_id (int): Program ID
            program_data (dict): Dictionary containing updated program information
        
        Returns:
            tuple: (success: bool, result: dict/str)
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if program exists
            cursor.execute("""
                SELECT id FROM programs 
                WHERE id = ? AND isDeleted = 0
            """, (program_id,))
            
            if not cursor.fetchone():
                return False, "Program not found."
            
            # Check for duplicate acronym (excluding current program)
            if 'acronym' in program_data:
                cursor.execute("""
                    SELECT id FROM programs 
                    WHERE acronym = ? AND id != ? AND isDeleted = 0
                """, (program_data['acronym'], program_id))
                
                if cursor.fetchone():
                    return False, "A program with this acronym already exists."
            
            # Check for duplicate code (excluding current program)
            if 'code' in program_data:
                cursor.execute("""
                    SELECT id FROM programs 
                    WHERE code = ? AND id != ? AND isDeleted = 0
                """, (program_data['code'], program_id))
                
                if cursor.fetchone():
                    return False, "A program with this code already exists."
            
            # Build update query dynamically
            update_fields = []
            update_values = []
            
            for key, value in program_data.items():
                if key in ['name', 'acronym', 'code', 'description', 'color']:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            if update_fields:
                update_fields.append("updated_at = datetime('now')")
                update_values.append(program_id)
                
                query = f"UPDATE programs SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, update_values)
            
            conn.commit()
            
            # Return updated program data
            cursor.execute("""
                SELECT id, name, acronym, code, description, color, created_at, updated_at
                FROM programs WHERE id = ?
            """, (program_id,))
            
            program = cursor.fetchone()
            if program:
                program_dict = {
                    'id': program['id'],
                    'name': program['name'],
                    'acronym': program['acronym'],
                    'code': program['code'],
                    'description': program['description'],
                    'color': program['color'],
                    'created_at': program['created_at'],
                    'updated_at': program['updated_at']
                }
                return True, program_dict
            else:
                return False, "Failed to retrieve updated program."
            
        except Exception as e:
            conn.rollback()
            print(f"Error updating program: {e}")
            return False, f"Failed to update program: {str(e)}"
        finally:
            conn.close()

    def delete_program(self, program_id):
        """
        Soft delete a program (set isDeleted = 1)
        
        Args:
            program_id (int): Program ID
        
        Returns:
            tuple: (success: bool, result: str)
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if program exists
            cursor.execute("""
                SELECT id FROM programs 
                WHERE id = ? AND isDeleted = 0
            """, (program_id,))
            
            if not cursor.fetchone():
                return False, "Program not found."
            
            # Soft delete by setting isDeleted flag
            cursor.execute("""
                UPDATE programs 
                SET isDeleted = 1, updated_at = datetime('now')
                WHERE id = ?
            """, (program_id,))
            
            conn.commit()
            return True, "Program deleted successfully."
            
        except Exception as e:
            conn.rollback()
            print(f"Error deleting program: {e}")
            return False, f"Failed to delete program: {str(e)}"
        finally:
            conn.close()

    def check_program_in_use(self, program_id):
        """
        Check if a program is being used by students or sections
        
        Args:
            program_id (int): Program ID
        
        Returns:
            tuple: (success: bool, result: dict/str)
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get all students and their sections
            cursor.execute("""
                SELECT u.id, s.section 
                FROM users u
                JOIN students s ON u.id = s.user_id
                WHERE u.isDeleted = 0 AND u.role = 'Student'
            """)
            students_data = cursor.fetchall()
            
            # Get all sections for this program
            cursor.execute("""
                SELECT id FROM sections 
                WHERE program_id = ? AND isDeleted = 0
            """, (program_id,))
            program_sections = [row['id'] for row in cursor.fetchall()]
            
            # Filter students in Python
            student_count = 0
            for student in students_data:
                if student['section'] in program_sections:
                    student_count += 1
            
            # Count sections directly
            section_count = len(program_sections)
            
            usage_info = {
                'in_use': student_count > 0 or section_count > 0,
                'student_count': student_count,
                'section_count': section_count
            }
            
            return True, usage_info
            
        except Exception as e:
            print(f"Error checking program usage: {e}")
            return False, f"Failed to check program usage: {str(e)}"
        finally:
            conn.close()

    def get_program_statistics(self, program_id, academic_year=None, semester=None):
        """
        Get comprehensive statistics for a specific program
        
        Args:
            program_id (int): Program ID
            academic_year (str): Optional academic year filter (e.g., "2024-2025")
            semester (str): Optional semester filter (e.g., "1st Semester")
        
        Returns:
            tuple: (success: bool, result: dict/str)
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get all students and their sections
            cursor.execute("""
                SELECT u.id, s.section 
                FROM users u
                JOIN students s ON u.id = s.user_id
                WHERE u.isDeleted = 0 AND u.role = 'Student'
            """)
            students_data = cursor.fetchall()
            
            # Get all sections for this program
            cursor.execute("""
                SELECT id FROM sections 
                WHERE program_id = ? AND isDeleted = 0
            """, (program_id,))
            program_sections = [row['id'] for row in cursor.fetchall()]
            
            # Filter students in Python
            program_student_ids = []
            for student in students_data:
                if student['section'] in program_sections:
                    program_student_ids.append(student['id'])
            
            total_students = len(program_student_ids)
            
            # Get total courses in the program
            cursor.execute("""
                SELECT COUNT(*) as total_courses 
                FROM courses 
                WHERE program_id = ? AND isDeleted = 0
            """, (program_id,))
            total_courses = cursor.fetchone()['total_courses']
            
            # Get total sections
            total_sections = len(program_sections)
            
            # Get attendance logs with academic year and semester filtering
            if academic_year or semester:
                # Get assigned courses that match the filters
                filter_conditions = ["1=1"]
                filter_params = []
                
                if academic_year:
                    filter_conditions.append("academic_year = ?")
                    filter_params.append(academic_year)
                
                if semester:
                    filter_conditions.append("semester = ?")
                    filter_params.append(semester)
                
                cursor.execute(f"""
                    SELECT id FROM assigned_courses 
                    WHERE {' AND '.join(filter_conditions)}
                """, filter_params)
                
                valid_assigned_course_ids = [row['id'] for row in cursor.fetchall()]
                
                # Get attendance logs only for these assigned courses
                cursor.execute("""
                    SELECT user_id, status, assigned_course_id
                    FROM attendance_logs
                """)
                all_attendance_data = cursor.fetchall()
                
                # Filter in Python
                attendance_data = []
                for log in all_attendance_data:
                    if log['assigned_course_id'] in valid_assigned_course_ids:
                        attendance_data.append(log)
            else:
                # Get all attendance logs
                cursor.execute("""
                    SELECT user_id, status 
                    FROM attendance_logs
                """)
                attendance_data = cursor.fetchall()
            
            # Filter attendance logs for students in this program
            total_present = 0
            total_absents = 0
            total_late = 0
            total_records = 0
            
            for log in attendance_data:
                if log['user_id'] in program_student_ids:
                    total_records += 1
                    if log['status'] == 'present':
                        total_present += 1
                    elif log['status'] == 'absent':
                        total_absents += 1
                    elif log['status'] == 'late':
                        total_late += 1
            
            # Calculate attendance rate
            attendance_rate = 0
            if total_records > 0:
                attendance_rate = round((total_present / total_records) * 100, 1)
            
            statistics = {
                'total_students': total_students,
                'total_courses': total_courses,
                'total_sections': total_sections,
                'total_absents': total_absents,
                'total_present': total_present,
                'total_late': total_late,
                'attendance_rate': f"{attendance_rate}%",
                'total_attendance_records': total_records,
                'academic_year': academic_year or 'All Years',
                'semester': semester or 'All Semesters'
            }
            
            return True, statistics
            
        except Exception as e:
            print(f"Error getting program statistics: {e}")
            return False, f"Failed to get program statistics: {str(e)}"
        finally:
            conn.close()

    def get_available_academic_years(self):
        """Get list of available academic years from assigned_courses"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT academic_year 
                FROM assigned_courses 
                ORDER BY academic_year DESC
            """)
            years = [row['academic_year'] for row in cursor.fetchall()]
            return True, years
        except Exception as e:
            print(f"Error getting academic years: {e}")
            return False, []
        finally:
            conn.close()

    def get_available_semesters(self):
        """Get list of available semesters from assigned_courses"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT semester 
                FROM assigned_courses 
                ORDER BY semester
            """)
            semesters = [row['semester'] for row in cursor.fetchall()]
            return True, semesters
        except Exception as e:
            print(f"Error getting semesters: {e}")
            return False, []
        finally:
            conn.close()

    def get_program_key_metrics(self, program_id, academic_year=None, semester=None):
        """
        Get key metrics for program analytics
        
        Args:
            program_id (int): Program ID
            academic_year (str): Optional academic year filter
            semester (str): Optional semester filter
        
        Returns:
            tuple: (success: bool, result: dict/str)
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get program sections
            cursor.execute("""
                SELECT id FROM sections 
                WHERE program_id = ? AND isDeleted = 0
            """, (program_id,))
            program_sections = [row['id'] for row in cursor.fetchall()]
            
            if not program_sections:
                return True, {
                    'current_month': '0%',
                    'previous_month': '0%',
                    'best_month': '0%',
                    'lowest_month': '0%',
                    'most_active_day': 'N/A'
                }
            
            # Get students in this program
            cursor.execute("""
                SELECT u.id
                FROM users u
                JOIN students s ON u.id = s.user_id
                WHERE u.isDeleted = 0 AND u.role = 'Student' AND s.section IN ({})
            """.format(','.join('?' * len(program_sections))), program_sections)
            program_student_ids = [row['id'] for row in cursor.fetchall()]
            
            if not program_student_ids:
                return True, {
                    'current_month': '0%',
                    'previous_month': '0%',
                    'best_month': '0%',
                    'lowest_month': '0%',
                    'most_active_day': 'N/A'
                }
            
            # Filter assigned courses based on year/semester if provided
            if academic_year or semester:
                filter_conditions = ["1=1"]
                filter_params = []
                
                if academic_year:
                    filter_conditions.append("academic_year = ?")
                    filter_params.append(academic_year)
                
                if semester:
                    filter_conditions.append("semester = ?")
                    filter_params.append(semester)
                
                cursor.execute(f"""
                    SELECT id FROM assigned_courses 
                    WHERE {' AND '.join(filter_conditions)}
                """, filter_params)
                
                valid_assigned_course_ids = [row['id'] for row in cursor.fetchall()]
                
                if not valid_assigned_course_ids:
                    return True, {
                        'current_month': '0%',
                        'previous_month': '0%',
                        'best_month': '0%',
                        'lowest_month': '0%',
                        'most_active_day': 'N/A'
                    }
                
                # Get attendance logs for filtered courses
                cursor.execute("""
                    SELECT al.user_id, al.status, al.date, al.assigned_course_id
                    FROM attendance_logs al
                    WHERE al.assigned_course_id IN ({})
                """.format(','.join('?' * len(valid_assigned_course_ids))), valid_assigned_course_ids)
                
                all_attendance_data = cursor.fetchall()
                
                # Filter for program students
                attendance_data = [log for log in all_attendance_data if log['user_id'] in program_student_ids]
            else:
                # Get all attendance logs for program students
                cursor.execute("""
                    SELECT al.user_id, al.status, al.date
                    FROM attendance_logs al
                    WHERE al.user_id IN ({})
                """.format(','.join('?' * len(program_student_ids))), program_student_ids)
                
                attendance_data = cursor.fetchall()
            
            if not attendance_data:
                return True, {
                    'current_month': '0%',
                    'previous_month': '0%',
                    'best_month': '0%',
                    'lowest_month': '0%',
                    'most_active_day': 'N/A'
                }
            
            # Calculate monthly attendance rates
            from datetime import datetime, timedelta
            import calendar
            
            monthly_stats = {}
            daily_stats = {}
            
            for log in attendance_data:
                try:
                    log_date = datetime.strptime(log['date'], '%Y-%m-%d')
                    month_key = f"{log_date.year}-{log_date.month:02d}"
                    day_name = calendar.day_name[log_date.weekday()]
                    
                    # Monthly stats
                    if month_key not in monthly_stats:
                        monthly_stats[month_key] = {'total': 0, 'present': 0, 'date_obj': log_date}
                    
                    monthly_stats[month_key]['total'] += 1
                    if log['status'] == 'present':
                        monthly_stats[month_key]['present'] += 1
                    
                    # Daily stats
                    if day_name not in daily_stats:
                        daily_stats[day_name] = {'total': 0, 'present': 0}
                    
                    daily_stats[day_name]['total'] += 1
                    if log['status'] == 'present':
                        daily_stats[day_name]['present'] += 1
                        
                except ValueError:
                    continue
            
            # Calculate monthly percentages with month names
            monthly_percentages = {}
            month_names = {}
            for month, stats in monthly_stats.items():
                if stats['total'] > 0:
                    percentage = (stats['present'] / stats['total']) * 100
                    monthly_percentages[month] = round(percentage, 1)
                    # Store month name for display
                    month_names[month] = stats['date_obj'].strftime('%B %Y')
            
            # Get current and previous month
            now = datetime.now()
            current_month_key = f"{now.year}-{now.month:02d}"
            
            prev_month = now.replace(day=1) - timedelta(days=1)
            previous_month_key = f"{prev_month.year}-{prev_month.month:02d}"
            
            current_month_rate = monthly_percentages.get(current_month_key, 0)
            previous_month_rate = monthly_percentages.get(previous_month_key, 0)
            
            # Get month names for current and previous
            current_month_name = now.strftime('%B %Y')
            previous_month_name = prev_month.strftime('%B %Y')
            
            # Find best and worst months
            if monthly_percentages:
                best_month_key = max(monthly_percentages, key=monthly_percentages.get)
                worst_month_key = min(monthly_percentages, key=monthly_percentages.get)
                
                best_month_rate = monthly_percentages[best_month_key]
                lowest_month_rate = monthly_percentages[worst_month_key]
                
                best_month_name = month_names.get(best_month_key, 'Unknown')
                worst_month_name = month_names.get(worst_month_key, 'Unknown')
            else:
                best_month_rate = 0
                lowest_month_rate = 0
                best_month_name = 'N/A'
                worst_month_name = 'N/A'
            
            # Find most active day
            daily_percentages = {}
            for day, stats in daily_stats.items():
                if stats['total'] > 0:
                    percentage = (stats['present'] / stats['total']) * 100
                    daily_percentages[day] = percentage
            
            if daily_percentages:
                most_active_day = max(daily_percentages, key=daily_percentages.get)
            else:
                most_active_day = 'N/A'
            
            metrics = {
                'current_month': f"{current_month_rate}% ({current_month_name})",
                'previous_month': f"{previous_month_rate}% ({previous_month_name})",
                'best_month': f"{best_month_rate}% ({best_month_name})",
                'lowest_month': f"{lowest_month_rate}% ({worst_month_name})",
                'most_active_day': most_active_day
            }
            
            return True, metrics
            
        except Exception as e:
            print(f"Error getting program key metrics: {e}")
            return False, f"Failed to get program key metrics: {str(e)}"
        finally:
            conn.close()
