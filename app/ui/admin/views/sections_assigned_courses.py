import customtkinter as ctk
import tkinter as tk
import re
from tkinter import messagebox
from app.ui.admin.components.modals import SuccessModal

class SectionAssignedCoursesPopup(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, section_data):
        super().__init__(parent)
        self.parent_view = parent
        self.db_manager = db_manager
        self.section_data = section_data
        self.courses_data = []
        self.faculty_data = []
        self.assignment_rows = []
        self.existing_assignments = []
        self.academic_years = []  # Store unique academic years
        self.current_academic_year_filter = None  # Track current filter
        
        self.title(f"Assigned Courses - {section_data.get('name', 'Section')}")
        self.geometry("900x650")  # Optimized size
        self.resizable(True, True)
        self.configure(fg_color="#F8FAFC")
        self.transient(parent)
        self.grab_set()
        
        self.load_data()
        self.load_existing_assignments()
        self.center_window()
        self.setup_ui()
        self.populate_existing_assignments()
        self.setup_academic_year_filter()  # Setup filter UI

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
                    # Try to get program_id from program_name
                    success, programs = self.db_manager.get_programs()
                    if success:
                        program_name = self.section_data.get('program_name', '')
                        for program in programs:
                            if program.get('name') == program_name:
                                program_id = program.get('id')
                                break
                
                if program_id:
                    success, courses = self.db_manager.get_courses_by_program_id(program_id)
                    if success:
                        self.courses_data = courses
                    else:
                        print(f"Error loading courses: {courses}")
                        self.courses_data = []
                else:
                    print("Could not determine program ID for section")
                    self.courses_data = []
                
                # Load all faculty
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

    def load_existing_assignments(self):
        """Load existing course assignments for this section"""
        try:
            if self.db_manager:
                section_id = self.section_data['id']
                success, assignments = self.db_manager.get_section_courses(section_id)
                if success:
                    self.existing_assignments = assignments
                else:
                    print(f"Error loading existing assignments: {assignments}")
                    self.existing_assignments = []
        except Exception as e:
            print(f"Error loading existing assignments: {e}")
            self.existing_assignments = []

    def setup_ui(self):
        # Main container - clean white background
        main_container = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0)
        main_container.pack(fill="both", expand=True)
        
        # Minimal header section
        header_section = ctk.CTkFrame(main_container, fg_color="#FAFAFA", corner_radius=0, height=60)
        header_section.pack(fill="x", padx=0, pady=0)
        header_section.pack_propagate(False)
        
        # Header content - centered and balanced
        header_content = ctk.CTkFrame(header_section, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=24, pady=16)
        
        # Title - clean typography
        ctk.CTkLabel(
            header_content,
            text="Course Assignments",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#1F2937",
        ).pack(side="left", anchor="w")
        
        # Section info - subtle and aligned
        section_info = f"{self.section_data.get('name', 'Unknown')} • {self.section_data.get('program_name', 'Unknown Program')}"
        ctk.CTkLabel(
            header_content,
            text=section_info,
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="#6B7280",
        ).pack(side="right", anchor="e")

        # Content area - minimal padding
        content_area = ctk.CTkFrame(main_container, fg_color="transparent")
        content_area.pack(fill="both", expand=True, padx=24, pady=16)
        
        # Table container - subtle border
        table_container = ctk.CTkFrame(content_area, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB")
        table_container.pack(fill="both", expand=True, pady=(0, 12))
        
        # Table header - fixed positioning instead of grid
        table_header = ctk.CTkFrame(table_container, fg_color="#F9FAFB", corner_radius=0, height=40)
        table_header.pack(fill="x", padx=0, pady=0)
        table_header.pack_propagate(False)
        
        # Header labels with fixed positioning - perfectly aligned
        header_frame = ctk.CTkFrame(table_header, fg_color="transparent")
        header_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Course header (25% width - further decreased)
        course_header = ctk.CTkLabel(
            header_frame,
            text="Course",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#374151",
            width=220,
            anchor="w"
        )
        course_header.pack(side="left", padx=(0, 4))
        
        # Academic Year header (12% width)
        year_header = ctk.CTkLabel(
            header_frame,
            text="Academic Year",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#374151",
            width=100,
            anchor="center"
        )
        year_header.pack(side="left", padx=2)
        
        # Semester header (15% width - increased)
        semester_header = ctk.CTkLabel(
            header_frame,
            text="Semester",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#374151",
            width=130,
            anchor="center"
        )
        semester_header.pack(side="left", padx=2)
        
        # Room header (10% width)
        room_header = ctk.CTkLabel(
            header_frame,
            text="Room",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#374151",
            width=90,
            anchor="center"
        )
        room_header.pack(side="left", padx=2)

        # Faculty header (18% width)
        faculty_header = ctk.CTkLabel(
            header_frame,
            text="Faculty",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#374151",
            width=150,
            anchor="center"
        )
        faculty_header.pack(side="left", padx=2)
        
        # Remove header (8% width)
        remove_header = ctk.CTkLabel(
            header_frame,
            text="Remove",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#374151",
            width=60,
            anchor="center"
        )
        remove_header.pack(side="left", padx=(4, 0))

        # Scrollable content area - clean
        self.scroll_frame = ctk.CTkScrollableFrame(
            table_container,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#E5E7EB",
            scrollbar_button_hover_color="#D1D5DB"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Add button - minimal and centered
        add_button_frame = ctk.CTkFrame(content_area, fg_color="transparent")
        add_button_frame.pack(fill="x", pady=(0, 12))
        
        add_btn = ctk.CTkButton(
            add_button_frame,
            text="+ Add Assignment",
            width=140,
            height=32,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="normal"),
            corner_radius=6,
            command=self.add_assignment_row
        )
        add_btn.pack(side="left")

        # Action bar - minimal and clean
        action_bar = ctk.CTkFrame(main_container, fg_color="#F9FAFB", corner_radius=0, height=56)
        action_bar.pack(side="bottom", fill="x", padx=0, pady=0)
        action_bar.pack_propagate(False)
        
        # Action buttons - perfectly centered and spaced
        button_container = ctk.CTkFrame(action_bar, fg_color="transparent")
        button_container.pack(expand=True, fill="both", padx=24, pady=12)
        
        cancel_btn = ctk.CTkButton(
            button_container,
            text="Cancel",
            fg_color="#F3F4F6",
            text_color="#374151",
            hover_color="#E5E7EB",
            width=100,
            height=32,
            font=ctk.CTkFont(size=12, weight="normal"),
            corner_radius=6,
            command=self.destroy
        )
        cancel_btn.pack(side="left")
        
        save_btn = ctk.CTkButton(
            button_container,
            text="Save Changes",
            fg_color="#059669",
            hover_color="#047857",
            text_color="#FFFFFF",
            width=120,
            height=32,
            font=ctk.CTkFont(size=12, weight="normal"),
            corner_radius=6,
            command=self.save_assignments
        )
        save_btn.pack(side="right")

    def populate_existing_assignments(self):
        """Populate the form with existing course assignments"""
        if not self.existing_assignments:
            # If no existing assignments, add one empty row
            self.add_assignment_row()
            return
        
        # Add a row for each existing assignment
        for assignment in self.existing_assignments:
            self.add_assignment_row(assignment)

    def create_course_mapping(self):
        """Create mapping between course full names and course data"""
        course_mapping = {}
        course_options = []
        
        for course in self.courses_data:
            code = course.get('code', '')
            name = course.get('name', '')
            
            if code and name:
                # Store full name with code for dropdown options
                display_name = f"{name} ({code})"
                course_options.append(display_name)
                # Map display name to full course data
                course_mapping[display_name] = {
                    'display_name': display_name,
                    'course_data': course
                }
                # Also map the course name alone for backward compatibility
                course_mapping[name] = {
                    'display_name': display_name,
                    'course_data': course
                }
            elif name:
                # Fallback if no code
                course_options.append(name)
                course_mapping[name] = {
                    'display_name': name,
                    'course_data': course
                }
        
        return course_mapping, course_options

    def create_faculty_mapping(self):
        """Create mapping for faculty - use full names throughout"""
        faculty_mapping = {}
        faculty_options = []
        
        for faculty in self.faculty_data:
            first_name = faculty.get('first_name', '')
            last_name = faculty.get('last_name', '')
            
            if first_name and last_name:
                full_name = f"{first_name} {last_name}"
                
                # Store full name for dropdown options
                faculty_options.append(full_name)
                # Map full name to faculty data
                faculty_mapping[full_name] = {
                    'full_name': full_name,
                    'faculty_data': faculty
                }
        
        return faculty_mapping, faculty_options

    def add_assignment_row(self, existing_assignment=None):
        """Add a new course assignment row with perfect alignment"""
        # Row container - clean and minimal
        row_card = ctk.CTkFrame(self.scroll_frame, fg_color="#FFFFFF", corner_radius=0, 
                               border_width=0, height=44)
        row_card.pack(fill="x", pady=1, padx=0)
        row_card.pack_propagate(False)
        
        # Add subtle separator line
        separator = ctk.CTkFrame(row_card, fg_color="#F3F4F6", height=1)
        separator.pack(fill="x", side="bottom")
        
        # Main content frame with fixed positioning
        content_frame = ctk.CTkFrame(row_card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=8, pady=6)
        
        # Create mappings
        course_mapping, course_options = self.create_course_mapping()
        faculty_mapping, faculty_options = self.create_faculty_mapping()
        
        if not course_options:
            course_options = ["No courses available"]
        if not faculty_options:
            faculty_options = ["No faculty available"]

        # Course dropdown - matches header width
        course_var = ctk.StringVar(value="Select course")
        
        # Store the actual selected value (not truncated)
        actual_course_value = ctk.StringVar(value="Select course")
        
        if existing_assignment:
            existing_name = existing_assignment.get('course_name', '')
            existing_code = existing_assignment.get('course_code', '')
            
            for display_name, mapping in course_mapping.items():
                course_data = mapping['course_data']
                if (course_data.get('name') == existing_name and 
                    course_data.get('code') == existing_code):  # Fixed: was existingCode
                    course_var.set(display_name)
                    actual_course_value.set(display_name)
                    break
        
        def on_course_select(selection):
            # Store the actual selection
            actual_course_value.set(selection)
            # Display truncated version if needed
            if len(selection) > 30:
                truncated = selection[:27] + "..."
                course_var.set(truncated)
            else:
                course_var.set(selection)
        
        course_menu = ctk.CTkOptionMenu(
            content_frame,
            variable=course_var,
            values=course_options,
            height=32,
            width=220,
            fg_color="#FFFFFF",
            text_color="#374151",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            dropdown_fg_color="#FFFFFF",
            dropdown_hover_color="#F9FAFB",
            dropdown_text_color="#374151",
            font=ctk.CTkFont(size=11),
            corner_radius=4,
            command=on_course_select
        )
        course_menu.pack(side="left", padx=(0, 4))

        # Academic Year entry - matches header width
        academic_year_var = ctk.StringVar()
        if existing_assignment:
            academic_year_var.set(existing_assignment.get('academic_year', ''))
        
        academic_year_entry = ctk.CTkEntry(
            content_frame,
            textvariable=academic_year_var,
            placeholder_text="2024-2025",
            height=32,
            width=100,
            fg_color="#FFFFFF",
            text_color="#374151",
            border_color="#E5E7EB",
            border_width=1,
            font=ctk.CTkFont(size=11),
            corner_radius=4,
            justify="center"
        )
        academic_year_entry.pack(side="left", padx=2)

        # Semester dropdown - matches header width (increased)
        semester_var = ctk.StringVar(value="Select")
        if existing_assignment:
            semester = existing_assignment.get('semester', '')
            semester_var.set(semester if semester else "Select")
        
        semester_options = ["1st Semester", "2nd Semester", "3rd Semester", "Summer"]
        semester_menu = ctk.CTkOptionMenu(
            content_frame,
            variable=semester_var,
            values=semester_options,
            height=32,
            width=130,
            fg_color="#FFFFFF",
            text_color="#374151",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            dropdown_fg_color="#FFFFFF",
            dropdown_hover_color="#F9FAFB",
            dropdown_text_color="#374151",
            font=ctk.CTkFont(size=11),
            corner_radius=4
        )
        semester_menu.pack(side="left", padx=2)

        # Room entry - matches header width
        room_var = ctk.StringVar()
        if existing_assignment:
            room_var.set(existing_assignment.get('room', ''))
        
        room_entry = ctk.CTkEntry(
            content_frame,
            textvariable=room_var,
            placeholder_text="Room",
            height=32,
            width=90,
            fg_color="#FFFFFF",
            text_color="#374151",
            border_color="#E5E7EB",
            border_width=1,
            font=ctk.CTkFont(size=11),
            corner_radius=4,
            justify="center"
        )
        room_entry.pack(side="left", padx=2)

        # Faculty dropdown - matches header width
        faculty_var = ctk.StringVar(value="Select faculty")
        
        if existing_assignment:
            existing_faculty = existing_assignment.get('faculty_name', '')
            if existing_faculty in faculty_mapping:
                faculty_var.set(existing_faculty)
        
        def on_faculty_select(selection):
            faculty_var.set(selection)
        
        faculty_menu = ctk.CTkOptionMenu(
            content_frame,
            variable=faculty_var,
            values=faculty_options,
            height=32,
            width=150,
            fg_color="#FFFFFF",
            text_color="#374151",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            dropdown_fg_color="#FFFFFF",
            dropdown_hover_color="#F9FAFB",
            dropdown_text_color="#374151",
            font=ctk.CTkFont(size=11),
            corner_radius=4,
            command=on_faculty_select
        )
        faculty_menu.pack(side="left", padx=2)

        # Remove button - enhanced X icon
        remove_btn = ctk.CTkButton(
            content_frame,
            text="✕",
            width=32,
            height=28,
            fg_color="#F87171",
            hover_color="#DC2626",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=4,
            border_width=0,
            command=lambda: self.remove_assignment_row(row_card)
        )
        remove_btn.pack(side="left", padx=(4, 0))

        # Store row data with actual course value
        row_data = {
            'frame': row_card,
            'course_var': actual_course_value,  # Use actual value, not display value
            'academic_year_entry': academic_year_entry,
            'semester_var': semester_var,
            'room_entry': room_entry,
            'faculty_var': faculty_var,
            'assignment_id': existing_assignment.get('assignment_id') if existing_assignment else None,
            'course_mapping': course_mapping,
            'faculty_mapping': faculty_mapping
        }
        self.assignment_rows.append(row_data)

    def remove_assignment_row(self, row_frame):
        """Remove a course assignment row with animation"""
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
        """Validate all assignment rows using mappings"""
        assignments = []
        seen_courses = set()
        filled_rows = 0

        for i, row_data in enumerate(self.assignment_rows):
            # Get values from widgets - use actual course value
            course_display_name = row_data['course_var'].get()
            academic_year = row_data['academic_year_entry'].get().strip()
            semester = row_data['semester_var'].get()
            room = row_data['room_entry'].get().strip()
            faculty_name = row_data['faculty_var'].get()

            # Check if row has any filled data
            row_has_data = (
                course_display_name not in ["Select", "Select course", "No courses available"] or
                academic_year or
                semester != "Select" or
                room or
                faculty_name not in ["Select", "Select faculty", "No faculty available"]
            )

            # Skip completely empty rows
            if not row_has_data:
                continue

            filled_rows += 1

            # Validate course selection
            if course_display_name in ["Select", "Select course", "No courses available"]:
                messagebox.showerror("Error", f"Please select a course for row {i+1}")
                return False

            # Check if course exists in mapping - be more flexible
            course_mapping = row_data['course_mapping']
            course_found = False
            selected_course_data = None
            
            # First try exact match
            if course_display_name in course_mapping:
                course_found = True
                selected_course_data = course_mapping[course_display_name]
            else:
                # Try to find by partial match (in case of truncation)
                for mapped_name, mapped_data in course_mapping.items():
                    if course_display_name in mapped_name or mapped_name in course_display_name:
                        course_found = True
                        selected_course_data = mapped_data
                        break
            
            if not course_found:
                messagebox.showerror("Error", f"Selected course is not valid for row {i+1}")
                return False

            # Check for duplicate courses using course ID instead of display name
            course_id = selected_course_data['course_data']['id']
            if course_id in seen_courses:
                messagebox.showerror("Error", f"Course '{course_display_name}' is assigned multiple times")
                return False
            seen_courses.add(course_id)

            # Validate academic year
            if not academic_year:
                messagebox.showerror("Error", f"Academic year is required for row {i+1}")
                return False
            
            # Validate academic year format
            import re
            if not re.match(r'^\d{4}-\d{4}$', academic_year):
                messagebox.showerror("Error", f"Academic year format should be YYYY-YYYY (e.g., 2024-2025) for row {i+1}")
                return False

            # Validate semester
            if semester == "Select":
                messagebox.showerror("Error", f"Please select a semester for row {i+1}")
                return False

            # Validate faculty
            if faculty_name in ["Select", "Select faculty", "No faculty available"]:
                messagebox.showerror("Error", f"Please select a faculty for row {i+1}")
                return False

            # Check if faculty exists in mapping
            faculty_mapping = row_data['faculty_mapping']
            if faculty_name not in faculty_mapping:
                messagebox.showerror("Error", f"Selected faculty is not valid for row {i+1}")
                return False

            # Get faculty ID using mapping
            faculty_id = faculty_mapping[faculty_name]['faculty_data']['id']

            if not course_id or not faculty_id:
                messagebox.showerror("Error", f"Invalid course or faculty selection for row {i+1}")
                return False

            assignments.append({
                'course_id': course_id,
                'faculty_id': faculty_id,
                'academic_year': academic_year,
                'semester': semester,
                'room': room if room else None,
                'assignment_id': row_data.get('assignment_id')
            })

        # Check if there are any filled rows
        if filled_rows == 0:
            messagebox.showerror("Error", "Please add at least one course assignment before saving")
            return False

        return assignments

    def save_assignments(self):
        """Save the course assignments with enhanced UX"""
        try:
            # Validate assignments - this will return False if validation fails
            assignments = self.validate_assignments()
            if assignments is False:
                return

            # Additional check for empty assignments list
            if not assignments:
                messagebox.showerror("Error", "No valid assignments to save")
                return

            if not self.db_manager:
                messagebox.showerror("Error", "Database connection not available")
                return

            # Process assignments one by one to avoid database locks
            assignment_errors = []
            created_assignments = []

            for assignment in assignments:
                assignment_data = {
                    'faculty_id': assignment['faculty_id'],
                    'course_id': assignment['course_id'],
                    'section_id': self.section_data['id'],
                    'academic_year': assignment['academic_year'],
                    'semester': assignment['semester'],
                    'room': assignment['room']
                }

                # Create assigned course entry using individual connections
                success, result = self.create_assigned_course(assignment_data)
                if success:
                    created_assignments.append(result)
                else:
                    assignment_errors.append(result)

            if assignment_errors:
                error_message = "Some course assignments failed:\n" + "\n".join(assignment_errors)
                messagebox.showwarning("Partial Success", error_message)
            else:
                # Close popup and refresh parent
                self.destroy()
                if hasattr(self.parent_view, 'refresh_sections'):
                    self.parent_view.after(100, lambda: self.parent_view.refresh_sections())
                self.parent_view.after(200, lambda: SuccessModal(self.parent_view))

        except Exception as e:
            print(f"Error saving assignments: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def create_assigned_course(self, assignment_data):
        """Create an assigned course entry with proper connection management"""
        try:
            from datetime import datetime
            
            # Use a single connection for this operation
            conn = self.db_manager.get_connection()
            try:
                cursor = conn.cursor()
                
                # First, delete any existing assignment for this course and section
                cursor.execute("""
                    UPDATE assigned_courses 
                    SET isDeleted = 1, updated_at = ?
                    WHERE course_id = ? AND section_id = ? AND isDeleted = 0
                """, (
                    datetime.now().isoformat(),
                    assignment_data['course_id'],
                    assignment_data['section_id']
                ))
                
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
                    0,  # isDeleted = 0
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                assignment_id = cursor.lastrowid
                
                return True, {"id": assignment_id, "message": "Course assigned successfully"}
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
            
        except Exception as e:
            print(f"Error creating assigned course: {e}")
            return False, str(e)

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

    def setup_academic_year_filter(self):
        """Setup the academic year filter UI"""
        filter_frame = ctk.CTkFrame(self.parent_view, fg_color="transparent")
        filter_frame.pack(fill="x", padx=24, pady=(16, 0))
        
        # Filter label
        ctk.CTkLabel(
            filter_frame,
            text="Filter by Academic Year:",
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="#374151",
        ).pack(side="left", padx=(0, 8))
        
        # Filter variable
        self.academic_year_filter_var = ctk.StringVar(value="All")
        
        # Academic year options - include "All" option
        academic_year_options = ["All"] + self.get_unique_academic_years()
        
        # Academic year filter menu
        academic_year_menu = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.academic_year_filter_var,
            values=academic_year_options,
            height=32,
            width=180,
            fg_color="#FFFFFF",
            text_color="#374151",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            dropdown_fg_color="#FFFFFF",
            dropdown_hover_color="#F9FAFB",
            dropdown_text_color="#374151",
            font=ctk.CTkFont(size=11),
            corner_radius=4,
            command=self.apply_academic_year_filter
        )
        academic_year_menu.pack(side="left", padx=2)

    def apply_academic_year_filter(self, selected_year=None):
        """Apply academic year filter to existing assignments"""
        if selected_year is None:
            selected_year = self.academic_year_filter_var.get()
        
        self.current_academic_year_filter = selected_year
        
        # Clear existing rows
        for row_data in self.assignment_rows:
            row_data['frame'].destroy()
        self.assignment_rows.clear()
        
        # Filter existing assignments based on academic year
        if selected_year == "All":
            filtered_assignments = self.existing_assignments
        else:
            filtered_assignments = [
                assignment for assignment in self.existing_assignments
                if assignment.get('academic_year') == selected_year
            ]
        
        # Repopulate with filtered assignments
        if filtered_assignments:
            for assignment in filtered_assignments:
                self.add_assignment_row(assignment)
        else:
            # If no assignments match filter, add one empty row
            self.add_assignment_row()
