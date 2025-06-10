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
        self.current_academic_year_filter = "All"
        self.assignments_data = []
        self.filtered_assignments = []
        
        self.title(f"Assigned Courses - {section_data.get('name', 'Section')}")
        self.geometry("1200x700")
        self.resizable(True, True)
        self.configure(fg_color="#F8FAFC")
        self.transient(parent)
        self.grab_set()
        
        self.center_window()
        self.setup_ui()
        self.load_assignments()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def get_unique_academic_years(self):
        """Get unique academic years from database for this section"""
        try:
            if self.db_manager:
                success, academic_years = self.db_manager.get_available_academic_years_for_section(self.section_data['id'])
                if success and academic_years:
                    return academic_years
                else:
                    from datetime import datetime
                    current_year = datetime.now().year
                    return [f"{current_year}-{current_year + 1}"]
            else:
                from datetime import datetime
                current_year = datetime.now().year
                return [f"{current_year}-{current_year + 1}"]
        except Exception as e:
            print(f"Error getting academic years: {e}")
            from datetime import datetime
            current_year = datetime.now().year
            return [f"{current_year}-{current_year + 1}"]

    def apply_academic_year_filter(self, selected_year=None):
        """Apply academic year filter to assignments"""
        if selected_year is None:
            selected_year = self.academic_year_filter_var.get()
        
        self.current_academic_year_filter = selected_year
        
        # Filter assignments based on academic year
        if selected_year == "All":
            self.filtered_assignments = self.assignments_data.copy()
        else:
            self.filtered_assignments = [
                assignment for assignment in self.assignments_data
                if assignment.get('academic_year') == selected_year
            ]
        
        # Refresh the table display
        self.refresh_assignments_table()

    def setup_ui(self):
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0)
        main_container.pack(fill="both", expand=True)
        
        # Header section with filter
        header_section = ctk.CTkFrame(main_container, fg_color="#FAFAFA", corner_radius=0, height=120)
        header_section.pack(fill="x", padx=0, pady=0)
        header_section.pack_propagate(False)
        
        # Header content
        header_content = ctk.CTkFrame(header_section, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=24, pady=16)
        
        # Top row - Title and section info
        top_row = ctk.CTkFrame(header_content, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 12))
        
        # Title
        ctk.CTkLabel(
            top_row,
            text="Course Assignments",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#1F2937",
        ).pack(side="left", anchor="w")
        
        # Section info
        section_info = f"{self.section_data.get('name', 'Unknown')} • {self.section_data.get('program_name', 'Unknown Program')}"
        ctk.CTkLabel(
            top_row,
            text=section_info,
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="#6B7280",
        ).pack(side="right", anchor="e")
        
        # Filter row
        filter_row = ctk.CTkFrame(header_content, fg_color="transparent")
        filter_row.pack(fill="x", pady=(0, 12))
        
        # Filter controls (left side)
        filter_frame = ctk.CTkFrame(filter_row, fg_color="transparent")
        filter_frame.pack(side="left")
        
        # Filter label
        ctk.CTkLabel(
            filter_frame,
            text="Filter by Academic Year:",
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="#6B7280",
        ).pack(side="left", padx=(0, 8))
        
        # Academic year filter dropdown
        academic_years = self.get_unique_academic_years()
        filter_options = ["All"] + academic_years
        
        self.academic_year_filter_var = ctk.StringVar(value="All")
        
        self.academic_year_filter_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.academic_year_filter_var,
            values=filter_options,
            height=32,
            width=140,
            fg_color="#FFFFFF",
            text_color="#374151",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            dropdown_fg_color="#FFFFFF",
            dropdown_hover_color="#F9FAFB",
            dropdown_text_color="#374151",
            font=ctk.CTkFont(size=12),
            corner_radius=6,
            command=self.apply_academic_year_filter
        )
        self.academic_year_filter_dropdown.pack(side="left", padx=(0, 12))
        
        # Clear filter button
        clear_filter_btn = ctk.CTkButton(
            filter_frame,
            text="Clear",
            width=60,
            height=32,
            fg_color="#F3F4F6",
            text_color="#6B7280",
            hover_color="#E5E7EB",
            font=ctk.CTkFont(size=11),
            corner_radius=6,
            command=lambda: self.apply_academic_year_filter("All")
        )
        clear_filter_btn.pack(side="left")
        
        # Add new course button (right side)
        add_course_btn = ctk.CTkButton(
            filter_row,
            text="Assign New Course",
            width=140,
            height=32,
            fg_color="#22C55E",
            hover_color="#16A34A",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="normal"),
            corner_radius=6,
            command=self.assign_new_course
        )
        add_course_btn.pack(side="right")

        # Content area
        content_area = ctk.CTkFrame(main_container, fg_color="transparent")
        content_area.pack(fill="both", expand=True, padx=24, pady=16)
        
        # Table container
        self.table_container = ctk.CTkFrame(content_area, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB")
        self.table_container.pack(fill="both", expand=True)
        
        self.setup_table_headers()

    def setup_table_headers(self):
        """Setup table headers"""
        # Header frame
        header_frame = ctk.CTkFrame(self.table_container, fg_color="#F9FAFB", corner_radius=0, height=40)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Configure columns
        columns = ["Course", "Academic Year", "Semester", "Room", "Faculty", "Schedule", "Actions"]
        col_widths = [250, 120, 120, 100, 150, 80, 120]
        
        # Create header labels
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=8, pady=8)
        
        for i, (col, width) in enumerate(zip(columns, col_widths)):
            ctk.CTkLabel(
                header_content,
                text=col,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#374151",
                width=width,
                anchor="w" if i == 0 else "center"
            ).pack(side="left", padx=2)

        # Scrollable content area
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.table_container,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#E5E7EB",
            scrollbar_button_hover_color="#D1D5DB"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def load_assignments(self):
        """Load course assignments from database"""
        try:
            if self.db_manager:
                section_id = self.section_data['id']
                success, assignments = self.db_manager.get_section_courses(section_id)
                if success:
                    self.assignments_data = assignments
                    self.filtered_assignments = assignments.copy()
                    self.refresh_assignments_table()
                else:
                    print(f"Error loading assignments: {assignments}")
                    self.assignments_data = []
                    self.filtered_assignments = []
        except Exception as e:
            print(f"Error loading assignments: {e}")
            self.assignments_data = []
            self.filtered_assignments = []

    def refresh_assignments_table(self):
        """Refresh the assignments table"""
        # Clear existing content
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        if not self.filtered_assignments:
            # Show no data message
            no_data_label = ctk.CTkLabel(
                self.scroll_frame,
                text="No course assignments found for the selected filter.",
                font=ctk.CTkFont(size=14),
                text_color="#6B7280"
            )
            no_data_label.pack(pady=40)
            return
        
        # Populate with filtered data
        for assignment in self.filtered_assignments:
            self.create_assignment_row(assignment)

    def create_assignment_row(self, assignment):
        """Create a row for an assignment"""
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#FFFFFF", corner_radius=0, height=44)
        row_frame.pack(fill="x", pady=1, padx=0)
        row_frame.pack_propagate(False)
        
        # Add separator
        separator = ctk.CTkFrame(row_frame, fg_color="#F3F4F6", height=1)
        separator.pack(fill="x", side="bottom")
        
        # Content frame
        content_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=8, pady=6)
        
        col_widths = [250, 120, 120, 100, 150, 80, 120]
        
        # Course name
        course_display = f"{assignment.get('course_name', 'Unknown')} ({assignment.get('course_code', 'N/A')})"
        course_label = ctk.CTkLabel(
            content_frame,
            text=course_display,
            font=ctk.CTkFont(size=11),
            text_color="#374151",
            width=col_widths[0],
            anchor="w"
        )
        course_label.pack(side="left", padx=2)
        
        # Academic Year
        academic_year_label = ctk.CTkLabel(
            content_frame,
            text=assignment.get('academic_year', 'N/A'),
            font=ctk.CTkFont(size=11),
            text_color="#374151",
            width=col_widths[1],
            anchor="center"
        )
        academic_year_label.pack(side="left", padx=2)
        
        # Semester
        semester_label = ctk.CTkLabel(
            content_frame,
            text=assignment.get('semester', 'N/A'),
            font=ctk.CTkFont(size=11),
            text_color="#374151",
            width=col_widths[2],
            anchor="center"
        )
        semester_label.pack(side="left", padx=2)
        
        # Room
        room_label = ctk.CTkLabel(
            content_frame,
            text=assignment.get('room', 'N/A'),
            font=ctk.CTkFont(size=11),
            text_color="#374151",
            width=col_widths[3],
            anchor="center"
        )
        room_label.pack(side="left", padx=2)
        
        # Faculty
        faculty_label = ctk.CTkLabel(
            content_frame,
            text=assignment.get('faculty_name', 'No Faculty Assigned'),
            font=ctk.CTkFont(size=11),
            text_color="#374151",
            width=col_widths[4],
            anchor="center"
        )
        faculty_label.pack(side="left", padx=2)
        
        # Schedule status
        has_schedule = assignment.get('has_schedule', False)
        schedule_text = "✓ Yes" if has_schedule else "✗ No"
        schedule_color = "#22C55E" if has_schedule else "#EF4444"
        
        schedule_label = ctk.CTkLabel(
            content_frame,
            text=schedule_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=schedule_color,
            width=col_widths[5],
            anchor="center"
        )
        schedule_label.pack(side="left", padx=2)
        
        # Actions dropdown
        action_var = tk.StringVar(value="Actions")
        actions = ["Edit", "Delete", "View Students"]
        action_menu = ctk.CTkOptionMenu(
            content_frame,
            values=actions,
            variable=action_var,
            width=col_widths[6],
            height=28,
            font=ctk.CTkFont(size=10),
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            command=lambda choice, data=assignment: self.handle_assignment_action(choice, data)
        )
        action_menu.pack(side="left", padx=2)

    def handle_assignment_action(self, action, assignment_data):
        """Handle assignment action selection"""
        if action == "Edit":
            self.edit_assignment(assignment_data)
        elif action == "Delete":
            self.delete_assignment(assignment_data)
        elif action == "View Students":
            from .sections_course_students_view import CourseStudentsViewModal
            CourseStudentsViewModal(self, self.db_manager, assignment_data, self.section_data)

    def edit_assignment(self, assignment_data):
        """Edit an assignment"""
        messagebox.showinfo("Edit", f"Edit functionality for {assignment_data.get('course_name')} will be implemented.")

    def delete_assignment(self, assignment_data):
        """Delete an assignment"""
        messagebox.showinfo("Delete", f"Delete functionality for {assignment_data.get('course_name')} will be implemented.")

    def assign_new_course(self):
        """Open popup to assign new course"""
        from .sections_assigned_courses import SectionAssignedCoursesPopup
        SectionAssignedCoursesPopup(self, self.db_manager, self.section_data)
