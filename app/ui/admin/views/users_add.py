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
        
        self.program_dropdown = ctk.CTkOptionMenu(
            program_left,
            width=190,
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
            values=["BSIT", "BSCS", "BSIS"]
        )
        self.program_dropdown.pack(pady=(2, 0))
        self.program_dropdown.set("BSIT")
        
        # Section (Right)
        section_right = ctk.CTkFrame(program_section_container, fg_color="transparent")
        section_right.pack(side="right", anchor="ne", padx=(20, 0))
        
        ctk.CTkLabel(
            section_right,
            text="Section",
            font=ctk.CTkFont("Inter", 11),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.section_dropdown = ctk.CTkOptionMenu(
            section_right,
            width=190,
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
            values=["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]
        )
        self.section_dropdown.pack(pady=(2, 0))
        self.section_dropdown.set("1-1")

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
            
            # Get values from form fields
            first_name = self.first_name_var.get().strip()
            last_name = self.last_name_var.get().strip()
            email = self.email_var.get().strip()
            contact_number = self.contact_number_var.get().strip()
            student_number = self.student_number_var.get().strip()
            password = self.password_var.get().strip()
            confirm_password = self.confirm_password_var.get().strip()
            program = self.program_dropdown.get()
            section = self.section_dropdown.get()

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

            # Validate email format
            if email and not email.endswith("@iskolarngbayan.pup.edu.ph"):
                errors.append("• Email must be a valid PUP email ending with @iskolarngbayan.pup.edu.ph")

            # Validate contact number (11 digits)
            if contact_number:
                if not contact_number.isdigit():
                    errors.append("• Contact number must contain only digits")
                elif len(contact_number) != 11:
                    errors.append("• Contact number must be exactly 11 digits")

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

            # Validate email and student ID uniqueness
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

            # Open face verification dialog
            self.open_face_verification_dialog()
            
        except Exception as e:
            self.show_validation_error(f"• An unexpected error occurred: {str(e)}")
            import traceback
            traceback.print_exc()

    def open_face_verification_dialog(self):
        """Open the face verification dialog"""
        from .users_modals import FacialRecognitionPopup
        FacialRecognitionPopup(self)
