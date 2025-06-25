import random
from datetime import datetime, timedelta
from .base_seeder import BaseSeeder
from .config import SEEDER_CONFIG, get_current_semester, get_semester_attendance_modifier, is_semester_month, get_semester_months, get_academic_year

class AttendanceSeeder(BaseSeeder):
    """Seeder for attendance logs with Philippine holidays consideration"""
    
    def seed(self, assigned_course_ids):
        """Seed attendance logs with realistic patterns and simulate student progression"""
        try:
            conn = self.get_connection()
            self.logger.info("Seeding attendance logs with progression simulation...")

            if not assigned_course_ids:
                self.logger.warning("No assigned courses found, skipping attendance seeding")
                return True

            students_list = self._get_students(conn)
            if not students_list:
                self.logger.warning("No students found, skipping attendance seeding")
                return True

            self.logger.info(f"Found {len(students_list)} students and {len(assigned_course_ids)} assigned courses")

            # Simulate student progression and attendance
            self._simulate_student_progression(conn, assigned_course_ids, students_list)

            conn.commit()
            self._log_attendance_statistics(conn)
            conn.close()
            return True

        except Exception as e:
            self.logger.error(f"Error seeding attendance: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False

    def _get_students(self, conn):
        """Get all students"""
        cursor = self.execute_query(conn, """
            SELECT u.id, u.first_name, u.last_name, st.section
            FROM users u
            JOIN students st ON u.id = st.user_id
            WHERE u.role = 'Student' AND u.isDeleted = 0
        """)
        return cursor.fetchall()
    
    def _simulate_student_progression(self, conn, assigned_course_ids, students_list):
        """
        Simulate student progression: assign courses, approvals, and attendance logs year by year.
        Promote students if all courses are passed, stop at 2025 or if not all passed.
        """
        from .config import get_academic_years_to_generate
        academic_years = get_academic_years_to_generate()
        # Assume academic_years are sorted, e.g., ['2023-2024', '2024-2025']
        max_year = 2025

        # Get all sections and their year levels
        cursor = self.execute_query(conn, """
            SELECT s.id, s.name, p.name as program_name, p.acronym
            FROM sections s
            JOIN programs p ON s.program_id = p.id
        """)
        section_info = {row[0]: row for row in cursor.fetchall()}

        # Get all assigned courses with details
        cursor = self.execute_query(conn, """
            SELECT ac.id, ac.section_id, ac.academic_year, ac.semester, c.id as course_id
            FROM assigned_courses ac
            JOIN courses c ON ac.course_id = c.id
        """)
        assigned_course_map = {}
        for row in cursor.fetchall():
            ac_id, section_id, academic_year, semester, course_id = row
            assigned_course_map.setdefault((section_id, academic_year, semester), []).append((ac_id, course_id))

        # For each student, simulate progression
        for student in students_list:
            user_id, first_name, last_name, section_id = student
            # Start at 1st year
            current_section_id = section_id
            year_level = 1
            for academic_year in academic_years:
                # Stop if year exceeds 2025
                if int(academic_year.split('-')[1]) > max_year:
                    break
                for semester in ["1st Semester", "2nd Semester", "Summer"]:
                    # Get assigned courses for this section/year/semester
                    assigned_courses = assigned_course_map.get((current_section_id, academic_year, semester), [])
                    if not assigned_courses:
                        continue

                    all_passed = True
                    for assigned_course_id, course_id in assigned_courses:
                        # Simulate approval status
                        approval_status = self._simulate_approval_status()
                        # Insert approval record
                        self._insert_or_update_approval(conn, user_id, assigned_course_id, approval_status)
                        # Only generate attendance if enrolled or passed
                        if approval_status in ("enrolled", "passed"):
                            self._generate_attendance_for_course(
                                conn, user_id, assigned_course_id, academic_year, semester
                            )
                        elif approval_status == "failed":
                            # 50% chance: student attended but failed (low scores), 50%: failed due to non-attendance
                            if random.random() < 0.5:
                                # Simulate poor attendance (e.g., 40-65%)
                                attendance_rate = random.uniform(0.40, 0.65)
                                self._generate_attendance_for_course(
                                    conn, user_id, assigned_course_id, academic_year, semester, attendance_rate=attendance_rate
                                )
                            # else: no attendance logs (failed due to non-attendance)
                        if approval_status != "passed":
                            all_passed = False

                    # If not all passed, stop progression for this student
                    if not all_passed:
                        break
                # Promote to next year if all passed
                if all_passed:
                    year_level += 1
                    # Find next section for this program/year
                    current_section_id = self._find_section_for_year(conn, current_section_id, year_level)
                    if not current_section_id:
                        break
                else:
                    break

    def _simulate_approval_status(self):
        """Randomly determine approval status for a course (simulate real-world outcomes)"""
        # 80% pass, 15% enrolled, 3% failed, 1% rejected, 1% pending
        r = random.random()
        if r < 0.80:
            return "passed"
        elif r < 0.95:
            return "enrolled"
        elif r < 0.98:
            return "failed"
        elif r < 0.99:
            return "rejected"
        else:
            return "pending"

    def _insert_or_update_approval(self, conn, user_id, assigned_course_id, status):
        """Insert or update assigned_course_approvals for a student/course"""
        # Get student_id from user_id
        cursor = self.execute_query(conn, "SELECT id FROM students WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return
        student_id = row[0]
        # Check if approval exists
        cursor = self.execute_query(conn, """
            SELECT id FROM assigned_course_approvals
            WHERE assigned_course_id = ? AND student_id = ?
        """, (assigned_course_id, student_id))
        approval = cursor.fetchone()
        if approval:
            self.execute_query(conn, """
                UPDATE assigned_course_approvals SET status = ? WHERE id = ?
            """, (status, approval[0]))
        else:
            self.execute_query(conn, """
                INSERT INTO assigned_course_approvals (assigned_course_id, student_id, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (assigned_course_id, student_id, status, self.get_current_time(), self.get_current_time()))

    def _generate_attendance_for_course(self, conn, user_id, assigned_course_id, academic_year, semester, attendance_rate=None):
        """Generate attendance logs for a student in a course for the given academic year and semester"""
        # Get course schedule
        schedule_days = self._get_course_schedule(conn, assigned_course_id)
        if not schedule_days:
            return
        # Get semester date range
        from .config import get_semester_date_ranges_for_academic_year
        periods = get_semester_date_ranges_for_academic_year(academic_year)
        for sem, start_date, end_date in periods:
            if sem == semester:
                class_dates = self._generate_class_dates(start_date, end_date, schedule_days)
                # Assign performance for this student
                if attendance_rate is None:
                    attendance_rate = 0.9
                student_performance = {user_id: {'attendance_rate': attendance_rate, 'category': 'average'}}
                for class_date in class_dates:
                    # Check if record already exists
                    existing = self.check_exists(conn, "attendance_logs", {
                        "user_id": user_id,
                        "assigned_course_id": assigned_course_id,
                        "date": class_date.strftime('%Y-%m-%d')
                    })
                    if existing:
                        continue
                    status = self._determine_attendance_status(user_id, student_performance, class_date)
                    self.execute_query(conn, """
                        INSERT INTO attendance_logs 
                        (user_id, assigned_course_id, date, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        assigned_course_id,
                        class_date.strftime('%Y-%m-%d'),
                        status,
                        self.get_current_time(),
                        self.get_current_time()
                    ))

    def _find_section_for_year(self, conn, current_section_id, year_level):
        """Find the section_id for the next year in the same program"""
        cursor = self.execute_query(conn, """
            SELECT s2.id
            FROM sections s1
            JOIN programs p ON s1.program_id = p.id
            JOIN sections s2 ON s2.program_id = p.id
            WHERE s1.id = ? AND s2.name LIKE ?
            ORDER BY s2.name
            LIMIT 1
        """, (current_section_id, f"{year_level}-%"))
        row = cursor.fetchone()
        if row:
            return row[0]
        return None
    
    def _get_course_info(self, conn, assigned_course_id):
        """Get course, section, and program information"""
        cursor = self.execute_query(conn, """
            SELECT c.name as course_name, s.name as section_name, p.name as program_name
            FROM assigned_courses ac
            JOIN courses c ON ac.course_id = c.id
            JOIN sections s ON ac.section_id = s.id
            JOIN programs p ON s.program_id = p.id
            WHERE ac.id = ?
        """, (assigned_course_id,))
        return cursor.fetchone()
    
    def _get_section_students(self, conn, section_name, program_name):
        """Get students enrolled in a specific section"""
        cursor = self.execute_query(conn, """
            SELECT u.id, u.first_name, u.last_name
            FROM users u
            JOIN students st ON u.id = st.user_id
            JOIN sections s ON st.section = s.id
            JOIN programs p ON s.program_id = p.id
            WHERE s.name = ? AND p.name = ? AND u.role = 'Student' AND u.isDeleted = 0
        """, (section_name, program_name))
        return cursor.fetchall()
    
    def _get_course_schedule(self, conn, assigned_course_id):
        """Get course schedule days"""
        cursor = self.execute_query(conn, """
            SELECT day_of_week FROM schedules 
            WHERE assigned_course_id = ?
        """, (assigned_course_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def _generate_class_dates(self, start_date, end_date, schedule_days):
        """Generate class dates based on schedule"""
        # Map day names to weekday numbers
        day_mapping = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
            'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        
        class_weekdays = [day_mapping[day] for day in schedule_days if day in day_mapping]
        
        class_dates = []
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() in class_weekdays:
                # Check for holidays and suspensions
                is_suspended, reason = self._is_class_suspended(current_date)
                if not is_suspended:
                    class_dates.append(current_date)
            current_date += timedelta(days=1)
        
        return class_dates
    
    def _is_class_suspended(self, date):
        """Check if classes are suspended on this date"""
        # Philippine holidays and academic suspensions
        date_str = date.strftime('%m-%d')
        
        # Major holidays when classes are typically suspended
        holidays = {
            "01-01": "New Year's Day",
            "02-25": "EDSA People Power Revolution",
            "04-09": "Araw ng Kagitingan",
            "05-01": "Labor Day",
            "06-12": "Independence Day",
            "08-21": "Ninoy Aquino Day",
            "08-26": "National Heroes Day",
            "11-01": "All Saints' Day",
            "11-30": "Bonifacio Day",
            "12-25": "Christmas Day",
            "12-30": "Rizal Day"
        }
        
        if date_str in holidays:
            return True, holidays[date_str]
        
        # Random weather suspensions (3% chance during rainy season)
        if date.month in [6, 7, 8, 9, 10, 11] and random.random() < 0.03:
            return True, "Weather Suspension"
        
        return False, None
    
    def _determine_attendance_status(self, student_id, student_performance, class_date):
        """Determine attendance status for a student using dynamic semester configuration"""
        perf = student_performance.get(student_id, {
            'attendance_rate': 0.85, 
            'category': 'average'
        })
        
        # Base attendance probability
        attendance_prob = perf['attendance_rate']
        
        # Adjust for day of week (students more likely to skip Friday classes)
        if class_date.weekday() == 4:  # Friday
            attendance_prob *= 0.95
        elif class_date.weekday() == 0:  # Monday
            attendance_prob *= 0.98
        
        # Use dynamic semester-based attendance modifier
        semester = get_current_semester(class_date)
        semester_modifier = get_semester_attendance_modifier(class_date, semester)
        attendance_prob *= semester_modifier
        
        # Log semester context for debugging (only occasionally to avoid spam)
        if random.random() < 0.001:  # 0.1% chance to log
            self.logger.debug(f"Date: {class_date.strftime('%Y-%m-%d')}, Semester: {semester}, Modifier: {semester_modifier:.2f}")
        
        # Ensure probability stays within reasonable bounds
        attendance_prob = max(0.1, min(1.0, attendance_prob))
        
        if random.random() < attendance_prob:
            # Student attends - determine if present or late
            late_probability = {
                'excellent': 0.02, 
                'very_good': 0.04, 
                'good': 0.07, 
                'average': 0.12, 
                'poor': 0.18
            }
            
            # Increase late probability during summer months using dynamic config
            month = class_date.month
            if is_semester_month(month, 'Summer'):
                base_late_prob = late_probability.get(perf['category'], 0.1)
                late_prob = min(0.25, base_late_prob * 1.3)  # 30% increase, capped at 25%
            else:
                late_prob = late_probability.get(perf['category'], 0.1)
            
            if random.random() < late_prob:
                return 'late'
            else:
                return 'present'
        else:
            return 'absent'
    
    def _assign_student_performance(self, students_list):
        """Assign performance categories to students based on their status"""
        performance_config = SEEDER_CONFIG['student_performance']
        student_performance = {}
        
        # Get student statuses
        conn = self.get_connection()
        cursor = self.execute_query(conn, """
            SELECT u.id, st.name as status_name
            FROM users u
            JOIN statuses st ON u.status_id = st.id
            WHERE u.role = 'Student' AND u.isDeleted = 0
        """)
        student_statuses = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        
        # Assign performance based on status
        for student_id, first_name, last_name, section_id in students_list:
            status = student_statuses.get(student_id, 'Enrolled')
            
            # Set attendance rates based on status
            if status == 'Suspended':
                # Suspended students: 70% and below attendance rate
                attendance_rate = random.uniform(0.40, 0.70)
                category = 'poor'
                consistency = random.uniform(0.60, 0.75)
            elif status == 'Dropout':
                # Dropout students: 60% and below attendance rate
                attendance_rate = random.uniform(0.30, 0.60)
                category = 'poor'
                consistency = random.uniform(0.50, 0.65)
            elif status == 'Graduated':
                # Graduated students: 80% and above attendance rate
                attendance_rate = random.uniform(0.80, 0.98)
                category = random.choice(['excellent', 'very_good'])
                consistency = random.uniform(0.85, 1.0)
            elif status == 'On Leave':
                # On leave students: moderate attendance before leave
                attendance_rate = random.uniform(0.70, 0.85)
                category = random.choice(['average', 'good'])
                consistency = random.uniform(0.75, 0.85)
            else:  # Enrolled students
                # Use original distribution for enrolled students
                categories = [
                    ('excellent', performance_config['excellent']['percentage'], performance_config['excellent']),
                    ('very_good', performance_config['very_good']['percentage'], performance_config['very_good']),
                    ('good', performance_config['good']['percentage'], performance_config['good']),
                    ('average', performance_config['average']['percentage'], performance_config['average']),
                    ('poor', performance_config['poor']['percentage'], performance_config['poor'])
                ]
                
                # Randomly assign based on distribution
                rand = random.random()
                cumulative = 0
                for cat_name, percentage, config in categories:
                    cumulative += percentage
                    if rand <= cumulative:
                        category = cat_name
                        attendance_rate = random.uniform(*config['attendance_range'])
                        consistency = random.uniform(*config['consistency_range'])
                        break
                else:
                    # Fallback
                    category = 'average'
                    attendance_rate = random.uniform(0.80, 0.84)
                    consistency = random.uniform(0.75, 0.85)
            
            student_performance[student_id] = {
                'category': category,
                'attendance_rate': attendance_rate,
                'consistency': consistency,
                'status': status
            }
        
        # Log status-based performance distribution
        status_counts = {}
        for perf in student_performance.values():
            status = perf['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        self.logger.info("Student performance by status:")
        for status, count in status_counts.items():
            avg_attendance = sum(p['attendance_rate'] for p in student_performance.values() if p['status'] == status) / count
            self.logger.info(f"  - {status}: {count} students, avg attendance: {avg_attendance:.1%}")
        
        return student_performance
    
    def _log_attendance_statistics(self, conn):
        """Log detailed attendance statistics"""
        # Overall statistics
        cursor = self.execute_query(conn, "SELECT COUNT(*) FROM attendance_logs")
        total_records = cursor.fetchone()[0]
        
        # Count unique students with attendance
        cursor = self.execute_query(conn, "SELECT COUNT(DISTINCT user_id) FROM attendance_logs")
        students_with_attendance = cursor.fetchone()[0]
        
        # Count total students
        cursor = self.execute_query(conn, "SELECT COUNT(*) FROM users WHERE role = 'Student' AND isDeleted = 0")
        total_students = cursor.fetchone()[0]
        
        # Status breakdown
        cursor = self.execute_query(conn, """
            SELECT status, COUNT(*) 
            FROM attendance_logs 
            GROUP BY status
        """)
        status_counts = cursor.fetchall()
        
        # Course-wise statistics
        cursor = self.execute_query(conn, """
            SELECT c.name, COUNT(al.id) as record_count
            FROM attendance_logs al
            JOIN assigned_courses ac ON al.assigned_course_id = ac.id
            JOIN courses c ON ac.course_id = c.id
            GROUP BY c.name
            ORDER BY record_count DESC
        """)
        course_stats = cursor.fetchall()
        
        self.logger.info(f"✓ Total attendance records: {total_records}")
        self.logger.info(f"✓ Students with attendance data: {students_with_attendance}/{total_students} ({(students_with_attendance/total_students*100):.1f}%)")
        
        for status, count in status_counts:
            percentage = (count / total_records * 100) if total_records > 0 else 0
            self.logger.info(f"  - {status.title()}: {count} ({percentage:.1f}%)")
        
        self.logger.info("✓ Course-wise attendance records:")
        for course_name, count in course_stats[:5]:  # Top 5 courses
            self.logger.info(f"  - {course_name}: {count} records")
        
        # Verify all students have some attendance
        if students_with_attendance < total_students:
            self.logger.warning(f"⚠️  {total_students - students_with_attendance} students still have no attendance data")
        else:
            self.logger.info("✅ All students have attendance data!")
    
    def _get_semester_date_ranges(self, current_date):
        """Get date ranges for all configured academic years dynamically"""
        from .config import get_academic_years_to_generate, get_semester_date_ranges_for_academic_year
        
        periods = []
        
        # Get academic years from config
        academic_years = get_academic_years_to_generate()
        
        self.logger.info(f"Generating attendance periods for academic years: {', '.join(academic_years)}")
        
        # Generate periods for each configured academic year
        for academic_year in academic_years:
            self.logger.info(f"Processing academic year: {academic_year}")
            
            # Get semester periods for this academic year
            year_periods = get_semester_date_ranges_for_academic_year(academic_year)
            
            for semester, start_date, end_date in year_periods:
                period_name = f"{semester} {academic_year}"
                
                # For current academic year, limit end date to current date
                if academic_year == get_academic_year(current_date):
                    end_date = min(end_date, current_date)
                    # Skip future periods
                    if start_date > current_date:
                        continue
                
                periods.append((period_name, start_date, end_date))
        
        self.logger.info(f"Generated {len(periods)} semester periods across all configured academic years")
        
        return periods
    
    def _filter_courses_by_semester_period(self, conn, assigned_course_ids, period_name, period_academic_year=None):
        """Filter assigned courses that belong to the specified semester period and academic year"""
        if not assigned_course_ids:
            return []
        
        # Extract semester from period name
        if 'Summer' in period_name:
            semester = 'Summer'
        elif '1st Semester' in period_name:
            semester = '1st Semester'
        elif '2nd Semester' in period_name:
            semester = '2nd Semester'
        else:
            semester = '1st Semester'  # Default fallback

        # Academic year passed as argument (from above)
        academic_year = period_academic_year
        if not academic_year:
            if '2023-2024' in period_name:
                academic_year = '2023-2024'
            elif '2024-2025' in period_name:
                academic_year = '2024-2025'
            else:
                from .config import get_academic_year
                academic_year = get_academic_year()

        # Only select assigned courses with matching semester and academic year
        placeholders = ','.join(['?'] * len(assigned_course_ids))
        cursor = self.execute_query(conn, f"""
            SELECT ac.id
            FROM assigned_courses ac
            WHERE ac.id IN ({placeholders}) AND ac.semester = ? AND ac.academic_year = ?
        """, assigned_course_ids + [semester, academic_year])
        
        matching_courses = [row[0] for row in cursor.fetchall()]
        
        if matching_courses:
            self.logger.info(f"Found {len(matching_courses)} courses for {period_name} ({semester} - {academic_year})")
            return matching_courses
        else:
            self.logger.warning(f"No courses found for {period_name} ({semester} - {academic_year}), using fallback")
            # If no exact match, return a subset of available courses for this semester type and academic year
            cursor = self.execute_query(conn, f"""
                SELECT ac.id
                FROM assigned_courses ac
                WHERE ac.id IN ({placeholders}) AND ac.semester = ? AND ac.academic_year = ?
                LIMIT 5
            """, assigned_course_ids + [semester, academic_year])
            
            fallback_courses = [row[0] for row in cursor.fetchall()]
            if fallback_courses:
                self.logger.info(f"Using {len(fallback_courses)} fallback courses for {period_name}")
            return fallback_courses
    
    def _is_student_enrolled_in_course(self, conn, student_id, assigned_course_id):
        """
        Check if the student is enrolled or passed in the assigned_course_approvals table.
        Only students with status 'enrolled' or 'passed' are eligible for attendance logs.
        """
        cursor = self.execute_query(conn, """
            SELECT status FROM assigned_course_approvals
            WHERE assigned_course_id = ?
              AND student_id = (
                  SELECT id FROM students WHERE user_id = ?
              )
            LIMIT 1
        """, (assigned_course_id, student_id))
        row = cursor.fetchone()
        if row and row[0] in ('enrolled', 'passed'):
            return True
        return False
