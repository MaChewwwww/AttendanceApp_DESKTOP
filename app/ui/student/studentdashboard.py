import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import io
import threading
import time
import base64
from io import BytesIO
import numpy as np

class StudentDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db_manager = controller.db_manager
        self.user_data = controller.user_data
        
        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Camera variables
        self.camera = None
        self.is_camera_active = False
        
        # Create a simple dashboard with logout button
        self.create_dashboard()
        
    def create_dashboard(self):
        """Create a simple dashboard with logout button"""
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Header frame
        header_frame = ctk.CTkFrame(main_frame, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Welcome message
        name = f"{self.user_data['first_name']} {self.user_data['last_name']}"
        welcome_label = ctk.CTkLabel(
            header_frame,
            text=f"Welcome, {name}!",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        welcome_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Logout button
        logout_button = ctk.CTkButton(
            header_frame,
            text="Logout",
            command=self.handle_logout,
            width=100,
            height=35
        )
        logout_button.grid(row=0, column=2, padx=20, pady=20)
        
        # Content frame
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Face validation section
        validation_frame = ctk.CTkFrame(content_frame)
        validation_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        validation_frame.grid_columnconfigure(0, weight=1)
        
        # Title label
        title_label = ctk.CTkLabel(
            validation_frame,
            text="Face Validation",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 10))
        
        # Instructions
        instruction_label = ctk.CTkLabel(
            validation_frame,
            text="Use the camera to validate your identity and record attendance",
            font=ctk.CTkFont(size=12)
        )
        instruction_label.grid(row=1, column=0, pady=(0, 20))
        
        # Camera container
        self.camera_container = ctk.CTkFrame(validation_frame, width=640, height=480)
        self.camera_container.grid(row=2, column=0, pady=10)
        self.camera_container.grid_propagate(False)  # Don't shrink
        
        # Camera placeholder
        self.camera_placeholder = ctk.CTkLabel(
            self.camera_container,
            text="Camera will appear here\nClick 'Start Camera' to begin",
            font=ctk.CTkFont(size=12)
        )
        self.camera_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        
        # Button frame
        button_frame = ctk.CTkFrame(validation_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=20)
        
        # Start camera button
        self.camera_button = ctk.CTkButton(
            button_frame,
            text="Start Camera",
            command=self.toggle_camera,
            width=150,
            height=40
        )
        self.camera_button.pack(side="left", padx=10)
        
        # Validate button
        self.validate_button = ctk.CTkButton(
            button_frame,
            text="Validate Face",
            command=self.validate_face,
            width=150,
            height=40,
            state="disabled"
        )
        self.validate_button.pack(side="left", padx=10)
    
    def toggle_camera(self):
        """Toggle camera on/off"""
        if self.is_camera_active:
            self.stop_camera()
            self.camera_button.configure(text="Start Camera")
            self.validate_button.configure(state="disabled")
        else:
            if self.start_camera():
                self.camera_button.configure(text="Stop Camera")
                self.validate_button.configure(state="normal")
    
    def start_camera(self):
        """Start the camera feed"""
        try:
            self.camera = cv2.VideoCapture(0)  # Use default camera (0)
            if not self.camera.isOpened():
                messagebox.showerror("Camera Error", "Could not open camera. Please check your camera connection.")
                return False
                
            self.is_camera_active = True
            
            # Create a label for the camera feed
            self.camera_label = tk.Label(self.camera_container)
            self.camera_label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Hide placeholder
            self.camera_placeholder.place_forget()
            
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
                
                # Resize to fit the camera container
                img = img.resize((640, 480), Image.LANCZOS)
                
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
            
        # Clear camera label if it exists
        if hasattr(self, 'camera_label') and self.camera_label.winfo_exists():
            self.camera_label.destroy()
            
        # Show placeholder again
        self.camera_placeholder.place(relx=0.5, rely=0.5, anchor="center")
    
    def validate_face(self):
        """Validate the user's face against stored image"""
        if not self.camera or not self.is_camera_active:
            messagebox.showerror("Error", "Camera is not active. Please start the camera first.")
            return
        
        # Check if user has a stored face image
        if not self.user_data.get('face_image_b64'):
            messagebox.showwarning("Missing Face Image", "You don't have a registered face image. Please update your profile first.")
            return
        
        # Capture the current frame
        ret, frame = self.camera.read()
        if not ret:
            messagebox.showerror("Camera Error", "Failed to capture image from camera.")
            return
            
        # Get stored face image
        try:
            stored_image_data = base64.b64decode(self.user_data['face_image_b64'])
            stored_image = Image.open(BytesIO(stored_image_data))
            stored_image_np = np.array(stored_image)
            
            # Convert to grayscale for comparison
            stored_gray = cv2.cvtColor(stored_image_np, cv2.COLOR_RGB2GRAY)
            
            # Convert current frame to grayscale
            current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Resize stored image to match current frame
            stored_gray_resized = cv2.resize(stored_gray, (current_gray.shape[1], current_gray.shape[0]))
            
            # Simple face validation using structural similarity
            # In a real app, you'd use a more sophisticated face recognition algorithm
            similarity = self.compare_images(stored_gray_resized, current_gray)
            
            # Display a loading indicator
            self.configure(cursor="wait")
            self.update_idletasks()
            
            # Threshold for similarity (adjust as needed)
            # This is a very simplistic approach - real face recognition would use ML
            if similarity > 0.4:  # Arbitrary threshold, higher is more similar
                # Success - Log attendance
                # Assuming we'll use a default course/section for this prototype
                course_id = 1
                section_id = 1
                
                # Convert image to bytes for database
                img_byte_arr = io.BytesIO()
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                img.save(img_byte_arr, format='PNG')
                img_data = img_byte_arr.getvalue()
                
                success, result = self.db_manager.log_attendance(
                    self.user_data['id'],
                    course_id,
                    section_id,
                    img_data
                )
                
                # Reset cursor
                self.configure(cursor="")
                
                if success:
                    messagebox.showinfo(
                        "Face Validated",
                        "Your identity has been verified and attendance recorded successfully!"
                    )
                    
                    # Stop camera
                    self.stop_camera()
                    self.camera_button.configure(text="Start Camera")
                    self.validate_button.configure(state="disabled")
                else:
                    messagebox.showerror("Error", f"Failed to record attendance: {result}")
            else:
                # Reset cursor
                self.configure(cursor="")
                messagebox.showwarning(
                    "Face Validation Failed",
                    "Face does not match the registered image. Please try again."
                )
                
        except Exception as e:
            # Reset cursor
            self.configure(cursor="")
            messagebox.showerror("Error", f"Error during face validation: {str(e)}")
    
    def compare_images(self, img1, img2):
        """Compare two grayscale images using structural similarity"""
        try:
            # Use Structural Similarity Index (SSIM)
            # A more robust approach would use a deep learning model
            from skimage.metrics import structural_similarity as ssim
            similarity = ssim(img1, img2)
            print(f"Similarity score: {similarity}")
            return similarity
        except ImportError:
            # Fallback if scikit-image is not available
            # Use a very basic histogram comparison
            hist1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([img2], [0], None, [256], [0, 256])
            
            cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
            cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)
            
            similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            print(f"Fallback similarity score: {similarity}")
            return similarity
    
    def handle_logout(self):
        """Handle logout button click"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Clean up camera if active
            if self.is_camera_active:
                self.stop_camera()
                
            self.controller.logout()