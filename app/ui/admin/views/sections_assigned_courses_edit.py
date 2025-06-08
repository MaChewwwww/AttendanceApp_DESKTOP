import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from app.ui.admin.components.modals import SuccessModal, DeleteModal

class AddAssignmentModal(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, section_data, courses_data, faculty_data, on_success=None):
        super().__init__(parent)
        self.parent_view = parent
        self.db_manager = db_manager
        self.section_data = section_data
        self.courses_data = courses_data
        self.faculty_data = faculty_data
        self.on_success = on_success
        
        self.title("Add Course Assignment")
        self.geometry("480x600")
        self.resizable(False, False)
        self.configure(fg_color="#F8FAFC")
        self.transient(parent)
        self.grab_set()
        
        self.center_window()
        self.setup_ui()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=8)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        ctk.CTkLabel(
            main_container,
            text="Add Course Assignment",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1F2937"
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            main_container,
            text="Create a new assignment for this course",
            font=ctk.CTkFont(size=11),
            text_color="#6B7280"
        ).pack(pady=(0, 15))
        
        # Form container
        form_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20)
        
        # Course selection
        ctk.CTkLabel(form_frame, text="Course *", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.course_var = ctk.StringVar(value="Select course")
        course_options = []
        self.course_mapping = {}
        
        for course in self.courses_data:
            display_name = f"{course.get('name', '')} ({course.get('code', '')})" if course.get('code') else course.get('name', '')
            course_options.append(display_name)
            self.course_mapping[display_name] = course
        
        self.course_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.course_var,
            values=course_options or ["No courses available"],
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.course_menu.pack(fill="x", pady=(0, 10))
        
        # Academic Year
        ctk.CTkLabel(form_frame, text="Academic Year *", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.academic_year_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="2024-2025",
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.academic_year_entry.pack(fill="x", pady=(0, 10))
        
        # Semester
        ctk.CTkLabel(form_frame, text="Semester *", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.semester_var = ctk.StringVar(value="Select semester")
        self.semester_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.semester_var,
            values=["1st Semester", "2nd Semester", "3rd Semester", "Summer"],
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.semester_menu.pack(fill="x", pady=(0, 10))
        
        # Room
        ctk.CTkLabel(form_frame, text="Room", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.room_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Room number/name",
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.room_entry.pack(fill="x", pady=(0, 10))
        
        # Faculty dropdown
        ctk.CTkLabel(form_frame, text="Faculty *", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.faculty_var = ctk.StringVar(value="Select faculty")
        faculty_options = []
        self.faculty_mapping = {}
        
        for faculty in self.faculty_data:
            display_name = f"{faculty.get('first_name', '')} {faculty.get('last_name', '')}"
            faculty_options.append(display_name)
            self.faculty_mapping[display_name] = faculty
        
        self.faculty_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.faculty_var,
            values=faculty_options or ["No faculty available"],
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.faculty_menu.pack(fill="x", pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#F3F4F6",
            text_color="#374151",
            hover_color="#E5E7EB",
            command=self.destroy
        ).pack(side="left")
        
        ctk.CTkButton(
            button_frame,
            text="Assign New Course",
            width=140,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#059669",
            hover_color="#047857",
            command=self.save_assignment
        ).pack(side="right")

    def save_assignment(self):
        try:
            # Validate inputs
            course_name = self.course_var.get()
            if course_name in ["Select course", "No courses available"]:
                messagebox.showerror("Error", "Please select a course")
                return
            
            # Check if course exists in mapping
            if course_name not in self.course_mapping:
                messagebox.showerror("Error", "Selected course is not valid")
                return
            
            academic_year = self.academic_year_entry.get().strip()
            if not academic_year:
                messagebox.showerror("Error", "Academic year is required")
                return
            
            # Validate academic year format
            import re
            if not re.match(r'^\d{4}-\d{4}$', academic_year):
                messagebox.showerror("Error", "Academic year format should be YYYY-YYYY (e.g., 2024-2025)")
                return
            
            semester = self.semester_var.get()
            if semester in ["Select semester"]:
                messagebox.showerror("Error", "Please select a semester")
                return
            
            faculty_name = self.faculty_var.get()
            if faculty_name in ["Select faculty", "No faculty available"]:
                messagebox.showerror("Error", "Please select a faculty")
                return
            
            # Check if faculty exists in mapping
            if faculty_name not in self.faculty_mapping:
                messagebox.showerror("Error", "Selected faculty is not valid")
                return
            
            room = self.room_entry.get().strip()
            
            # Get IDs
            course_id = self.course_mapping[course_name]['id']
            faculty_id = self.faculty_mapping[faculty_name]['id']
            
            # Create assignment
            assignment_data = {
                'faculty_id': faculty_id,
                'course_id': course_id,
                'section_id': self.section_data['id'],
                'academic_year': academic_year,
                'semester': semester,
                'room': room if room else None
            }
            
            success, result = self.create_assigned_course(assignment_data)
            if success:
                self.destroy()
                if self.on_success:
                    self.on_success()
                self.parent_view.after(100, lambda: SuccessModal(self.parent_view))
            else:
                messagebox.showerror("Error", f"Failed to create assignment: {result}")
                
        except Exception as e:
            print(f"Error saving assignment: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def create_assigned_course(self, assignment_data):
        try:
            from datetime import datetime
            
            conn = self.db_manager.get_connection()
            try:
                cursor = conn.cursor()
                
                # Check for existing assignment
                cursor.execute("""
                    SELECT id FROM assigned_courses 
                    WHERE course_id = ? AND section_id = ? AND isDeleted = 0
                """, (assignment_data['course_id'], assignment_data['section_id']))
                
                if cursor.fetchone():
                    return False, "Course is already assigned to this section"
                
                # Create new assignment
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
                    0,
                    datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                ))
                
                conn.commit()
                return True, "Assignment created successfully"
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            return False, str(e)

class EditAssignmentModal(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, assignment_data, courses_data, faculty_data, on_success=None):
        super().__init__(parent)
        self.parent_view = parent
        self.db_manager = db_manager
        self.assignment_data = assignment_data
        self.courses_data = courses_data
        self.faculty_data = faculty_data
        self.on_success = on_success
        
        self.title("Edit Course Assignment")
        self.geometry("480x600")
        self.resizable(False, False)
        self.configure(fg_color="#F8FAFC")
        self.transient(parent)
        self.grab_set()
        
        self.center_window()
        self.setup_ui()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=8)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        ctk.CTkLabel(
            main_container,
            text="Edit Course Assignment",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1F2937"
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            main_container,
            text="Update assignment details",
            font=ctk.CTkFont(size=11),
            text_color="#6B7280"
        ).pack(pady=(0, 15))
        
        # Form container
        form_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20)
        
        # Course dropdown - enabled for edit mode
        ctk.CTkLabel(form_frame, text="Course *", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.course_var = ctk.StringVar()
        course_options = []
        self.course_mapping = {}
        
        # Populate course options
        for course in self.courses_data:
            display_name = f"{course.get('name', '')} ({course.get('code', '')})" if course.get('code') else course.get('name', '')
            course_options.append(display_name)
            self.course_mapping[display_name] = course
        
        # Set current course
        current_course_display = f"{self.assignment_data.get('course_name', '')} ({self.assignment_data.get('course_code', '')})"
        self.course_var.set(current_course_display)
        
        self.course_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.course_var,
            values=course_options or ["No courses available"],
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.course_menu.pack(fill="x", pady=(0, 10))
        
        # Academic Year
        ctk.CTkLabel(form_frame, text="Academic Year *", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.academic_year_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="2024-2025",
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.academic_year_entry.pack(fill="x", pady=(0, 10))
        self.academic_year_entry.insert(0, self.assignment_data.get('academic_year', ''))
        
        # Semester
        ctk.CTkLabel(form_frame, text="Semester *", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.semester_var = ctk.StringVar(value=self.assignment_data.get('semester', 'Select semester'))
        self.semester_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.semester_var,
            values=["1st Semester", "2nd Semester", "3rd Semester", "Summer"],
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.semester_menu.pack(fill="x", pady=(0, 10))
        
        # Room
        ctk.CTkLabel(form_frame, text="Room", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.room_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Room number/name",
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.room_entry.pack(fill="x", pady=(0, 10))
        self.room_entry.insert(0, self.assignment_data.get('room', ''))
        
        # Faculty dropdown
        ctk.CTkLabel(form_frame, text="Faculty *", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.faculty_var = ctk.StringVar()
        faculty_options = []
        self.faculty_mapping = {}
        
        # Populate faculty options using the existing data
        for faculty in self.faculty_data:
            display_name = f"{faculty.get('first_name', '')} {faculty.get('last_name', '')}"
            faculty_options.append(display_name)
            self.faculty_mapping[display_name] = faculty
        
        # Set current faculty
        current_faculty = self.assignment_data.get('faculty_name', 'Select faculty')
        self.faculty_var.set(current_faculty)
        
        self.faculty_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.faculty_var,
            values=faculty_options or ["No faculty available"],
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.faculty_menu.pack(fill="x", pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#F3F4F6",
            text_color="#374151",
            hover_color="#E5E7EB",
            command=self.destroy
        ).pack(side="left")
        
        ctk.CTkButton(
            button_frame,
            text="Update Assignment",
            width=140,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self.update_assignment
        ).pack(side="right")

    def update_assignment(self):
        try:
            # Validate inputs
            course_name = self.course_var.get()
            if course_name in ["Select course", "No courses available"]:
                messagebox.showerror("Error", "Please select a course")
                return
            
            # Check if course exists in mapping
            if course_name not in self.course_mapping:
                messagebox.showerror("Error", "Selected course is not valid")
                return
            
            academic_year = self.academic_year_entry.get().strip()
            if not academic_year:
                messagebox.showerror("Error", "Academic year is required")
                return
            
            # Validate academic year format
            import re
            if not re.match(r'^\d{4}-\d{4}$', academic_year):
                messagebox.showerror("Error", "Academic year format should be YYYY-YYYY (e.g., 2024-2025)")
                return
            
            semester = self.semester_var.get()
            if semester in ["Select semester"]:
                messagebox.showerror("Error", "Please select a semester")
                return
            
            faculty_name = self.faculty_var.get()
            if faculty_name in ["Select faculty", "No faculty available"]:
                messagebox.showerror("Error", "Please select a faculty")
                return
            
            # Check if faculty exists in mapping
            if faculty_name not in self.faculty_mapping:
                messagebox.showerror("Error", "Selected faculty is not valid")
                return
            
            room = self.room_entry.get().strip()
            
            # Get IDs
            course_id = self.course_mapping[course_name]['id']
            faculty_id = self.faculty_mapping[faculty_name]['id']
            
            # Update assignment
            success, result = self.update_assigned_course(faculty_id, course_id, academic_year, semester, room)
            if success:
                self.destroy()
                if self.on_success:
                    self.on_success()
                self.parent_view.after(100, lambda: SuccessModal(self.parent_view))
            else:
                messagebox.showerror("Error", f"Failed to update assignment: {result}")
                
        except Exception as e:
            print(f"Error updating assignment: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_assigned_course(self, faculty_id, course_id, academic_year, semester, room):
        try:
            from datetime import datetime
            
            conn = self.db_manager.get_connection()
            try:
                cursor = conn.cursor()
                
                # Get section_id from assignment_data instead of self.section_data
                section_id = self.assignment_data.get('section_id')
                if not section_id:
                    # If section_id is not in assignment_data, we can't check for duplicates
                    # but we can still proceed with the update
                    pass
                else:
                    # Check for duplicate course assignment (excluding current assignment)
                    cursor.execute("""
                        SELECT id FROM assigned_courses 
                        WHERE course_id = ? AND section_id = ? AND id != ? AND isDeleted = 0
                    """, (course_id, section_id, self.assignment_data['assignment_id']))
                    
                    if cursor.fetchone():
                        return False, "Course is already assigned to this section"
                
                cursor.execute("""
                    UPDATE assigned_courses 
                    SET faculty_id = ?, course_id = ?, academic_year = ?, semester = ?, room = ?, updated_at = ?
                    WHERE id = ? AND isDeleted = 0
                """, (
                    faculty_id,
                    course_id,
                    academic_year,
                    semester,
                    room if room else None,
                    datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                    self.assignment_data['assignment_id']
                ))
                
                conn.commit()
                return True, "Assignment updated successfully"
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            return False, str(e)

class SectionAssignedCoursesEditPopup(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, section_data):
        super().__init__(parent)
        self.parent_view = parent
        self.db_manager = db_manager
        self.section_data = section_data
        self.courses_data = []
        self.faculty_data = []
        self.existing_assignments = []
        
        self.title(f"Assigned Courses - {section_data.get('name', 'Section')}")
        self.geometry("1200x700")
        self.resizable(True, True)
        self.configure(fg_color="#F8FAFC")
        self.transient(parent)
        self.grab_set()
        
        self.load_data()
        self.load_existing_assignments()
        self.center_window()
        self.setup_ui()

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
            if self.db_manager:
                # Load courses for the section's program
                program_id = self.section_data.get('program_id')
                if not program_id:
                    conn = self.db_manager.get_connection()
                    try:
                        cursor = conn.execute("""
                            SELECT s.program_id, p.name as program_name
                            FROM sections s
                            JOIN programs p ON s.program_id = p.id
                            WHERE s.id = ? AND s.isDeleted = 0
                        """, (self.section_data['id'],))
                        section_row = cursor.fetchone()
                        if section_row:
                            program_id = section_row['program_id']
                            self.section_data['program_id'] = program_id
                            self.section_data['program_name'] = section_row['program_name']
                    finally:
                        conn.close()
                
                if program_id:
                    success, courses = self.db_manager.get_courses_by_program_id(program_id)
                    if success:
                        self.courses_data = courses
                
                success, faculty = self.db_manager.get_all_faculty()
                if success:
                    self.faculty_data = faculty
                    
        except Exception as e:
            print(f"Error loading data: {e}")

    def load_existing_assignments(self):
        """Load existing course assignments"""
        try:
            if self.db_manager:
                success, assignments = self.db_manager.get_section_courses(self.section_data['id'])
                if success:
                    # Check schedule status for each assignment
                    for assignment in assignments:
                        assignment['has_schedule'] = self.check_assignment_schedule(assignment['assignment_id'])
                    self.existing_assignments = assignments
        except Exception as e:
            print(f"Error loading assignments: {e}")

    def check_assignment_schedule(self, assignment_id):
        """Check if an assigned course has any schedules"""
        try:
            conn = self.db_manager.get_connection()
            try:
                cursor = conn.execute("""
                    SELECT COUNT(*) as schedule_count
                    FROM schedules
                    WHERE assigned_course_id = ?
                """, (assignment_id,))
                
                result = cursor.fetchone()
                return result['schedule_count'] > 0 if result else False
                
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Error checking schedule: {e}")
            return False

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0)
        main_container.pack(fill="both", expand=True)
        
        # Header section
        header_section = ctk.CTkFrame(main_container, fg_color="#FAFAFA", corner_radius=0, height=60)
        header_section.pack(fill="x", padx=0, pady=0)
        header_section.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_section, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=24, pady=16)
        
        # Title and Add button
        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(fill="x")
        
        ctk.CTkLabel(
            title_frame,
            text="Course Assignments",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#1F2937",
        ).pack(side="left")
        
        # Add button
        ctk.CTkButton(
            title_frame,
            text="Assign New Course",
            width=140,
            height=32,
            fg_color="#22C55E",
            hover_color="#16A34A",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="normal"),
            corner_radius=6,
            command=self.add_assignment
        ).pack(side="right")
        
        # Section info
        section_info = f"{self.section_data.get('name', 'Unknown')} • {self.section_data.get('program_name', 'Unknown Program')}"
        ctk.CTkLabel(
            header_content,
            text=section_info,
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="#6B7280",
        ).pack(anchor="w", pady=(5, 0))

        # Content area
        content_area = ctk.CTkFrame(main_container, fg_color="transparent")
        content_area.pack(fill="both", expand=True, padx=24, pady=16)
        
        # Table container
        table_container = ctk.CTkFrame(content_area, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB")
        table_container.pack(fill="both", expand=True)
        
        # Table setup
        self.setup_table(table_container)

    def setup_table(self, parent):
        # Table header
        table_header = ctk.CTkFrame(parent, fg_color="#F9FAFB", corner_radius=0, height=40)
        table_header.pack(fill="x")
        table_header.pack_propagate(False)
        
        header_frame = ctk.CTkFrame(table_header, fg_color="transparent")
        header_frame.pack(fill="both", expand=True, padx=15, pady=8)
        
        # Header columns - adjusted widths to include Schedule column
        headers = [
            ("Course", 320),
            ("Academic Year", 110),
            ("Semester", 120),
            ("Room", 90),
            ("Faculty", 180),
            ("Schedule", 80),
            ("Actions", 90)
        ]
        
        for header_text, width in headers:
            ctk.CTkLabel(
                header_frame,
                text=header_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#374151",
                width=width,
                anchor="w"
            ).pack(side="left", padx=(0, 8))

        # Scrollable content
        self.scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.populate_table()

    def populate_table(self):
        # Clear existing content
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        if not self.existing_assignments:
            # No assignments message
            no_data_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            no_data_frame.pack(fill="x", pady=40)
            
            ctk.CTkLabel(
                no_data_frame,
                text="No course assignments found for this section",
                font=ctk.CTkFont(size=14),
                text_color="#6B7280"
            ).pack()
            return
        
        # Display assignments
        for assignment in self.existing_assignments:
            self.create_assignment_row(assignment)

    def create_assignment_row(self, assignment):
        # Determine row color based on schedule status
        has_schedule = assignment.get('has_schedule', False)
        if has_schedule:
            row_fg_color = "#F0FDF4"  # Light green background
            border_color = "#BBF7D0"  # Light green border
        else:
            row_fg_color = "#FEF2F2"  # Light red background
            border_color = "#FECACA"  # Light red border
        
        # Row container with conditional coloring
        row_frame = ctk.CTkFrame(
            self.scroll_frame, 
            fg_color=row_fg_color, 
            corner_radius=4, 
            height=40,
            border_width=1,
            border_color=border_color
        )
        row_frame.pack(fill="x", pady=2, padx=15)
        row_frame.pack_propagate(False)
        
        content_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=8)
        
        # Data columns with proper truncation and widths
        course_name = assignment.get('course_name', '')
        course_code = assignment.get('course_code', '')
        
        # Create course display with truncation
        if course_code:
            course_display = f"{course_name} ({course_code})"
        else:
            course_display = course_name
        
        # Truncate if too long (adjusted for smaller width)
        if len(course_display) > 35:
            course_display = course_display[:32] + "..."
        
        # Truncate faculty name if too long
        faculty_name = assignment.get('faculty_name', '')
        if len(faculty_name) > 22:
            faculty_name = faculty_name[:19] + "..."
        
        data_columns = [
            (course_display, 320),
            (assignment.get('academic_year', ''), 110),
            (assignment.get('semester', ''), 120),
            (assignment.get('room', ''), 90),
            (faculty_name, 180)
        ]
        
        for text, width in data_columns:
            ctk.CTkLabel(
                content_frame,
                text=text,
                font=ctk.CTkFont(size=12),
                text_color="#111827",
                width=width,
                anchor="w"
            ).pack(side="left", padx=(0, 8))
        
        # Schedule Status column
        schedule_status = "✓ Yes" if has_schedule else "✗ No"
        schedule_color = "#059669" if has_schedule else "#DC2626"
        
        ctk.CTkLabel(
            content_frame,
            text=schedule_status,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=schedule_color,
            width=80,
            anchor="w"
        ).pack(side="left", padx=(0, 8))
        
        # Actions dropdown
        action_var = tk.StringVar(value="Actions")
        action_menu = ctk.CTkOptionMenu(
            content_frame,
            values=["Edit", "Delete", "Schedule"],
            variable=action_var,
            width=90,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            command=lambda choice, data=assignment: self.handle_action(choice, data)
        )
        action_menu.pack(side="left")

    def handle_action(self, action, assignment_data):
        if action == "Edit":
            self.edit_assignment(assignment_data)
        elif action == "Delete":
            self.delete_assignment(assignment_data)
        elif action == "Schedule":
            from .schedules_edit import ScheduleEditPopup
            ScheduleEditPopup(self, self.db_manager, assignment_data)

    def add_assignment(self):
        AddAssignmentModal(
            self, 
            self.db_manager, 
            self.section_data, 
            self.courses_data, 
            self.faculty_data, 
            on_success=self.refresh_assignments
        )

    def edit_assignment(self, assignment_data):
        EditAssignmentModal(
            self, 
            self.db_manager, 
            assignment_data, 
            self.courses_data, 
            self.faculty_data, 
            on_success=self.refresh_assignments
        )

    def delete_assignment(self, assignment_data):
        def on_delete():
            try:
                success, message = self.delete_assigned_course(assignment_data['assignment_id'])
                if success:
                    self.after(100, self.refresh_assignments)
                    self.after(200, lambda: SuccessModal(self))
                else:
                    messagebox.showerror("Error", f"Failed to delete assignment: {message}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        DeleteModal(self, on_delete=on_delete)

    def delete_assigned_course(self, assignment_id):
        try:
            from datetime import datetime
            
            conn = self.db_manager.get_connection()
            try:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE assigned_courses 
                    SET isDeleted = 1, updated_at = ?
                    WHERE id = ?
                """, (datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), assignment_id))
                
                conn.commit()
                return True, "Assignment deleted successfully"
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            return False, str(e)

    def refresh_assignments(self):
        """Refresh the assignments table"""
        self.load_existing_assignments()
        self.populate_table()
        
        # Also refresh parent if it has refresh method
        if hasattr(self.parent_view, 'refresh_sections'):
            self.parent_view.after(100, self.parent_view.refresh_sections)
