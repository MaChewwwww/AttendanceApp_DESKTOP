import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import cv2
import threading
import time
import io
import os
import winsound  # For Windows sound effects
import re  # For regex pattern matching
from datetime import datetime
from PIL import Image, ImageTk

class RegisterForm(ctk.CTkFrame):
    def __init__(self, parent, db_manager=None, on_success=None):
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        self.on_success = on_success
        
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
        
        # Create StringVar for form fields - no test data
        self.first_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.contact_number_var = tk.StringVar()
        self.student_number_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()
        
        # Create the registration form
        self._create_register_form()
        
    def _create_register_form(self):
        """Create the registration form UI"""
        # Header container for title
        header_container = ctk.CTkFrame(self, fg_color="transparent")
        header_container.place(x=40, y=15)
        
        # Title "Sign up as Student" on same row
        title_frame = ctk.CTkFrame(header_container, fg_color="transparent")
        title_frame.pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Sign up as ",
            font=ctk.CTkFont("Roboto", 20, "bold"),
            text_color="#000000"
        ).pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="Student",
            font=ctk.CTkFont("Roboto", 20, "bold"),
            text_color="#1E3A8A"
        ).pack(side="left")
        
        # Divider - extended to cover full title width
        divider = ctk.CTkFrame(
            header_container,
            fg_color="#1E3A8A",
            width=180,
            height=2
        )
        divider.pack(anchor="w", pady=(5, 0))
        
        # Card Frame - better centered
        self.card_frame = ctk.CTkFrame(
            self,
            width=420,
            height=560,
            corner_radius=12,
            fg_color="#ffffff",
            border_width=1,
            border_color="#d1d1d1"
        )
        self.card_frame.place(x=40, y=70)
        self.card_frame.pack_propagate(False)
        
        # Store original position for shake animation
        self.original_card_x = 40

        # Create two columns with tighter spacing
        left_column = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        left_column.place(x=15, y=15)  # Reduced margins
        
        right_column = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        right_column.place(x=215, y=15)  # Adjusted for smaller width
        
        # First Name Label and Input (Left Column)
        ctk.CTkLabel(
            left_column,
            text="First Name",
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            text_color="#707070"
        ).pack(anchor="w")
        
        self.first_name_entry = ctk.CTkEntry(
            left_column,
            width=180,  # Reduced width
            height=26,  # Reduced height
            corner_radius=5,
            border_width=1,
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            textvariable=self.first_name_var
        )
        self.first_name_entry.pack(pady=(2, 10))  # Reduced spacing
        
        # Last Name Label and Input (Right Column)
        ctk.CTkLabel(
            right_column,
            text="Last Name",
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            text_color="#707070"
        ).pack(anchor="w")
        
        self.last_name_entry = ctk.CTkEntry(
            right_column,
            width=180,  # Reduced width
            height=26,  # Reduced height
            corner_radius=5,
            border_width=1,
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            textvariable=self.last_name_var
        )
        self.last_name_entry.pack(pady=(2, 10))  # Reduced spacing
        
        # Date of Birth Row - more compact
        dob_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        dob_container.place(x=15, y=75)  # Adjusted position
        
        # Date of Birth Label
        ctk.CTkLabel(
            dob_container,
            text="Date of Birth",
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            text_color="#707070"
        ).pack(anchor="w")
        
        # Date Input Fields Container
        date_fields = ctk.CTkFrame(dob_container, fg_color="transparent")
        date_fields.pack(pady=(2, 0))
        
        # Month Dropdown Container - smaller
        month_container = ctk.CTkFrame(
            date_fields,
            width=120,  # Reduced width
            height=28,
            corner_radius=5,
            fg_color="#ffffff",
            border_width=1,
            border_color="#d1d1d1"
        )
        month_container.pack(side="left", padx=(0, 8))  # Reduced padding
        month_container.pack_propagate(False)
        
        # Month Dropdown with month names
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        self.month_dropdown = ctk.CTkOptionMenu(
            month_container,
            width=118,
            height=26,
            corner_radius=5,
            font=ctk.CTkFont("Roboto", 10),  # Smaller font
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
        self.month_dropdown.set("January")  # Changed from "June" to "January"
        
        # Day Dropdown Container - smaller
        day_container = ctk.CTkFrame(
            date_fields,
            width=80,  # Reduced width
            height=28,
            corner_radius=5,
            fg_color="#ffffff",
            border_width=1,
            border_color="#d1d1d1"
        )
        day_container.pack(side="left", padx=(0, 8))  # Reduced padding
        day_container.pack_propagate(False)
        
        self.day_dropdown = ctk.CTkOptionMenu(
            day_container,
            width=78,
            height=26,
            corner_radius=5,
            font=ctk.CTkFont("Roboto", 10),  # Smaller font
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
        
        # Year Dropdown Container - smaller
        year_container = ctk.CTkFrame(
            date_fields,
            width=100,  # Reduced width
            height=28,
            corner_radius=5,
            fg_color="#ffffff",
            border_width=1,
            border_color="#d1d1d1"
        )
        year_container.pack(side="left")
        year_container.pack_propagate(False)
        
        # Year Dropdown
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
            font=ctk.CTkFont("Roboto", 10),  # Smaller font
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
        self.year_dropdown.set("2001")  # Changed to 2001
        
        # Schedule dropdown height configuration after widget creation
        self.after(100, self._configure_year_dropdown_height)

        # Configure dropdown to show limited items
        try:
            if hasattr(self.year_dropdown, '_dropdown_menu'):
                self.year_dropdown._dropdown_menu.configure(tearoff=0)
        except:
            pass
        
        # Initialize days based on default month and year
        self._update_days()

        # Contact Number - more compact
        contact_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        contact_container.place(x=15, y=135)  # Adjusted position
        
        ctk.CTkLabel(
            contact_container,
            text="Contact Number",
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            text_color="#707070"
        ).pack(anchor="w")
        
        self.contact_entry = ctk.CTkEntry(
            contact_container,
            width=180,  # Reduced width
            height=26,  # Reduced height
            corner_radius=5,
            border_width=1,
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            textvariable=self.contact_number_var
        )
        self.contact_entry.pack(pady=(2, 0))
        
        # Student Number - more compact
        student_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        student_container.place(x=15, y=185)  # Adjusted position
        
        ctk.CTkLabel(
            student_container,
            text="Student Number",
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            text_color="#707070"
        ).pack(anchor="w")
        
        self.student_entry = ctk.CTkEntry(
            student_container,
            width=385,  # Adjusted for smaller card
            height=26,  # Reduced height
            corner_radius=5,
            border_width=1,
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            textvariable=self.student_number_var
        )
        self.student_entry.pack(pady=(2, 0))
        
        # Webmail Address - more compact
        webmail_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        webmail_container.place(x=15, y=235)  # Adjusted position
        
        ctk.CTkLabel(
            webmail_container,
            text="Webmail Address",
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            text_color="#707070"
        ).pack(anchor="w")
        
        self.webmail_entry = ctk.CTkEntry(
            webmail_container,
            width=385,  # Adjusted for smaller card
            height=26,  # Reduced height
            corner_radius=5,
            border_width=1,
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            textvariable=self.email_var
        )
        self.webmail_entry.pack(pady=(2, 0))
        
        # Password - more compact
        password_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        password_container.place(x=15, y=285)  # Adjusted position
        
        ctk.CTkLabel(
            password_container,
            text="Password",
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            text_color="#707070"
        ).pack(anchor="w")
        
        self.password_entry = ctk.CTkEntry(
            password_container,
            width=385,  # Adjusted for smaller card
            height=26,  # Reduced height
            corner_radius=5,
            border_width=1,
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            show="•",
            textvariable=self.password_var
        )
        self.password_entry.pack(pady=(2, 0))
        
        # Confirm Password - more compact
        confirm_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        confirm_container.place(x=15, y=335)  # Adjusted position
        
        ctk.CTkLabel(
            confirm_container,
            text="Confirm Password",
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            text_color="#707070"
        ).pack(anchor="w")
        
        self.confirm_entry = ctk.CTkEntry(
            confirm_container,
            width=385,  # Adjusted for smaller card
            height=26,  # Reduced height
            corner_radius=5,
            border_width=1,
            font=ctk.CTkFont("Roboto", 11),  # Smaller font
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            show="•",
            textvariable=self.confirm_password_var
        )
        self.confirm_entry.pack(pady=(2, 0))
        
        # Terms and Condition Checkbox - more compact
        terms_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        terms_container.place(x=15, y=400)  # Adjusted position
        
        self.terms_checkbox = ctk.CTkCheckBox(
            terms_container,
            text="I agree to the Terms and Conditions",
            font=ctk.CTkFont("Roboto", 10),
            text_color="#1E3A8A",  # Changed to blue to highlight clickable text
            fg_color="#1E3A8A",
            hover_color="#1E3A8A",
            border_color="#d1d1d1",
            checkbox_width=14,
            checkbox_height=14,
            corner_radius=2,
            border_width=1
        )
        self.terms_checkbox.pack(anchor="w")
        
        # Bind click event to open terms modal when clicking on the text
        self.terms_checkbox.bind("<Button-1>", self._on_terms_checkbox_click)
        
        # Validation Label (initially hidden) - more compact
        self.validation_label = ctk.CTkLabel(
            self.card_frame,
            text="",
            font=ctk.CTkFont("Roboto", 10),  # Smaller font
            text_color="#dc2626",
            wraplength=380,
            justify="left"
        )
        self.validation_label.place(x=15, y=425)  # Adjusted position
        self.validation_label.place_forget()
        
        # Sign Up Button - more compact
        self.signup_button = ctk.CTkButton(
            self.card_frame,
            text="Sign Up",
            width=140,  # Reduced width
            height=34,  # Reduced height
            corner_radius=8,
            border_width=1,
            font=ctk.CTkFont("Roboto", 11, "bold"),  # Smaller font
            fg_color="#1E3A8A",
            hover_color="#152a63",
            command=self.handle_register
        )
        self.signup_button.place(x=260, y=505)  # Adjusted position

    def get_form_data(self):
        """Get all form data as a dictionary"""
        return {
            'first_name': self.first_name_var.get(),
            'last_name': self.last_name_var.get(),
            'email': self.email_var.get(),
            'contact_number': self.contact_number_var.get(),
            'student_number': self.student_number_var.get(),
            'password': self.password_var.get(),
            'confirm_password': self.confirm_password_var.get()
        }

    def on_registration_success(self, email):
        """Handle successful registration"""
        # Reset form fields
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.email_var.set("")
        self.student_number_var.set("")
        self.password_var.set("")
        self.confirm_password_var.set("")
        
        # Call parent success handler
        if self.on_success:
            self.on_success(email)

    def play_error_sound(self):
        """Play error sound effect"""
        try:
            # Use Windows system error sound
            winsound.MessageBeep(winsound.MB_ICONHAND)
        except Exception as e:
            # Fallback to system beep if winsound fails
            try:
                print('\a')  # ASCII bell character
            except:
                pass  # Silent fallback

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

    def show_validation_error(self, message):
        """Show validation error with sound and animation"""
        # Play error sound
        self.play_error_sound()
        
        # Start shake animation
        self.shake_card()
        
        # Show error message
        self.validation_label.configure(text=message)
        self.validation_label.place(x=15, y=425)

    def hide_validation_error(self):
        """Hide the validation error label"""
        self.validation_label.place_forget()

    def handle_register(self):
        """Process the registration form submission"""
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

            # Check terms and conditions
            if not self.terms_checkbox.get():
                errors.append("• Please agree to the Terms and Conditions")

            # Validate email and student ID uniqueness before camera
            if self.db_manager:
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
                    # Don't add to errors list to avoid showing in GUI unless it's a real connection issue
                    pass

            # Show errors if any exist
            if errors:
                error_message = "\n".join(errors)
                self.show_validation_error(error_message)
                return

            # Open face verification dialog only after all validations pass
            self.open_face_verification_dialog()
            
        except Exception as e:
            self.show_validation_error(f"• An unexpected error occurred: {str(e)}")
            import traceback
            traceback.print_exc()

    def open_face_verification_dialog(self):
        """Open the face verification dialog"""
        self.verification_dialog = ctk.CTkToplevel(self)
        self.verification_dialog.title("Face Verification")
        self.verification_dialog.geometry("454x450")  # Back to original height
        self.verification_dialog.resizable(False, False)
        self.verification_dialog.configure(fg_color="#222222")

        # Make dialog modal
        self.verification_dialog.grab_set()

        # Center dialog
        self.verification_dialog.update_idletasks()
        width = self.verification_dialog.winfo_width()
        height = self.verification_dialog.winfo_height()
        x = (self.verification_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.verification_dialog.winfo_screenheight() // 2) - (height // 2)
        self.verification_dialog.geometry(f"{width}x{height}+{x}+{y}")

        self._create_verification_dialog_content()
        
        # Bind dialog close to cleanup
        self.verification_dialog.protocol("WM_DELETE_WINDOW", self.on_verification_dialog_closing)

    def _create_verification_dialog_content(self):
        """Create content for the face verification dialog"""
        # Card Frame
        card = ctk.CTkFrame(self.verification_dialog, width=454, height=450, corner_radius=12, fg_color="#ffffff", border_width=0)  # Back to original height
        card.place(x=0, y=0)
        card.pack_propagate(False)

        # Info icon (top right)
        info_btn = ctk.CTkButton(
            card, 
            text="i", 
            width=24, 
            height=24, 
            corner_radius=12, 
            fg_color="#f5f5f5", 
            text_color="#222", 
            font=ctk.CTkFont("Roboto", 14, "bold"), 
            hover_color="#e0e0e0", 
            command=lambda: messagebox.showinfo("Info", "Please ensure you're in a well-lit environment before capturing your photo for the best image quality", parent=self.verification_dialog)
        )
        info_btn.place(x=420, y=10)

        # Camera Preview Frame - Set to 240px height
        self.face_preview_frame = ctk.CTkFrame(card, width=410, height=240, fg_color="#fafafa", border_width=1, border_color="#d1d1d1")
        self.face_preview_frame.place(x=22, y=38)
        self.face_preview_frame.pack_propagate(False)

        # Default Preview Label (centered)
        self.preview_label = ctk.CTkLabel(
            self.face_preview_frame,
            text="Camera will appear here\nClick 'Open Camera' to begin",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#a0a0a0"
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Open Camera Button - adjusted position
        self.camera_button = ctk.CTkButton(
            card,
            text="Open Camera",
            width=410,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont("Roboto", 13, "bold"),
            fg_color="#ffffff",
            text_color="#222",
            border_width=1,
            border_color="#d1d1d1",
            hover_color="#f5f5f5",
            command=self.toggle_camera
        )
        self.camera_button.place(x=22, y=290)  # Adjusted from y=330 to y=290

        # Retake and Capture Buttons - adjusted position
        self.retake_button = ctk.CTkButton(
            card,
            text="Retake",
            width=200,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 13, "bold"),
            fg_color="#e5e5e5",
            text_color="#707070",
            border_width=0,
            hover_color="#cccccc",
            state="disabled",  # Start disabled
            command=self.retake_photo
        )
        self.retake_button.place(x=22, y=335)  # Adjusted from y=375 to y=335

        self.capture_button = ctk.CTkButton(
            card,
            text="Capture",
            width=200,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 13, "bold"),
            fg_color="#1E3A8A",
            text_color="#fff",
            border_width=0,
            hover_color="#152a63",
            state="disabled",
            command=self.capture_face
        )
        self.capture_button.place(x=232, y=335)  # Adjusted from y=375 to y=335

        # Register Button - adjusted position
        self.register_button = ctk.CTkButton(
            card,
            text="Complete Registration",
            width=410,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 13, "bold"),
            fg_color="#1E3A8A",
            text_color="#fff",
            border_width=0,
            hover_color="#152a63",
            command=self.complete_registration,
            state="disabled"
        )
        self.register_button.place(x=22, y=385)  # Adjusted from y=420 to y=385

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
            
            # Create canvas for camera display - 240px height
            self.camera_canvas = tk.Canvas(
                self.face_preview_frame,
                width=410,
                height=240,
                bg="#fafafa",
                highlightthickness=0
            )
            self.camera_canvas.place(x=0, y=0)
            
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
                    

                    # Draw face positioning guide rectangle - made larger
                    rect_w, rect_h = 160, 180  # Increased from 120, 140 to 160, 180
                    cv2.rectangle(frame_rgb, 
                                 (center_x - rect_w//2, center_y - rect_h//2),
                                 (center_x + rect_w//2, center_y + rect_h//2),
                                 (0, 255, 0), 2)
                    
                    # Convert to PIL Image (do this in thread)
                    try:
                        pil_image = Image.fromarray(frame_rgb)
                        
                        # Schedule UI update on main thread with the PIL image
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
                                        self.camera_canvas.create_image(205, 120, image=photo, anchor="center")  # Updated center position
                                        
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
        
        # Update UI on main thread
        if self.verification_dialog and self.verification_dialog.winfo_exists():
            self.verification_dialog.after(0, self._update_ui_after_camera_close)

    def show_face_preview(self):
        """Show face image preview"""
        try:
            # Clear existing widgets in preview frame
            for widget in self.face_preview_frame.winfo_children():
                widget.destroy()
            
            if self.face_image:
                # Create canvas for displaying captured image - 240px height
                preview_canvas = tk.Canvas(
                    self.face_preview_frame,
                    width=410,
                    height=240,
                    bg="#fafafa",
                    highlightthickness=0
                )
                preview_canvas.place(x=0, y=0)
                
                # Convert image to PhotoImage and display
                preview_img = self.face_image.copy()
                preview_img.thumbnail((410, 240), Image.LANCZOS)
                photo = ImageTk.PhotoImage(preview_img)
                
                preview_canvas.create_image(205, 120, image=photo, anchor="center")
                
                # Keep reference to prevent garbage collection
                preview_canvas.image = photo
            else:
                # Show success message using CTkLabel
                preview_text = ctk.CTkLabel(
                    self.face_preview_frame,
                    text="✓ Photo Captured Successfully!\nReady for registration",
                    font=ctk.CTkFont("Roboto", 14, "bold"),
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

    def complete_registration(self):
        """Complete the registration process"""
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
            
            # Get form data
            first_name = self.first_name_var.get().strip()
            last_name = self.last_name_var.get().strip()
            email = self.email_var.get().strip()
            contact_number = self.contact_number_var.get().strip()
            student_number = self.student_number_var.get().strip()
            password = self.password_var.get().strip()
            
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
            
            # Validate date of birth
            try:
                if day and month and year:
                    day_int = int(day)
                    month_int = int(month)
                    year_int = int(year)
                    date_of_birth = f"{year}-{month}-{day}"
                else:
                    date_of_birth = None
            except ValueError:
                messagebox.showwarning(
                    "Invalid Date",
                    "Please select a valid date of birth.",
                    parent=self.verification_dialog
                )
                self.verification_dialog.configure(cursor="")
                return
            
            # Reset cursor
            self.verification_dialog.configure(cursor="")
            
            # Clean up camera
            if self.is_camera_active:
                self.stop_camera()
            
            # Prepare registration data for OTP verification
            registration_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'student_number': student_number,
                'password': password,
                'face_image': self.face_image_data,
                'contact_number': contact_number,
                'date_of_birth': date_of_birth
            }
            
            # Close verification dialog
            self.verification_dialog.destroy()
            
            # Open registration OTP dialog
            self.open_registration_otp_dialog(email, registration_data)
                
        except Exception as e:
            self.verification_dialog.configure(cursor="")
            messagebox.showerror(
                "Registration Error", 
                f"An unexpected error occurred during registration:\n{str(e)}",
                parent=self.verification_dialog
            )
            import traceback
            traceback.print_exc()

    def open_registration_otp_dialog(self, email, registration_data):
        """Open the registration OTP verification dialog"""
        try:
            # Import the registration OTP dialog
            from .register_otp import RegisterOTPDialog
            
            root_window = self.winfo_toplevel()
            dialog = RegisterOTPDialog(
                root_window,
                db_manager=self.db_manager,
                email=email,
                registration_data=registration_data,
                on_success=self.on_registration_success
            )
            dialog.focus()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open OTP verification: {str(e)}")

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
            
    def _update_ui_after_camera_close(self):
        """Update UI after camera window is closed"""
        self.camera_button.configure(text="Open Camera")
        self.capture_button.configure(state="disabled")
        
        # Only show preview label if no face is captured
        if not self.face_image:
            self.preview_label = ctk.CTkLabel(
                self.face_preview_frame,
                text="Camera will appear here\nClick 'Open Camera' to begin",
                font=ctk.CTkFont("Roboto", 12),
                text_color="#a0a0a0"
            )
            self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

    def capture_face(self):
        """Capture face using the Capture button"""
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
            
            messagebox.showinfo("Success", "Face image captured successfully! You can now proceed with registration.", parent=self.verification_dialog)
            
        except Exception as e:
            print(f"Capture error: {e}")
            messagebox.showerror("Error", f"Failed to capture image: {str(e)}", parent=self.verification_dialog)

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
        
        self.capture_button.configure(state="disabled")
        
        # Enable registration button
        self.register_button.configure(state="normal")
        
        # Enable and style retake button
        self.retake_button.configure(
            state="normal",
            fg_color="#dc2626",  # Red color for retake
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
            font=ctk.CTkFont("Roboto", 12),
            text_color="#a0a0a0"
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.start_camera()

    def _reset_buttons_for_retake(self):
        """Reset button states when retaking photo"""
        # Re-enable camera button
        self.camera_button.configure(
            state="normal",
            text="Close Camera",  # Will be set to "Open Camera" after camera starts
            fg_color="#ffffff",
            text_color="#222",
            hover_color="#f5f5f5"
        )
        
        # Disable registration button since no face is captured
        self.register_button.configure(state="disabled")
        
        # Disable and reset retake button
        self.retake_button.configure(
            state="disabled",
            fg_color="#e5e5e5",
            text_color="#707070",
            hover_color="#cccccc"
        )
        
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
                font=ctk.CTkFont("Roboto", 12),
                text_color="#a0a0a0"
            )
            self.preview_label.place(relx=0.5, rely=0.5, anchor="center")
        # Capture button will be enabled when camera starts

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

    def _configure_year_dropdown_height(self):
        """Configure the year dropdown to limit its height and enable scrolling"""
        try:
            # Access the internal dropdown menu
            if hasattr(self.year_dropdown, '_dropdown_menu') and self.year_dropdown._dropdown_menu:
                menu = self.year_dropdown._dropdown_menu
                
                # Configure the menu to be scrollable with limited height
                menu.configure(
                    tearoff=0,
                    postcommand=self._setup_year_dropdown_scroll
                )
                
        except Exception as e:
            print(f"Could not configure dropdown height: {e}")
    
    def _setup_year_dropdown_scroll(self):
        """Setup scrolling for the year dropdown menu"""
        try:
            if hasattr(self.year_dropdown, '_dropdown_menu') and self.year_dropdown._dropdown_menu:
                menu = self.year_dropdown._dropdown_menu
                
                # Get screen height to calculate max menu height
                screen_height = self.winfo_screenheight()
                max_menu_height = min(300, screen_height // 3)  # Limit to 300px or 1/3 of screen
                
                # Calculate the number of items that can fit
                item_height = 25  # Approximate height per menu item
                max_visible_items = max_menu_height // item_height
                
                # If we have more items than can fit, enable scrolling
                total_items = len(self.year_dropdown.cget("values"))
                if total_items > max_visible_items:
                    # Find the index of the current selection (2001)
                    current_value = self.year_dropdown.get()
                    try:
                        current_index = self.year_dropdown.cget("values").index(current_value)
                        
                        # Calculate scroll position to center around current value
                        start_index = max(0, current_index - max_visible_items // 2)
                        
                        # Set the view to start at the calculated position
                        menu.yview_moveto(start_index / total_items)
                        
                    except (ValueError, AttributeError):
                        # If we can't find the current value, scroll to a reasonable position
                        # Try to find 2001 or scroll to middle
                        try:
                            year_2001_index = self.year_dropdown.cget("values").index("2001")
                            start_index = max(0, year_2001_index - max_visible_items // 2)
                            menu.yview_moveto(start_index / total_items)
                        except ValueError:
                            # Just scroll to middle if 2001 not found
                            menu.yview_moveto(0.5)
                            
        except Exception as e:
            print(f"Error setting up dropdown scroll: {e}")
    
    def _limit_dropdown_height(self):
        """Legacy method - replaced by _setup_year_dropdown_scroll"""
        # This method is kept for compatibility but the new _setup_year_dropdown_scroll
        # provides better scrolling functionality
        self._setup_year_dropdown_scroll()

    def open_terms_modal(self, event=None):
        """Open the Terms of Use & Privacy Statement modal"""
        # Create modal dialog
        self.terms_modal = ctk.CTkToplevel(self)
        self.terms_modal.title("Terms of Use & Privacy Statement")
        self.terms_modal.geometry("700x600")  # Increased size for better readability
        self.terms_modal.resizable(True, True)
        self.terms_modal.configure(fg_color="#ffffff")
        
        # Make modal and center it
        self.terms_modal.grab_set()
        self.terms_modal.update_idletasks()
        
        # Center the modal
        width = self.terms_modal.winfo_width()
        height = self.terms_modal.winfo_height()
        x = (self.terms_modal.winfo_screenwidth() // 2) - (width // 2)
        y = (self.terms_modal.winfo_screenheight() // 2) - (height // 2)
        self.terms_modal.geometry(f"{width}x{height}+{x}+{y}")
        
        # Header
        header_frame = ctk.CTkFrame(self.terms_modal, fg_color="transparent", height=50)
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="Terms of Use & Privacy Statement",
            font=ctk.CTkFont("Roboto", 20, "bold"),
            text_color="#1E3A8A"
        ).pack(anchor="w")
        
        # Scrollable text frame
        text_frame = ctk.CTkScrollableFrame(
            self.terms_modal,
            width=660,  # Increased width
            height=450,  # Increased height
            fg_color="#f8f9fa",
            border_width=1,
            border_color="#e9ecef"
        )
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Updated Terms and Conditions Content
        terms_content = """
FACIAL RECOGNITION ATTENDANCE SYSTEM - ATTENDIFY

Terms of Use

1. Acceptance of Terms
By accessing or using the Facial Recognition Attendance System Attendify, you agree to be bound by these Terms of Use. If you do not agree to these Terms, you are not authorized to access nor use the system.

2. Purpose of the System
The system is developed to streamline and automate attendance tracking through facial recognition technology. It is intended solely for authorized use by organizations, administrators, and approved users for attendance monitoring and management.

3. User Responsibilities
By using the System, you agree to:
• Use the System only for its intended purpose and in accordance with applicable laws and regulations.
• Refrain from attempting to reverse-engineer, modify, disrupt, or misuse the System or any data it processes.
• Maintain the confidentiality of any account credentials provided to you and promptly notify us of any unauthorized use.

4. Intellectual Property
The System, including all software, algorithms, designs, and associated intellectual property, is owned by Attendify or its licensors. You may not copy, reproduce, distribute, or create derivative works from the System without prior written consent from Attendify.

5. Termination
Attendify reserves the right to suspend or terminate your access to the System at any time, with or without notice, if you violate these Terms or engage in unlawful or unauthorized activities.

6. Limitation of Liability
The System is provided "as is" without warranties of any kind. Attendify shall not be liable for any damages arising from the use or inability to use the System, including but not limited to system errors, data loss, or downtime.

7. Changes to Terms
We may update these Terms at any time. Continued use of the System after changes constitutes your acceptance of the revised Terms.

Privacy Statement

1. Information We Collect
The Facial Recognition Attendance System collects the following personal information:
• Biometric Data: Facial images or templates used for attendance tracking.
• Personal Information: Name, employee ID, or other identifiers linked to attendance records.
• Usage Data: Logs of system interactions, such as timestamps of attendance records.

2. How We Use Your Information
We collect and use data to:
• Authenticate identities and record attendance.
• Enhance the System's reliability, performance, and accuracy.
• Comply with legal obligations or organizational policies.

3. Data Storage and Security
All biometric data is encrypted and stored securely to prevent unauthorized access. Personal and usage data are stored with industry-standard security measures. We retain data only as long as necessary to fulfill attendance purposes or legal obligations.

4. Data Sharing
We do not share your data with third parties unless:
• You have given explicit consent.
• It is required by law or a valid legal request.
• It is shared with trusted service providers under strict confidentiality agreements to help operate or support the System.

5. Your Rights
You may have the right, in accordance with applicable laws, to:
• Access, review, correct, or request deletion of your personal data.
• Request information about how your data is collected and used.

6. Data Retention
Biometric and personal data are deleted once they are no longer needed for attendance tracking or as required by applicable law. You may request earlier deletion of your data where legally permitted.

7. Contact Us
For any questions, concerns, or requests related to these Terms or our Privacy Statement, please contact us at:
📧 attendify.attendancesystem@gmail.com

8. Changes to Privacy Statement
This Privacy Statement may be updated periodically. Any significant changes will be communicated through the System or via other appropriate means.

By clicking "I Agree," you acknowledge that you have read, understood, and agree to be bound by these Terms of Use and Privacy Statement.
        """
        
        # Add terms content to scrollable frame
        terms_label = ctk.CTkLabel(
            text_frame,
            text=terms_content.strip(),
            font=ctk.CTkFont("Roboto", 11),
            text_color="#333333",
            justify="left",
            wraplength=620  # Increased wrap length
        )
        terms_label.pack(anchor="w", padx=10, pady=10)
        
        # Button frame for centering
        button_frame = ctk.CTkFrame(self.terms_modal, fg_color="transparent", height=60)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        button_frame.pack_propagate(False)
        
        # Agree button (centered)
        agree_button = ctk.CTkButton(
            button_frame,
            text="I Agree",
            width=120,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12, "bold"),
            fg_color="#1E3A8A",
            hover_color="#152a63",
            command=self.agree_to_terms
        )
        agree_button.pack(anchor="center")
        
        # Handle modal close
        self.terms_modal.protocol("WM_DELETE_WINDOW", self.close_terms_modal)

    def agree_to_terms(self):
        """Handle agreeing to terms - check the checkbox and close modal"""
        self.terms_checkbox.select()  # Check the checkbox
        self.close_terms_modal()
    
    def close_terms_modal(self):
        """Close the terms modal"""
        if hasattr(self, 'terms_modal') and self.terms_modal:
            self.terms_modal.destroy()
            self.terms_modal = None

    def _on_terms_checkbox_click(self, event):
        """Handle clicking on terms checkbox - open modal if clicking on text area"""
        # Get the click position relative to the checkbox widget
        x = event.x
        
        # If click is beyond the checkbox itself (i.e., on the text), open terms modal
        # Checkbox is about 14px wide, so clicks beyond x=20 are likely on text
        if x > 20:
            # Prevent the checkbox from toggling
            self.after(1, lambda: self.terms_checkbox.deselect() if self.terms_checkbox.get() else self.terms_checkbox.select())
            # Open terms modal
            self.open_terms_modal()
