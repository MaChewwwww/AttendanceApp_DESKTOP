import customtkinter as ctk
import tkinter as tk
from app.db_manager import DatabaseManager
from datetime import datetime, timedelta

class UsersViewModal(ctk.CTkToplevel):
    def __init__(self, parent, user_data, user_type="student"):
        super().__init__(parent)
        self.user_data = user_data
        self.user_type = user_type
        self.db_manager = DatabaseManager()
        self.table_data = []
        self.filtered_data = []
        self.current_search = ""
        
        # Get user details from database
        self.user_details = self.get_user_details()
        
        self.title(f"View User - {self.user_details.get('full_name', 'Unknown')}")
        self.geometry("800x720")
        self.resizable(False, False)
        self.configure(fg_color="#F5F5F5")
        self.transient(parent)
        self.grab_set()
        self._center_window(800, 720)
        self.setup_ui()
        self.load_data()

    def _center_window(self, width, height):
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def get_user_details(self):
        """Get detailed user information from database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Use user ID from user_data 
            user_id = self.user_data.get('id')
            
            if not user_id:
                conn.close()
                return {}
            
            if self.user_type == "student":
                query = """
                SELECT u.*, s.student_number, st.name as status_name,
                       sec.name as section_name, p.name as program_name
                FROM users u
                LEFT JOIN students s ON u.id = s.user_id
                LEFT JOIN statuses st ON u.status_id = st.id
                LEFT JOIN sections sec ON s.section = sec.id
                LEFT JOIN programs p ON sec.course_id = p.id
                WHERE u.id = ? AND u.role = 'Student' AND u.isDeleted = 0
                LIMIT 1
                """
            else:
                query = """
                SELECT u.*, f.employee_number, st.name as status_name
                FROM users u
                LEFT JOIN faculties f ON u.id = f.user_id
                LEFT JOIN statuses st ON u.status_id = st.id
                WHERE u.id = ? AND u.role IN ('Faculty', 'Admin') AND u.isDeleted = 0
                LIMIT 1
                """
            
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_dict = dict(result)
                # Add full_name for consistency
                user_dict['full_name'] = f"{user_dict['first_name']} {user_dict['last_name']}"
                return user_dict
            else:
                return {}
                
        except Exception as e:
            print(f"Error getting user details: {e}")
            return {}

    def load_data(self):
        """Load attendance or course data based on user type"""
        if not self.user_details:
            return
            
        if self.user_type == "student":
            self.load_student_attendance()
        else:
            self.load_faculty_courses()
        
        self.apply_filter()

    def load_student_attendance(self):
        """Load attendance summary for student"""
        try:
            user_id = self.user_details.get('id')
            if not user_id:
                return
                
            success, summary = self.db_manager.get_student_attendance_summary(user_id)
            
            if success:
                self.table_data = []
                for course in summary:
                    # Calculate attendance percentage
                    total = course['total_classes']
                    present = course['present_count']
                    absent = course['absent_count']
                    late = course['late_count']
                    
                    if total > 0:
                        percentage = round((present / total) * 100, 1)
                    else:
                        percentage = 0
                    
                    self.table_data.append({
                        'course': course['course_name'],
                        'section': course['section_name'],
                        'present': present,
                        'absent': absent,
                        'late': late,
                        'total': total,
                        'percentage': f"{percentage}%"
                    })
                
                # If no attendance records found, leave table_data empty for centered message
                if not self.table_data:
                    self.table_data = []
            else:
                print(f"Error loading student attendance: {summary}")
                # Set empty data for centered message
                self.table_data = []
                
        except Exception as e:
            print(f"Error in load_student_attendance: {e}")
            # Set empty data for centered message
            self.table_data = []

    def load_faculty_courses(self):
        """Load assigned courses for faculty"""
        try:
            user_id = self.user_details.get('id')
            if not user_id:
                return
                
            success, courses = self.db_manager.get_assigned_courses(user_id)
            
            if success:
                self.table_data = []
                for course in courses:
                    # Get student count for each course
                    student_count = self.get_course_student_count(course['id'])
                    
                    # Format schedule
                    schedule = f"{course.get('schedule_day', 'TBD')} {course.get('schedule_time', '')}"
                    
                    self.table_data.append({
                        'course': course['course_name'],
                        'section': course['section_name'],
                        'schedule': schedule.strip(),
                        'room': course.get('room', 'TBD'),
                        'students': student_count,
                        'semester': course.get('semester', 'N/A'),
                        'academic_year': course.get('academic_year', 'N/A')
                    })
                
                # If no courses assigned, leave table_data empty for centered message
                if not self.table_data:
                    self.table_data = []
            else:
                print(f"Error loading faculty courses: {courses}")
                # Set empty data for centered message
                self.table_data = []
                
        except Exception as e:
            print(f"Error in load_faculty_courses: {e}")
            # Set empty data for centered message
            self.table_data = []

    def get_course_student_count(self, assigned_course_id):
        """Get number of students enrolled in a course"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get distinct students who have attendance records for this course
            cursor.execute("""
                SELECT COUNT(DISTINCT al.user_id) as student_count
                FROM attendance_logs al
                WHERE al.assigned_course_id = ?
            """, (assigned_course_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result['student_count'] if result else 0
            
        except Exception as e:
            print(f"Error getting student count: {e}")
            return 0

    def apply_filter(self):
        """Apply search filter to data"""
        if not self.current_search.strip():
            self.filtered_data = self.table_data.copy()
        else:
            search_term = self.current_search.lower()
            self.filtered_data = []
            
            for item in self.table_data:
                # Search in all text fields
                if any(search_term in str(value).lower() for value in item.values()):
                    self.filtered_data.append(item)
        
        self.refresh_table()

    def on_search_change(self, event=None):
        """Handle search input changes"""
        if hasattr(self, 'search_entry'):
            self.current_search = self.search_entry.get()
            self.apply_filter()

    def refresh_table(self):
        """Refresh the table display"""
        if hasattr(self, 'table_frame'):
            # Clear existing table content (except header)
            for widget in self.table_frame.winfo_children():
                info = widget.grid_info()
                if info and info.get('row', 0) > 0:  # Keep header (row 0)
                    widget.destroy()
            
            self.populate_table()

    def setup_ui(self):
        # Get user info for display - handle both dict and fallback cases
        if self.user_details:
            name = self.user_details.get('full_name')
        else:
            # Fallback: construct name from user_data if it's a dict
            if isinstance(self.user_data, dict):
                name = self.user_data.get('full_name', 'Unknown User')
            else:
                # Legacy fallback for tuple/list format
                name = self.user_data[0] if len(self.user_data) > 0 else 'Unknown User'
        
        self.title(f"View User - {name}")
        
        if self.user_type == "student":
            program = self.user_details.get('program_name', 'Unknown Program')
            section = self.user_details.get('section_name', 'Unknown Section')
            student_number = self.user_details.get('student_number', 'N/A')
            subtitle = f"{program} • {section} • ID: {student_number}"
        else:
            role = self.user_details.get('role', 'Faculty')
            emp_num = self.user_details.get('employee_number', 'N/A')
            subtitle = f"{role} • Employee #{emp_num}"
        
        # Top frame for user info
        top_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # User info frame (left side)
        user_info_frame = ctk.CTkFrame(top_frame, fg_color="#F5F5F5")
        user_info_frame.pack(side="left", fill="y")
        
        ctk.CTkLabel(
            user_info_frame, 
            text=name, 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color="#000"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            user_info_frame, 
            text=subtitle, 
            font=ctk.CTkFont(size=14), 
            text_color="#666"
        ).pack(anchor="w")
        
        # Status badge frame (right side)
        status_frame = ctk.CTkFrame(top_frame, fg_color="#F5F5F5")
        status_frame.pack(side="right", padx=(20, 0))
        
        # Large, prominent status text - no background
        status = self.user_details.get('status_name', 'No Status')
        status_color = self.get_status_color(status)
        
        ctk.CTkLabel(
            status_frame,
            text=status,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=status_color,
            fg_color="transparent"
        ).pack(pady=8)

        # Search bar with export button aligned
        search_bar_container = ctk.CTkFrame(self, fg_color="#F5F5F5")
        search_bar_container.pack(pady=(0, 10), padx=20, fill="x")
        
        # Search entry frame
        search_entry_frame = ctk.CTkFrame(
            search_bar_container, 
            fg_color="#fff", 
            border_color="#BDBDBD", 
            border_width=1, 
            corner_radius=0, 
            height=36
        )
        search_entry_frame.pack(side="left", pady=0, padx=0)
        search_entry_frame.pack_propagate(False)
        
        search_icon = ctk.CTkLabel(
            search_entry_frame, 
            text="🔍", 
            font=ctk.CTkFont(size=16), 
            text_color="#757575", 
            fg_color="#fff", 
            width=28, 
            height=28
        )
        search_icon.pack(side="left", padx=(8, 0), pady=4)
        
        self.search_entry = ctk.CTkEntry(
            search_entry_frame, 
            placeholder_text="Search courses...", 
            width=200, 
            fg_color="#fff",
            border_color="#fff", 
            border_width=0, 
            text_color="#000", 
            font=ctk.CTkFont(size=15), 
            height=28
        )
        self.search_entry.pack(side="left", padx=(2, 8), pady=4)
        self.search_entry.bind('<Return>', self.on_search_change)

        # Export button aligned with search
        export_btn = ctk.CTkButton(
            search_bar_container, 
            text="Export", 
            fg_color="#1E3A8A", 
            hover_color="#1D4ED8", 
            text_color="#fff", 
            width=70, 
            height=36, 
            corner_radius=8,
            command=self.export_data
        )
        export_btn.pack(side="right")

        # Table
        self.table_frame = ctk.CTkFrame(self, fg_color="#fff", border_color="#E5E7EB", border_width=1, corner_radius=8)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.setup_table_headers()

    def setup_table_headers(self):
        """Setup table column headers"""
        if self.user_type == "student":
            columns = ["Course", "Section", "Present", "Absent", "Late", "Total", "Attendance %"]
            col_weights = [3, 2, 1, 1, 1, 1, 2]
        else:
            columns = ["Course", "Section", "Schedule", "Room", "Students", "Semester"]
            col_weights = [3, 2, 2, 2, 1, 2]
        
        # Configure column weights
        for i, weight in enumerate(col_weights):
            self.table_frame.grid_columnconfigure(i, weight=weight)
        
        # Create headers
        for i, col in enumerate(columns):
            ctk.CTkLabel(
                self.table_frame,
                text=col,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#6B7280",
                anchor="w"
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")

    def populate_table(self):
        """Populate table with filtered data"""
        if not self.filtered_data:
            # Show centered "no data" message
            no_data_label = ctk.CTkLabel(
                self.table_frame,
                text="No data found for this user.",
                font=ctk.CTkFont(size=16),
                text_color="#6B7280"
            )
            
            if self.user_type == "student":
                colspan = 7
            else:
                colspan = 6
                
            no_data_label.grid(row=1, column=0, columnspan=colspan, pady=40)
            return
        
        # Populate with data
        for idx, item in enumerate(self.filtered_data, start=1):
            if self.user_type == "student":
                values = [
                    item['course'],
                    item['section'],
                    str(item['present']),
                    str(item['absent']),
                    str(item['late']),
                    str(item['total']),
                    item['percentage']
                ]
            else:
                values = [
                    item['course'],
                    item['section'],
                    item['schedule'],
                    item['room'],
                    str(item['students']),
                    item['semester']
                ]
            
            for col_idx, value in enumerate(values):
                # Color code attendance percentage for students
                text_color = "#000"
                if self.user_type == "student" and col_idx == 6:  # Attendance percentage column
                    percentage = float(value.replace('%', ''))
                    if percentage >= 90:
                        text_color = "#22C55E"  # Green
                    elif percentage >= 80:
                        text_color = "#F59E0B"  # Yellow
                    else:
                        text_color = "#EF4444"  # Red
                
                ctk.CTkLabel(
                    self.table_frame,
                    text=value,
                    font=ctk.CTkFont(size=12),
                    text_color=text_color,
                    fg_color="#fff",
                    anchor="w"
                ).grid(row=idx, column=col_idx, sticky="nsew", padx=10, pady=6)

    def get_status_color(self, status):
        """Get color for status display"""
        status_colors = {
            'Enrolled': '#22C55E',
            'Graduated': '#F59E0B', 
            'Dropout': '#EF4444',
            'On Leave': '#6B7280',
            'Suspended': '#DC2626',
            'Active': '#10B981',
            'Inactive': '#9CA3AF',
            'Retired': '#8B5CF6',
            'Probationary': '#F97316',
            'Tenure Track': '#3B82F6',
            'Tenured': '#059669'
        }
        return status_colors.get(status, '#6B7280')

    def get_status_bg_color(self, status):
        """Get background color for status badge"""
        status_bg_colors = {
            # Student statuses
            'Enrolled': '#DCFCE7',      # Light Green
            'Graduated': '#FEF3C7',     # Light Yellow/Amber
            'Dropout': '#FEE2E2',       # Light Red
            'On Leave': '#F3F4F6',      # Light Gray
            'Suspended': '#FEE2E2',     # Light Red
            
            # Faculty statuses
            'Active': '#D1FAE5',        # Light Emerald
            'Inactive': '#F9FAFB',      # Very Light Gray
            'Retired': '#EDE9FE',       # Light Purple
            'Probationary': '#FED7AA',  # Light Orange
            'Tenure Track': '#DBEAFE',  # Light Blue
            'Tenured': '#D1FAE5',       # Light Green
            
            # Default
            'No Status': '#F3F4F6',     # Light Gray
        }
        
        return status_bg_colors.get(status, status_bg_colors['No Status'])

    def export_data(self):
        """Export current data to CSV"""
        try:
            import csv
            from tkinter import filedialog
            
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export User Data"
            )
            
            if not filename:
                return
            
            # Prepare data for export
            if self.user_type == "student":
                headers = ["Course", "Section", "Present", "Absent", "Late", "Total", "Attendance %"]
                rows = [[item['course'], item['section'], item['present'], 
                        item['absent'], item['late'], item['total'], item['percentage']] 
                       for item in self.filtered_data]
            else:
                headers = ["Course", "Section", "Schedule", "Room", "Students", "Semester", "Academic Year"]
                rows = [[item['course'], item['section'], item['schedule'], 
                        item['room'], item['students'], item['semester'], item['academic_year']] 
                       for item in self.filtered_data]
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write user info header
                user_name = self.user_details.get('full_name', 'Unknown User')
                writer.writerow([f"User Data Export - {user_name}"])
                writer.writerow([f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                writer.writerow([])  # Empty row
                
                # Write table headers and data
                writer.writerow(headers)
                writer.writerows(rows)
            
            # Show success message
            tk.messagebox.showinfo("Export Successful", f"Data exported to {filename}")
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            tk.messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")

    def show_filter_popup(self):
        """Show filter popup - placeholder for now"""
        pass
