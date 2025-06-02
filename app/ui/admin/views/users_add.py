import customtkinter as ctk
import sqlite3
import bcrypt
import base64
import re
import winsound
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk
from app.db_manager import DatabaseManager
from .users_add_camera import IndependentFacialRecognitionWindow

class UsersAddModal(ctk.CTkToplevel):
    def __init__(self, parent, user_type="student"):
        super().__init__(parent)
        self.parent_view = parent
        self.user_type = user_type
        self.db_manager = DatabaseManager()
        
        # Face verification variables
        self.face_image = None
        self.face_image_data = None
        
        # Animation variables
        self.shake_animation_running = False
        self.original_card_x = None
        
        # Setup modal
        self.title(f"Add {user_type.title()}")
        self.geometry("520x700")
        self.resizable(False, False)
        self.configure(fg_color="#fff")
        self.transient(parent)
        self.grab_set()
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create form based on user type
        if user_type == "student":
            self.create_student_form()
        else:
            self.create_faculty_form()

    def create_student_form(self):
        """Create form for adding a student"""
        # Load dropdown options from backend
        self.load_dropdown_options()
        
        # Header
        header_container = ctk.CTkFrame(self, fg_color="transparent")
        header_container.place(x=40, y=15)
        
        # Title
        title_frame = ctk.CTkFrame(header_container, fg_color="transparent")
        title_frame.pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Add New ",
            font=ctk.CTkFont("Inter", 20, "bold"),
            text_color="#000000"
        ).pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="Student",
            font=ctk.CTkFont("Inter", 20, "bold"),
            text_color="#1E3A8A"
        ).pack(side="left")
        
        # Divider
        divider = ctk.CTkFrame(
            header_container,
            fg_color="#1E3A8A",
            width=180,
            height=2
        )
        divider.pack(anchor="w", pady=(5, 0))
        
        # Card Frame
        self.card_frame = ctk.CTkFrame(
            self,
            width=440,
            height=620,
            corner_radius=12,
            fg_color="#ffffff",
            border_width=1,
            border_color="#d1d1d1"
        )
        self.card_frame.place(x=40, y=70)
        self.card_frame.pack_propagate(False)
        
        # Store original position for shake animation
        self.original_card_x = 40

        # Create two columns
        left_column = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        left_column.place(x=15, y=15)
        
        right_column = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        right_column.place(x=225, y=15)
        
        # First Name (Left Column)
        ctk.CTkLabel(
            left_column,
            text="First Name",
            font=ctk.CTkFont("Inter", 11),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.first_name_entry = ctk.CTkEntry(
            left_column,
            width=190,
            height=26,
            corner_radius=5,
            border_width=1,
            font=ctk.CTkFont("Inter", 11),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000"
        )
        self.first_name_entry.pack(pady=(2, 10))
        
        # Last Name (Right Column)
        ctk.CTkLabel(
            right_column,
            text="Last Name",
            font=ctk.CTkFont("Inter", 11),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.last_name_entry = ctk.CTkEntry(
            right_column,
            width=190,
            height=26,
            corner_radius=5,
            border_width=1,
            font=ctk.CTkFont("Inter", 11),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000"
        )
        self.last_name_entry.pack(pady=(2, 10))
        
        # Date of Birth Row
        dob_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        dob_container.place(x=15, y=75)
        
        ctk.CTkLabel(
            dob_container,
            text="Date of Birth",
            font=ctk.CTkFont("Inter", 11),
            text_color="#707070"
        ).pack(anchor="w")
        
        # Date Input Fields Container
        date_fields = ctk.CTkFrame(dob_container, fg_color="transparent")
        date_fields.pack(pady=(2, 0))
        
        # Month Dropdown
        month_container = ctk.CTkFrame(
            date_fields,
            width=130,
            height=28,
            corner_radius=5,
            fg_color="#ffffff",
            border_width=1,
            border_color="#d1d1d1"
        )
        month_container.pack(side="left", padx=(0, 8))
        month_container.pack_propagate(False)
        
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        self.month_dropdown = ctk.CTkOptionMenu(
            month_container,
            width=128,
            height=26,
            corner_radius=5,
            font=ctk.CTkFont("Inter", 10),
            fg_color="#ffffff",
            button_color="#ffffff",
            button_hover_color="#f5f5f5",
            text_color="#000000",
            dropdown_fg_color="#ffffff",
            dropdown_text_color="#000000",
            dropdown_hover_color="#f5f5f5",
            values=month_names,
            command=self._on_month_year_change
        )
        self.month_dropdown.place(x=1, y=1)
        self.month_dropdown.set("January")
        
        # Day Dropdown
        day_container = ctk.CTkFrame(
            date_fields,
            width=80,
            height=28,
            corner_radius=5,
            fg_color="#ffffff",
            border_width=1,
            border_color="#d1d1d1"
        )
        day_container.pack(side="left", padx=(0, 8))
        day_container.pack_propagate(False)
        
        self.day_dropdown = ctk.CTkOptionMenu(
            day_container,
            width=78,
            height=26,
            corner_radius=5,
            font=ctk.CTkFont("Inter", 10),
            fg_color="#ffffff",
            button_color="#ffffff",
            button_hover_color="#f5f5f5",
            text_color="#000000",
            dropdown_fg_color="#ffffff",
            dropdown_text_color="#000000",
            dropdown_hover_color="#f5f5f5",
            values=["01"]
        )
        self.day_dropdown.place(x=1, y=1)
        
        # Year Dropdown
        year_container = ctk.CTkFrame(
            date_fields,
            width=100,
            height=28,
            corner_radius=5,
            fg_color="#ffffff",
            border_width=1,
            border_color="#d1d1d1"
        )
        year_container.pack(side="left")
        year_container.pack_propagate(False)
        
        current_year = datetime.now().year
        min_age = 16
        max_birth_year = current_year - min_age
        min_birth_year = current_year - 80
        
        year_values = [str(i) for i in range(min_birth_year, max_birth_year + 1)]
        
        self.year_dropdown = ctk.CTkOptionMenu(
            year_container,
            width=98,
            height=26,
            corner_radius=5,
            font=ctk.CTkFont("Inter", 10),
            fg_color="#ffffff",
            button_color="#ffffff",
            button_hover_color="#f5f5f5",
            text_color="#000000",
            dropdown_fg_color="#ffffff",
            dropdown_text_color="#000000",
            dropdown_hover_color="#f5f5f5",
            values=year_values,
            command=self._on_month_year_change,
            dynamic_resizing=False
        )
        self.year_dropdown.place(x=1, y=1)
        self.year_dropdown.set("2001")
        
        # Initialize days
        self._update_days()

        # Contact Number
        contact_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        contact_container.place(x=15, y=135)
        
        ctk.CTkLabel(
            contact_container,
            text="Contact Number",
            font=ctk.CTkFont("Inter", 11),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.contact_entry = ctk.CTkEntry(
            contact_container,
            width=190,
            height=26,
            corner_radius=5,
            border_width=1,
            font=ctk.CTkFont("Inter", 11),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000"
        )
        self.contact_entry.pack(pady=(2, 0))

        # Student Number
        student_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        student_container.place(x=15, y=185)
        
        ctk.CTkLabel(
            student_container,
            text="Student Number",
            font=ctk.CTkFont("Inter", 11),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.student_entry = ctk.CTkEntry(
            student_container,
            width=405,
            height=26,
            corner_radius=5,
            border_width=1,
            font=ctk.CTkFont("Inter", 11),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000"
        )
        self.student_entry.pack(pady=(2, 0))

        # Program and Section Row
        program_section_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        program_section_container.place(x=15, y=235)
        
        # Program (Left)
        program_left = ctk.CTkFrame(program_section_container, fg_color="transparent")
        program_left.pack(side="left", anchor="nw")
        
        ctk.CTkLabel(
            program_left,
            text="Program",
            font=ctk.CTkFont("Inter", 11),
            text_color="#707070"
        ).pack(anchor="w")
        
        # Program dropdown - wrapped in container for border
        program_dropdown_container = ctk.CTkFrame(
            program_left,
            fg_color="#ffffff",
            border_width=1,
            border_color="#d1d1d1",
            corner_radius=5,
            height=28
        )
        program_dropdown_container.pack(pady=(2, 0))
        program_dropdown_container.pack_propagate(False)
        
        # Use backend data for program options
        program_options = [p['abbreviation'] for p in self.dropdown_data.get('programs', [])]
        if not program_options:
            program_options = ["BSIT", "BSCS", "BSIS"]  # Fallback
        
        self.program_dropdown = ctk.CTkOptionMenu(
            program_dropdown_container,
            width=188,
            height=26,
            corner_radius=5,
            font=ctk.CTkFont("Inter", 11),
            fg_color="#ffffff",
            button_color="#ffffff",
            button_hover_color="#f5f5f5",
            text_color="#000000",
            dropdown_fg_color="#ffffff",
            dropdown_text_color="#000000",
            dropdown_hover_color="#f5f5f5",
            values=program_options,
            command=self.on_program_change
        )
        self.program_dropdown.pack(fill="both", expand=True, padx=1, pady=1)
        self.program_dropdown.set(program_options[0] if program_options else "BSIT")
        
        # Section (Right)
        section_right = ctk.CTkFrame(program_section_container, fg_color="transparent")
        section_right.pack(side="right", anchor="ne", padx=(20, 0))
        
        ctk.CTkLabel(
            section_right,
            text="Section",
            font=ctk.CTkFont("Inter", 11),
            text_color="#707070"
        ).pack(anchor="w")
        
        # Section dropdown - wrapped in container for border
        section_dropdown_container = ctk.CTkFrame(
            section_right,
            fg_color="#ffffff",
            border_width=1,
            border_color="#d1d1d1",
            corner_radius=5,
            height=28
        )
        section_dropdown_container.pack(pady=(2, 0))
        section_dropdown_container.pack_propagate(False)
        
        # Initially load sections for the first program
        self.section_dropdown = ctk.CTkOptionMenu(
            section_dropdown_container,
            width=188,
            height=26,
            corner_radius=5,
            font=ctk.CTkFont("Inter", 11),
            fg_color="#ffffff",
            button_color="#ffffff",
            button_hover_color="#f5f5f5",
            text_color="#000000",
            dropdown_fg_color="#ffffff",
            dropdown_text_color="#000000",
            dropdown_hover_color="#f5f5f5",
            values=["Loading..."]
        )
        self.section_dropdown.pack(fill="both", expand=True, padx=1, pady=1)
        self.section_dropdown.set("Loading...")
        
        # Load sections for the default program
        self.after(100, self.initialize_sections)

        # Webmail Address
        webmail_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        webmail_container.place(x=15, y=295)
        
        ctk.CTkLabel(
            webmail_container,
            text="Webmail Address",
            font=ctk.CTkFont("Inter", 11),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.webmail_entry = ctk.CTkEntry(
            webmail_container,
            width=405,
            height=26,
            corner_radius=5,
            border_width=1,
            font=ctk.CTkFont("Inter", 11),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000"
        )
        self.webmail_entry.pack(pady=(2, 0))

        # Password
        password_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        password_container.place(x=15, y=345)
        
        ctk.CTkLabel(
            password_container,
            text="Password",
            font=ctk.CTkFont("Inter", 11),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.password_entry = ctk.CTkEntry(
            password_container,
            width=405,
            height=26,
            corner_radius=5,
            border_width=1,
            font=ctk.CTkFont("Inter", 11),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            show="•"
        )
        self.password_entry.pack(pady=(2, 0))

        # Confirm Password
        confirm_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        confirm_container.place(x=15, y=395)
        
        ctk.CTkLabel(
            confirm_container,
            text="Confirm Password",
            font=ctk.CTkFont("Inter", 11),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.confirm_entry = ctk.CTkEntry(
            confirm_container,
            width=405,
            height=26,
            corner_radius=5,
            border_width=1,
            font=ctk.CTkFont("Inter", 11),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            show="•"
        )
        self.confirm_entry.pack(pady=(2, 0))

        # Validation Label (initially hidden)
        self.validation_label = ctk.CTkLabel(
            self.card_frame,
            text="",
            font=ctk.CTkFont("Inter", 10),
            text_color="#dc2626",
            wraplength=400,
            justify="left"
        )
        self.validation_label.place(x=15, y=450)
        self.validation_label.place_forget()

        # Buttons
        button_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        button_frame.place(x=15, y=570)
        
        # Cancel Button
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=120,
            height=34,
            corner_radius=8,
            border_width=1,
            font=ctk.CTkFont("Inter", 11, "bold"),
            fg_color="transparent",
            text_color="#666666",
            border_color="#d1d1d1",
            hover_color="#f5f5f5",
            command=self.destroy
        )
        cancel_button.pack(side="left", padx=(0, 10))

        # Add Student Button
        self.add_button = ctk.CTkButton(
            button_frame,
            text="Add Student",
            width=140,
            height=34,
            corner_radius=8,
            border_width=1,
            font=ctk.CTkFont("Inter", 11, "bold"),
            fg_color="#1E3A8A",
            hover_color="#152a63",
            command=self.handle_submit_student
        )
        self.add_button.pack(side="left")

    def create_faculty_form(self):
        """Create form for adding faculty - placeholder for now"""
        # Header
        ctk.CTkLabel(
            self,
            text="Add Faculty Feature",
            font=ctk.CTkFont("Inter", 20, "bold"),
            text_color="#1E3A8A"
        ).pack(pady=50)
        
        ctk.CTkLabel(
            self,
            text="Faculty addition form will be implemented here",
            font=ctk.CTkFont("Inter", 14),
            text_color="#666666"
        ).pack(pady=20)
        
        # Close button
        ctk.CTkButton(
            self,
            text="Close",
            width=120,
            height=34,
            corner_radius=8,
            font=ctk.CTkFont("Inter", 11, "bold"),
            fg_color="#1E3A8A",
            hover_color="#152a63",
            command=self.destroy
        ).pack(pady=20)

    def load_dropdown_options(self):
        """Load dropdown options from backend"""
        try:
            # Get programs from database
            success_programs, programs_data = self.db_manager.get_programs()
            if not success_programs:
                print(f"Error loading programs: {programs_data}")
                programs_data = []
            
            # Get all sections from database  
            success_sections, sections_data = self.db_manager.get_sections()
            if not success_sections:
                print(f"Error loading sections: {sections_data}")
                sections_data = []
            
            # Transform programs data to match expected format
            programs = []
            for program in programs_data:
                # Extract abbreviation from name or description
                name = program.get('name', '')
                description = program.get('description', '')
                
                # Try to extract abbreviation (usually in parentheses or first letters)
                abbreviation = name
                if '(' in name and ')' in name:
                    # Extract text in parentheses as abbreviation
                    start = name.find('(') + 1
                    end = name.find(')')
                    abbreviation = name[start:end]
                elif 'Bachelor of Science in' in name:
                    # Extract first letters after "Bachelor of Science in"
                    parts = name.replace('Bachelor of Science in ', '').split()
                    abbreviation = 'BS' + ''.join([part[0] for part in parts if part])
                
                programs.append({
                    'id': program['id'],
                    'name': name,
                    'abbreviation': abbreviation
                })
            
            # Transform sections data to match expected format
            sections = []
            for section in sections_data:
                sections.append({
                    'id': section['id'],
                    'name': section['name'],
                    'program_id': section['program_id']
                })
            
            self.dropdown_data = {
                'programs': programs,
                'sections': sections
            }
            
            print(f"Loaded from database: {len(programs)} programs, {len(sections)} sections")
                
        except Exception as e:
            print(f"Error in load_dropdown_options: {e}")
            # Use fallback data on error
            self.dropdown_data = {
                'programs': [
                    {'id': 1, 'abbreviation': 'BSIT', 'name': 'Bachelor of Science in Information Technology'},
                    {'id': 2, 'abbreviation': 'BSCS', 'name': 'Bachelor of Science in Computer Science'},
                    {'id': 3, 'abbreviation': 'BSIS', 'name': 'Bachelor of Science in Information Systems'}
                ],
                'sections': [
                    {'id': 1, 'name': 'A', 'program_id': 1},
                    {'id': 2, 'name': 'B', 'program_id': 1},
                    {'id': 3, 'name': 'A', 'program_id': 2},
                    {'id': 4, 'name': 'B', 'program_id': 2},
                    {'id': 5, 'name': 'A', 'program_id': 3},
                    {'id': 6, 'name': 'B', 'program_id': 3}
                ]
            }

    def on_program_change(self, selected_program):
        """Handle program selection change to filter sections"""
        try:
            # Find the program ID for the selected abbreviation
            selected_program_id = None
            for program in self.dropdown_data.get('programs', []):
                if program['abbreviation'] == selected_program:
                    selected_program_id = program['id']
                    break
            
            if selected_program_id:
                # Filter sections by program
                filtered_sections = [
                    s['name'] for s in self.dropdown_data.get('sections', [])
                    if s.get('program_id') == selected_program_id
                ]
                
                if filtered_sections:
                    # Update section dropdown with filtered options
                    self.section_dropdown.configure(values=filtered_sections)
                    self.section_dropdown.set(filtered_sections[0])  # Set to first available section
                else:
                    # No sections found for this program
                    self.section_dropdown.configure(values=["No sections available"])
                    self.section_dropdown.set("No sections available")
            else:
                # If no valid program selected
                self.section_dropdown.configure(values=["Select program first"])
                self.section_dropdown.set("Select program first")
            
        except Exception as e:
            print(f"Error handling program change: {e}")
            self.section_dropdown.configure(values=["Error loading sections"])
            self.section_dropdown.set("Error loading sections")

    def initialize_sections(self):
        """Initialize sections based on the default program selection"""
        if hasattr(self, 'program_dropdown'):
            default_program = self.program_dropdown.get()
            if default_program and default_program != "Loading...":
                self.on_program_change(default_program)

    def _on_month_year_change(self, value=None):
        """Called when month or year changes to update available days"""
        self._update_days()
    
    def _update_days(self):
        """Update the day dropdown based on selected month and year"""
        try:
            month_name = self.month_dropdown.get()
            year = int(self.year_dropdown.get())
            
            # Convert month name to number
            month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            month_num = month_names.index(month_name) + 1
            
            # Get number of days in the month
            days_in_month = self._get_days_in_month(month_num, year)
            
            # Get current selected day
            current_day = self.day_dropdown.get()
            
            # Create new day values
            day_values = [str(i).zfill(2) for i in range(1, days_in_month + 1)]
            
            # Update the dropdown values
            self.day_dropdown.configure(values=day_values)
            
            # Restore selection if still valid, otherwise set to first day
            if current_day and int(current_day) <= days_in_month:
                self.day_dropdown.set(current_day)
            else:
                self.day_dropdown.set("01")
                
        except (ValueError, AttributeError):
            # Fallback to 31 days if something goes wrong
            day_values = [str(i).zfill(2) for i in range(1, 32)]
            self.day_dropdown.configure(values=day_values)
            self.day_dropdown.set("01")
    
    def _get_days_in_month(self, month, year):
        """Get the number of days in a given month and year"""
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        elif month == 2:
            return 29 if self._is_leap_year(year) else 28
        else:
            return 31
    
    def _is_leap_year(self, year):
        """Check if a year is a leap year"""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def show_validation_error(self, message):
        """Show validation error with sound and animation"""
        try:
            # Play error sound
            winsound.MessageBeep(winsound.MB_ICONHAND)
        except Exception:
            pass  # Silent fallback
        
        # Start shake animation
        self.shake_card()
        
        # Show error message
        self.validation_label.configure(text=message)
        self.validation_label.place(x=15, y=450)

    def hide_validation_error(self):
        """Hide the validation error label"""
        self.validation_label.place_forget()

    def shake_card(self):
        """Animate the card with a shake effect"""
        if self.shake_animation_running:
            return
            
        self.shake_animation_running = True
        
        # Shake parameters
        shake_distance = 8
        shake_duration = 400
        shake_steps = 8
        step_duration = shake_duration // shake_steps
        
        def animate_step(step):
            if step >= shake_steps:
                # Return to original position
                self.card_frame.place(x=self.original_card_x, y=70)
                self.shake_animation_running = False
                return
            
            # Calculate shake offset
            if step % 2 == 0:
                offset = shake_distance
            else:
                offset = -shake_distance
                
            # Reduce shake intensity over time
            intensity = 1 - (step / shake_steps)
            actual_offset = int(offset * intensity)
            
            # Apply shake
            self.card_frame.place(x=self.original_card_x + actual_offset, y=70)
            
            # Schedule next step
            self.after(step_duration, lambda: animate_step(step + 1))
        
        # Start animation
        animate_step(0)

    def handle_submit_student(self):
        """Handle submit button - validate form then open camera"""
        try:
            print("Submit button clicked - starting validation")
            
            # Hide any previous validation errors
            self.hide_validation_error()
            
            # Collect form data
            form_data = {
                'first_name': self.first_name_entry.get().strip(),
                'last_name': self.last_name_entry.get().strip(),
                'email': self.webmail_entry.get().strip(),
                'contact_number': self.contact_entry.get().strip(),
                'student_number': self.student_entry.get().strip(),
                'password': self.password_entry.get().strip(),
                'confirm_password': self.confirm_entry.get().strip(),
                'program': self.program_dropdown.get(),
                'section': self.section_dropdown.get()
            }
            
            # Get date of birth
            day = self.day_dropdown.get()
            month_name = self.month_dropdown.get()
            year = self.year_dropdown.get()
            
            # Convert month name to number
            month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            month = str(month_names.index(month_name) + 1).zfill(2)
            form_data['birthday'] = f"{year}-{month}-{day.zfill(2)}"
            
            # Validate form data (including email and student number uniqueness)
            validation_errors = self.validate_form_data(form_data)
            
            if validation_errors:
                error_message = "Please fix the following errors:\n\n" + "\n".join(f"• {error}" for error in validation_errors)
                self.show_validation_error(error_message)
                return
            
            print("Validation passed - opening camera")
            
            # Store form data for later use
            self.pending_form_data = form_data
            
            # Release grab COMPLETELY before opening camera
            try:
                self.grab_release()
                self.update()  # Force update to release grab
            except Exception as e:
                print(f"Could not release grab: {e}")
            
            # Open camera modal for face capture
            self.open_face_verification_dialog()
                
        except Exception as e:
            print(f"Error in submit: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred:\n\n{str(e)}")

    def validate_form_data(self, form_data):
        """Validate form data before submission"""
        errors = []
        
        # Validate required fields
        if not form_data.get('first_name'):
            errors.append("First name is required")
        elif len(form_data['first_name']) < 2:
            errors.append("First name must be at least 2 characters")
        
        if not form_data.get('last_name'):
            errors.append("Last name is required")
        elif len(form_data['last_name']) < 2:
            errors.append("Last name must be at least 2 characters")
        
        if not form_data.get('email'):
            errors.append("Email is required")
        else:
            # Email format validation
            email_pattern = r'^[a-zA-Z0-9._%+-]+@iskolarngbayan\.pup\.edu\.ph$'
            if not re.match(email_pattern, form_data['email']):
                errors.append("Email must use @iskolarngbayan.pup.edu.ph domain")
            else:
                # Check if email already exists in database
                try:
                    email_exists, _ = self.db_manager.check_email_exists(form_data['email'])
                    if email_exists:
                        errors.append("Email address is already in use")
                except Exception as e:
                    print(f"Error checking email existence: {e}")
                    errors.append("Unable to verify email availability")
        
        if not form_data.get('student_number'):
            errors.append("Student number is required")
        else:
            # Check if student number already exists in database
            try:
                student_exists, _ = self.db_manager.check_student_id_exists(form_data['student_number'])
                if student_exists:
                    errors.append("Student number is already in use")
            except Exception as e:
                print(f"Error checking student number existence: {e}")
                errors.append("Unable to verify student number availability")
        
        # Validate contact number
        if form_data.get('contact_number'):
            contact = form_data['contact_number'].strip()
            if contact:
                clean_contact = re.sub(r'[\s\-\(\)\+]', '', contact)
                if not clean_contact.isdigit():
                    errors.append("Contact number must contain only digits")
                elif len(clean_contact) != 11:
                    errors.append("Contact number must be exactly 11 digits")
                elif not clean_contact.startswith('09'):
                    errors.append("Contact number must start with 09")
        
        # Validate password
        if not form_data.get('password'):
            errors.append("Password is required")
        else:
            password = form_data['password']
            if len(password) < 6:
                errors.append("Password must be at least 6 characters long")
            elif len(password) > 50:
                errors.append("Password must be less than 50 characters")
            else:
                # Check for uppercase letter
                if not any(c.isupper() for c in password):
                    errors.append("Password must contain at least one uppercase letter")
                
                # Check for lowercase letter
                if not any(c.islower() for c in password):
                    errors.append("Password must contain at least one lowercase letter")
                
                # Check for special character
                special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
                if not any(c in special_chars for c in password):
                    errors.append("Password must contain at least one special character")
        
        # Validate password confirmation
        if form_data.get('password') != form_data.get('confirm_password'):
            errors.append("Passwords do not match")
        
        return errors

    def open_face_verification_dialog(self):
        """Open facial recognition popup using separate camera module"""
        # Create camera window with callback - NO GRAB SET HERE
        self.camera_window = IndependentFacialRecognitionWindow(self.on_face_capture_complete)

    def on_face_capture_complete(self, face_image, face_image_data):
        """Callback when face capture is completed - save to database with verified=1"""
        try:
            self.face_image = face_image
            self.face_image_data = face_image_data
            
            # Restore grab to parent modal FIRST
            try:
                self.grab_set()
                self.focus_force()
                self.lift()
                self.update()  # Force update
            except Exception as e:
                print(f"Could not restore grab: {e}")
            
            # Wait a moment for grab to take effect
            self.after(100, self._show_confirmation_dialog)
                
        except Exception as e:
            print(f"Error in face capture complete: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred:\n\n{str(e)}")

    def _show_confirmation_dialog(self):
        """Show confirmation dialog after face capture"""
        try:
            # Show confirmation dialog with topmost attribute
            confirmation_msg = f"Add new student '{self.pending_form_data['first_name']} {self.pending_form_data['last_name']}'?\n\n"
            confirmation_msg += f"Student Number: {self.pending_form_data['student_number']}\n"
            confirmation_msg += f"Email: {self.pending_form_data['email']}\n"
            confirmation_msg += f"Program: {self.pending_form_data['program']}\n"
            confirmation_msg += f"Section: {self.pending_form_data['section']}\n\n"
            confirmation_msg += "Student will be registered as VERIFIED with face authentication."
            
            # Create a temporary toplevel for the messagebox to ensure it appears on top
            temp_parent = ctk.CTkToplevel(self)
            temp_parent.withdraw()  # Hide the window
            temp_parent.attributes('-topmost', True)
            temp_parent.grab_set()  # Grab on temp window
            
            try:
                result = messagebox.askyesno("Confirm Add Student", confirmation_msg, parent=temp_parent)
            finally:
                temp_parent.destroy()
            
            if not result:
                return
            
            # Show loading state
            self.add_button.configure(text="Adding...", state="disabled")
            self.update_idletasks()
            
            # Save to database
            success, message = self.save_student_to_database()
            
            if success:
                # Show success with topmost
                success_parent = ctk.CTkToplevel(self)
                success_parent.withdraw()
                success_parent.attributes('-topmost', True)
                success_parent.grab_set()
                
                try:
                    messagebox.showinfo(
                        "Success", 
                        f"Student '{self.pending_form_data['first_name']} {self.pending_form_data['last_name']}' "
                        f"added successfully with face verification!\n\nStatus: VERIFIED ✓",
                        parent=success_parent
                    )
                finally:
                    success_parent.destroy()
                
                # Refresh the parent view if possible
                if hasattr(self.parent_view, 'load_filtered_data'):
                    self.parent_view.load_filtered_data()
                elif hasattr(self.parent_view, 'refresh'):
                    self.parent_view.refresh()
                
                self.destroy()
            else:
                # Show error with topmost
                error_parent = ctk.CTkToplevel(self)
                error_parent.withdraw()
                error_parent.attributes('-topmost', True)
                error_parent.grab_set()
                
                try:
                    messagebox.showerror("Add Failed", f"Failed to add student:\n\n{message}", parent=error_parent)
                finally:
                    error_parent.destroy()
                
                # Reset button
                self.add_button.configure(text="Add Student", state="normal")
                
        except Exception as e:
            print(f"Error in confirmation dialog: {e}")
            # Reset button
            self.add_button.configure(text="Add Student", state="normal")

    def save_student_to_database(self):
        """Save student to database with correct schema structure (users + students tables)"""
        try:
            # Get database connection
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Hash password using bcrypt
            password_bytes = self.pending_form_data['password'].encode('utf-8')
            password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
            password_hash_str = password_hash.decode('utf-8')
            
            # Convert face image to base64 or binary
            face_image_data = None
            if self.face_image_data:
                face_image_data = self.face_image_data  # Store as binary (LargeBinary)
            
            # Get section ID
            section_id = None
            program_id = None
            
            # Find program ID
            for program in self.dropdown_data.get('programs', []):
                if program['abbreviation'] == self.pending_form_data['program']:
                    program_id = program['id']
                    break
            
            # Find section ID
            if program_id:
                for section in self.dropdown_data.get('sections', []):
                    if (section['name'] == self.pending_form_data['section'] and 
                        section.get('program_id') == program_id):
                        section_id = section['id']
                        break
            
            # Get "Enrolled" status ID (default for new students)
            status_id = None
            try:
                cursor.execute("SELECT id FROM statuses WHERE name = 'Enrolled' LIMIT 1")
                result = cursor.fetchone()
                if result:
                    status_id = result[0]
            except Exception as e:
                print(f"Error getting status ID: {e}")
            
            # Start transaction
            cursor.execute("BEGIN")
            
            try:
                # First, insert into users table with status_id and isDeleted
                cursor.execute("""
                    INSERT INTO users (
                        first_name, last_name, email, birthday, password_hash, 
                        contact_number, role, status_id, face_image, verified, isDeleted, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 'Student', ?, ?, 1, 0, ?)
                """, (
                    self.pending_form_data['first_name'],
                    self.pending_form_data['last_name'],
                    self.pending_form_data['email'],
                    self.pending_form_data.get('birthday'),
                    password_hash_str,
                    self.pending_form_data.get('contact_number'),
                    status_id,
                    face_image_data,
                    datetime.now()
                ))
                
                # Get the user_id
                user_id = cursor.lastrowid
                
                # Then, insert into students table
                cursor.execute("""
                    INSERT INTO students (
                        user_id, student_number, section
                    ) VALUES (?, ?, ?)
                """, (
                    user_id,
                    self.pending_form_data['student_number'],
                    section_id
                ))
                
                # Commit transaction
                cursor.execute("COMMIT")
                
                student_id = cursor.lastrowid
                
                return (True, f"Student {self.pending_form_data['first_name']} {self.pending_form_data['last_name']} added successfully with User ID: {user_id}, Student ID: {student_id}")
                
            except Exception as e:
                # Rollback transaction on error
                cursor.execute("ROLLBACK")
                raise e
            
        except sqlite3.IntegrityError as e:
            error_message = str(e).lower()
            if "email" in error_message:
                return (False, "Email address is already in use")
            elif "student_number" in error_message:
                return (False, "Student number is already in use")
            else:
                return (False, f"Data integrity error: {str(e)}")
        except Exception as e:
            print(f"Error saving student to database: {e}")
            return (False, f"Failed to save student: {str(e)}")
