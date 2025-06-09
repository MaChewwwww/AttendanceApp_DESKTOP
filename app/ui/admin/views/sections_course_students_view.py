import customtkinter as ctk
import tkinter as tk
from datetime import datetime

class CourseStudentsViewModal(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, course_data, section_data):
        super().__init__(parent)
        self.db_manager = db_manager
        self.course_data = course_data
        self.section_data = section_data
        self.table_data = []
        self.filtered_data = []
        self.current_search = ""
        
        course_name = course_data.get('course_name', 'Unknown Course')
        section_name = section_data.get('name', 'Unknown Section')
        
        self.title(f"Course Attendance - {course_name}")
        self.geometry("900x720")
        self.resizable(False, False)
        self.configure(fg_color="#F5F5F5")
        self.transient(parent)
        self.grab_set()
        self._center_window(900, 720)
        
        # Create main scrollable frame first
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color="#F5F5F5")
        self.main_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Initialize student count label reference
        self.student_count_label = None
        
        self.setup_ui()
        self.load_data()

    def _center_window(self, width, height):
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def load_data(self):
        """Load students and their attendance data for this course"""
        try:
            course_id = self.course_data.get('course_id')
            section_id = self.section_data.get('id')
            
            if not course_id or not section_id:
                print("Missing course_id or section_id")
                return
            
            # Get all students in this section
            students = self.get_section_students(section_id)
            
            # For each student, get their attendance data for this specific course
            self.table_data = []
            for student in students:
                attendance_stats = self.get_student_course_attendance(student['id'], course_id)
                
                self.table_data.append({
                    'student_id': student['id'],
                    'student_name': f"{student['first_name']} {student['last_name']}",
                    'student_number': student.get('student_number', 'N/A'),
                    'email': student.get('email', 'N/A'),
                    'present': attendance_stats['present'],
                    'absent': attendance_stats['absent'],
                    'late': attendance_stats['late'],
                    'total': attendance_stats['total'],
                    'percentage': f"{attendance_stats['percentage']:.1f}%",
                    'status': student.get('status_name', 'Active')
                })
            
            # Update student count display
            if self.student_count_label:
                self.student_count_label.configure(text=f"{len(self.table_data)} Students")
            
            self.apply_filter()
            
        except Exception as e:
            print(f"Error loading course students data: {e}")
            self.table_data = []

    def get_section_students(self, section_id):
        """Get all students in the section"""
        try:
            conn = self.db_manager.get_connection()
            
            query = """
                SELECT u.id, u.first_name, u.last_name, u.email, 
                       s.student_number, stat.name as status_name
                FROM students s
                JOIN users u ON s.user_id = u.id
                LEFT JOIN statuses stat ON u.status_id = stat.id
                WHERE s.section = ? AND u.isDeleted = 0
                ORDER BY u.last_name, u.first_name
            """
            
            cursor = conn.execute(query, (section_id,))
            students = cursor.fetchall()
            
            return [{
                'id': row['id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'email': row['email'],
                'student_number': row['student_number'],
                'status_name': row['status_name'] or 'Active'
            } for row in students]
            
        except Exception as e:
            print(f"Error getting section students: {e}")
            return []
        finally:
            conn.close()

    def get_student_course_attendance(self, student_id, course_id):
        """Get attendance statistics for a specific student in a specific course"""
        try:
            conn = self.db_manager.get_connection()
            
            # First, get the assigned_course_id for this course and section
            assigned_course_query = """
                SELECT id FROM assigned_courses 
                WHERE course_id = ? AND section_id = ? AND isDeleted = 0
            """
            
            cursor = conn.execute(assigned_course_query, (course_id, self.section_data.get('id')))
            assigned_course = cursor.fetchone()
            
            if not assigned_course:
                return {'present': 0, 'absent': 0, 'late': 0, 'total': 0, 'percentage': 0.0}
            
            assigned_course_id = assigned_course['id']
            
            # Get attendance statistics for this student and course
            attendance_query = """
                SELECT 
                    COUNT(CASE WHEN status = 'present' THEN 1 END) as present_count,
                    COUNT(CASE WHEN status = 'absent' THEN 1 END) as absent_count,
                    COUNT(CASE WHEN status = 'late' THEN 1 END) as late_count,
                    COUNT(*) as total_logs
                FROM attendance_logs
                WHERE user_id = ? AND assigned_course_id = ?
            """
            
            cursor = conn.execute(attendance_query, (student_id, assigned_course_id))
            result = cursor.fetchone()
            
            if result:
                present = result['present_count'] or 0
                absent = result['absent_count'] or 0
                late = result['late_count'] or 0
                total = result['total_logs'] or 0
                
                # Calculate percentage (count late as present)
                if total > 0:
                    percentage = ((present + late) / total) * 100
                else:
                    percentage = 0.0
                
                return {
                    'present': present,
                    'absent': absent,
                    'late': late,
                    'total': total,
                    'percentage': percentage
                }
            else:
                return {'present': 0, 'absent': 0, 'late': 0, 'total': 0, 'percentage': 0.0}
                
        except Exception as e:
            print(f"Error getting student course attendance: {e}")
            return {'present': 0, 'absent': 0, 'late': 0, 'total': 0, 'percentage': 0.0}
        finally:
            conn.close()

    def apply_filter(self):
        """Apply search filter to data"""
        if not self.current_search.strip():
            self.filtered_data = self.table_data.copy()
        else:
            search_term = self.current_search.lower()
            self.filtered_data = []
            
            for item in self.table_data:
                # Search in student name, number, and email
                if (search_term in item['student_name'].lower() or 
                    search_term in item['student_number'].lower() or 
                    search_term in item['email'].lower()):
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
        course_name = self.course_data.get('course_name', 'Unknown Course')
        course_code = self.course_data.get('course_code', '')
        section_name = self.section_data.get('name', 'Unknown Section')
        program_acronym = self.section_data.get('program_acronym', '')
        
        # Display course code if available
        display_course = f"{course_name} ({course_code})" if course_code else course_name
        subtitle = f"{program_acronym} {section_name} • Course Attendance Details"
        
        # Top frame for course info
        top_frame = ctk.CTkFrame(self.main_frame, fg_color="#F5F5F5")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Course info frame (left side)
        course_info_frame = ctk.CTkFrame(top_frame, fg_color="#F5F5F5")
        course_info_frame.pack(side="left", fill="y")
        
        ctk.CTkLabel(
            course_info_frame, 
            text=display_course, 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color="#000"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            course_info_frame, 
            text=subtitle, 
            font=ctk.CTkFont(size=14), 
            text_color="#666"
        ).pack(anchor="w")
        
        # Stats frame (right side) - show total students
        stats_frame = ctk.CTkFrame(top_frame, fg_color="#F5F5F5")
        stats_frame.pack(side="right", padx=(20, 0))
        
        # Create student count label with initial value
        self.student_count_label = ctk.CTkLabel(
            stats_frame,
            text="Loading...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1E3A8A",
            fg_color="transparent"
        )
        self.student_count_label.pack(pady=8)

        # Search bar with export button
        search_bar_container = ctk.CTkFrame(self.main_frame, fg_color="#F5F5F5")
        search_bar_container.pack(pady=(0, 10), padx=20, fill="x")

        # Search entry with icon
        search_entry_frame = ctk.CTkFrame(search_bar_container, fg_color="#fff", border_color="#BDBDBD", border_width=1, corner_radius=0, height=36)
        search_entry_frame.pack(side="left", pady=0, padx=0)
        search_entry_frame.pack_propagate(False)
        search_icon = ctk.CTkLabel(search_entry_frame, text="\U0001F50D", font=ctk.CTkFont(size=16), text_color="#757575", fg_color="#fff", width=28, height=28)
        search_icon.pack(side="left", padx=(8, 0), pady=4)
        
        self.search_entry = ctk.CTkEntry(search_entry_frame, placeholder_text="Search students...", width=200, fg_color="#fff",
                            border_color="#fff", border_width=0, text_color="#222", font=ctk.CTkFont(size=15), height=28)
        self.search_entry.pack(side="left", padx=(2, 8), pady=4)
        
        # Set current search value if it exists
        if self.current_search:
            self.search_entry.insert(0, self.current_search)
        
        # Bind search functionality
        self.search_entry.bind('<Return>', lambda e: self.on_search_change())
        self.search_entry.bind('<KeyRelease>', lambda e: self.on_search_change())

        # Export button aligned with search - right side
        export_btn = ctk.CTkButton(
            search_bar_container, 
            text="📊 Export", 
            fg_color="#1E3A8A", 
            hover_color="#1D4ED8", 
            text_color="#fff", 
            width=100, 
            height=36, 
            corner_radius=6,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.export_data
        )
        export_btn.pack(side="right", padx=(10, 0))

        # Table
        self.table_frame = ctk.CTkFrame(self.main_frame, fg_color="#fff", border_color="#E5E7EB", border_width=1, corner_radius=8)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.setup_table_headers()
        # Don't populate table here - wait for data to load

    def setup_table_headers(self):
        """Setup table column headers"""
        columns = ["Student Name", "Student ID", "Email", "Present", "Absent", "Late", "Total", "Attendance %", "Status"]
        col_weights = [3, 2, 3, 1, 1, 1, 1, 2, 2]
        
        # Configure column weights
        for i, weight in enumerate(col_weights):
            self.table_frame.grid_columnconfigure(i, weight=weight)
        
        # Create headers
        for i, col in enumerate(columns):
            ctk.CTkLabel(
                self.table_frame,
                text=col,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#6B7280",
                anchor="w"
            ).grid(row=0, column=i, padx=8, pady=8, sticky="w")

    def populate_table(self):
        """Populate table with filtered data"""
        if not self.filtered_data:
            # Show centered "no data" message
            no_data_label = ctk.CTkLabel(
                self.table_frame,
                text="No students found for this course.",
                font=ctk.CTkFont(size=16),
                text_color="#6B7280"
            )
            no_data_label.grid(row=1, column=0, columnspan=9, pady=40)
            return
        
        # Populate with data
        for idx, student in enumerate(self.filtered_data, start=1):
            values = [
                student['student_name'],
                student['student_number'],
                student['email'],
                str(student['present']),
                str(student['absent']),
                str(student['late']),
                str(student['total']),
                student['percentage'],
                student['status']
            ]
            
            for col_idx, value in enumerate(values):
                # Color code attendance percentage
                text_color = "#000"
                if col_idx == 7:  # Attendance percentage column
                    try:
                        percentage = float(value.replace('%', ''))
                        if percentage >= 90:
                            text_color = "#22C55E"  # Green
                        elif percentage >= 75:
                            text_color = "#F59E0B"  # Yellow
                        else:
                            text_color = "#EF4444"  # Red
                    except:
                        text_color = "#000"
                
                # Color code status
                elif col_idx == 8:  # Status column
                    text_color = self.get_status_color(value)
                
                ctk.CTkLabel(
                    self.table_frame,
                    text=value,
                    font=ctk.CTkFont(size=11),
                    text_color=text_color,
                    fg_color="#fff",
                    anchor="w"
                ).grid(row=idx, column=col_idx, sticky="nsew", padx=8, pady=4)

    def get_status_color(self, status):
        """Get color for status display"""
        status_colors = {
            'Enrolled': '#22C55E',
            'Active': '#22C55E',
            'Graduated': '#F59E0B', 
            'Dropout': '#EF4444',
            'On Leave': '#6B7280',
            'Suspended': '#DC2626',
            'Inactive': '#9CA3AF'
        }
        return status_colors.get(status, '#6B7280')

    def export_data(self):
        """Export current data to CSV"""
        try:
            import csv
            from tkinter import filedialog
            
            course_name = self.course_data.get('course_name', 'Unknown Course')
            section_name = self.section_data.get('name', 'Unknown Section')
            
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Course Attendance Data",
                initialfile=f"{course_name}_{section_name}_attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not filename:
                return
            
            # Prepare data for export
            headers = ["Student Name", "Student ID", "Email", "Present", "Absent", "Late", "Total", "Attendance %", "Status"]
            rows = [[student['student_name'], student['student_number'], student['email'], 
                    student['present'], student['absent'], student['late'], 
                    student['total'], student['percentage'], student['status']] 
                   for student in self.filtered_data]
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write course info header
                writer.writerow([f"Course Attendance Report - {course_name}"])
                writer.writerow([f"Section: {section_name}"])
                writer.writerow([f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                writer.writerow([f"Total Students: {len(self.filtered_data)}"])
                writer.writerow([])  # Empty row
                
                # Write table headers and data
                writer.writerow(headers)
                writer.writerows(rows)
            
            # Show success message
            tk.messagebox.showinfo("Export Successful", f"Data exported to {filename}")
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            tk.messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
