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
        
        self.setup_ui()

    def setup_ui(self):
        # Header - more compact
        top_frame = ctk.CTkFrame(self.main_frame, fg_color="#F5F5F5")
        top_frame.pack(fill="x", padx=20, pady=(15, 10))  # Reduced padding
        
        section_name = self.section_data.get('name', 'N/A')
        program_acronym = self.section_data.get('program_acronym', 'N/A')
        
        # Main title - smaller
        ctk.CTkLabel(
            top_frame, 
            text=f"{program_acronym} {section_name}", 
            font=ctk.CTkFont(size=22, weight="bold"),  # Reduced from 28
            text_color="#111827"
        ).pack(anchor="w")
        
        # Subtitle - smaller
        ctk.CTkLabel(
            top_frame, 
            text="Course Attendance Overview - Academic Year 2024-2025", 
            font=ctk.CTkFont(size=12),  # Reduced from 14
            text_color="#6B7280"
        ).pack(anchor="w", pady=(3, 0))  # Reduced padding

        # Chart Frame - more compact
        chart_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="#fff", 
            corner_radius=8,  # Reduced from 12
            border_width=1, 
            border_color="#E5E7EB"
        )
        chart_frame.pack(fill="x", padx=20, pady=(0, 15))  # Reduced padding
        
        # Create matplotlib chart
        self.create_attendance_chart(chart_frame)

        # Courses Table - more compact
        table_title_frame = ctk.CTkFrame(self.main_frame, fg_color="#F5F5F5")
        table_title_frame.pack(fill="x", padx=20, pady=(0, 8))  # Reduced padding
        
        ctk.CTkLabel(
            table_title_frame,
            text="Course Details",
            font=ctk.CTkFont(size=15, weight="bold"),  # Reduced from 18
            text_color="#000"
        ).pack(anchor="w")

        # Table Frame - more compact
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

    def get_section_courses_attendance(self):
        """Get courses and their attendance data for this section"""
        if not self.db_manager or not self.section_data.get('id'):
            return []
        
        try:
            section_id = self.section_data.get('id')
            
            # Get courses assigned to this section
            success, courses = self.db_manager.get_section_courses(section_id)
            
            if not success or not courses:
                print(f"No courses found for section {section_id}")
                return []
            
            courses_with_attendance = []
            
            for course in courses:
                # Get attendance statistics for each course in this section
                course_stats = self.get_course_attendance_stats(course['course_id'], section_id)
                
                course_data = {
                    'course_id': course['course_id'],
                    'course_name': course.get('course_name', 'Unknown Course'),
                    'course_code': course.get('course_code', 'N/A'),
                    'present_rate': course_stats['present_rate'],
                    'absent_rate': course_stats['absent_rate']
                }
                
                courses_with_attendance.append(course_data)
            
            return courses_with_attendance
            
        except Exception as e:
            print(f"Error getting section courses attendance: {e}")
            return []

    def get_course_attendance_stats(self, course_id, section_id):
        """Get attendance statistics for a specific course and section"""
        try:
            conn = self.db_manager.get_connection()
            
            # Query to get attendance statistics for students in this section for this course
            query = """
                SELECT 
                    COUNT(CASE WHEN al.status = 'present' THEN 1 END) as present_count,
                    COUNT(CASE WHEN al.status = 'absent' THEN 1 END) as absent_count,
                    COUNT(CASE WHEN al.status = 'late' THEN 1 END) as late_count,
                    COUNT(*) as total_logs
                FROM attendance_logs al
                JOIN assigned_courses ac ON al.assigned_course_id = ac.id
                JOIN users u ON al.user_id = u.id
                JOIN students s ON u.id = s.user_id
                WHERE ac.course_id = ? 
                  AND ac.section_id = ? 
                  AND s.section = ?
                  AND u.isDeleted = 0
                  AND ac.isDeleted = 0
            """
            
            cursor = conn.execute(query, (course_id, section_id, section_id))
            result = cursor.fetchone()
            
            if result and result['total_logs'] > 0:
                present_count = result['present_count'] or 0
                absent_count = result['absent_count'] or 0
                late_count = result['late_count'] or 0
                total_logs = result['total_logs']
                
                # Count late as present for attendance rate calculation
                effective_present = present_count + late_count
                
                present_rate = (effective_present / total_logs) * 100 if total_logs > 0 else 0
                absent_rate = (absent_count / total_logs) * 100 if total_logs > 0 else 0
                
            else:
                # No attendance data found, return default values
                present_rate = 0.0
                absent_rate = 0.0
            
            conn.close()
            
            return {
                'present_rate': round(present_rate, 1),
                'absent_rate': round(absent_rate, 1)
            }
            
        except Exception as e:
            print(f"Error getting course attendance stats: {e}")
            return {
                'present_rate': 0.0,
                'absent_rate': 0.0
            }

    def handle_course_action(self, action, course_data):
        """Handle course action selection"""
        if action == "View Details":
            print(f"View details for course: {course_data['course_name']}")
            # TODO: Open course details popup
        elif action == "Export Data":
            print(f"Export data for course: {course_data['course_name']}")
            # TODO: Export course attendance data
