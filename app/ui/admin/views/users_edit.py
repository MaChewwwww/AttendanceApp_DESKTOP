import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import cv2
import threading
import time
import io
import os
from PIL import Image, ImageTk
from app.db_manager import DatabaseManager

class UsersEditModal(ctk.CTkToplevel):
    def __init__(self, parent, user_data, user_type="student"):
        super().__init__(parent)
        self.user_data = user_data
        self.user_type = user_type
        self.db_manager = DatabaseManager()
        
        # Camera variables
        self.face_image = None
        self.face_image_data = None
        self.camera = None
        self.is_camera_active = False
        self.camera_thread = None
        self.current_frame = None
        self.camera_canvas = None
        self.current_photo = None
        
        # Get detailed user data if only ID is provided
        if isinstance(user_data, (int, str)):
            success, detailed_data = self.db_manager.get_user_details(int(user_data))
            if success:
                self.user_data = detailed_data
            else:
                messagebox.showerror("Error", f"Failed to load user data: {detailed_data}")
                self.destroy()
                return
        
        # Store form field variables
        self.form_fields = {}
        
        self.title(f"Edit {self.user_type.title()}")
        self.geometry("640x720")
        self.resizable(False, False)
        self.configure(fg_color="#fff")
        self.transient(parent)
        self.grab_set()
        self._center_window(640, 720)
        self.setup_ui()
        self.populate_form_data()

    def _center_window(self, width, height):
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        # Title
        title_text = f"Edit {self.user_type.title()} Profile"
        ctk.CTkLabel(self, text=title_text, font=ctk.CTkFont(size=18, weight="bold"), text_color="#000").pack(anchor="w", padx=30, pady=(20, 10))
        
        # Main form frame
        form_frame = ctk.CTkFrame(self, fg_color="#fff")
        form_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))
        
        # Two columns for entries
        left_col = ctk.CTkFrame(form_frame, fg_color="#fff")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        right_col = ctk.CTkFrame(form_frame, fg_color="#fff")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Left column entries
        self.form_fields['first_name'] = self.create_form_field(left_col, "First Name")
        self.form_fields['last_name'] = self.create_form_field(left_col, "Last Name")
        self.form_fields['email'] = self.create_form_field(left_col, "Email")
        self.form_fields['password'] = self.create_form_field(left_col, "Password", show="*")
        
        # Right column entries
        if self.user_type == "student":
            self.form_fields['section'] = self.create_form_field(right_col, "Section")
        else:
            self.form_fields['employee_number'] = self.create_form_field(right_col, "Employee Number")
        
        # Contact Number field
        self.form_fields['contact_number'] = self.create_form_field(right_col, "Contact Number")
        
        # Facial recognition button
        fr_btn = ctk.CTkButton(
            right_col, 
            text="Take Facial Recognition", 
            fg_color="#1E3A8A", 
            hover_color="#1E3A8A", 
            text_color="#fff", 
            width=220, 
            height=32, 
            corner_radius=8, 
            command=self.open_facial_recognition
        )
        fr_btn.pack(fill="x", pady=(10, 8))
        
        # Face data status (text only - no image preview)
        self.face_status_frame = ctk.CTkFrame(right_col, fg_color="#fff", height=50)
        self.face_status_frame.pack(fill="x", pady=(0, 10))
        self.face_status_frame.pack_propagate(False)
        
        self.face_status_label = ctk.CTkLabel(
            self.face_status_frame, 
            text="No Face Data", 
            font=ctk.CTkFont(size=13, weight="bold"), 
            text_color="#757575",
            anchor="w"
        )
        self.face_status_label.pack(anchor="w", padx=10, pady=15)
        
        # Bottom buttons
        btns_frame = ctk.CTkFrame(self, fg_color="#fff")
        btns_frame.pack(fill="x", padx=30, pady=(10, 20))
        
        ctk.CTkButton(
            btns_frame, 
            text="Cancel", 
            fg_color="#E5E7EB", 
            text_color="#000", 
            hover_color="#D1D5DB", 
            width=600, 
            height=36, 
            corner_radius=8, 
            command=self.destroy
        ).pack(fill="x", pady=(0, 8))
        
        ctk.CTkButton(
            btns_frame, 
            text="Save Changes", 
            fg_color="#1E3A8A", 
            hover_color="#1E3A8A", 
            text_color="#fff", 
            width=600, 
            height=36, 
            corner_radius=8, 
            command=self.show_caution_modal
        ).pack(fill="x")

    def create_form_field(self, parent, label_text, show=None):
        """Create a form field with label and entry"""
        ctk.CTkLabel(parent, text=label_text, anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
        entry = ctk.CTkEntry(parent, width=220, fg_color="#fff", text_color="#000", show=show)
        entry.pack(fill="x", pady=(0, 10))
        return entry

    def populate_form_data(self):
        """Populate form fields with user data"""
        if not self.user_data:
            return
        
        # Populate form fields
        if 'first_name' in self.form_fields and self.user_data.get('first_name'):
            self.form_fields['first_name'].insert(0, self.user_data['first_name'])
            
        if 'last_name' in self.form_fields and self.user_data.get('last_name'):
            self.form_fields['last_name'].insert(0, self.user_data['last_name'])
            
        if 'email' in self.form_fields and self.user_data.get('email'):
            self.form_fields['email'].insert(0, self.user_data['email'])
            
        if 'contact_number' in self.form_fields and self.user_data.get('contact_number'):
            self.form_fields['contact_number'].insert(0, self.user_data['contact_number'])
            
        if self.user_type == "student":
            if 'section' in self.form_fields and self.user_data.get('section_name'):
                self.form_fields['section'].insert(0, self.user_data['section_name'])
        else:
            if 'employee_number' in self.form_fields and self.user_data.get('employee_number'):
                self.form_fields['employee_number'].insert(0, self.user_data['employee_number'])
        
        # Load existing face image if available
        self.load_existing_face_image()

    def load_existing_face_image(self):
        """Load existing face image from user data"""
        try:
            if self.user_data.get('face_image'):
                # Decode base64 or binary data
                face_data = self.user_data['face_image']
                
                if isinstance(face_data, str):
                    # If it's base64 string
                    import base64
                    face_data = base64.b64decode(face_data)
                
                # Convert to PIL Image
                self.face_image = Image.open(io.BytesIO(face_data))
                self.face_image_data = face_data
                
                # Update status
                self.update_face_status()
            else:
                # No face data
                self.face_image_data = None
                self.update_face_status()
                
        except Exception as e:
            print(f"Error loading existing face image: {e}")
            self.update_face_status(error=True)

    def update_face_status(self, error=False):
        """Update the face data status with text only"""
        try:
            if error:
                # Error state
                self.face_status_label.configure(
                    text="✗ Error loading face data",
                    text_color="#dc2626"
                )
                self.face_status_frame.configure(fg_color="#fef2f2")
            elif self.face_image_data or (hasattr(self, 'face_image') and self.face_image):
                # Valid face data
                self.face_status_label.configure(
                    text="✓ Face data available",
                    text_color="#10b981"
                )
                self.face_status_frame.configure(fg_color="#f0fdf4")
            else:
                # No face data
                self.face_status_label.configure(
                    text="No Face Data",
                    text_color="#757575"
                )
                self.face_status_frame.configure(fg_color="#fff")
                
        except Exception as e:
            print(f"Error updating face status: {e}")

    def update_image_preview(self):
        """Update face status (renamed for compatibility)"""
        self.update_face_status()

    def open_facial_recognition(self):
        """Open facial recognition popup"""
        # Create completely independent window
        popup = IndependentFacialRecognitionWindow(self)

    def on_face_capture_complete(self, face_image, face_image_data):
        """Callback when face capture is completed"""
        self.face_image = face_image
        self.face_image_data = face_image_data
        self.update_face_status()

    def show_caution_modal(self):
        """Show caution modal before saving"""
        def on_continue():
            print('Changes saved!')
            # Place your save logic here
        
        from .users_modals import CautionModal
        CautionModal(self, on_continue=on_continue)

class IndependentFacialRecognitionWindow:
    """Completely independent facial recognition window using tkinter directly"""
    
    def __init__(self, parent_edit):
        self.parent_edit = parent_edit
        
        # Create independent Tkinter window (not CTk)
        self.root = tk.Toplevel()
        self.root.title("Facial Recognition")
        self.root.geometry("454x450")
        self.root.resizable(False, False)
        self.root.configure(bg="#222222")
        
        # Camera variables
        self.camera = None
        self.is_camera_active = False
        self.camera_thread = None
        self.current_frame = None
        self.face_image = None
        self.face_image_data = None
        self.video_label = None
        
        # Make it stay on top and modal-like
        self.root.attributes('-topmost', True)
        
        # Set up proper parent relationship for modal behavior
        try:
            # Try to get the actual tkinter root window
            if hasattr(parent_edit, 'winfo_toplevel'):
                # Get the top-level window
                top_level = parent_edit.winfo_toplevel()
                # Set transient to the main tkinter root instead
                main_root = top_level.nametowidget(top_level.winfo_parent()) if top_level.winfo_parent() else top_level
                if main_root != self.root:
                    self.root.transient(main_root)
            else:
                # Fallback - just make it modal without transient
                pass
        except Exception as e:
            print(f"Could not set transient relationship: {e}")
            # Continue without transient - window will still be modal through grab
        
        # Center window
        self._center_window()
        
        # Setup UI
        self._setup_ui()
        
        # Handle close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Focus and grab for modal behavior
        self.root.focus_force()
        
        # Set grab after a small delay to ensure window is ready
        self.root.after(100, self._set_grab)
    
    def _set_grab(self):
        """Set grab with error handling"""
        try:
            self.root.grab_set()
        except Exception as e:
            print(f"Could not set grab: {e}")
            # Continue without grab - window will still work
    
    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 454) // 2
        y = (screen_height - 450) // 2
        self.root.geometry(f"454x450+{x}+{y}")
    
    def _setup_ui(self):
        """Setup the UI to match original design with proper spacing"""
        # Main container with proper padding and rounded corners effect
        self.main_frame = tk.Frame(
            self.root, 
            bg="#ffffff", 
            relief="flat", 
            bd=0,
            padx=0,
            pady=0
        )
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Create inner content frame with proper margins
        content_frame = tk.Frame(
            self.main_frame,
            bg="#ffffff",
            relief="flat",
            bd=0
        )
        content_frame.pack(fill="both", expand=True, padx=22, pady=22)
        
        # Info button (top right with proper positioning)
        info_btn = tk.Button(
            content_frame,
            text="i",
            font=("Roboto", 14, "bold"),
            bg="#f5f5f5",
            fg="#222222",
            relief="flat",
            bd=0,
            width=2,
            height=1,
            command=self._show_info,
            cursor="hand2"
        )
        info_btn.place(x=388, y=0)
        
        # Camera preview frame (exact positioning like original)
        self.preview_frame = tk.Frame(
            content_frame, 
            bg="#fafafa", 
            relief="solid", 
            bd=1,
            highlightthickness=0
        )
        self.preview_frame.place(x=0, y=30, width=410, height=240)
        
        # Video display label with proper centering
        self.video_label = tk.Label(
            self.preview_frame,
            text="Camera will appear here\nClick 'Open Camera' to begin",
            font=("Roboto", 12),
            bg="#fafafa",
            fg="#a0a0a0",
            justify="center",
            wraplength=350
        )
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Camera button with exact positioning
        self.camera_btn = tk.Button(
            content_frame,
            text="Open Camera",
            font=("Roboto", 13, "bold"),
            bg="#ffffff",
            fg="#222222",
            relief="solid",
            bd=1,
            borderwidth=1,
            highlightthickness=0,
            command=self._toggle_camera,
            cursor="hand2"
        )
        self.camera_btn.place(x=0, y=280, width=410, height=32)
        
        # Action buttons frame for proper alignment
        action_frame = tk.Frame(content_frame, bg="#ffffff")
        action_frame.place(x=0, y=325, width=410, height=38)
        
        # Retake button (left side with exact spacing)
        self.retake_btn = tk.Button(
            action_frame,
            text="Retake",
            font=("Roboto", 13, "bold"),
            bg="#e5e5e5",
            fg="#707070",
            relief="flat",
            bd=0,
            state="disabled",
            command=self._retake_image,
            cursor="hand2",
            highlightthickness=0
        )
        self.retake_btn.place(x=0, y=0, width=200, height=38)
        
        # Capture button (right side with exact spacing)
        self.capture_btn = tk.Button(
            action_frame,
            text="Capture",
            font=("Roboto", 13, "bold"),
            bg="#1E3A8A",
            fg="#ffffff",
            relief="flat",
            bd=0,
            state="disabled",
            command=self._capture_image,
            cursor="hand2",
            highlightthickness=0
        )
        self.capture_btn.place(x=210, y=0, width=200, height=38)
        
        # Save button (full width with proper positioning)
        self.save_btn = tk.Button(
            content_frame,
            text="Save Photo",
            font=("Roboto", 13, "bold"),
            bg="#1E3A8A",
            fg="#ffffff",
            relief="flat",
            bd=0,
            state="disabled",
            command=self._save_photo,
            cursor="hand2",
            highlightthickness=0
        )
        self.save_btn.place(x=0, y=375, width=410, height=38)
    
    def _show_info(self):
        """Show info message like original - ensure it appears on top"""
        # Temporarily disable topmost to show messagebox properly
        self.root.attributes('-topmost', False)
        tk.messagebox.showinfo(
            "Camera Info", 
            "Please ensure you're in a well-lit environment before capturing your photo for the best image quality",
            parent=self.root
        )
        # Re-enable topmost after messagebox
        self.root.attributes('-topmost', True)
    
    def _toggle_camera(self):
        """Toggle camera on/off"""
        if self.is_camera_active:
            self._stop_camera()
        else:
            self._start_camera()
    
    def _start_camera(self):
        """Start camera capture"""
        try:
            # Try to open camera
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self._show_error("Could not open camera. Please check your camera connection.")
                return
            
            self.is_camera_active = True
            self.camera_btn.configure(text="Close Camera", bg="#ffffff")
            self.capture_btn.configure(state="normal", bg="#1E3A8A", fg="#ffffff")
            
            # Hide placeholder text
            self.video_label.configure(text="")
            
            # Start camera thread
            self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
            self.camera_thread.start()
            
        except Exception as e:
            self._show_error(f"Error starting camera: {str(e)}")
    
    def _stop_camera(self):
        """Stop camera capture"""
        self.is_camera_active = False
        
        # Wait for thread to finish
        if self.camera_thread and self.camera_thread.is_alive():
            self.camera_thread.join(timeout=1.0)
        
        # Release camera
        if self.camera:
            self.camera.release()
            self.camera = None
        
        # Update UI
        self.camera_btn.configure(text="Open Camera", bg="#ffffff")
        self.capture_btn.configure(state="disabled", bg="#cccccc", fg="#999999")
        
        # Show placeholder if no image captured
        if not self.face_image:
            self.video_label.configure(
                image="",
                text="Camera will appear here\nClick 'Open Camera' to begin"
            )
    
    def _camera_loop(self):
        """Camera loop running in separate thread"""
        while self.is_camera_active:
            try:
                if self.camera and self.camera.isOpened():
                    ret, frame = self.camera.read()
                    if ret:
                        self.current_frame = frame.copy()
                        
                        # Resize and convert frame to match original dimensions
                        frame_resized = cv2.resize(frame, (410, 240))
                        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                        
                        # Add guide rectangle like original
                        h, w = frame_rgb.shape[:2]
                        center_x, center_y = w // 2, h // 2
                        rect_w, rect_h = 160, 180
                        cv2.rectangle(frame_rgb, 
                                     (center_x - rect_w//2, center_y - rect_h//2),
                                     (center_x + rect_w//2, center_y + rect_h//2),
                                     (0, 255, 0), 2)
                        
                        # Convert to PhotoImage
                        pil_image = Image.fromarray(frame_rgb)
                        photo = ImageTk.PhotoImage(pil_image)
                        
                        # Update display in main thread
                        self.root.after(0, self._update_video_display, photo)
                
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                print(f"Camera loop error: {e}")
                break
        
        print("Camera loop ended")
    
    def _update_video_display(self, photo):
        """Update video display (runs in main thread)"""
        try:
            if self.video_label and self.video_label.winfo_exists():
                self.video_label.configure(image=photo, text="")
                self.video_label.image = photo  # Keep reference
        except Exception as e:
            print(f"Video display error: {e}")
    
    def _capture_image(self):
        """Capture current frame"""
        if self.current_frame is None:
            self._show_warning("No frame available. Please wait for camera to initialize.")
            return
        
        try:
            # Convert frame to RGB
            frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            self.face_image = Image.fromarray(frame_rgb)
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            self.face_image.save(img_byte_arr, format='PNG')
            self.face_image_data = img_byte_arr.getvalue()
            
            # Stop camera and show captured image
            self._stop_camera()
            self._show_captured_image()
            self._update_buttons_after_capture()
            
            self._show_info_msg("Face image captured successfully!")
            
        except Exception as e:
            self._show_error(f"Failed to capture image: {str(e)}")
    
    def _show_captured_image(self):
        """Show the captured image"""
        try:
            if self.face_image:
                # Resize for display to match frame size
                display_img = self.face_image.copy()
                display_img.thumbnail((410, 240), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(display_img)
                
                # Update display
                self.video_label.configure(image=photo, text="")
                self.video_label.image = photo
        except Exception as e:
            print(f"Error showing captured image: {e}")
    
    def _update_buttons_after_capture(self):
        """Update button states after capture like original"""
        self.camera_btn.configure(
            state="disabled",
            text="Photo Captured",
            bg="#e5e5e5",
            fg="#707070"
        )
        
        self.capture_btn.configure(state="disabled", bg="#cccccc", fg="#999999")
        self.save_btn.configure(state="normal", bg="#1E3A8A", fg="#ffffff")
        
        self.retake_btn.configure(
            state="normal",
            bg="#dc2626",
            fg="#ffffff"
        )
    
    def _retake_image(self):
        """Retake photo"""
        # Clear captured data
        self.face_image = None
        self.face_image_data = None
        
        # Reset button states like original
        self.camera_btn.configure(
            state="normal",
            text="Open Camera",
            bg="#ffffff",
            fg="#222222"
        )
        
        self.save_btn.configure(state="disabled", bg="#cccccc", fg="#999999")
        self.retake_btn.configure(
            state="disabled",
            bg="#e5e5e5",
            fg="#707070"
        )
        
        # Clear preview and restart camera
        self.video_label.configure(
            image="",
            text="Camera will appear here\nClick 'Open Camera' to begin"
        )
        
        # Restart camera
        self._start_camera()
    
    def _save_photo(self):
        """Save photo and close window"""
        try:
            if self.face_image and self.face_image_data:
                # Send data to parent
                if hasattr(self.parent_edit, 'on_face_capture_complete'):
                    self.parent_edit.on_face_capture_complete(self.face_image, self.face_image_data)
                else:
                    # Fallback
                    self.parent_edit.face_image = self.face_image
                    self.parent_edit.face_image_data = self.face_image_data
                    self.parent_edit.update_face_status()
                
                self._show_info_msg("Face image saved successfully!")
                self._on_closing()
            else:
                self._show_warning("No face image to save.")
        except Exception as e:
            self._show_error(f"Failed to save photo: {str(e)}")
    
    def _show_error(self, message):
        """Show error message ensuring it appears on top"""
        self.root.attributes('-topmost', False)
        tk.messagebox.showerror("Error", message, parent=self.root)
        self.root.attributes('-topmost', True)
    
    def _show_warning(self, message):
        """Show warning message ensuring it appears on top"""
        self.root.attributes('-topmost', False)
        tk.messagebox.showwarning("Warning", message, parent=self.root)
        self.root.attributes('-topmost', True)
    
    def _show_info_msg(self, message):
        """Show info message ensuring it appears on top"""
        self.root.attributes('-topmost', False)
        tk.messagebox.showinfo("Success", message, parent=self.root)
        self.root.attributes('-topmost', True)
    
    def _on_closing(self):
        """Handle window closing"""
        try:
            # Stop camera
            self.is_camera_active = False
            
            # Wait for thread
            if self.camera_thread and self.camera_thread.is_alive():
                self.camera_thread.join(timeout=1.0)
            
            # Release camera
            if self.camera:
                self.camera.release()
            
            # Release grab and destroy window
            try:
                self.root.grab_release()
            except Exception as e:
                print(f"Could not release grab: {e}")
            
            try:
                self.root.destroy()
            except Exception as e:
                print(f"Could not destroy window: {e}")
            
        except Exception as e:
            print(f"Error closing window: {e}")
            try:
                self.root.destroy()
            except:
                pass
