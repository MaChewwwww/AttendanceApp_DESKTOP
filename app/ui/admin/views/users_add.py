import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import cv2
import threading
import time
import io
import os
import winsound
import re
from datetime import datetime
from PIL import Image, ImageTk
from app.db_manager import DatabaseManager

class UsersAddModal(ctk.CTkToplevel):
    def __init__(self, parent, user_type="student"):
        super().__init__(parent)
        self.parent_view = parent
        self.user_type = user_type
        self.db_manager = DatabaseManager()
        
        # Face verification variables
        self.face_image = None
        self.face_image_data = None
        self.camera = None
        self.is_camera_active = False
        self.camera_thread = None
        self.verification_dialog = None
        
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
        # Create StringVar for form fields
        self.first_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.contact_number_var = tk.StringVar()
        self.student_number_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()
        
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
            text_color="#000000",
            textvariable=self.first_name_var
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
            text_color="#000000",
            textvariable=self.last_name_var
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
            text_color="#000000",
            textvariable=self.contact_number_var
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
            text_color="#000000",
            textvariable=self.student_number_var
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
            text_color="#000000",
            textvariable=self.email_var
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
            show="•",
            textvariable=self.password_var
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
            show="•",
            textvariable=self.confirm_password_var
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
            command=self.handle_add_student
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
            # Get dropdown options for student type
            success, dropdown_data = self.db_manager.get_user_update_dropdown_data("student")
            
            if success:
                self.dropdown_data = dropdown_data
                print(f"Loaded dropdown options: {len(dropdown_data.get('programs', []))} programs, {len(dropdown_data.get('sections', []))} sections")
            else:
                print(f"Error loading dropdown options: {dropdown_data}")
                self.dropdown_data = {'programs': [], 'sections': []}
                
        except Exception as e:
            print(f"Error in load_dropdown_options: {e}")
            self.dropdown_data = {'programs': [], 'sections': []}

    def on_program_change(self, selected_program):
        """Handle program selection change to filter sections"""
        try:
            # Find the program ID for the selected abbreviation
            selected_program_id = None
            for program in self.dropdown_data.get('programs', []):
                if program.get('abbreviation') == selected_program:
                    selected_program_id = program.get('id')
                    break
            
            if selected_program_id:
                # Filter sections for this program
                program_sections = []
                for section in self.dropdown_data.get('sections', []):
                    if section.get('program_id') == selected_program_id:
                        program_sections.append(section.get('name', ''))
                
                if program_sections:
                    # Update section dropdown with filtered sections
                    self.section_dropdown.configure(
                        values=program_sections,
                        fg_color="#ffffff",
                        text_color="#000000",
                        state="normal"
                    )
                    self.section_dropdown.set(program_sections[0])
                else:
                    # No sections available for this program
                    self.section_dropdown.configure(
                        values=["No sections available"],
                        fg_color="#f5f5f5",
                        text_color="#999999",
                        state="disabled"
                    )
                    self.section_dropdown.set("No sections available")
            else:
                # Program not found, show fallback
                fallback_sections = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]
                self.section_dropdown.configure(
                    values=fallback_sections,
                    fg_color="#ffffff",
                    text_color="#000000",
                    state="normal"
                )
                self.section_dropdown.set(fallback_sections[0])
            
        except Exception as e:
            print(f"Error handling program change: {e}")
            # Fallback to default sections on error
            fallback_sections = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]
            self.section_dropdown.configure(
                values=fallback_sections,
                fg_color="#ffffff",
                text_color="#000000",
                state="normal"
            )
            self.section_dropdown.set(fallback_sections[0])

    def initialize_sections(self):
        """Initialize sections based on the default program selection"""
        if hasattr(self, 'program_dropdown'):
            default_program = self.program_dropdown.get()
            self.on_program_change(default_program)

    # ...existing date handling methods from register.py...
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
            
            # Restore selection if still valid, otherwise set to last valid day
            if current_day and int(current_day) <= days_in_month:
                self.day_dropdown.set(current_day)
            else:
                self.day_dropdown.set(str(days_in_month).zfill(2))
                
        except (ValueError, AttributeError):
            # Fallback to 31 days if something goes wrong
            day_values = [str(i).zfill(2) for i in range(1, 32)]
            self.day_dropdown.configure(values=day_values)
            self.day_dropdown.set("15")
    
    def _get_days_in_month(self, month, year):
        """Get the number of days in a given month and year"""
        if month in [1, 3, 5, 7, 8, 10, 12]:  # 31 days
            return 31
        elif month in [4, 6, 9, 11]:  # 30 days
            return 30
        elif month == 2:  # February
            return 29 if self._is_leap_year(year) else 28
        else:
            return 31  # Fallback
    
    def _is_leap_year(self, year):
        """Check if a year is a leap year"""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def show_validation_error(self, message):
        """Show validation error with sound and animation"""
        # Play error sound
        try:
            winsound.MessageBeep(winsound.MB_ICONHAND)
        except Exception:
            try:
                print('\a')  # ASCII bell character
            except:
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
        shake_duration = 400  # milliseconds
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

    def handle_add_student(self):
        """Process the add student form submission"""
        try:
            # Hide any previous validation errors
            self.hide_validation_error()
            
            # Get values from form fields directly from the entry widgets
            first_name = self.first_name_entry.get().strip()
            last_name = self.last_name_entry.get().strip()
            email = self.webmail_entry.get().strip()
            contact_number = self.contact_entry.get().strip()
            student_number = self.student_entry.get().strip()
            password = self.password_entry.get().strip()
            confirm_password = self.confirm_entry.get().strip()
            
            # Get dropdown values directly
            program = self.program_dropdown.get()
            section = self.section_dropdown.get()
            month_name = self.month_dropdown.get()
            day = self.day_dropdown.get()
            year = self.year_dropdown.get()

            # Debug print to see what values we're getting
            print(f"Form values - First: '{first_name}', Last: '{last_name}', Email: '{email}'")
            print(f"Contact: '{contact_number}', Student#: '{student_number}'")
            print(f"Program: '{program}', Section: '{section}'")
            print(f"Date: '{month_name}' '{day}' '{year}'")
            print(f"Password length: {len(password)}, Confirm length: {len(confirm_password)}")

            # Collect all validation errors
            errors = []

            # Validate required fields
            if not first_name:
                errors.append("• First name is required")
            if not last_name:
                errors.append("• Last name is required")
            if not email:
                errors.append("• Email address is required")
            if not contact_number:
                errors.append("• Contact number is required")
            if not student_number:
                errors.append("• Student number is required")
            if not password:
                errors.append("• Password is required")
            if not confirm_password:
                errors.append("• Confirm password is required")

            # Validate dropdown selections - improved validation
            if not program or program in ["Select Program", "", "Loading..."]:
                errors.append("• Program is required")
            if not section or section in ["Select Section", "", "Loading...", "No sections available"]:
                errors.append("• Section is required")

            # Validate date of birth
            if not month_name or month_name in ["Select Month", ""]:
                errors.append("• Month is required")
            if not day or day in ["Select Day", ""]:
                errors.append("• Day is required")
            if not year or year in ["Select Year", ""]:
                errors.append("• Year is required")

            # Validate program and section consistency
            if program and section and not any("required" in error for error in errors if "Program" in error or "Section" in error):
                # Check if section belongs to selected program
                program_id = None
                for prog in self.dropdown_data.get('programs', []):
                    if prog.get('abbreviation') == program:
                        program_id = prog.get('id')
                        break
                
                if program_id:
                    # Check if section belongs to this program
                    section_valid = False
                    for sect in self.dropdown_data.get('sections', []):
                        if sect.get('name') == section and sect.get('program_id') == program_id:
                            section_valid = True
                            break
                    
                    if not section_valid:
                        errors.append("• Selected section does not belong to the selected program")
                else:
                    errors.append("• Invalid program selection")

            # Validate email format
            if email and not email.endswith("@iskolarngbayan.pup.edu.ph"):
                errors.append("• Email must be a valid PUP email ending with @iskolarngbayan.pup.edu.ph")

            # Validate contact number (11 digits starting with 09)
            if contact_number:
                if not contact_number.isdigit():
                    errors.append("• Contact number must contain only digits")
                elif len(contact_number) != 11:
                    errors.append("• Contact number must be exactly 11 digits")
                elif not contact_number.startswith('09'):
                    errors.append("• Contact number must start with 09")

            # Validate password requirements
            if password:
                if len(password) < 6:
                    errors.append("• Password must be at least 6 characters long")
                if not re.search(r'[a-z]', password):
                    errors.append("• Password must contain at least one lowercase letter")
                if not re.search(r'[A-Z]', password):
                    errors.append("• Password must contain at least one uppercase letter")
                if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                    errors.append("• Password must contain at least one special character")

            # Validate password match
            if password and confirm_password and password != confirm_password:
                errors.append("• Passwords do not match")

            # Validate date of birth format and create date string
            date_of_birth = None
            if month_name and day and year and not any("required" in error for error in errors if "Month" in error or "Day" in error or "Year" in error):
                try:
                    # Convert month name to number
                    month_names = [
                        "January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"
                    ]
                    month_num = month_names.index(month_name) + 1
                    
                    # Create date object to validate
                    birth_date = datetime(int(year), month_num, int(day))
                    date_of_birth = birth_date.strftime('%Y-%m-%d')
                    
                    # Check if date is not in the future
                    if birth_date.date() > datetime.now().date():
                        errors.append("• Date of birth cannot be in the future")
                    
                    # Check minimum age (16 years)
                    today = datetime.now().date()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    if age < 16:
                        errors.append("• Student must be at least 16 years old")
                        
                except (ValueError, IndexError) as e:
                    errors.append("• Invalid date of birth")

            # Validate email and student ID uniqueness (only if basic validation passes)
            if not errors:
                try:
                    # Check if email already exists
                    if email and hasattr(self.db_manager, 'check_email_exists'):
                        email_exists, _ = self.db_manager.check_email_exists(email)
                        if email_exists:
                            errors.append("• An account with this email address already exists")
                    
                    # Check if student number already exists  
                    if student_number and hasattr(self.db_manager, 'check_student_id_exists'):
                        student_exists, _ = self.db_manager.check_student_id_exists(student_number)
                        if student_exists:
                            errors.append("• An account with this student number already exists")

                except Exception as db_error:
                    print(f"Database validation error: {db_error}")

            # Show errors if any exist
            if errors:
                error_message = "\n".join(errors)
                self.show_validation_error(error_message)
                return

            # Store form data for later use
            self.student_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'contact_number': contact_number,
                'student_number': student_number,
                'password': password,
                'program': program,
                'section': section,
                'date_of_birth': date_of_birth
            }

            # Open face verification dialog
            self.open_face_verification_dialog()
            
        except Exception as e:
            self.show_validation_error(f"• An unexpected error occurred: {str(e)}")
            import traceback
            traceback.print_exc()

    def open_face_verification_dialog(self):
        """Open the face verification dialog"""
        self.verification_dialog = ctk.CTkToplevel(self)
        self.verification_dialog.title("Face Verification")
        self.verification_dialog.geometry("454x450")
        self.verification_dialog.resizable(False, False)
        self.verification_dialog.configure(fg_color="#222222")
        
        # Set minimum size to prevent shrinking
        self.verification_dialog.minsize(454, 450)
        self.verification_dialog.maxsize(454, 450)

        # Make dialog modal
        self.verification_dialog.grab_set()

        # Center dialog with explicit positioning
        self.verification_dialog.update_idletasks()
        
        # Force the geometry before centering
        self.verification_dialog.geometry("454x450")
        
        # Calculate center position
        screen_width = self.verification_dialog.winfo_screenwidth()
        screen_height = self.verification_dialog.winfo_screenheight()
        x = (screen_width - 454) // 2
        y = (screen_height - 450) // 2
        
        # Set position explicitly
        self.verification_dialog.geometry(f"454x450+{x}+{y}")
        
        # Force update to ensure size is applied
        self.verification_dialog.update()

        self._create_verification_dialog_content()
        
        # Bind dialog close to cleanup
        self.verification_dialog.protocol("WM_DELETE_WINDOW", self.on_verification_dialog_closing)

    def _create_verification_dialog_content(self):
        """Create content for the face verification dialog"""
        # Card Frame with explicit sizing
        card = ctk.CTkFrame(
            self.verification_dialog, 
            width=454, 
            height=450, 
            corner_radius=12, 
            fg_color="#ffffff", 
            border_width=0
        )
        card.place(x=0, y=0)
        card.pack_propagate(False)
        
        # Ensure card maintains its size
        card.grid_propagate(False)

        # Info icon (top right)
        info_btn = ctk.CTkButton(
            card, 
            text="i", 
            width=24, 
            height=24, 
            corner_radius=12, 
            fg_color="#f5f5f5", 
            text_color="#222", 
            font=ctk.CTkFont("Inter", 14, "bold"), 
            hover_color="#e0e0e0", 
            command=lambda: messagebox.showinfo("Camera Info", "Please ensure you're in a well-lit environment before capturing your photo for the best image quality", parent=self.verification_dialog)
        )
        info_btn.place(x=420, y=10)

        # Camera Preview Frame with explicit sizing
        self.face_preview_frame = ctk.CTkFrame(
            card, 
            width=410, 
            height=240, 
            fg_color="#fafafa", 
            border_width=1, 
            border_color="#d1d1d1"
        )
        self.face_preview_frame.place(x=22, y=38)
        self.face_preview_frame.pack_propagate(False)
        self.face_preview_frame.grid_propagate(False)

        # Default Preview Label (centered)
        self.preview_label = ctk.CTkLabel(
            self.face_preview_frame,
            text="Camera will appear here\nClick 'Open Camera' to begin",
            font=ctk.CTkFont("Inter", 12),
            text_color="#a0a0a0"
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Open Camera Button with explicit sizing
        self.camera_button = ctk.CTkButton(
            card,
            text="Open Camera",
            width=410,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont("Inter", 13, "bold"),
            fg_color="#ffffff",
            text_color="#222",
            border_width=1,
            border_color="#d1d1d1",
            hover_color="#f5f5f5",
            command=self.toggle_camera
        )
        self.camera_button.place(x=22, y=290)

        # Retake and Capture Buttons with explicit sizing
        self.retake_button = ctk.CTkButton(
            card,
            text="Retake",
            width=200,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont("Inter", 13, "bold"),
            fg_color="#e5e5e5",
            text_color="#707070",
            border_width=0,
            hover_color="#cccccc",
            state="disabled",
            command=self.retake_photo
        )
        self.retake_button.place(x=22, y=335)

        self.capture_button = ctk.CTkButton(
            card,
            text="Capture",
            width=200,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont("Inter", 13, "bold"),
            fg_color="#1E3A8A",
            text_color="#fff",
            border_width=0,
            hover_color="#152a63",
            state="disabled",
            command=self.capture_face
        )
        self.capture_button.place(x=232, y=335)

        # Add Student Button (renamed from register_button)
        self.add_student_button = ctk.CTkButton(
            card,
            text="Add Student",
            width=410,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont("Inter", 13, "bold"),
            fg_color="#1E3A8A",
            text_color="#fff",
            border_width=0,
            hover_color="#152a63",
            command=self.complete_student_registration,
            state="disabled"
        )
        self.add_student_button.place(x=22, y=385)

    def toggle_camera(self):
        """Toggle camera on/off"""
        try:
            if self.is_camera_active:
                self.stop_camera()
            else:
                self.start_camera()
        except Exception as e:
            print(f"Error in toggle_camera: {e}")
            messagebox.showerror("Camera Error", f"Error with camera: {str(e)}", parent=self.verification_dialog)

    def start_camera(self):
        """Start camera capture with embedded display"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                messagebox.showerror("Camera Error", "Could not open camera. Please check your camera connection.", parent=self.verification_dialog)
                return False

            self.is_camera_active = True
            self.camera_button.configure(text="Close Camera")
            self.capture_button.configure(state="normal")
            
            # Hide the placeholder
            self.preview_label.place_forget()
            
            # Create canvas for camera display with explicit sizing
            self.camera_canvas = tk.Canvas(
                self.face_preview_frame,
                width=410,
                height=240,
                bg="#fafafa",
                highlightthickness=0
            )
            self.camera_canvas.place(x=0, y=0, width=410, height=240)
            
            # Initialize photo reference
            self.current_photo = None
            
            # Start video feed thread
            self.camera_thread = threading.Thread(target=self._update_camera_display)
            self.camera_thread.daemon = True
            self.camera_thread.start()
            
            return True
        except Exception as e:
            messagebox.showerror("Camera Error", f"Error starting camera: {str(e)}", parent=self.verification_dialog)
            return False

    def stop_camera(self):
        """Stop camera capture"""
        try:
            self.is_camera_active = False
            
            # Clean up camera display and resources
            self._cleanup_camera_window()
            self._update_ui_after_camera_close()
                
        except Exception as e:
            print(f"Error in stop_camera: {e}")

    def _update_camera_display(self):
        """Update camera feed display using threading"""
        while self.is_camera_active:
            try:
                ret, frame = self.camera.read()
                if ret:
                    # Store current frame for capture (use original resolution)
                    self.current_frame = frame.copy()
                    
                    # Resize frame to fit preview area - 240px height
                    frame_resized = cv2.resize(frame, (410, 240))
                    
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                    
                    # Add overlay guide
                    h, w = frame_rgb.shape[:2]
                    center_x, center_y = w // 2, h // 2
                    
                    # Draw face positioning guide rectangle
                    rect_w, rect_h = 160, 180
                    cv2.rectangle(frame_rgb, 
                                 (center_x - rect_w//2, center_y - rect_h//2),
                                 (center_x + rect_w//2, center_y + rect_h//2),
                                 (0, 255, 0), 2)
                    
                    # Convert to PIL Image
                    try:
                        pil_image = Image.fromarray(frame_rgb)
                        
                        # Schedule UI update on main thread
                        if (hasattr(self, 'camera_canvas') and 
                            self.camera_canvas and 
                            self.verification_dialog and 
                            self.verification_dialog.winfo_exists()):
                            
                            def update_canvas(img=pil_image):
                                try:
                                    if (hasattr(self, 'camera_canvas') and 
                                        self.camera_canvas and 
                                        self.camera_canvas.winfo_exists()):
                                        
                                        # Create PhotoImage on main thread
                                        photo = ImageTk.PhotoImage(img)
                                        
                                        # Clear canvas and display image
                                        self.camera_canvas.delete("all")
                                        self.camera_canvas.create_image(205, 120, image=photo, anchor="center")
                                        
                                        # Keep reference to prevent garbage collection
                                        self.current_photo = photo
                                        
                                except tk.TclError:
                                    # Widget was destroyed, stop the camera feed
                                    self.is_camera_active = False
                                except Exception as e:
                                    print(f"Canvas update error: {e}")
                            
                            # Schedule the update on main thread
                            self.verification_dialog.after(0, update_canvas)
                        else:
                            # Canvas doesn't exist, stop the feed
                            break
                            
                    except Exception as img_error:
                        print(f"Image processing error: {img_error}")
                        break
                        
            except Exception as e:
                print(f"Camera display error: {e}")
                break

            time.sleep(0.03)  # ~30 FPS
        
        # Ensure camera is properly released when thread ends
        self.is_camera_active = False

    def _cleanup_camera_window(self):
        """Clean up camera display and resources"""
        # Signal thread to stop
        self.is_camera_active = False
        
        # Wait for thread to finish
        if hasattr(self, 'camera_thread') and self.camera_thread and self.camera_thread.is_alive():
            try:
                self.camera_thread.join(0.5)  # Wait up to 0.5 seconds
            except Exception:
                pass

        # Release camera
        if hasattr(self, 'camera') and self.camera and self.camera.isOpened():
            try:
                self.camera.release()
            except Exception:
                pass
            finally:
                self.camera = None

        # Clear camera canvas safely
        if hasattr(self, 'camera_canvas') and self.camera_canvas:
            try:
                if self.camera_canvas.winfo_exists():
                    self.camera_canvas.destroy()
            except Exception:
                pass
            finally:
                self.camera_canvas = None
        
        # Clear photo reference
        self.current_photo = None

    def _update_ui_after_camera_close(self):
        """Update UI after camera window is closed"""
        # Only update camera button text if face hasn't been captured
        if not self.face_image:
            self.camera_button.configure(text="Open Camera")
            self.capture_button.configure(state="disabled")
            
            # Show preview label if no face is captured
            self.preview_label = ctk.CTkLabel(
                self.face_preview_frame,
                text="Camera will appear here\nClick 'Open Camera' to begin",
                font=ctk.CTkFont("Inter", 12),
                text_color="#a0a0a0"
            )
            self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

    def capture_face(self):
        """Capture current frame"""
        if not self.is_camera_active:
            messagebox.showwarning("Camera Error", "Camera is not active. Please open camera first.", parent=self.verification_dialog)
            return
        
        if not hasattr(self, 'current_frame') or self.current_frame is None:
            messagebox.showwarning("Camera Error", "No frame available. Please wait for camera to initialize.", parent=self.verification_dialog)
            return
        
        try:
            frame = self.current_frame.copy()
            
            # Validate face in the image
            validation_result = self.validate_face_image(frame)
            if not validation_result[0]:
                messagebox.showwarning("Face Validation Failed", validation_result[1], parent=self.verification_dialog)
                return

            # Convert to RGB and store
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.face_image = Image.fromarray(frame_rgb)
            
            # Convert to bytes for database storage
            img_byte_arr = io.BytesIO()
            self.face_image.save(img_byte_arr, format='PNG')
            self.face_image_data = img_byte_arr.getvalue()

            # Check image size
            if len(self.face_image_data) > 5 * 1024 * 1024:
                messagebox.showwarning(
                    "Image Too Large",
                    "The captured image exceeds the 5MB limit. Please try again.",
                    parent=self.verification_dialog
                )
                self.face_image = None
                self.face_image_data = None
                return

            # Stop camera and show preview
            self.stop_camera()
            self.show_face_preview()
            
            # Update button states after successful capture
            self._update_buttons_after_capture()
            
            messagebox.showinfo("Success", "Face image captured successfully! You can now add the student.", parent=self.verification_dialog)
            
        except Exception as e:
            print(f"Capture error: {e}")
            messagebox.showerror("Error", f"Failed to capture image: {str(e)}", parent=self.verification_dialog)

    def show_face_preview(self):
        """Show face image preview"""
        try:
            # Clear existing widgets in preview frame
            for widget in self.face_preview_frame.winfo_children():
                widget.destroy()
            
            if self.face_image:
                # Create canvas for displaying captured image
                preview_canvas = tk.Canvas(
                    self.face_preview_frame,
                    width=410,
                    height=240,
                    bg="#fafafa",
                    highlightthickness=0
                )
                preview_canvas.place(x=0, y=0, width=410, height=240)
                
                # Convert image to PhotoImage and display
                preview_img = self.face_image.copy()
                preview_img.thumbnail((410, 240), Image.LANCZOS)
                photo = ImageTk.PhotoImage(preview_img)
                
                preview_canvas.create_image(205, 120, image=photo, anchor="center")
                
                # Keep reference to prevent garbage collection
                preview_canvas.image = photo
            else:
                # Show success message
                preview_text = ctk.CTkLabel(
                    self.face_preview_frame,
                    text="✓ Photo Captured Successfully!\nReady for registration",
                    font=ctk.CTkFont("Inter", 14, "bold"),
                    text_color="#4CAF50"
                )
                preview_text.place(relx=0.5, rely=0.5, anchor="center")
            
        except Exception as e:
            print(f"Error showing face preview: {e}")

    def validate_face_image(self, image):
        """Validate that the image contains a properly visible face"""
        try:
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'

            if not os.path.exists(face_cascade_path) or not os.path.exists(eye_cascade_path):
                print("Warning: Face detection cascades not found. Skipping face validation.")
                return (True, "Face validation skipped")

            face_cascade = cv2.CascadeClassifier(face_cascade_path)
            eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            if len(faces) == 0:
                return (False, "No face detected. Please ensure your face is clearly visible.")
            if len(faces) > 1:
                return (False, "Multiple faces detected. Please ensure only your face is in the image.")

            (x, y, w, h) = faces[0]
            roi_gray = gray[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(
                roi_gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            if len(eyes) < 2:
                return (False, "Eyes not clearly visible. Please remove sunglasses or any accessories covering your face.")

            return (True, "Face validation successful")
        except Exception as e:
            print(f"Face validation error: {str(e)}")
            return (True, "Face validation skipped due to an error")

    def _update_buttons_after_capture(self):
        """Update button states after successful face capture"""
        # Disable camera button and capture button since face is already captured
        self.camera_button.configure(
            state="disabled",
            text="Photo Captured",
            fg_color="#e5e5e5",
            text_color="#707070",
            hover_color="#e5e5e5"
        )
        
        self.capture_button.configure(state="disabled", fg_color="#cccccc", text_color="#999999")
        
        # Enable add student button
        self.add_student_button.configure(state="normal")
        
        # Enable and style retake button
        self.retake_button.configure(
            state="normal",
            fg_color="#dc2626",
            text_color="#ffffff",
            hover_color="#b91c1c"
        )

    def retake_photo(self):
        """Retake photo - restart camera"""
        self.face_image = None
        self.face_image_data = None
        
        # Reset button states for retaking
        self._reset_buttons_for_retake()
        
        # Clear preview
        for widget in self.face_preview_frame.winfo_children():
            widget.destroy()
        
        self.preview_label = ctk.CTkLabel(
            self.face_preview_frame,
            text="Camera will appear here\nClick 'Open Camera' to begin",
            font=ctk.CTkFont("Inter", 12),
            text_color="#a0a0a0"
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.start_camera()

    def _reset_buttons_for_retake(self):
        """Reset button states when retaking photo"""
        # Re-enable camera button
        self.camera_button.configure(
            state="normal",
            text="Close Camera",
            fg_color="#ffffff",
            text_color="#222",
            hover_color="#f5f5f5"
        )
        
        # Disable add student button since no face is captured
        self.add_student_button.configure(state="disabled")
        
        # Disable and reset retake button
        self.retake_button.configure(
            state="disabled",
            fg_color="#e5e5e5",
            text_color="#707070",
            hover_color="#cccccc"
        )

    def complete_student_registration(self):
        """Complete the student registration process"""
        try:
            if not self.face_image_data or len(self.face_image_data) == 0:
                messagebox.showwarning(
                    "Face Image Required", 
                    "A face image is required for registration. Please capture your face using the camera.",
                    parent=self.verification_dialog
                )
                return
            
            # Show loading cursor
            self.verification_dialog.configure(cursor="wait")
            self.verification_dialog.update_idletasks()
            
            # Prepare registration data
            registration_data = self.student_data.copy()
            registration_data['face_image'] = self.face_image_data
            registration_data['verified'] = 1  # Auto-verify for admin-created accounts
            
            # Reset cursor
            self.verification_dialog.configure(cursor="")
            
            # Clean up camera
            if self.is_camera_active:
                self.stop_camera()
            
            # Register the student directly (skip OTP verification)
            success, result = self.db_manager.register_user(registration_data)
            
            if success:
                # Close verification dialog
                self.verification_dialog.destroy()
                
                # Show success message
                messagebox.showinfo(
                    "Success", 
                    f"Student {registration_data['first_name']} {registration_data['last_name']} has been successfully added to the system!",
                    parent=self
                )
                
                # Close the add user modal
                self.destroy()
                
                # Refresh the parent view if it has a refresh method
                if hasattr(self.parent_view, 'refresh_users') and callable(self.parent_view.refresh_users):
                    self.parent_view.refresh_users()
                elif hasattr(self.parent_view, 'load_users') and callable(self.parent_view.load_users):
                    self.parent_view.load_users()
                    
            else:
                messagebox.showerror(
                    "Registration Error", 
                    f"Failed to register student:\n{result}",
                    parent=self.verification_dialog
                )
                
        except Exception as e:
            self.verification_dialog.configure(cursor="")
            messagebox.showerror(
                "Registration Error", 
                f"An unexpected error occurred during registration:\n{str(e)}",
                parent=self.verification_dialog
            )
            import traceback
            traceback.print_exc()

    def on_verification_dialog_closing(self):
        """Handle verification dialog closing"""
        try:
            # Stop camera and clean up
            if self.is_camera_active:
                self.stop_camera()
            
            # Reset face capture state
            self.face_image = None
            self.face_image_data = None
            
            # Destroy dialog
            if self.verification_dialog:
                self.verification_dialog.destroy()
                
        except Exception as e:
            print(f"Error while closing verification dialog: {str(e)}")
