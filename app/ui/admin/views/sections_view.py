import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class SectionViewPopup(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, section_data):
        super().__init__(parent)
        self.db_manager = db_manager
        self.section_data = section_data
        self.title(f"Section View - {section_data.get('name', 'Unknown')}")
        self.geometry("850x850")  # Reduced from 1000x800
        self.resizable(False, False)
        self.configure(fg_color="#F5F5F5")
        self.transient(parent)
        self.grab_set()
        
        # Initialize filter variables first
        self.year_var = ctk.StringVar(value="All Years")
        self.semester_var = ctk.StringVar(value="All Semesters")
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create main scrollable frame
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color="#F5F5F5")
        self.main_frame.pack(fill="both", expand=True, padx=8, pady=8)  # Reduced padding
        
        # Store references to dynamic content containers
        self.chart_frame = None
        self.table_frame = None
        
        self.setup_ui()

    def setup_ui(self):
        # Header - more compact with filters
        top_frame = ctk.CTkFrame(self.main_frame, fg_color="#F5F5F5")
        top_frame.pack(fill="x", padx=20, pady=(15, 10))  # Reduced padding
        
        section_name = self.section_data.get('name', 'N/A')
        program_acronym = self.section_data.get('program_acronym', 'N/A')
        
        # Header row with section name, subtitle, and controls
        header_row = ctk.CTkFrame(top_frame, fg_color="#F5F5F5")
        header_row.pack(fill="x")
        
        # Section name and subtitle (left)
        name_subtitle = ctk.CTkFrame(header_row, fg_color="#F5F5F5")
        name_subtitle.pack(side="left", anchor="n")
        
        # Main title - smaller
        ctk.CTkLabel(
            name_subtitle, 
            text=f"{program_acronym} {section_name}", 
            font=ctk.CTkFont(size=22, weight="bold"),  # Reduced from 28
            text_color="#111827"
        ).pack(anchor="w")
        
        # Subtitle - smaller
        ctk.CTkLabel(
            name_subtitle, 
            text="Course Attendance Overview - Academic Year 2024-2025", 
            font=ctk.CTkFont(size=12),  # Reduced from 14
            text_color="#6B7280"
        ).pack(anchor="w", pady=(3, 0))  # Reduced padding

        # Filters (right)
        controls_frame = ctk.CTkFrame(header_row, fg_color="#F5F5F5")
        controls_frame.pack(side="right", anchor="n")
        
        # Get available options from database
        if self.db_manager:
            success, years = self.db_manager.get_available_academic_years()
            available_years = years if success else []
            
            success, semesters = self.db_manager.get_available_semesters()
            available_semesters = semesters if success else []
        else:
            available_years = ["2024-2025", "2023-2024"]
            available_semesters = ["1st Semester", "2nd Semester"]
        
        # Year selection
        year_values = ["All Years"] + available_years
        year_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            values=year_values,
            variable=self.year_var,
            width=120,
            height=32,
            command=self.on_filter_change
        )
        year_dropdown.grid(row=0, column=0, padx=(0, 10), pady=(0, 5))
        
        # Semester selection
        semester_values = ["All Semesters"] + available_semesters
        semester_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            values=semester_values,
            variable=self.semester_var,
            width=120,
            height=32,
            command=self.on_filter_change
        )
        semester_dropdown.grid(row=0, column=1, pady=(0, 5))

        # Chart Frame - more compact (this will be dynamically updated)
        self.chart_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="#fff", 
            corner_radius=8,  # Reduced from 12
            border_width=1, 
            border_color="#E5E7EB"
        )
        self.chart_frame.pack(fill="x", padx=20, pady=(0, 15))  # Reduced padding
        
        # Create matplotlib chart
        self.create_attendance_chart(self.chart_frame)

        # Courses Table - more compact
        table_title_frame = ctk.CTkFrame(self.main_frame, fg_color="#F5F5F5")
        table_title_frame.pack(fill="x", padx=20, pady=(0, 8))  # Reduced padding
        
        ctk.CTkLabel(
            table_title_frame,
            text="Course Details",
            font=ctk.CTkFont(size=15, weight="bold"),  # Reduced from 18
            text_color="#000"
        ).pack(anchor="w")

        # Table Frame - more compact (this will be dynamically updated)
        self.table_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="#fff", 
            border_color="#E5E7EB", 
            border_width=1, 
            corner_radius=8  # Reduced from 12
        )
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))  # Reduced padding
        
        # Setup courses table
        self.setup_courses_table()

    def setup_courses_table(self):
        """Setup the courses table"""
        # Table headers
        columns = ["Course Name", "Course Code", "Attendance Rate", "Actions"]
        col_widths = [4, 2, 2, 2]
        
        for i, weight in enumerate(col_widths):
            self.table_frame.grid_columnconfigure(i, weight=weight)
        
        # Header row with compact spacing
        for i, col in enumerate(columns):
            ctk.CTkLabel(
                self.table_frame, 
                text=col, 
                font=ctk.CTkFont(size=12, weight="bold"),  # Reduced from 14
                text_color="#374151", 
                anchor="w"
            ).grid(row=0, column=i, padx=15, pady=10, sticky="w")  # Reduced from pady=15
        
        # Load and display courses
        self.load_courses()

    def load_courses(self):
        """Load courses for this section"""
        courses_data = self.get_section_courses_attendance()
        
        # Clear existing rows (except header)
        for widget in self.table_frame.winfo_children():
            info = widget.grid_info()
            if info and info['row'] > 0:
                widget.destroy()
        
        if not courses_data:
            # Show no data message
            no_data_label = ctk.CTkLabel(
                self.table_frame,
                text="No courses found for this section",
                font=ctk.CTkFont(size=14),  # Reduced from 16
                text_color="#6B7280"
            )
            no_data_label.grid(row=1, column=0, columnspan=4, pady=30)  # Reduced from 50
            return
        
        # Add course rows with compact spacing
        for idx, course in enumerate(courses_data, start=1):
            # Course Name
            ctk.CTkLabel(
                self.table_frame, 
                text=course['course_name'], 
                font=ctk.CTkFont(size=11),  # Reduced from 13
                text_color="#111827",
                anchor="w"
            ).grid(row=idx, column=0, sticky="ew", padx=15, pady=6)  # Reduced from pady=10
            
            # Course Code
            ctk.CTkLabel(
                self.table_frame, 
                text=course['course_code'] or 'N/A', 
                font=ctk.CTkFont(size=11),  # Reduced from 13
                text_color="#111827",
                anchor="w"
            ).grid(row=idx, column=1, sticky="ew", padx=15, pady=6)  # Reduced from pady=10
            
            # Attendance Rate
            attendance_rate = course['present_rate']
            color = "#22C55E" if attendance_rate >= 75 else "#F59E0B" if attendance_rate >= 50 else "#EF4444"
            
            ctk.CTkLabel(
                self.table_frame, 
                text=f"{attendance_rate:.1f}%", 
                font=ctk.CTkFont(size=11, weight="bold"),  # Reduced from 13
                text_color=color,
                anchor="w"
            ).grid(row=idx, column=2, sticky="ew", padx=15, pady=6)  # Reduced from pady=10
            
            # Actions dropdown - more compact
            action_var = tk.StringVar(value="Actions")
            actions = ["View Details", "Export Data"]
            action_menu = ctk.CTkOptionMenu(
                self.table_frame,
                values=actions,
                variable=action_var,
                width=95,  # Reduced from 110
                height=28,  # Reduced from 32
                font=ctk.CTkFont(size=10),  # Reduced from 12
                fg_color="#F3F4F6",
                text_color="#222",
                button_color="#E5E7EB",
                button_hover_color="#D1D5DB",
                dropdown_fg_color="#fff",
                dropdown_hover_color="#E5E7EB",
                dropdown_text_color="#222",
                command=lambda choice, course_data=course: self.handle_course_action(choice, course_data)
            )
            action_menu.grid(row=idx, column=3, sticky="w", padx=15, pady=6)  # Reduced from pady=10

    def create_attendance_chart(self, parent):
        """Create a bar chart showing attendance rates for courses in this section"""
        # Get course attendance data
        courses_data = self.get_section_courses_attendance()
        
        if not courses_data:
            # Show no data message
            no_data_label = ctk.CTkLabel(
                parent,
                text="No course attendance data available for this section",
                font=ctk.CTkFont(size=14),  # Reduced from 16
                text_color="#6B7280"
            )
            no_data_label.pack(pady=40)  # Reduced from 60
            return
        
        # Create matplotlib figure with more compact proportions
        fig, ax = plt.subplots(figsize=(10, 3.5))  # Reduced from (12, 5)
        fig.patch.set_facecolor('#ffffff')
        
        # Extract data for chart - use course codes instead of course names
        course_codes = [course['course_code'] or f"Course {i+1}" for i, course in enumerate(courses_data)]
        present_rates = [course['present_rate'] for course in courses_data]
        absent_rates = [course['absent_rate'] for course in courses_data]
        
        # Set up the bar positions
        x = np.arange(len(course_codes))
        width = 0.35
        
        # Create bars with shortened legend labels
        bars1 = ax.bar(x - width/2, present_rates, width, label='Present', color='#22C55E', alpha=0.85)
        bars2 = ax.bar(x + width/2, absent_rates, width, label='Absent', color='#EF4444', alpha=0.85)
        
        # Customize the chart - more compact
        ax.set_xlabel('Course Codes', fontsize=10, fontweight='bold')  # Reduced from 12
        ax.set_ylabel('Percentage (%)', fontsize=10, fontweight='bold')  # Reduced from 12
        ax.set_title('Attendance Rate by Course', fontsize=12, fontweight='bold', pad=15)  # Reduced from 14 and pad 25
        ax.set_xticks(x)
        ax.set_xticklabels(course_codes, rotation=0, ha='center', fontsize=9)  # Reduced from 11
        ax.legend(fontsize=9, loc='upper right')  # Reduced from 11
        ax.grid(True, alpha=0.3, axis='y')
        
        # Set y-axis limit from 0% to 100% with ticks every 25%
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
        
        # Add value labels on bars - smaller font
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}%',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 2),  # Reduced from 3
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=7, fontweight='bold')  # Reduced from 9
        
        add_labels(bars1)
        add_labels(bars2)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Embed the chart in tkinter with compact spacing
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))  # Reduced padding

    def on_filter_change(self, value=None):
        """Called when year or semester selection changes"""
        self.refresh_content()

    def refresh_content(self):
        """Refresh only the chart and table content dynamically"""
        # Clear and refresh chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        self.create_attendance_chart(self.chart_frame)
        
        # Clear and refresh table
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.setup_courses_table()
        
        print(f"Content refreshed - Academic Year: {self.year_var.get()}, Semester: {self.semester_var.get()}")

    def get_section_courses_attendance(self):
        """Get courses and their attendance data for this section"""
        if not self.db_manager or not self.section_data.get('id'):
            return []
        
        try:
            section_id = self.section_data.get('id')
            
            # Get filter values
            academic_year = None if self.year_var.get() == "All Years" else self.year_var.get()
            semester = None if self.semester_var.get() == "All Semesters" else self.semester_var.get()
            
            # Use the new backend method that properly handles filtering
            success, courses_stats = self.db_manager.sections.get_section_courses_attendance_stats(
                section_id, academic_year, semester
            )
            
            if not success:
                print(f"Failed to get attendance stats for section {section_id}")
                return []
            
            return courses_stats
            
        except Exception as e:
            print(f"Error getting section courses attendance: {e}")
            return []

    def handle_course_action(self, action, course_data):
        """Handle course action selection"""
        if action == "View Details":
            from .sections_course_students_view import CourseStudentsViewModal
            CourseStudentsViewModal(self, self.db_manager, course_data, self.section_data)
        elif action == "Export Data":
            self.export_course_data(course_data)

    def export_course_data(self, course_data):
        """Export course attendance data to CSV"""
        try:
            import csv
            from tkinter import filedialog, messagebox
            from datetime import datetime
            
            # Get course attendance data for this section
            section_id = self.section_data.get('id')
            if not section_id:
                messagebox.showerror("Error", "Section information not available")
                return
            
            # Get filter values
            academic_year = None if self.year_var.get() == "All Years" else self.year_var.get()
            semester = None if self.semester_var.get() == "All Semesters" else self.semester_var.get()
            
            # Get detailed student attendance data for this course
            students_data = self.get_course_student_attendance_data(course_data, academic_year, semester)
            
            if not students_data:
                messagebox.showwarning("No Data", "No attendance data available for this course.")
                return
            
            # Prepare filename
            course_name = course_data.get('course_name', 'Unknown Course').replace(' ', '_')
            section_name = self.section_data.get('name', 'Unknown Section')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Ask user where to save the file
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Course Attendance Data",
                initialfile=f"{course_name}_{section_name}_attendance_{timestamp}.csv"
            )
            
            if not filename:
                return
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header information
                writer.writerow([f"Course Attendance Report"])
                writer.writerow([f"Course: {course_data.get('course_name', 'Unknown')}"])
                writer.writerow([f"Course Code: {course_data.get('course_code', 'N/A')}"])
                writer.writerow([f"Section: {section_name}"])
                writer.writerow([f"Academic Year: {academic_year or 'All Years'}"])
                writer.writerow([f"Semester: {semester or 'All Semesters'}"])
                writer.writerow([f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                writer.writerow([])  # Empty row
                
                # Course statistics
                writer.writerow(["Course Statistics:"])
                writer.writerow(["Overall Attendance Rate", f"{course_data.get('present_rate', 0):.1f}%"])
                writer.writerow(["Total Students", len(students_data)])
                writer.writerow(["Total Attendance Logs", course_data.get('total_logs', 0)])
                writer.writerow([])  # Empty row
                
                # Student data headers
                writer.writerow(["Student Attendance Details:"])
                writer.writerow([
                    "Student Name", "Student ID", "Email", 
                    "Present", "Absent", "Late", "Total", "Attendance %"
                ])
                
                # Student data rows
                for student in students_data:
                    writer.writerow([
                        student.get('student_name', ''),
                        student.get('student_number', ''),
                        student.get('email', ''),
                        student.get('present', 0),
                        student.get('absent', 0),
                        student.get('late', 0),
                        student.get('total', 0),
                        f"{student.get('percentage', 0):.1f}%"
                    ])
            
            # Show success message
            messagebox.showinfo("Export Successful", 
                              f"Course attendance data exported successfully!\n\nFile: {filename}\nStudents: {len(students_data)}")
            
        except Exception as e:
            print(f"Error exporting course data: {e}")
            messagebox.showerror("Export Error", f"Failed to export course data:\n{str(e)}")

    def get_course_student_attendance_data(self, course_data, academic_year=None, semester=None):
        """Get detailed student attendance data for a specific course"""
        try:
            if not self.db_manager:
                return []
            
            section_id = self.section_data.get('id')
            course_id = course_data.get('course_id')
            
            if not section_id or not course_id:
                return []
            
            # Get all students in this section
            conn = self.db_manager.get_connection()
            
            # Get students query
            students_query = """
                SELECT u.id, u.first_name, u.last_name, u.email, 
                       s.student_number
                FROM students s
                JOIN users u ON s.user_id = u.id
                WHERE s.section = ? AND u.isDeleted = 0
                ORDER BY u.last_name, u.first_name
            """
            
            cursor = conn.execute(students_query, (section_id,))
            students = cursor.fetchall()
            
            if not students:
                conn.close()
                return []
            
            # Get assigned course ID
            assigned_course_query = """
                SELECT id FROM assigned_courses 
                WHERE course_id = ? AND section_id = ? AND isDeleted = 0
            """
            params = [course_id, section_id]
            
            if academic_year:
                assigned_course_query += " AND academic_year = ?"
                params.append(academic_year)
            
            if semester:
                assigned_course_query += " AND semester = ?"
                params.append(semester)
            
            cursor = conn.execute(assigned_course_query, params)
            assigned_course = cursor.fetchone()
            
            if not assigned_course:
                conn.close()
                return []
            
            assigned_course_id = assigned_course['id']
            
            # Get attendance data for each student
            students_data = []
            for student in students:
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
                
                cursor = conn.execute(attendance_query, (student['id'], assigned_course_id))
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
                    
                    students_data.append({
                        'student_name': f"{student['first_name']} {student['last_name']}",
                        'student_number': student['student_number'] or 'N/A',
                        'email': student['email'] or 'N/A',
                        'present': present,
                        'absent': absent,
                        'late': late,
                        'total': total,
                        'percentage': percentage
                    })
            
            conn.close()
            return students_data
            
        except Exception as e:
            print(f"Error getting course student attendance data: {e}")
            if 'conn' in locals():
                conn.close()
            return []
