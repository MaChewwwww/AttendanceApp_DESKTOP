import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import os
import sys
import cv2
import threading
import time
import io
import numpy as np

class RegisterScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db_manager = controller.db_manager
        
        # Configure the grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Camera variables
        self.camera = None
        self.is_camera_active = False
        self.face_image = None
        self.face_image_data = None
        
        # Create registration form
        self.create_register_form()
        
    def create_register_form(self):
        # Left side - image or logo
        left_frame = ttk.Frame(self, bootstyle="light")
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        # Try to load and display a logo
        try:
            # Get the absolute path to the assets directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            image_path = os.path.join(base_dir, "assets", "images", "attendance_logo.png")
            
            # Check if the file exists, use a placeholder if not
            if not os.path.exists(image_path):
                # Create a solid color placeholder
                logo_img = Image.new('RGB', (300, 300), color=(32, 32, 96))
                logo_photo = ImageTk.PhotoImage(logo_img)
            else:
                # Load the actual logo
                logo_img = Image.open(image_path)
                logo_img = logo_img.resize((300, 300))
                logo_photo = ImageTk.PhotoImage(logo_img)
                
            logo_label = ttk.Label(left_frame, image=logo_photo)
            logo_label.image = logo_photo  # Keep a reference to prevent garbage collection
            logo_label.pack(expand=True, fill="both", padx=20, pady=20)
            
        except Exception as e:
            print(f"Error loading logo: {e}")
            # If logo fails, just show app name
            app_name = ttk.Label(
                left_frame, 
                text="Attendance App", 
                font=("TkDefaultFont", 24, "bold"),
                bootstyle="light"
            )
            app_name.pack(expand=True)
        
        # Right side - registration form
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Create a canvas with scrollbar for the form
        canvas = tk.Canvas(right_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(40, 0), pady=40)
        scrollbar.pack(side="right", fill="y", padx=(0, 40), pady=40)
        
        # Title
        title_label = ttk.Label(
            scrollable_frame, 
            text="Student Registration", 
            font=("TkDefaultFont", 16, "bold")
        )
        title_label.pack(pady=(0, 20), fill="x")
        
        # Form fields
        # First Name
        first_name_frame = ttk.Frame(scrollable_frame)
        first_name_frame.pack(fill="x", pady=5)
        
        first_name_label = ttk.Label(first_name_frame, text="First Name:", width=15, anchor="w")
        first_name_label.pack(side="left")
        
        self.first_name_var = tk.StringVar()
        first_name_entry = ttk.Entry(first_name_frame, textvariable=self.first_name_var)
        first_name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Middle Name (optional)
        middle_name_frame = ttk.Frame(scrollable_frame)
        middle_name_frame.pack(fill="x", pady=5)
        
        middle_name_label = ttk.Label(middle_name_frame, text="Middle Name:", width=15, anchor="w")
        middle_name_label.pack(side="left")
        
        self.middle_name_var = tk.StringVar()
        middle_name_entry = ttk.Entry(middle_name_frame, textvariable=self.middle_name_var)
        middle_name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Last Name
        last_name_frame = ttk.Frame(scrollable_frame)
        last_name_frame.pack(fill="x", pady=5)
        
        last_name_label = ttk.Label(last_name_frame, text="Last Name:", width=15, anchor="w")
        last_name_label.pack(side="left")
        
        self.last_name_var = tk.StringVar()
        last_name_entry = ttk.Entry(last_name_frame, textvariable=self.last_name_var)
        last_name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Email
        email_frame = ttk.Frame(scrollable_frame)
        email_frame.pack(fill="x", pady=5)
        
        email_label = ttk.Label(email_frame, text="Email:", width=15, anchor="w")
        email_label.pack(side="left")
        
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(email_frame, textvariable=self.email_var)
        email_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Student Number
        student_number_frame = ttk.Frame(scrollable_frame)
        student_number_frame.pack(fill="x", pady=5)
        
        student_number_label = ttk.Label(student_number_frame, text="Student Number:", width=15, anchor="w")
        student_number_label.pack(side="left")
        
        self.student_number_var = tk.StringVar()
        student_number_entry = ttk.Entry(student_number_frame, textvariable=self.student_number_var)
        student_number_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Password
        password_frame = ttk.Frame(scrollable_frame)
        password_frame.pack(fill="x", pady=5)
        
        password_label = ttk.Label(password_frame, text="Password:", width=15, anchor="w")
        password_label.pack(side="left")
        
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="•")
        password_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Confirm Password
        confirm_password_frame = ttk.Frame(scrollable_frame)
        confirm_password_frame.pack(fill="x", pady=5)
        
        confirm_password_label = ttk.Label(confirm_password_frame, text="Confirm Password:", width=15, anchor="w")
        confirm_password_label.pack(side="left")
        
        self.confirm_password_var = tk.StringVar()
        confirm_password_entry = ttk.Entry(confirm_password_frame, textvariable=self.confirm_password_var, show="•")
        confirm_password_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Face Image Section
        face_frame = ttk.LabelFrame(scrollable_frame, text="Face Registration", padding=10)
        face_frame.pack(fill="x", pady=10, padx=5)
        
        # Create a frame for the webcam feed/image preview
        self.face_preview_frame = ttk.Frame(face_frame, width=320, height=240)
        self.face_preview_frame.pack(pady=10)
        
        # Default preview label
        self.preview_label = ttk.Label(
            self.face_preview_frame, 
            text="No face image captured",
            font=("TkDefaultFont", 10),
            bootstyle="secondary"
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Buttons for face capture
        face_buttons_frame = ttk.Frame(face_frame)
        face_buttons_frame.pack(fill="x", pady=5)
        
        self.camera_button = ttk.Button(
            face_buttons_frame,
            text="Open Camera",
            command=self.toggle_camera,
            bootstyle="info",
            width=15
        )
        self.camera_button.pack(side="left", padx=5)
        
        self.capture_button = ttk.Button(
            face_buttons_frame,
            text="Capture",
            command=self.capture_face,
            bootstyle="success",
            width=15,
            state="disabled"
        )
        self.capture_button.pack(side="left", padx=5)
        
        self.browse_button = ttk.Button(
            face_buttons_frame,
            text="Browse...",
            command=self.browse_face_image,
            bootstyle="secondary",
            width=15
        )
        self.browse_button.pack(side="left", padx=5)
        
        # Buttons frame for registration
        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.pack(pady=20)
        
        # Register button
        register_button = ttk.Button(
            buttons_frame,
            text="Register",
            command=self.handle_register,
            bootstyle="success",
            width=15
        )
        register_button.pack(side="left", padx=5)
        
        # Back button
        back_button = ttk.Button(
            buttons_frame,
            text="Back to Login",
            command=self.handle_back,
            bootstyle="secondary",
            width=15
        )
        back_button.pack(side="left", padx=5)
        
        # Set focus to first name field
        first_name_entry.focus_set()
        
    def toggle_camera(self):
        """Toggle the camera on/off"""
        if self.is_camera_active:
            self.stop_camera()
            self.camera_button.configure(text="Open Camera")
            self.capture_button.configure(state="disabled")
        else:
            if self.start_camera():
                self.camera_button.configure(text="Close Camera")
                self.capture_button.configure(state="normal")
            
    def start_camera(self):
        """Start the camera feed"""
        try:
            self.camera = cv2.VideoCapture(0)  # Use default camera (0)
            if not self.camera.isOpened():
                messagebox.showerror("Camera Error", "Could not open camera. Please check your camera connection.")
                return False
                
            self.is_camera_active = True
            
            # Create a label for the camera feed if it doesn't exist
            if hasattr(self, 'preview_label'):
                self.preview_label.destroy()
            
            self.camera_label = ttk.Label(self.face_preview_frame)
            self.camera_label.place(x=0, y=0)
            
            # Start the video feed in a separate thread
            self.camera_thread = threading.Thread(target=self.update_camera_feed)
            self.camera_thread.daemon = True
            self.camera_thread.start()
            
            return True
        except Exception as e:
            messagebox.showerror("Camera Error", f"Error starting camera: {str(e)}")
            return False
            
    def update_camera_feed(self):
        """Update the camera feed in the UI"""
        while self.is_camera_active:
            ret, frame = self.camera.read()
            if ret:
                # Convert to RGB for PIL
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PIL Image
                img = Image.fromarray(frame_rgb)
                
                # Resize to fit the preview frame
                img = img.resize((320, 240), Image.LANCZOS)
                
                # Convert to PhotoImage
                img_tk = ImageTk.PhotoImage(image=img)
                
                # Update label
                if hasattr(self, 'camera_label') and self.camera_label.winfo_exists():
                    self.camera_label.configure(image=img_tk)
                    self.camera_label.image = img_tk  # Keep a reference
            
            time.sleep(0.03)  # ~30 FPS
            
    def stop_camera(self):
        """Stop the camera feed"""
        self.is_camera_active = False
        if hasattr(self, 'camera_thread'):
            self.camera_thread.join(0.2)  # Wait briefly for thread to finish
            
        if self.camera and self.camera.isOpened():
            self.camera.release()
            self.camera = None
            
        # Clear camera label if it exists and show preview label
        if hasattr(self, 'camera_label') and self.camera_label.winfo_exists():
            self.camera_label.destroy()
            
        # Show preview if we have an image
        if self.face_image:
            self.show_face_preview(self.face_image)
        else:
            self.preview_label = ttk.Label(
                self.face_preview_frame, 
                text="No face image captured",
                font=("TkDefaultFont", 10),
                bootstyle="secondary"
            )
            self.preview_label.place(relx=0.5, rely=0.5, anchor="center")
            
    def capture_face(self):
        """Capture the current camera frame as the face image"""
        if not self.camera or not self.is_camera_active:
            return
            
        # Capture the current frame
        ret, frame = self.camera.read()
        if ret:
            # Convert to RGB for PIL
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Validate face before saving
            validation_result = self.validate_face_image(frame)
            if not validation_result[0]:
                messagebox.showwarning("Face Validation Failed", validation_result[1])
                return
                
            # Save to PIL Image
            self.face_image = Image.fromarray(frame_rgb)
            
            # Convert to bytes for database storage
            img_byte_arr = io.BytesIO()
            self.face_image.save(img_byte_arr, format='PNG')
            self.face_image_data = img_byte_arr.getvalue()
            
            # Check file size
            if len(self.face_image_data) > 5 * 1024 * 1024:  # 5MB in bytes
                messagebox.showwarning(
                    "Image Too Large", 
                    "The captured image exceeds the 5MB limit. Please try again with a smaller resolution."
                )
                self.face_image = None
                self.face_image_data = None
                return
            
            # Stop the camera
            self.stop_camera()
            
            # Show success message
            messagebox.showinfo("Success", "Face image captured successfully!")
            
            # Update UI
            self.camera_button.configure(text="Open Camera")
            
            # Show the captured image
            self.show_face_preview(self.face_image)
            
    def show_face_preview(self, image):
        """Show the face image preview"""
        # Clear any existing preview
        for widget in self.face_preview_frame.winfo_children():
            widget.destroy()
            
        # Resize image to fit the preview area
        preview_img = image.copy()
        preview_img = preview_img.resize((320, 240), Image.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(preview_img)
        
        # Create label to show the image
        preview_label = ttk.Label(self.face_preview_frame, image=photo)
        preview_label.image = photo  # Keep a reference
        preview_label.place(x=0, y=0)

    def validate_face_image(self, image):
        """
        Validate face image for registration:
        1. Check if a face is detected
        2. Check if only one face is present
        3. Check if the person isn't wearing sunglasses
        
        Returns: (success, message)
        """
        try:
            # Load face detection model
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            
            if not os.path.exists(face_cascade_path) or not os.path.exists(eye_cascade_path):
                # If cascade files not found, return success but show a warning
                print("Warning: Face detection cascades not found. Skipping face validation.")
                return (True, "Face validation skipped")
                
            face_cascade = cv2.CascadeClassifier(face_cascade_path)
            eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Check if at least one face is detected
            if len(faces) == 0:
                return (False, "No face detected. Please ensure your face is clearly visible.")
                
            # Check if only one face is present
            if len(faces) > 1:
                return (False, "Multiple faces detected. Please ensure only your face is in the image.")
                
            # Check for eyes to detect if sunglasses are being worn
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
                
            # All checks passed
            return (True, "Face validation successful")
            
        except Exception as e:
            print(f"Face validation error: {str(e)}")
            # In case of errors, we'll allow the image but log the error
            return (True, "Face validation skipped due to an error")
        
            
    def browse_face_image(self):
        """Allow user to select a face image from file system"""
        # Stop camera if it's running
        if self.is_camera_active:
            self.stop_camera()
            self.camera_button.configure(text="Open Camera")
            
        # Open file dialog
        filetypes = [
            ("Image files", "*.png;*.jpg;*.jpeg;*.bmp"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes, title="Select Face Image")
        
        if filename:
            try:
                # Check file size first (5MB limit)
                file_size = os.path.getsize(filename)
                if file_size > 5 * 1024 * 1024:  # 5MB in bytes
                    messagebox.showwarning(
                        "File Too Large", 
                        "The selected image exceeds the 5MB limit. Please select a smaller image."
                    )
                    return
                
                # Load the image
                image = Image.open(filename)
                
                # Convert to OpenCV format for face validation
                opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Validate face
                validation_result = self.validate_face_image(opencv_image)
                if not validation_result[0]:
                    messagebox.showwarning("Face Validation Failed", validation_result[1])
                    return
                
                # Resize if too large
                max_size = (800, 600)
                image.thumbnail(max_size, Image.LANCZOS)
                
                # Save as face image
                self.face_image = image
                
                # Convert to bytes for database storage
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                self.face_image_data = img_byte_arr.getvalue()
                
                # Show the image preview
                self.show_face_preview(image)
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not load image: {str(e)}")
                
    def handle_register(self):
        """Handle registration form submission"""
        # Get form values
        first_name = self.first_name_var.get().strip()
        middle_name = self.middle_name_var.get().strip()
        last_name = self.last_name_var.get().strip()
        email = self.email_var.get().strip()
        student_number = self.student_number_var.get().strip()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        # Basic validation
        if not first_name or not last_name or not email or not student_number or not password:
            messagebox.showwarning("Registration Failed", "Please fill in all required fields.")
            return
            
        if password != confirm_password:
            messagebox.showwarning("Registration Failed", "Passwords do not match.")
            return
            
        # Check if face image is provided
        if not self.face_image_data:
            if not messagebox.askyesno("Face Image Missing", 
                                     "No face image provided. This is recommended for attendance tracking. Continue anyway?"):
                return
            
        # Display a loading indicator
        self.config(cursor="wait")
        self.update_idletasks()
        
        # Attempt registration
        success, result = self.db_manager.register(
            first_name=first_name,
            middle_name=middle_name if middle_name else None,
            last_name=last_name,
            email=email,
            student_number=student_number,
            password=password,
            face_image=self.face_image_data
        )
        
        # Reset cursor
        self.config(cursor="")
        
        if success:
            messagebox.showinfo(
                "Registration Successful",
                "Your account has been created! You can now log in."
            )
            self.controller.show_login()
        else:
            messagebox.showerror("Registration Failed", result)
            
    def handle_back(self):
        """Go back to login screen"""
        # Clean up camera resources if active
        if self.is_camera_active:
            self.stop_camera()
            
        self.controller.show_login()
        
    def on_closing(self):
        """Clean up resources when closing"""
        if self.is_camera_active:
            self.stop_camera()