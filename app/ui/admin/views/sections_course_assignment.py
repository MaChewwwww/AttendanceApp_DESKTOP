import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from app.ui.admin.components.modals import SuccessModal
import re

class SectionCourseAssignmentPopup(ctk.CTkToplevel):
    def __init__(self, parent, section_data, db_manager):
        super().__init__(parent)
        self.parent_popup = parent
        self.section_data = section_data
        self.db_manager = db_manager
        self.courses_data = []
        self.faculty_data = []
        self.assignment_rows = []
        
        self.title("Assign Courses to Section")
        self.geometry("800x600")
        self.resizable(True, True)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
        
        self.load_data()
        self.center_window()
        self.setup_ui()
        self.add_assignment_row()  # Add first row by default

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def load_data(self):
        """Load courses and faculty data"""
        try:
            # Load courses for the selected program using program ID
            if self.db_manager:
                # Use the program ID from section_data to get courses specifically for this program
                program_id = self.section_data['program_id']
                success, courses = self.db_manager.get_courses_by_program_id(program_id)
                if success:
                    self.courses_data = courses
                else:
                    print(f"Error loading courses: {courses}")
                    self.courses_data = []
                
                # Load all faculty without filters
                success, faculty = self.db_manager.get_all_faculty()
                if success:
                    self.faculty_data = faculty
                else:
                    print(f"Error loading faculty: {faculty}")
                    self.faculty_data = []
        except Exception as e:
            print(f"Error loading data: {e}")
            self.courses_data = []
            self.faculty_data = []

    def setup_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=24, pady=(24, 12))
        
        ctk.CTkLabel(
            header_frame,
            text="Assign Courses to Section",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="#111",
        ).pack(side="left")
        
        # Section info
        section_info = f"Section: {self.section_data['name']} | Program: {self.section_data['program_data']['name']}"
        ctk.CTkLabel(
            header_frame,
            text=section_info,
            font=ctk.CTkFont(size=12),
            text_color="#666",
        ).pack(side="left", padx=(20, 0))

        # Scrollable frame for assignments
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#fff",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # Column headers
        headers_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        headers_frame.pack(fill="x", pady=(10, 5))
        headers_frame.grid_columnconfigure(0, weight=2)  # Course
        headers_frame.grid_columnconfigure(1, weight=1)  # Academic Year
        headers_frame.grid_columnconfigure(2, weight=1)  # Semester
        headers_frame.grid_columnconfigure(3, weight=1)  # Room
        headers_frame.grid_columnconfigure(4, weight=2)  # Faculty
        headers_frame.grid_columnconfigure(5, weight=0)  # Remove button
        
        headers = ["Course", "Academic Year", "Semester", "Room", "Faculty", ""]
        for i, header in enumerate(headers):
            if header:  # Skip empty header for remove button column
                ctk.CTkLabel(
                    headers_frame,
                    text=header,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#374151"
                ).grid(row=0, column=i, sticky="w", padx=(10, 5), pady=5)

        # Add course button
        add_btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_btn_frame.pack(fill="x", padx=24, pady=(0, 16))
        
        ctk.CTkButton(
            add_btn_frame,
            text="+ Add Another Course",
            width=150,
            height=32,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#fff",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.add_assignment_row
        ).pack(side="left")

        # Bottom buttons
        button_frame = ctk.CTkFrame(self, fg_color="#FAFAFA")
        button_frame.pack(side="bottom", fill="x", padx=0, pady=0)
        
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(fill="x", padx=24, pady=16)
        
        cancel_btn = ctk.CTkButton(
            button_container,
            text="Cancel",
            fg_color="#D1D5DB",
            text_color="#222",
            hover_color="#BDBDBD",
            width=140,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.cancel_creation
        )
        cancel_btn.pack(side="left", padx=(0, 8))
        
        submit_btn = ctk.CTkButton(
            button_container,
            text="Create Section & Assign Courses",
            fg_color="#1E3A8A",
            hover_color="#1D4ED8",
            text_color="#fff",
            width=220,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.submit_section_and_courses
        )
        submit_btn.pack(side="right", padx=(8, 0))

    def add_assignment_row(self):
        """Add a new course assignment row"""
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)
        row_frame.grid_columnconfigure(0, weight=2)
        row_frame.grid_columnconfigure(1, weight=1)
        row_frame.grid_columnconfigure(2, weight=1)
        row_frame.grid_columnconfigure(3, weight=1)
        row_frame.grid_columnconfigure(4, weight=2)
        row_frame.grid_columnconfigure(5, weight=0)

        # Course dropdown
        course_var = ctk.StringVar(value="Select Course")
        course_names = [f"{course['name']} ({course['code']})" if course.get('code') else course['name'] 
                       for course in self.courses_data]
        if not course_names:
            course_names = ["No courses available"]
        
        course_menu = ctk.CTkOptionMenu(
            row_frame,
            variable=course_var,
            values=course_names,
            width=200,
            height=32,
            fg_color="#fff",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            font=ctk.CTkFont(size=11)
        )
        course_menu.grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=2)

        # Academic Year entry
        academic_year_var = ctk.StringVar()
        academic_year_entry = ctk.CTkEntry(
            row_frame,
            textvariable=academic_year_var,
            placeholder_text="2023-2024",
            width=100,
            height=32,
            fg_color="#fff",
            text_color="#222",
            border_color="#BDBDBD",
            border_width=1,
            font=ctk.CTkFont(size=11)
        )
        academic_year_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # Semester dropdown
        semester_var = ctk.StringVar(value="Select Semester")
        semester_menu = ctk.CTkOptionMenu(
            row_frame,
            variable=semester_var,
            values=["1st Semester", "2nd Semester", "3rd Semester", "Summer"],
            width=120,
            height=32,
            fg_color="#fff",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            font=ctk.CTkFont(size=11)
        )
        semester_menu.grid(row=0, column=2, sticky="ew", padx=5, pady=2)

        # Room entry
        room_var = ctk.StringVar()
        room_entry = ctk.CTkEntry(
            row_frame,
            textvariable=room_var,
            placeholder_text="Room",
            width=80,
            height=32,
            fg_color="#fff",
            text_color="#222",
            border_color="#BDBDBD",
            border_width=1,
            font=ctk.CTkFont(size=11)
        )
        room_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=2)

        # Faculty dropdown
        faculty_var = ctk.StringVar(value="Select Faculty")
        faculty_names = [f"{faculty['first_name']} {faculty['last_name']}" for faculty in self.faculty_data]
        if not faculty_names:
            faculty_names = ["No faculty available"]
        
        faculty_menu = ctk.CTkOptionMenu(
            row_frame,
            variable=faculty_var,
            values=faculty_names,
            width=180,
            height=32,
            fg_color="#fff",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            font=ctk.CTkFont(size=11)
        )
        faculty_menu.grid(row=0, column=4, sticky="ew", padx=5, pady=2)

        # Remove button
        remove_btn = ctk.CTkButton(
            row_frame,
            text="✕",
            width=30,
            height=30,
            fg_color="#EF4444",
            hover_color="#DC2626",
            text_color="#fff",
            font=ctk.CTkFont(size=12),
            command=lambda: self.remove_assignment_row(row_frame)
        )
        remove_btn.grid(row=0, column=5, padx=(5, 10), pady=2)

        # Store row data
        row_data = {
            'frame': row_frame,
            'course_var': course_var,
            'academic_year_var': academic_year_var,
            'semester_var': semester_var,
            'room_var': room_var,
            'faculty_var': faculty_var
        }
        self.assignment_rows.append(row_data)

    def remove_assignment_row(self, row_frame):
        """Remove a course assignment row"""
        if len(self.assignment_rows) <= 1:
            messagebox.showwarning("Warning", "At least one course assignment is required")
            return
        
        # Find and remove the row data
        for i, row_data in enumerate(self.assignment_rows):
            if row_data['frame'] == row_frame:
                row_frame.destroy()
                self.assignment_rows.pop(i)
                break

    def validate_academic_year(self, academic_year):
        """Validate academic year format (YYYY-YYYY)"""
        pattern = r'^\d{4}-\d{4}$'
        if not re.match(pattern, academic_year):
            return False
        
        years = academic_year.split('-')
        start_year = int(years[0])
        end_year = int(years[1])
        
        return end_year == start_year + 1

    def validate_assignments(self):
        """Validate all assignment rows"""
        if not self.assignment_rows:
            messagebox.showerror("Error", "At least one course assignment is required")
            return False

        assignments = []
        seen_courses = set()

        for i, row_data in enumerate(self.assignment_rows):
            # Get values directly from widgets instead of variables
            course_selection = row_data['course_var'].get()
            # Get academic year directly from the entry widget
            academic_year = ""
            for widget in row_data['frame'].winfo_children():
                if isinstance(widget, ctk.CTkEntry) and widget.cget("placeholder_text") == "2023-2024":
                    academic_year = widget.get().strip()
                    break
            
            semester = row_data['semester_var'].get()
            
            # Get room directly from the entry widget
            room = ""
            for widget in row_data['frame'].winfo_children():
                if isinstance(widget, ctk.CTkEntry) and widget.cget("placeholder_text") == "Room":
                    room = widget.get().strip()
                    break
            
            faculty_selection = row_data['faculty_var'].get()

            # Validate course selection
            if course_selection == "Select Course" or course_selection == "No courses available":
                messagebox.showerror("Error", f"Please select a course for row {i+1}")
                return False

            # Check for duplicate courses
            if course_selection in seen_courses:
                messagebox.showerror("Error", f"Course '{course_selection}' is assigned multiple times")
                return False
            seen_courses.add(course_selection)

            # Validate academic year
            if not academic_year:
                messagebox.showerror("Error", f"Academic year is required for row {i+1}")
                return False
            
            if not self.validate_academic_year(academic_year):
                messagebox.showerror("Error", f"Academic year format should be YYYY-YYYY (e.g., 2023-2024) for row {i+1}")
                return False

            # Validate semester
            if semester == "Select Semester":
                messagebox.showerror("Error", f"Please select a semester for row {i+1}")
                return False

            # Validate faculty
            if faculty_selection == "Select Faculty" or faculty_selection == "No faculty available":
                messagebox.showerror("Error", f"Please select a faculty for row {i+1}")
                return False

            # Find course and faculty IDs
            course_id = None
            for course in self.courses_data:
                course_display = f"{course['name']} ({course['code']})" if course.get('code') else course['name']
                if course_display == course_selection:
                    course_id = course['id']
                    break

            faculty_id = None
            for faculty in self.faculty_data:
                faculty_display = f"{faculty['first_name']} {faculty['last_name']}"
                if faculty_display == faculty_selection:
                    faculty_id = faculty['id']
                    break

            if not course_id or not faculty_id:
                messagebox.showerror("Error", f"Invalid course or faculty selection for row {i+1}")
                return False

            assignments.append({
                'course_id': course_id,
                'faculty_id': faculty_id,
                'academic_year': academic_year,
                'semester': semester,
                'room': room if room else None
            })

        return assignments

    def submit_section_and_courses(self):
        """Submit section and course assignments to database"""
        try:
            # Validate assignments
            assignments = self.validate_assignments()
            if not assignments:
                return

            if not self.db_manager:
                messagebox.showerror("Error", "Database connection not available")
                return

            # Create section first
            success, section_result = self.db_manager.create_section(self.section_data)
            
            if not success:
                messagebox.showerror("Error", f"Failed to create section: {section_result}")
                return

            section_id = section_result['id']

            # Create assigned courses
            assignment_errors = []
            created_assignments = []

            for assignment in assignments:
                assignment_data = {
                    'faculty_id': assignment['faculty_id'],
                    'course_id': assignment['course_id'],
                    'section_id': section_id,
                    'academic_year': assignment['academic_year'],
                    'semester': assignment['semester'],
                    'room': assignment['room']
                }

                # Create assigned course entry
                success, result = self.create_assigned_course(assignment_data)
                if success:
                    created_assignments.append(result)
                else:
                    assignment_errors.append(result)

            if assignment_errors:
                # If there were errors, show them but still consider partial success
                error_message = "Section created but some course assignments failed:\n" + "\n".join(assignment_errors)
                messagebox.showwarning("Partial Success", error_message)
            
            # Close popups and refresh
            parent_view = self.parent_popup.parent_view
            self.parent_popup.destroy()  # Close the original create section popup
            self.destroy()  # Close this assignment popup
            
            # Refresh parent view and show success
            parent_view.after(100, lambda: parent_view.refresh_sections())
            parent_view.after(200, lambda: SuccessModal(parent_view))

        except Exception as e:
            print(f"Error submitting section and courses: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def create_assigned_course(self, assignment_data):
        """Create an assigned course entry"""
        try:
            from datetime import datetime
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO assigned_courses (faculty_id, course_id, section_id, academic_year, semester, room, isDeleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assignment_data['faculty_id'],
                assignment_data['course_id'],
                assignment_data['section_id'],
                assignment_data['academic_year'],
                assignment_data['semester'],
                assignment_data['room'],
                0,  # isDeleted = 0
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            assignment_id = cursor.lastrowid
            conn.close()
            
            return True, {"id": assignment_id, "message": "Course assigned successfully"}
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            print(f"Error creating assigned course: {e}")
            return False, str(e)

    def cancel_creation(self):
        """Cancel section creation"""
        self.destroy()
