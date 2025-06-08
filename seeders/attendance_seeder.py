import random
from datetime import datetime, timedelta
from .base_seeder import BaseSeeder
from .config import SEEDER_CONFIG, get_current_semester, get_semester_attendance_modifier, is_semester_month, get_semester_months, get_academic_year

class AttendanceSeeder(BaseSeeder):
    """Seeder for attendance logs with Philippine holidays consideration"""
    
    def seed(self, assigned_course_ids):
        """Seed attendance logs with realistic patterns"""
        try:
            conn = self.get_connection()
            self.logger.info("Seeding attendance logs...")
            
            if not assigned_course_ids:
                self.logger.warning("No assigned courses found, skipping attendance seeding")
                return True
            
            # Get students
            students_list = self._get_students(conn)
            
            if not students_list:
                self.logger.warning("No students found, skipping attendance seeding")
                return True
            
            self.logger.info(f"Found {len(students_list)} students and {len(assigned_course_ids)} assigned courses")
            
            # Generate attendance for recent weeks - ensure ALL students get attendance
            self._generate_comprehensive_attendance(conn, assigned_course_ids, students_list)
            
            conn.commit()
            
            # Log summary with detailed statistics
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
    
    def _generate_comprehensive_attendance(self, conn, assigned_course_ids, students_list):
        """Generate attendance for multiple weeks with realistic patterns - ensure ALL students get data"""
        current_time = self.get_current_time()
        
        # Instead of using fixed past 8 weeks, generate attendance for semester periods
        current_date = datetime.now()
        current_semester = get_current_semester(current_date)
        
        # Generate attendance for current semester and some historical data
        attendance_periods = self._get_semester_date_ranges(current_date)
        
        self.logger.info(f"Current semester: {current_semester}")
        self.logger.info(f"Generating attendance for {len(attendance_periods)} semester periods")
        
        # Assign student performance categories
        student_performance = self._assign_student_performance(students_list)
        
        total_records_created = 0
        students_with_attendance = set()
        
        # Generate attendance for each semester period
        for period_name, start_date, end_date in attendance_periods:
            self.logger.info(f"Processing {period_name}: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            # Filter assigned courses that match this semester
            period_courses = self._filter_courses_by_semester_period(conn, assigned_course_ids, period_name)
            
            if not period_courses:
                self.logger.info(f"No courses found for {period_name}, using all available courses")
                period_courses = assigned_course_ids[:10]  # Use first 10 courses as fallback
            
            # First, try to create attendance for course-section matches
            for i, assigned_course_id in enumerate(period_courses):
                self.logger.info(f"Processing {period_name} course assignment {i+1}/{len(period_courses)} (ID: {assigned_course_id})")
                
                # Get course and section info
                course_info = self._get_course_info(conn, assigned_course_id)
                if not course_info:
                    continue
                
                course_name, section_name, program_name = course_info
                
                # Get students enrolled in this section
                section_students = self._get_section_students(conn, section_name, program_name)
                if not section_students:
                    section_students = self._get_students_by_section_name_only(conn, section_name)
                    if not section_students:
                        continue
                
                # Get course schedule
                schedule_days = self._get_course_schedule(conn, assigned_course_id)
                if not schedule_days:
                    continue
                
                # Generate class dates for this semester period
                class_dates = self._generate_class_dates(start_date, end_date, schedule_days)
                
                # Generate attendance for each class date
                for class_date in class_dates:
                    for student_id, first_name, last_name in section_students:
                        # Check if record already exists
                        existing = self.check_exists(conn, "attendance_logs", {
                            "user_id": student_id,
                            "assigned_course_id": assigned_course_id,
                            "date": class_date.strftime('%Y-%m-%d')
                        })
                        
                        if existing:
                            students_with_attendance.add(student_id)
                            continue
                        
                        # Determine attendance status
                        status = self._determine_attendance_status(student_id, student_performance, class_date)
                        
                        # Insert attendance log
                        try:
                            self.execute_query(conn, """
                                INSERT INTO attendance_logs 
                                (user_id, assigned_course_id, date, status, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                                student_id, 
                                assigned_course_id, 
                                class_date.strftime('%Y-%m-%d'),
                                status, 
                                current_time, 
                                current_time
                            ))
                            total_records_created += 1
                            students_with_attendance.add(student_id)
                        except Exception as e:
                            self.logger.error(f"Failed to insert attendance for student {student_id}: {e}")
        
        # Ensure ALL students have at least some attendance data
        all_student_ids = {student[0] for student in students_list}
        students_without_attendance = all_student_ids - students_with_attendance
        
        if students_without_attendance:
            self.logger.info(f"Creating attendance for {len(students_without_attendance)} students without data")
            self._create_fallback_attendance(conn, students_without_attendance, assigned_course_ids, 
                                           student_performance, start_date, end_date, current_time)
            total_records_created += len(students_without_attendance) * 10  # Estimate
        
        self.logger.info(f"Total attendance records created: {total_records_created}")
        self.logger.info(f"Students with attendance data: {len(students_with_attendance)}")
    
    def _get_students_by_section_name_only(self, conn, section_name):
        """Get students by section name only (fallback when program match fails)"""
        cursor = self.execute_query(conn, """
            SELECT u.id, u.first_name, u.last_name
            FROM users u
            JOIN students st ON u.id = st.user_id
            JOIN sections s ON st.section = s.id
            WHERE s.name = ? AND u.role = 'Student' AND u.isDeleted = 0
        """, (section_name,))
        return cursor.fetchall()
    
    def _create_fallback_attendance(self, conn, student_ids, assigned_course_ids, 
                                  student_performance, start_date, end_date, current_time):
        """Create fallback attendance data for students without any attendance records"""
        if not assigned_course_ids:
            return
        
        # Use first few assigned courses for fallback
        fallback_courses = assigned_course_ids[:3]  # Use first 3 courses
        
        for student_id in student_ids:
            for assigned_course_id in fallback_courses:
                # Get course schedule
                schedule_days = self._get_course_schedule(conn, assigned_course_id)
                if not schedule_days:
                    # Create default schedule if none exists
                    schedule_days = ['Monday', 'Wednesday', 'Friday']
                
                # Generate some class dates (limited to avoid too much data)
                class_dates = self._generate_class_dates(start_date, end_date, schedule_days)
                
                # Only create attendance for last 2 weeks to keep it reasonable
                recent_dates = [d for d in class_dates if d >= datetime.now() - timedelta(weeks=2)]
                
                for class_date in recent_dates:
                    # Check if record already exists
                    existing = self.check_exists(conn, "attendance_logs", {
                        "user_id": student_id,
                        "assigned_course_id": assigned_course_id,
                        "date": class_date.strftime('%Y-%m-%d')
                    })
                    
                    if existing:
                        continue
                    
                    # Determine attendance status
                    status = self._determine_attendance_status(student_id, student_performance, class_date)
                    
                    # Insert attendance log
                    try:
                        self.execute_query(conn, """
                            INSERT INTO attendance_logs 
                            (user_id, assigned_course_id, date, status, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            student_id, 
                            assigned_course_id, 
                            class_date.strftime('%Y-%m-%d'),
                            status, 
                            current_time, 
                            current_time
                        ))
                    except Exception as e:
                        self.logger.error(f"Failed to insert fallback attendance for student {student_id}: {e}")
    
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
    
    def _filter_courses_by_semester_period(self, conn, assigned_course_ids, period_name):
        """Filter assigned courses that belong to the specified semester period"""
        if not assigned_course_ids:
            return []
        
        # Extract semester and academic year from period name
        if 'Summer' in period_name:
            semester = 'Summer'
        elif '1st Semester' in period_name:
            semester = '1st Semester'
        elif '2nd Semester' in period_name:
            semester = '2nd Semester'
        else:
            semester = '1st Semester'  # Default fallback
        
        # Extract academic year from period name
        if '2023-2024' in period_name:
            academic_year = '2023-2024'
        elif '2024-2025' in period_name:
            academic_year = '2024-2025'
        else:
            # Default to current academic year
            from .config import get_academic_year
            academic_year = get_academic_year()
        
        # Get assigned courses that match this semester and academic year
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
            # If no exact match, return a subset of available courses for this semester type
            cursor = self.execute_query(conn, f"""
                SELECT ac.id
                FROM assigned_courses ac
                WHERE ac.id IN ({placeholders}) AND ac.semester = ?
                LIMIT 5
            """, assigned_course_ids + [semester])
            
            fallback_courses = [row[0] for row in cursor.fetchall()]
            if fallback_courses:
                self.logger.info(f"Using {len(fallback_courses)} fallback courses for {period_name}")
            return fallback_courses
