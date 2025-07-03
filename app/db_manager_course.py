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
        """Soft delete a course by setting isDeleted = 1"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Check if course exists and is not already deleted
            cursor.execute("""
                SELECT id, name FROM courses 
                WHERE id = ? AND isDeleted = 0
            """, (course_id,))
            
            course = cursor.fetchone()
            if not course:
                conn.close()
                return False, "Course not found or already deleted"
            
            # Soft delete by setting isDeleted = 1
            cursor.execute("""
                UPDATE courses 
                SET isDeleted = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (course_id,))
            
            if cursor.rowcount == 0:
                conn.close()
                return False, "Failed to delete course"
            
            conn.commit()
            conn.close()
            return True, "Course deleted successfully"
            
        except Exception as e:
            if 'conn' in locals():
                conn.close()
            print(f"Error in delete_course: {e}")
            return False, f"Database error: {str(e)}"

    def get_course_statistics(self, course_id, academic_year=None, semester=None):
        """Get comprehensive statistics for a specific course"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Build base query for course statistics
            base_query = """
            SELECT 
                COUNT(DISTINCT al.user_id) as total_students,
                COUNT(al.id) as total_records,
                SUM(CASE WHEN al.status = 'present' THEN 1 ELSE 0 END) as total_present,
                SUM(CASE WHEN al.status = 'late' THEN 1 ELSE 0 END) as total_late,
                SUM(CASE WHEN al.status = 'absent' THEN 1 ELSE 0 END) as total_absents,
                COUNT(DISTINCT DATE(al.date)) as total_classes
            FROM attendance_logs al
            JOIN assigned_courses ac ON al.assigned_course_id = ac.id
            WHERE ac.course_id = ? AND ac.isDeleted = 0
            """
            
            params = [course_id]
            
            # Add academic year filter if provided
            if academic_year:
                base_query += " AND ac.academic_year = ?"
                params.append(academic_year)
            
            # Removed semester filter completely
            
            cursor.execute(base_query, params)
            result = cursor.fetchone()
            
            if result:
                total_students = result['total_students'] or 0
                total_records = result['total_records'] or 0
                total_present = result['total_present'] or 0
                total_late = result['total_late'] or 0
                total_absents = result['total_absents'] or 0
                total_classes = result['total_classes'] or 0
                
                # Calculate attendance rate
                if total_records > 0:
                    attendance_rate = round((total_present / total_records) * 100, 1)
                else:
                    attendance_rate = 0
                
                stats = {
                    'total_students': total_students,
                    'attendance_rate': f"{attendance_rate}%",
                    'total_classes': total_classes,
                    'total_absents': total_absents,
                    'total_present': total_present,
                    'total_late': total_late
                }
                
                return True, stats
            else:
                # Return empty stats if no data found
                return True, {
                    'total_students': 0,
                    'attendance_rate': '0%',
                    'total_classes': 0,
                    'total_absents': 0,
                    'total_present': 0,
                    'total_late': 0
                }
            
        except Exception as e:
            print(f"Error getting course statistics: {e}")
            return False, str(e)
        finally:
            conn.close()

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
            
            # Simple query to get all assigned courses and sections
            query = """
            SELECT DISTINCT ac.course_id, s.name as section_name
            FROM assigned_courses ac
            JOIN sections s ON ac.section_id = s.id
            WHERE ac.isDeleted = 0 AND s.isDeleted = 0
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Filter in Python - check if section name starts with the year number
            assigned_courses = []
            for row in results:
                section_name = row['section_name']
                if section_name and str(section_name)[0] == str(year_number):
                    assigned_courses.append({'course_id': row['course_id']})
            
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
            
            # Simple query to get all assigned courses and sections
            query = """
            SELECT DISTINCT ac.course_id, s.name as section_name
            FROM assigned_courses ac
            JOIN sections s ON ac.section_id = s.id
            WHERE ac.isDeleted = 0 AND s.isDeleted = 0
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Filter in Python - exact section name match
            assigned_courses = []
            for row in results:
                if row['section_name'] == section_name:
                    assigned_courses.append({'course_id': row['course_id']})
            
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
            
            # Simple query to get all assignments for this course
            cursor.execute("""
                SELECT id FROM assigned_courses 
                WHERE course_id = ? AND isDeleted = 0
            """, (course_id,))
            
            assignments = cursor.fetchall()
            assignment_count = len(assignments)
            
            return True, {
                'in_use': assignment_count > 0,
                'assignment_count': assignment_count
            }
            
        except Exception as e:
            print(f"Error checking course usage: {e}")
            return False, str(e)
        finally:
            conn.close()

    def get_course_section_statistics(self, course_id, academic_year=None, semester=None):
        """Get section-based statistics for a specific course"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get section statistics
            section_query = """
            SELECT 
                s.name as section_name,
                COUNT(DISTINCT al.user_id) as total_students,
                COUNT(al.id) as total_records,
                SUM(CASE WHEN al.status = 'present' THEN 1 ELSE 0 END) as present_count
            FROM sections s
            JOIN assigned_courses ac ON s.id = ac.section_id
            LEFT JOIN attendance_logs al ON al.assigned_course_id = ac.id
            WHERE ac.course_id = ? AND ac.isDeleted = 0
            """
            
            params = [course_id]
            
            # Add academic year filter if provided
            if academic_year:
                section_query += " AND ac.academic_year = ?"
                params.append(academic_year)
            
            # Removed semester filter completely
            
            section_query += " GROUP BY s.id, s.name"
            
            cursor.execute(section_query, params)
            section_results = cursor.fetchall()
            
            section_stats = {}
            best_section = None
            worst_section = None
            best_rate = 0
            worst_rate = 100
            
            for row in section_results:
                section_name = row['section_name']
                total_students = row['total_students'] or 0
                total_records = row['total_records'] or 0
                present_count = row['present_count'] or 0
                
                if total_records > 0:
                    attendance_rate = (present_count / total_records) * 100
                else:
                    attendance_rate = 0
                
                section_stats[section_name] = {
                    'attendance_rate': round(attendance_rate, 1),
                    'total_students': total_students,
                    'total_records': total_records,
                    'present_count': present_count
                }
                
                # Track best and worst sections
                if attendance_rate > best_rate:
                    best_rate = attendance_rate
                    best_section = {'name': section_name, 'rate': round(attendance_rate, 1)}
                
                if attendance_rate < worst_rate:
                    worst_rate = attendance_rate
                    worst_section = {'name': section_name, 'rate': round(attendance_rate, 1)}
            
            result = {
                'section_stats': section_stats,
                'best_section': best_section,
                'worst_section': worst_section
            }
            
            return True, result
            
        except Exception as e:
            print(f"Error getting course section statistics: {e}")
            return False, str(e)
        finally:
            conn.close()

    def get_course_schedule_statistics(self, course_id, academic_year=None, semester=None):
        """Get schedule-based statistics for a specific course"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get schedule data from schedules table with attendance data
            schedule_query = """
            SELECT DISTINCT 
                s.day_of_week,
                s.start_time,
                s.end_time,
                ac.academic_year, 
                al.status
            FROM schedules s
            JOIN assigned_courses ac ON s.assigned_course_id = ac.id
            LEFT JOIN attendance_logs al ON al.assigned_course_id = ac.id
            WHERE ac.course_id = ? AND ac.isDeleted = 0
            """
            
            cursor.execute(schedule_query, [course_id])
            schedule_data = cursor.fetchall()
            
            # Filter by academic year only (removed semester filtering)
            filtered_schedules = []
            for schedule in schedule_data:
                include_schedule = True
                
                # academic_year filtering only
                if academic_year and academic_year != "All Years":
                    if schedule['academic_year'] != academic_year:
                        include_schedule = False
                
                if include_schedule:
                    filtered_schedules.append(schedule)
            
            # Process schedule statistics using Python
            schedule_stats = {}
            
            for schedule in filtered_schedules:
                day_of_week = schedule['day_of_week']
                start_time = schedule['start_time']
                end_time = schedule['end_time']
                
                if not day_of_week or not start_time or not end_time:
                    continue
                
                # Format the schedule time as "Monday : 9:00 - 10:00"
                try:
                    # Extract time from datetime strings
                    if isinstance(start_time, str):
                        # Parse the datetime string and extract time
                        from datetime import datetime
                        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                        start_time_str = start_dt.strftime('%H:%M')
                        end_time_str = end_dt.strftime('%H:%M')
                    else:
                        # If it's already a datetime object
                        start_time_str = start_time.strftime('%H:%M')
                        end_time_str = end_time.strftime('%H:%M')
                    
                    schedule_time = f"{day_of_week} : {start_time_str} - {end_time_str}"
                except Exception as e:
                    print(f"Error formatting schedule time: {e}")
                    # Fallback to basic format
                    schedule_time = f"{day_of_week} : Schedule"
                
                if schedule_time not in schedule_stats:
                    schedule_stats[schedule_time] = {
                        'total_records': 0,
                        'present_count': 0
                    }
                
                if schedule['status']:
                    schedule_stats[schedule_time]['total_records'] += 1
                    if schedule['status'].lower() == 'present':
                        schedule_stats[schedule_time]['present_count'] += 1
            
            # Find best performing schedule
            best_schedule = None
            best_rate = 0
            
            for schedule_time, stats in schedule_stats.items():
                if stats['total_records'] > 0:
                    rate = (stats['present_count'] / stats['total_records']) * 100
                    if rate > best_rate:
                        best_rate = rate
                        best_schedule = schedule_time
            
            result = {
                'best_schedule': {
                    'time': best_schedule,
                    'rate': round(best_rate, 1)
                } if best_schedule else None
            }
            
            return True, result
            
        except Exception as e:
            print(f"Error getting course schedule statistics: {e}")
            return False, str(e)
        finally:
            conn.close()

    def get_available_academic_years(self):
        """Get list of available academic years from assigned courses"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT academic_year 
                FROM assigned_courses 
                WHERE academic_year IS NOT NULL 
                AND academic_year != ''
                AND isDeleted = 0
                ORDER BY academic_year DESC
            """)
            years = [row[0] for row in cursor.fetchall()]
            return True, years
        except Exception as e:
            print(f"Error getting available academic years: {e}")
            return False, str(e)
        finally:
            conn.close()

    def get_available_semesters(self):
        """Get list of available semesters from assigned courses"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT semester 
                FROM assigned_courses 
                WHERE semester IS NOT NULL 
                AND semester != ''
                AND isDeleted = 0
                ORDER BY semester
            """)
            semesters = [row[0] for row in cursor.fetchall()]
            return True, semesters
        except Exception as e:
            print(f"Error getting available semesters: {e}")
            return False, str(e)
        finally:
            conn.close()

    def get_course_monthly_attendance(self, course_id, academic_year=None, semester=None):
        """Get monthly attendance data for a specific course grouped by sections - only months with actual data"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get monthly attendance data by section - only for months that have actual attendance records
            monthly_query = """
            SELECT 
                s.name as section_name,
                CASE 
                    WHEN SUBSTR(al.date, 6, 2) = '01' THEN 'Jan'
                    WHEN SUBSTR(al.date, 6, 2) = '02' THEN 'Feb'
                    WHEN SUBSTR(al.date, 6, 2) = '03' THEN 'Mar'
                    WHEN SUBSTR(al.date, 6, 2) = '04' THEN 'Apr'
                    WHEN SUBSTR(al.date, 6, 2) = '05' THEN 'May'
                    WHEN SUBSTR(al.date, 6, 2) = '06' THEN 'Jun'
                    WHEN SUBSTR(al.date, 6, 2) = '07' THEN 'Jul'
                    WHEN SUBSTR(al.date, 6, 2) = '08' THEN 'Aug'
                    WHEN SUBSTR(al.date, 6, 2) = '09' THEN 'Sep'
                    WHEN SUBSTR(al.date, 6, 2) = '10' THEN 'Oct'
                    WHEN SUBSTR(al.date, 6, 2) = '11' THEN 'Nov'
                    WHEN SUBSTR(al.date, 6, 2) = '12' THEN 'Dec'
                    ELSE 'Unknown'
                END as month,
                SUBSTR(al.date, 1, 4) as year,
                COUNT(al.id) as total_records,
                SUM(CASE WHEN al.status = 'present' THEN 1 ELSE 0 END) as present_count
            FROM sections s
            JOIN assigned_courses ac ON s.id = ac.section_id
            INNER JOIN attendance_logs al ON al.assigned_course_id = ac.id
            WHERE ac.course_id = ? AND ac.isDeleted = 0
            AND al.date IS NOT NULL 
            """
            
            params = [course_id]
            
            # Apply academic_year filter only if provided
            if academic_year:
                monthly_query += " AND ac.academic_year = ?"
                params.append(academic_year)
            
            # Removed semester filter completely
            
            monthly_query += """
            GROUP BY s.id, s.name, year, month
            HAVING COUNT(al.id) > 0
            ORDER BY s.name, year, SUBSTR(al.date, 6, 2)
            """
            
            cursor.execute(monthly_query, params)
            monthly_results = cursor.fetchall()
            
            if not monthly_results:
                # No data found for the selected filters
                return True, {
                    'months': [],
                    'sections_data': {}
                }
            
            # Process the data into a structured format
            sections_data = {}
            months_with_data = set()
            
            for row in monthly_results:
                section_name = row['section_name']
                month = row['month']
                year = row['year']
                total_records = row['total_records'] or 0
                present_count = row['present_count'] or 0
                
                # Track months that have data
                months_with_data.add((month, year))
                
                if section_name not in sections_data:
                    sections_data[section_name] = {}
                
                # Use year-month as key for more precise matching
                month_key = f"{month}-{year}"
                
                # Calculate attendance rate for this month
                if total_records > 0:
                    attendance_rate = (present_count / total_records) * 100
                else:
                    attendance_rate = 0
                
                sections_data[section_name][month_key] = round(attendance_rate, 1)
            
            # Create ordered list of months that actually have data
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            # Sort months chronologically by converting to sortable format
            sorted_months_with_data = []
            for month, year in months_with_data:
                month_num = month_names.index(month) + 1
                sorted_months_with_data.append((year, month_num, month))
            
            sorted_months_with_data.sort()  # Sort by year, then month
            
            # Extract the ordered month list
            months_list = []
            month_keys_list = []
            for year, month_num, month in sorted_months_with_data:
                months_list.append(month)
                month_keys_list.append(f"{month}-{year}")
            
            # Create the final data structure with only months that have data
            chart_data = {}
            
            for section_name in sections_data.keys():
                chart_data[section_name] = []
                for month_key in month_keys_list:
                    # Get attendance rate for this month or 0 if no data for this specific section
                    rate = sections_data[section_name].get(month_key, 0)
                    chart_data[section_name].append(rate)
            
            # Remove duplicate month names while preserving order and data alignment
            unique_months = []
            final_chart_data = {}
            seen_months = {}
            
            for i, month in enumerate(months_list):
                if month not in seen_months:
                    # First occurrence of this month
                    seen_months[month] = len(unique_months)
                    unique_months.append(month)
                    
                    # Initialize data for this unique month
                    for section_name in chart_data.keys():
                        if section_name not in final_chart_data:
                            final_chart_data[section_name] = []
                        final_chart_data[section_name].append(chart_data[section_name][i])
                else:
                    # Duplicate month - average with existing data
                    month_index = seen_months[month]
                    for section_name in chart_data.keys():
                        if section_name in final_chart_data:
                            existing_rate = final_chart_data[section_name][month_index]
                            new_rate = chart_data[section_name][i]
                            # Average the rates if both have data
                            if existing_rate > 0 and new_rate > 0:
                                avg_rate = (existing_rate + new_rate) / 2
                                final_chart_data[section_name][month_index] = round(avg_rate, 1)
                            elif new_rate > 0:  # Use new rate if existing was 0
                                final_chart_data[section_name][month_index] = new_rate
            
            result = {
                'months': unique_months,
                'sections_data': final_chart_data
            }
            
            return True, result
            
        except Exception as e:
            print(f"Error getting course monthly attendance: {e}")
            return False, str(e)
        finally:
            conn.close()

    def get_courses_by_program_id(self, program_id):
        """Get courses by program ID"""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.execute("""
                SELECT c.id, c.name, c.code, c.description, c.program_id,
                       p.name as program_name, p.acronym as program_acronym
                FROM courses c
                JOIN programs p ON c.program_id = p.id
                WHERE c.program_id = ? AND c.isDeleted = 0 AND p.isDeleted = 0
                ORDER BY c.name
            """, (program_id,))
            
            courses = cursor.fetchall()
            
            # Convert to list of dictionaries
            result = []
            for row in courses:
                result.append({
                    'id': row['id'],
                    'name': row['name'],
                    'code': row['code'],
                    'description': row['description'],
                    'program_id': row['program_id'],
                    'program_name': row['program_name'],
                    'program_acronym': row['program_acronym']
                })
            
            return True, result
            
        except Exception as e:
            print(f"Error getting courses by program ID: {e}")
            return False, str(e)
        finally:
            conn.close()