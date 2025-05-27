import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from customtkinter.windows.widgets.image import CTkImage  # Add this import
import cv2
import threading
import time
import io
import numpy as np
import os

# Set appearance mode and theme
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("dark-blue")  

class LoginRegister(ctk.CTk):
    def __init__(self, db_manager=None):
        super().__init__()
        self.title("Iskoptrix - Face Recognition Attendance System")
        self.geometry("1000x600")
        self.resizable(False, False)
        
        # Store database manager reference
        self.db_manager = db_manager
        
        # Initialize variables
        self.camera = None
        self.is_camera_active = False
        self.face_image = None
        self.face_image_data = None
        self.user_data = None
        self.on_login_success = None  # Callback for successful login

        # Create StringVar for form fields
        self.first_name_var = tk.StringVar()
        self.middle_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.student_number_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()

        # Build the UI layout
        self._create_main_layout()
        self.show_login()

    def _create_main_layout(self):
        """Create the main UI layout"""
        # Main Container
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left Frame (Branding)
        self.left_frame = ctk.CTkFrame(self.main_frame, width=300, corner_radius=15, fg_color="#1e1e2f")
        self.left_frame.pack(side="left", fill="both", padx=(0, 6))

        # Branding text
        ctk.CTkLabel(
            self.left_frame,
            text="Iskoptrix",
            font=ctk.CTkFont("Roboto", 28, "bold"),
            text_color="#ffffff"
        ).place(relx=0.5, rely=0.4, anchor="center")
        
        ctk.CTkLabel(
            self.left_frame,
            text="Face Recognition Attendance System",
            font=ctk.CTkFont("Roboto", 16),
            text_color="#a0a0a0"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Right Frame (Form)
        self.right_frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#2b2b3b")
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Form Container
        self.form_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.form_container.pack(fill="both", expand=True, pady=10, padx=20)

    def clear_form(self):
        """Clear all widgets from the form container"""
        # Reset variables before clearing form to prevent callbacks to non-existent widgets
        self.reset_form_fields()
        
        # Now destroy widgets
        for widget in self.form_container.winfo_children():
            widget.destroy()
    
    # 1. First modify the reset_form_fields method:

    def reset_form_fields(self):
        """Reset all form fields by creating new StringVar instances"""
        # Instead of setting values to empty strings, create brand new StringVars
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.first_name_var = tk.StringVar() 
        self.middle_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.student_number_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()
        
        # Reset face data
        self.face_image = None
        self.face_image_data = None

    def show_login(self):
        """Show the login form"""
        self.reset_form_fields()
        self.clear_form()

        # Inner frame to center the form
        inner_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        inner_frame.pack(expand=True)

        # Title
        ctk.CTkLabel(
            inner_frame,
            text="Welcome Back",
            font=ctk.CTkFont("Roboto", 16, "bold"),
            text_color="#ffffff"
        ).pack(pady=(0, 6))

        # Grid Frame for Side-by-Side Labels and Inputs
        grid_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        grid_frame.pack(pady=(4, 4))

        # Row 1: Email Label and Input
        ctk.CTkLabel(grid_frame, text="Email", font=ctk.CTkFont("Roboto", 9)).grid(
            row=0, column=0, padx=(0, 8), pady=(0, 2), sticky="w")
            
        self.email_entry = ctk.CTkEntry(
            grid_frame,
            width=240,
            height=26,
            corner_radius=6,
            font=ctk.CTkFont("Roboto", 9),
            fg_color="#3a3a4a",
            border_width=0,
            textvariable=self.email_var
        )
        self.email_entry.grid(row=0, column=1)

        # Row 2: Password Label and Input
        ctk.CTkLabel(grid_frame, text="Password", font=ctk.CTkFont("Roboto", 9)).grid(
            row=1, column=0, padx=(0, 8), pady=(6, 2), sticky="w")
            
        self.password_entry = ctk.CTkEntry(
            grid_frame,
            width=240,
            height=26,
            corner_radius=6,
            font=ctk.CTkFont("Roboto", 9),
            fg_color="#3a3a4a",
            border_width=0,
            show="*",
            textvariable=self.password_var
        )
        self.password_entry.grid(row=1, column=1)

        # Login Button
        self.login_button = ctk.CTkButton(
            inner_frame,
            text="Login",
            width=120,
            height=30,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 11, "bold"),
            fg_color="#6363ff",
            hover_color="#4b4bff",
            command=self.handle_login
        )
        self.login_button.pack(pady=10)

        # Register Link
        link = ctk.CTkLabel(
            inner_frame,
            text="Don't have an account? Register",
            font=ctk.CTkFont("Roboto", 9),
            text_color="#6363ff",
            cursor="hand2"
        )
        link.pack(pady=(4, 6))
        link.bind("<Button-1>", lambda e: self.show_register())

    def show_register(self):
        """Show the registration form"""
        self.reset_form_fields()
        self.clear_form()

        # Inner frame to center the form
        inner_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        inner_frame.pack(expand=True)

        # Title
        ctk.CTkLabel(
            inner_frame,
            text="Create Account",
            font=ctk.CTkFont("Roboto", 16, "bold"),
            text_color="#ffffff"
        ).pack(pady=10)

        # Frame for stacked fields
        fields_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        fields_frame.pack(pady=(4, 4))

        # Helper function to add form fields
        def add_field(parent, label_text, var, is_password=False):
            field_wrapper = ctk.CTkFrame(parent, fg_color="transparent")
            field_wrapper.pack(fill="x")

            label = ctk.CTkLabel(
                field_wrapper,
                text=label_text,
                font=ctk.CTkFont("Roboto", 9),
                anchor="w",
                width=240
            )
            label.pack(anchor="w", padx=(10, 0))

            entry = ctk.CTkEntry(
                field_wrapper,
                width=240,
                height=26,
                corner_radius=6,
                font=ctk.CTkFont("Roboto", 9),
                fg_color="#3a3a4a",
                border_width=0,
                show="*" if is_password else "",
                textvariable=var
            )
            entry.pack(padx=(10, 0))
            return entry

        # Add all fields with associated StringVars
        self.first_name_entry = add_field(fields_frame, "First Name", self.first_name_var)
        self.middle_name_entry = add_field(fields_frame, "Middle Name", self.middle_name_var)
        self.last_name_entry = add_field(fields_frame, "Last Name", self.last_name_var)
        self.email_entry = add_field(fields_frame, "Email", self.email_var)
        self.student_number_entry = add_field(fields_frame, "Student ID", self.student_number_var)
        self.password_entry = add_field(fields_frame, "Password", self.password_var, is_password=True)
        self.confirm_password_entry = add_field(fields_frame, "Confirm Password", self.confirm_password_var, is_password=True)

        # Register Button
        register_button = ctk.CTkButton(
            inner_frame,
            text="Register",
            width=240,
            height=30,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 11, "bold"),
            fg_color="#6363ff",
            hover_color="#4b4bff",
            command=self.open_verification_dialog
        )
        register_button.pack(pady=10)

        # Login Link
        link = ctk.CTkLabel(
            inner_frame,
            text="Already have an account? Login",
            font=ctk.CTkFont("Roboto", 9),
            text_color="#6363ff",
            cursor="hand2"
        )
        link.pack(pady=(4, 6))
        link.bind("<Button-1>", lambda e: self.show_login())

        # Set focus to first name field
        self.first_name_entry.focus_set()

    # Method to set a callback for successful login
    def set_login_success_callback(self, callback):
        """Set a callback function to be called after successful login"""
        self.on_login_success = callback

    # Login handling method
    def handle_login(self):
        """Handle login button click"""
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        
        if not email or not password:
            messagebox.showwarning("Login Failed", "Please enter both email and password.")
            return
        
        self.config(cursor="wait")
        self.update_idletasks()
        
        # Call the database manager
        if self.db_manager:
            success, result = self.db_manager.login(email, password)
        else:
            success, result = False, "Database manager not initialized"
        
        self.config(cursor="")
        
        if success:
            # Clear form fields
            self.email_var.set("")
            self.password_var.set("")
            
            # Store the user data and determine role
            self.user_data = result
            self.store_user_data(result)
            
            # Call external success handler if provided
            if self.on_login_success:
                self.on_login_success(result)
        else:
            messagebox.showerror("Login Failed", result)

    def store_user_data(self, user_data):
        """Store user data after successful login"""
        self.user_data = user_data
        
        # Save the user ID for convenience
        self.user_id = user_data.get('id')
        
        # Save role for navigation decisions
        self.user_role = user_data.get('role', 'student').lower()
        
        # Check if user has a face image
        self.has_face_image = bool(user_data.get('face_image'))

    # --- Face Registration Dialog Methods ---
    def open_verification_dialog(self):
        """Open dialog for face verification during registration, but validate fields first"""
        # Basic validation before opening dialog
        first_name = self.first_name_var.get().strip()
        last_name = self.last_name_var.get().strip()
        email = self.email_var.get().strip()
        student_number = self.student_number_var.get().strip()
        password = self.password_var.get().strip()
        confirm_password = self.confirm_password_var.get().strip()

        # Validate required fields
        if not first_name or not last_name or not email or not student_number or not password:
            messagebox.showwarning("Registration Failed", "Please fill in all required fields.")
            return

        if password != confirm_password:
            messagebox.showwarning("Registration Failed", "Passwords do not match.")
            return
            
        # Show waiting cursor during validation
        self.config(cursor="wait")
        self.update_idletasks()
        
        # Check if email or student ID already exists
        if self.db_manager:
            # Check email
            email_exists, _ = self.db_manager.check_email_exists(email)
            if email_exists:
                self.config(cursor="")
                messagebox.showwarning("Registration Failed", "This email address is already registered.")
                return
                
            # Check student number 
            student_id_exists, _ = self.db_manager.check_student_id_exists(student_number)
            if student_id_exists:
                self.config(cursor="")
                messagebox.showwarning("Registration Failed", "This student ID is already registered.")
                return
        
        # Restore cursor
        self.config(cursor="")
        
        # All validations passed, now open the face verification dialog
        # Create a new dialog window with MUCH LARGER SIZE
        self.dialog = ctk.CTkToplevel(self)
        self.dialog.title("Complete Registration")
        self.dialog.geometry("500x700")  # INCREASED SIGNIFICANTLY from 450x600 to 500x700
        self.dialog.resizable(False, False)
        self.dialog.configure(fg_color="#2b2b3b")

        # Make dialog modal
        self.dialog.grab_set()

        # Center dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

        self._create_verification_dialog_content()

    def _create_verification_dialog_content(self):
        """Create content for the face verification dialog"""
        # Inner frame to center content
        inner_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        inner_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            inner_frame,
            text="Complete Registration",
            font=ctk.CTkFont("Roboto", 16, "bold"),
            text_color="#ffffff"
        ).pack(pady=(0, 10))

        # Face Registration Section
        face_frame = ctk.CTkFrame(inner_frame, fg_color="#2b2b3b")
        face_frame.pack(fill="x", pady=10)

        # Face Preview Frame
        self.face_preview_frame = ctk.CTkFrame(face_frame, width=320, height=240, fg_color="#3a3a4a")
        self.face_preview_frame.pack(pady=10)
        self.face_preview_frame.pack_propagate(False)

        # Default Preview Label
        self.preview_label = ctk.CTkLabel(
            self.face_preview_frame,
            text="No face image captured",
            font=ctk.CTkFont("Roboto", 10),
            text_color="#a0a0a0"
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Camera Controls Frame - Use a centered approach
        face_buttons_frame = ctk.CTkFrame(face_frame, fg_color="transparent")
        face_buttons_frame.pack(fill="x", pady=5)
        
        # Add a spacer frame on the left for centering
        left_spacer = ctk.CTkFrame(face_buttons_frame, fg_color="transparent", width=20)
        left_spacer.pack(side="left", expand=True)

        # Open Camera Button
        self.camera_button = ctk.CTkButton(
            face_buttons_frame,
            text="Open Camera",
            width=120,
            height=30,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 11),
            fg_color="#6363ff",
            hover_color="#4b4bff",
            command=self.toggle_camera
        )
        self.camera_button.pack(side="left", padx=5)

        # Capture Button
        self.capture_button = ctk.CTkButton(
            face_buttons_frame,
            text="Capture",
            width=120,
            height=30,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 11),
            fg_color="#6363ff",
            hover_color="#4b4bff",
            state="disabled",
            command=self.capture_face
        )
        self.capture_button.pack(side="left", padx=5)
        
        # Add a spacer frame on the right for centering
        right_spacer = ctk.CTkFrame(face_buttons_frame, fg_color="transparent", width=20)
        right_spacer.pack(side="left", expand=True)

        # Instructions Label
        ctk.CTkLabel(
            inner_frame,
            text="* Face image is required for registration",
            font=ctk.CTkFont("Roboto", 10, weight="normal", slant="italic"),
            text_color="#ff9f9f",
            justify="left"
        ).pack(pady=(5, 0))
        
        # Submit Button - New addition below camera controls
        self.submit_button = ctk.CTkButton(
            inner_frame,
            text="Submit Registration",
            width=200,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12, "bold"),
            fg_color="#4CAF50",  # Green color to differentiate from other buttons
            hover_color="#388E3C",  # Darker green on hover
            command=self.handle_register
        )
        self.submit_button.pack(pady=15)

        # Bind dialog close to cleanup
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_dialog_closing)

    # --- Camera handling methods ---
    def toggle_camera(self):
        """Toggle camera on/off"""
        try:
            if self.is_camera_active:
                self.stop_camera()
                self.camera_button.configure(text="Open Camera")
                self.capture_button.configure(state="disabled")
            else:
                if self.start_camera():
                    self.camera_button.configure(text="Close Camera")
                    self.capture_button.configure(state="normal")
        except Exception as e:
            print(f"Error in toggle_camera: {e}")
            # Try to clean up
            self.is_camera_active = False
            if hasattr(self, 'camera') and self.camera and self.camera.isOpened():
                self.camera.release()
                self.camera = None

    def start_camera(self):
        """Start camera capture"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                # Use dialog as parent if it exists, otherwise use main window
                parent = self.dialog if hasattr(self, 'dialog') and self.dialog else self
                messagebox.showerror("Camera Error", "Could not open camera. Please check your camera connection.", parent=parent)
                return False

            self.is_camera_active = True

            # Remove preview label if it exists
            if hasattr(self, 'preview_label') and self.preview_label.winfo_exists():
                self.preview_label.destroy()

            # Create label for camera feed
            self.camera_label = ctk.CTkLabel(self.face_preview_frame, text="")
            self.camera_label.place(x=0, y=0)

            # Start video feed thread
            self.camera_thread = threading.Thread(target=self.update_camera_feed)
            self.camera_thread.daemon = True
            self.camera_thread.start()

            return True
        except Exception as e:
            parent = self.dialog if hasattr(self, 'dialog') and self.dialog else self
            messagebox.showerror("Camera Error", f"Error starting camera: {str(e)}", parent=parent)
            return False

    def update_camera_feed(self):
        """Update camera feed display"""
        while self.is_camera_active:
            try:
                ret, frame = self.camera.read()
                if ret:
                    # Convert to RGB for PIL
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    
                    # Use CTkImage instead of ImageTk.PhotoImage
                    img_ctk = ctk.CTkImage(
                        light_image=img, 
                        dark_image=img, 
                        size=(320, 240)
                    )
                    
                    # Update label with proper error handling
                    if (hasattr(self, 'camera_label') and 
                        self.camera_label and 
                        self.camera_label.winfo_exists()):
                        try:
                            self.camera_label.configure(image=img_ctk)
                        except tk.TclError:
                            # Widget was destroyed, stop the camera feed
                            print("Camera label destroyed, stopping feed")
                            break
                    else:
                        # Camera label doesn't exist, stop the feed
                        break
            except Exception as e:
                print(f"Error updating camera feed: {e}")
                break

            time.sleep(0.03)  # ~30 FPS
        
        # Ensure camera is properly released when thread ends
        self.is_camera_active = False

    def stop_camera(self):
        """Stop camera capture"""
        try:
            # Signal thread to stop
            self.is_camera_active = False
            
            # Wait for thread to finish
            if hasattr(self, 'camera_thread') and self.camera_thread.is_alive():
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

            # Clear camera label safely
            if hasattr(self, 'camera_label') and self.camera_label:
                try:
                    if self.camera_label.winfo_exists():
                        self.camera_label.destroy()
                except Exception:
                    pass
                finally:
                    self.camera_label = None

            # Show preview or placeholder
            if self.face_image:
                self.show_face_preview(self.face_image)
            else:
                try:
                    if hasattr(self, 'face_preview_frame') and self.face_preview_frame.winfo_exists():
                        self.preview_label = ctk.CTkLabel(
                            self.face_preview_frame,
                            text="No face image captured",
                            font=ctk.CTkFont("Roboto", 10),
                            text_color="#a0a0a0"
                        )
                        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")
                except Exception:
                    pass
        except Exception as e:
            print(f"Error in stop_camera: {e}")

    def capture_face(self):
        """Capture a face from the camera"""
        if not self.camera or not self.is_camera_active:
            messagebox.showwarning("Camera Error", "Camera is not active. Please open camera first.", parent=self.dialog)
            return

        try:
            ret, frame = self.camera.read()
            if not ret:
                messagebox.showerror("Camera Error", "Failed to capture image from camera.", parent=self.dialog)
                return
                
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            validation_result = self.validate_face_image(frame)
            if not validation_result[0]:
                messagebox.showwarning("Face Validation Failed", validation_result[1], parent=self.dialog)
                return

            # Save captured image
            self.face_image = Image.fromarray(frame_rgb)
            img_byte_arr = io.BytesIO()
            self.face_image.save(img_byte_arr, format='PNG')
            self.face_image_data = img_byte_arr.getvalue()

            # Debug print to verify image data is set
            print(f"Face image captured. Data size: {len(self.face_image_data) if self.face_image_data else 0} bytes")

            # Check file size
            if len(self.face_image_data) > 5 * 1024 * 1024:
                messagebox.showwarning(
                    "Image Too Large",
                    "The captured image exceeds the 5MB limit. Please try again with a smaller resolution.",
                    parent=self.dialog
                )
                self.face_image = None
                self.face_image_data = None
                return

            # Stop camera and show preview
            self.stop_camera()
            self.camera_button.configure(text="Open Camera")
            self.capture_button.configure(state="disabled")
            
            # Show the captured image
            self.show_face_preview(self.face_image)
            
            messagebox.showinfo("Success", "Face image captured successfully!", parent=self.dialog)
            
        except cv2.error as e:
            messagebox.showerror("Camera Error", f"OpenCV error: {str(e)}", parent=self.dialog)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture image: {str(e)}", parent=self.dialog)

    def show_face_preview(self, image):
        """Show face image preview"""
        try:
            for widget in self.face_preview_frame.winfo_children():
                widget.destroy()
            
            # Create a CTkImage for proper HiDPI support
            preview_img = image.copy()
            img_ctk = ctk.CTkImage(
                light_image=preview_img, 
                dark_image=preview_img, 
                size=(320, 240)
            )
            
            # Create new label with CTkImage
            preview_label = ctk.CTkLabel(
                self.face_preview_frame, 
                image=img_ctk,
                text=""
            )
            preview_label.place(x=0, y=0)
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

    def browse_face_image(self):
        """Browse for a face image file"""
        if self.is_camera_active:
            self.stop_camera()
            self.camera_button.configure(text="Open Camera")

        filetypes = [
            ("Image files", "*.png;*.jpg;*.jpeg;*.bmp"),
            ("All files", "*.*")
        ]
        
        try:
            filename = filedialog.askopenfilename(filetypes=filetypes, title="Select Face Image")
            if not filename:
                return

            file_size = os.path.getsize(filename)
            if file_size > 5 * 1024 * 1024:
                messagebox.showwarning(
                    "File Too Large",
                    "The selected image exceeds the 5MB limit. Please select a smaller image."
                )
                return

            image = Image.open(filename)
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            validation_result = self.validate_face_image(opencv_image)
            
            if not validation_result[0]:
                messagebox.showwarning("Face Validation Failed", validation_result[1])
                return

            max_size = (800, 600)
            image.thumbnail(max_size, Image.LANCZOS)
            self.face_image = image
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            self.face_image_data = img_byte_arr.getvalue()
            self.show_face_preview(image)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {str(e)}")

    def handle_register(self):
        """Process the registration form submission"""
        try:
            # Create local copies of all values
            first_name = self.first_name_var.get().strip()
            last_name = self.last_name_var.get().strip()
            middle_name = self.middle_name_var.get().strip()
            email = self.email_var.get().strip()
            student_number = self.student_number_var.get().strip()
            password = self.password_var.get().strip()
            confirm_password = self.confirm_password_var.get().strip()
            
            # Debug print to check face image data
            print(f"Checking face image data: {len(self.face_image_data) if self.face_image_data else 0} bytes")
            
            # Validation - Use dialog as parent for messageboxes
            if not first_name or not last_name or not email or not student_number or not password:
                # Create messagebox with dialog as parent
                dialog = tk.Toplevel(self.dialog)
                dialog.withdraw()  # Hide the helper window
                messagebox.showwarning("Registration Failed", "Please fill in all required fields.", parent=self.dialog)
                return

            if password != confirm_password:
                messagebox.showwarning("Registration Failed", "Passwords do not match.", parent=self.dialog)
                return

            # Check for face image data
            if not self.face_image_data or len(self.face_image_data) == 0:
                messagebox.showwarning(
                    "Face Image Required", 
                    "A face image is required for registration. Please capture your face using the camera.",
                    parent=self.dialog
                )
                return
            
            # Display waiting cursor
            self.config(cursor="wait")
            if hasattr(self, 'dialog') and self.dialog:
                self.dialog.config(cursor="wait")
            self.update_idletasks()
            if hasattr(self, 'dialog') and self.dialog:
                self.dialog.update_idletasks()
            
            # Register user via database manager
            if self.db_manager:
                success, result = self.db_manager.register(
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    email=email,
                    student_number=student_number,
                    password=password,
                    face_image=self.face_image_data
                )
            else:
                success, result = False, "Database manager not initialized"
            
            # Restore cursor
            self.config(cursor="")
            if hasattr(self, 'dialog') and self.dialog:
                self.dialog.config(cursor="")
            
            # Clean up camera resources if active
            if self.is_camera_active:
                self.is_camera_active = False
                if self.camera and self.camera.isOpened():
                    self.camera.release()
                    self.camera = None
            
            if success:
                # Create success message and clean up - Use dialog as parent
                messagebox.showinfo(
                    "Registration Successful",
                    "Your account has been created! You can now log in.",
                    parent=self.dialog
                )
                
                # Clear dialog before changing form
                if hasattr(self, 'dialog') and self.dialog:
                    try:
                        self.dialog.destroy()
                    except Exception:
                        pass
                    
                # Remember the email address for the login form
                remembered_email = email
                
                # Create completely new variables to avoid callbacks to destroyed widgets
                self.reset_form_fields()
                self.clear_form()
                
                # Show the login form with the remembered email
                self.show_login()
                
                # After a short delay, set the email field
                if remembered_email:
                    self.after(100, lambda e=remembered_email: self.email_var.set(e))
            else:
                messagebox.showerror("Registration Failed", result, parent=self.dialog)
                
        except Exception as e:
            messagebox.showerror("Registration Error", f"An unexpected error occurred: {str(e)}", parent=self.dialog)
            # Log the error for debugging
            import traceback
            traceback.print_exc()

    def on_dialog_closing(self):
        """Handle dialog closing"""
        try:
            # Stop camera first
            if self.is_camera_active:
                self.is_camera_active = False
                if self.camera and self.camera.isOpened():
                    self.camera.release()
                    self.camera = None
            
            # Now destroy dialog
            if hasattr(self, 'dialog') and self.dialog:
                self.dialog.destroy()
                
        except Exception as e:
            print(f"Error while closing dialog: {str(e)}")



# For testing as standalone
if __name__ == "__main__":
    app = LoginRegister()
    app.mainloop()