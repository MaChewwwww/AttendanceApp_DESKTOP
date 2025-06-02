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
        
        # Image/file preview box
        self.preview_frame = ctk.CTkFrame(right_col, fg_color="#fff")
        self.preview_frame.pack(fill="x", pady=(0, 10))
        
        self.img_frame = ctk.CTkFrame(self.preview_frame, fg_color="#222", width=40, height=40, corner_radius=6)
        self.img_frame.pack(side="left", pady=(0, 0), padx=(0, 8))
        self.img_frame.pack_propagate(False)
        
        self.img_label = ctk.CTkLabel(self.img_frame, text="", fg_color="#222")
        self.img_label.pack(expand=True, fill="both")
        
        file_info = ctk.CTkFrame(self.preview_frame, fg_color="#fff")
        file_info.pack(fill="x", pady=(0, 0))
        
        self.file_name_label = ctk.CTkLabel(file_info, text="No image", font=ctk.CTkFont(size=13, weight="bold"), text_color="#000")
        self.file_name_label.pack(anchor="w")
        
        self.file_type_label = ctk.CTkLabel(file_info, text="", font=ctk.CTkFont(size=11), text_color="#757575")
        self.file_type_label.pack(anchor="w")
        
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
                
                # Update preview
                self.update_image_preview()
                
        except Exception as e:
            print(f"Error loading existing face image: {e}")

    def update_image_preview(self):
        """Update the image preview area"""
        try:
            if self.face_image:
                # Create thumbnail for preview
                thumbnail = self.face_image.copy()
                thumbnail.thumbnail((40, 40), Image.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(thumbnail)
                
                # Update image label
                self.img_label.configure(image=photo, text="")
                self.img_label.image = photo  # Keep reference
                
                # Update file info
                self.file_name_label.configure(text="face_image.jpg")
                self.file_type_label.configure(text=".jpg")
                
                # Update frame color to indicate image present
                self.img_frame.configure(fg_color="#4CAF50")
            else:
                # No image
                self.img_label.configure(image="", text="")
                self.file_name_label.configure(text="No image")
                self.file_type_label.configure(text="")
                self.img_frame.configure(fg_color="#222")
                
        except Exception as e:
            print(f"Error updating image preview: {e}")

    def open_facial_recognition(self):
        """Open facial recognition popup"""
        FacialRecognitionPopup(self)

    def show_caution_modal(self):
        """Show caution modal before saving"""
        def on_continue():
            print('Changes saved!')
            # Place your save logic here
        
        from .users_modals import CautionModal
        CautionModal(self, on_continue=on_continue)

class FacialRecognitionPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_edit = parent
        self.title("Facial Recognition")
        self.geometry("454x450")
        self.resizable(False, False)
        self.configure(fg_color="#222222")
        
        # Camera variables
        self.camera = None
        self.is_camera_active = False
        self.camera_thread = None
        self.current_frame = None
        self.camera_canvas = None
        self.current_photo = None
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self._center_window()
        
        # Setup UI
        self.setup_ui()
        
        # Handle close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 454) // 2
        y = (screen_height - 450) // 2
        self.geometry(f"454x450+{x}+{y}")

    def setup_ui(self):
        """Setup the facial recognition UI"""
        # Card Frame
        card = ctk.CTkFrame(
            self, 
            width=454, 
            height=450, 
            corner_radius=12, 
            fg_color="#ffffff", 
            border_width=0
        )
        card.place(x=0, y=0)
        card.pack_propagate(False)

        # Info button
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
            command=lambda: messagebox.showinfo("Info", "Please ensure you're in a well-lit environment before capturing your photo for the best image quality", parent=self)
        )
        info_btn.place(x=420, y=10)

        # Camera Preview Frame
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

        # Default Preview Label
        self.preview_label = ctk.CTkLabel(
            self.face_preview_frame,
            text="Camera will appear here\nClick 'Open Camera' to begin",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#a0a0a0"
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Camera button
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
        self.camera_button.place(x=22, y=290)

        # Retake and Capture buttons
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
            font=ctk.CTkFont("Roboto", 13, "bold"),
            fg_color="#1E3A8A",
            text_color="#fff",
            border_width=0,
            hover_color="#152a63",
            state="disabled",
            command=self.capture_face
        )
        self.capture_button.place(x=232, y=335)

        # Save button
        self.save_button = ctk.CTkButton(
            card,
            text="Save Photo",
            width=410,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 13, "bold"),
            fg_color="#1E3A8A",
            text_color="#fff",
            border_width=0,
            hover_color="#152a63",
            command=self.save_photo,
            state="disabled"
        )
        self.save_button.place(x=22, y=385)

    def toggle_camera(self):
        """Toggle camera on/off"""
        try:
            if self.is_camera_active:
                self.stop_camera()
            else:
                self.start_camera()
        except Exception as e:
            messagebox.showerror("Camera Error", f"Error with camera: {str(e)}", parent=self)

    def start_camera(self):
        """Start camera capture"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                messagebox.showerror("Camera Error", "Could not open camera. Please check your camera connection.", parent=self)
                return False

            self.is_camera_active = True
            self.camera_button.configure(text="Close Camera")
            self.capture_button.configure(state="normal")
            
            # Hide placeholder
            self.preview_label.place_forget()
            
            # Create canvas for camera display
            self.camera_canvas = tk.Canvas(
                self.face_preview_frame,
                width=410,
                height=240,
                bg="#fafafa",
                highlightthickness=0
            )
            self.camera_canvas.place(x=0, y=0, width=410, height=240)
            
            # Start video feed thread
            self.camera_thread = threading.Thread(target=self._update_camera_display)
            self.camera_thread.daemon = True
            self.camera_thread.start()
            
            return True
        except Exception as e:
            messagebox.showerror("Camera Error", f"Error starting camera: {str(e)}", parent=self)
            return False

    def stop_camera(self):
        """Stop camera capture"""
        try:
            self.is_camera_active = False
            self._cleanup_camera()
            self._update_ui_after_camera_close()
        except Exception as e:
            print(f"Error stopping camera: {e}")

    def _update_camera_display(self):
        """Update camera feed display"""
        while self.is_camera_active:
            try:
                ret, frame = self.camera.read()
                if ret:
                    self.current_frame = frame.copy()
                    frame_resized = cv2.resize(frame, (410, 240))
                    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                    
                    # Add guide rectangle
                    h, w = frame_rgb.shape[:2]
                    center_x, center_y = w // 2, h // 2
                    rect_w, rect_h = 160, 180
                    cv2.rectangle(frame_rgb, 
                                 (center_x - rect_w//2, center_y - rect_h//2),
                                 (center_x + rect_w//2, center_y + rect_h//2),
                                 (0, 255, 0), 2)
                    
                    # Convert and display
                    pil_image = Image.fromarray(frame_rgb)
                    
                    if (hasattr(self, 'camera_canvas') and 
                        self.camera_canvas and 
                        self.winfo_exists()):
                        
                        def update_canvas(img=pil_image):
                            try:
                                if (hasattr(self, 'camera_canvas') and 
                                    self.camera_canvas and 
                                    self.camera_canvas.winfo_exists()):
                                    
                                    photo = ImageTk.PhotoImage(img)
                                    self.camera_canvas.delete("all")
                                    self.camera_canvas.create_image(205, 120, image=photo, anchor="center")
                                    self.current_photo = photo
                                    
                            except tk.TclError:
                                self.is_camera_active = False
                            except Exception as e:
                                print(f"Canvas update error: {e}")
                        
                        self.after(0, update_canvas)
                    else:
                        break
                        
            except Exception as e:
                print(f"Camera display error: {e}")
                break

            time.sleep(0.03)

    def _cleanup_camera(self):
        """Clean up camera resources"""
        self.is_camera_active = False
        
        if hasattr(self, 'camera_thread') and self.camera_thread and self.camera_thread.is_alive():
            try:
                self.camera_thread.join(0.5)
            except Exception:
                pass

        if hasattr(self, 'camera') and self.camera and self.camera.isOpened():
            try:
                self.camera.release()
            except Exception:
                pass
            finally:
                self.camera = None

        if hasattr(self, 'camera_canvas') and self.camera_canvas:
            try:
                if self.camera_canvas.winfo_exists():
                    self.camera_canvas.destroy()
            except Exception:
                pass
            finally:
                self.camera_canvas = None
        
        self.current_photo = None

    def _update_ui_after_camera_close(self):
        """Update UI after camera closes"""
        self.camera_button.configure(text="Open Camera")
        self.capture_button.configure(state="disabled")
        
        if not hasattr(self.parent_edit, 'face_image') or not self.parent_edit.face_image:
            self.preview_label = ctk.CTkLabel(
                self.face_preview_frame,
                text="Camera will appear here\nClick 'Open Camera' to begin",
                font=ctk.CTkFont("Roboto", 12),
                text_color="#a0a0a0"
            )
            self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

    def capture_face(self):
        """Capture face from camera"""
        if not self.is_camera_active or not hasattr(self, 'current_frame') or self.current_frame is None:
            messagebox.showwarning("Camera Error", "No frame available. Please wait for camera to initialize.", parent=self)
            return
        
        try:
            frame = self.current_frame.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Store in parent
            self.parent_edit.face_image = Image.fromarray(frame_rgb)
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            self.parent_edit.face_image.save(img_byte_arr, format='PNG')
            self.parent_edit.face_image_data = img_byte_arr.getvalue()

            # Stop camera and show preview
            self.stop_camera()
            self.show_face_preview()
            self._update_buttons_after_capture()
            
            messagebox.showinfo("Success", "Face image captured successfully!", parent=self)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture image: {str(e)}", parent=self)

    def show_face_preview(self):
        """Show captured face preview"""
        try:
            for widget in self.face_preview_frame.winfo_children():
                widget.destroy()
            
            if self.parent_edit.face_image:
                preview_canvas = tk.Canvas(
                    self.face_preview_frame,
                    width=410,
                    height=240,
                    bg="#fafafa",
                    highlightthickness=0
                )
                preview_canvas.place(x=0, y=0, width=410, height=240)
                
                preview_img = self.parent_edit.face_image.copy()
                preview_img.thumbnail((410, 240), Image.LANCZOS)
                photo = ImageTk.PhotoImage(preview_img)
                
                preview_canvas.create_image(205, 120, image=photo, anchor="center")
                preview_canvas.image = photo
            
        except Exception as e:
            print(f"Error showing face preview: {e}")

    def _update_buttons_after_capture(self):
        """Update button states after capture"""
        self.camera_button.configure(
            state="disabled",
            text="Photo Captured",
            fg_color="#e5e5e5",
            text_color="#707070"
        )
        
        self.capture_button.configure(state="disabled")
        self.save_button.configure(state="normal")
        
        self.retake_button.configure(
            state="normal",
            fg_color="#dc2626",
            text_color="#ffffff",
            hover_color="#b91c1c"
        )

    def retake_photo(self):
        """Retake photo"""
        self.parent_edit.face_image = None
        self.parent_edit.face_image_data = None
        
        self._reset_buttons_for_retake()
        
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
        """Reset buttons for retake"""
        self.camera_button.configure(
            state="normal",
            text="Close Camera",
            fg_color="#ffffff",
            text_color="#222"
        )
        
        self.save_button.configure(state="disabled")
        
        self.retake_button.configure(
            state="disabled",
            fg_color="#e5e5e5",
            text_color="#707070"
        )

    def save_photo(self):
        """Save photo and close modal"""
        try:
            # Update parent's image preview
            self.parent_edit.update_image_preview()
            
            messagebox.showinfo("Success", "Face image updated successfully!", parent=self)
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save photo: {str(e)}", parent=self)

    def on_closing(self):
        """Handle window closing"""
        try:
            if self.is_camera_active:
                self.stop_camera()
            self.destroy()
        except Exception as e:
            print(f"Error closing facial recognition popup: {e}")
