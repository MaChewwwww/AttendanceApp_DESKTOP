import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import cv2
import threading
import time
import io
import os
from PIL import Image, ImageTk

class RegisterForm(ctk.CTkFrame):
    def __init__(self, parent, db_manager=None):
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        
        # Face verification variables
        self.face_image = None
        self.face_image_data = None
        self.camera = None
        self.is_camera_active = False
        self.camera_thread = None
        self.verification_dialog = None
        
        # Create StringVar for form fields with test data
        self.first_name_var = tk.StringVar(value="John")
        self.middle_name_var = tk.StringVar(value="Michael")
        self.last_name_var = tk.StringVar(value="Doe")
        self.email_var = tk.StringVar(value="john.doe@example.com")
        self.contact_number_var = tk.StringVar(value="09123456789")
        self.student_number_var = tk.StringVar(value="2021-123456")
        self.password_var = tk.StringVar(value="password123")
        self.confirm_password_var = tk.StringVar(value="password123")
        
        # Create the registration form
        self._create_register_form()
        
    def _create_register_form(self):
        """Create the registration form UI"""
        # Title "Sign up as"
        ctk.CTkLabel(
            self,
            text="Sign up as",
            font=ctk.CTkFont("Roboto", 24, "bold"),
            text_color="#000000"
        ).place(x=20, y=20)
        
        # Student label
        ctk.CTkLabel(
            self,
            text="Student",
            font=ctk.CTkFont("Roboto", 24, "bold"),
            text_color="#1E3A8A"
        ).place(x=20, y=45)
        
        # Divider
        divider = ctk.CTkFrame(
            self,
            fg_color="#1E3A8A",
            width=50,
            height=2
        )
        divider.place(x=20, y=75)
        
        # Card Frame
        card_frame = ctk.CTkFrame(
            self,
            width=455,
            height=493,
            corner_radius=15,
            fg_color="#ffffff",
            border_width=1,
            border_color="#d1d1d1"
        )
        card_frame.place(x=20, y=100)
        card_frame.pack_propagate(False)
        
        # Create two columns
        left_column = ctk.CTkFrame(card_frame, fg_color="transparent")
        left_column.place(x=20, y=10)
        
        right_column = ctk.CTkFrame(card_frame, fg_color="transparent")
        right_column.place(x=237, y=10)
        
        # First Name Label and Input (Left Column)
        ctk.CTkLabel(
            left_column,
            text="First Name",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.first_name_entry = ctk.CTkEntry(
            left_column,
            width=200,
            height=23,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            textvariable=self.first_name_var
        )
        self.first_name_entry.pack(pady=(2, 5))
        
        # Last Name Label and Input (Right Column)
        ctk.CTkLabel(
            right_column,
            text="Last Name",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.last_name_entry = ctk.CTkEntry(
            right_column,
            width=200,
            height=23,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            textvariable=self.last_name_var
        )
        self.last_name_entry.pack(pady=(2, 5))
        
        # Date of Birth Row
        dob_container = ctk.CTkFrame(card_frame, fg_color="transparent")
        dob_container.place(x=20, y=75)
        
        # Date of Birth Label
        ctk.CTkLabel(
            dob_container,
            text="Date of Birth",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070"
        ).pack(anchor="w")
        
        # Date Input Fields Container
        date_fields = ctk.CTkFrame(dob_container, fg_color="transparent")
        date_fields.pack(pady=(2, 5))
        
        # Day Input
        self.day_entry = ctk.CTkEntry(
            date_fields,
            width=130,
            height=23,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            placeholder_text="Day"
        )
        self.day_entry.pack(side="left", padx=(0, 10))
        self.day_entry.insert(0, "15")
        
        # Month Input
        self.month_entry = ctk.CTkEntry(
            date_fields,
            width=130,
            height=23,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            placeholder_text="Month"
        )
        self.month_entry.pack(side="left", padx=(0, 10))
        self.month_entry.insert(0, "06")
        
        # Year Input
        self.year_entry = ctk.CTkEntry(
            date_fields,
            width=130,
            height=23,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            placeholder_text="Year"
        )
        self.year_entry.pack(side="left")
        self.year_entry.insert(0, "2000")
        
        # Contact Number
        contact_container = ctk.CTkFrame(card_frame, fg_color="transparent")
        contact_container.place(x=20, y=130)
        
        ctk.CTkLabel(
            contact_container,
            text="Contact Number",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.contact_entry = ctk.CTkEntry(
            contact_container,
            width=200,
            height=23,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            textvariable=self.contact_number_var
        )
        self.contact_entry.pack(pady=(2, 5))
        
        # Student Number
        student_container = ctk.CTkFrame(card_frame, fg_color="transparent")
        student_container.place(x=20, y=185)
        
        ctk.CTkLabel(
            student_container,
            text="Student Number",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.student_entry = ctk.CTkEntry(
            student_container,
            width=419,
            height=23,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            textvariable=self.student_number_var
        )
        self.student_entry.pack(pady=(2, 5))
        
        # Webmail Address
        webmail_container = ctk.CTkFrame(card_frame, fg_color="transparent")
        webmail_container.place(x=20, y=240)
        
        ctk.CTkLabel(
            webmail_container,
            text="Webmail Address",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.webmail_entry = ctk.CTkEntry(
            webmail_container,
            width=419,
            height=23,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            textvariable=self.email_var
        )
        self.webmail_entry.pack(pady=(2, 5))
        
        # Password
        password_container = ctk.CTkFrame(card_frame, fg_color="transparent")
        password_container.place(x=20, y=295)
        
        ctk.CTkLabel(
            password_container,
            text="Password",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.password_entry = ctk.CTkEntry(
            password_container,
            width=419,
            height=23,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            show="•",
            textvariable=self.password_var
        )
        self.password_entry.pack(pady=(2, 5))
        
        # Confirm Password
        confirm_container = ctk.CTkFrame(card_frame, fg_color="transparent")
        confirm_container.place(x=20, y=350)
        
        ctk.CTkLabel(
            confirm_container,
            text="Confirm Password",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070"
        ).pack(anchor="w")
        
        self.confirm_entry = ctk.CTkEntry(
            confirm_container,
            width=419,
            height=23,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            show="•",
            textvariable=self.confirm_password_var
        )
        self.confirm_entry.pack(pady=(2, 5))
        
        # Terms and Condition Checkbox
        terms_container = ctk.CTkFrame(card_frame, fg_color="transparent")
        terms_container.place(x=20, y=405)
        
        self.terms_checkbox = ctk.CTkCheckBox(
            terms_container,
            text="I agree to the Terms and Condition",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070",
            fg_color="#1E3A8A",
            hover_color="#1E3A8A",
            border_color="#d1d1d1",
            checkbox_width=15,
            checkbox_height=15,
            corner_radius=2,
            border_width=1
        )
        self.terms_checkbox.pack(anchor="w")
        self.terms_checkbox.select()  # Check the checkbox by default
        
        # Sign Up Button
        self.signup_button = ctk.CTkButton(
            card_frame,
            text="Sign Up",
            width=120,
            height=27,
            corner_radius=10,
            border_width=1,
            font=ctk.CTkFont("Roboto", 12, "bold"),
            fg_color="#1E3A8A",
            hover_color="#152a63",
            command=self.handle_register
        )
        self.signup_button.place(x=315, y=450)
        
        # Force update the display after creating all widgets
        self.after(100, self._refresh_test_data)
    
    def _refresh_test_data(self):
        """Refresh test data in the form fields"""
        # Ensure test data is displayed
        self.first_name_var.set("John")
        self.last_name_var.set("Doe")
        self.email_var.set("john.doe@example.com")
        self.contact_number_var.set("09123456789")
        self.student_number_var.set("2021-123456")
        self.password_var.set("password123")
        self.confirm_password_var.set("password123")
        
        # Update the entry widgets
        self.first_name_entry.update()
        self.last_name_entry.update()
        self.webmail_entry.update()
        self.contact_entry.update()
        self.student_entry.update()
        self.password_entry.update()
        self.confirm_entry.update()

    def get_form_data(self):
        """Get all form data as a dictionary"""
        return {
            'first_name': self.first_name_var.get(),
            'middle_name': self.middle_name_var.get(),
            'last_name': self.last_name_var.get(),
            'email': self.email_var.get(),
            'contact_number': self.contact_number_var.get(),
            'student_number': self.student_number_var.get(),
            'password': self.password_var.get(),
            'confirm_password': self.confirm_password_var.get()
        }

    def on_registration_success(self, email):
        """Handle successful registration"""
        # Reset form fields to test data for next registration
        self.first_name_var.set("John")
        self.middle_name_var.set("Michael")
        self.last_name_var.set("Doe")
        self.email_var.set("john.doe@example.com")
        self.contact_number_var.set("09123456789")
        self.student_number_var.set("2021-123456")
        self.password_var.set("password123")
        self.confirm_password_var.set("password123")
        
        # Reset date fields
        self.day_entry.delete(0, tk.END)
        self.day_entry.insert(0, "15")
        self.month_entry.delete(0, tk.END)
        self.month_entry.insert(0, "06")
        self.year_entry.delete(0, tk.END)
        self.year_entry.insert(0, "2000")
        
        # Check the terms checkbox
        self.terms_checkbox.select()
        
        # Show login screen
        self.master.show_login()
        
        # Set remembered email
        if email:
            self.after(100, lambda e=email: self.email_var.set(e))

    def handle_register(self):
        """Process the registration form submission"""
        try:
            # Get values from form fields
            first_name = self.first_name_var.get().strip()
            last_name = self.last_name_var.get().strip()
            middle_name = self.middle_name_var.get().strip()
            email = self.email_var.get().strip()
            contact_number = self.contact_number_var.get().strip()
            student_number = self.student_number_var.get().strip()
            password = self.password_var.get().strip()
            confirm_password = self.confirm_password_var.get().strip()

            # Validate required fields
            if not first_name or not last_name or not email or not contact_number or not student_number or not password:
                messagebox.showwarning("Registration Failed", "Please fill in all required fields.")
                return

            if password != confirm_password:
                messagebox.showwarning("Registration Failed", "Passwords do not match.")
                return

            # Check terms and conditions
            if not self.terms_checkbox.get():
                messagebox.showwarning("Registration Failed", "Please agree to the Terms and Conditions.")
                return

            # Open face verification dialog
            self.open_face_verification_dialog()
            
        except Exception as e:
            messagebox.showerror("Registration Error", f"An unexpected error occurred: {str(e)}")
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
            state="disabled",
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
            middle_name = self.middle_name_var.get().strip()
            email = self.email_var.get().strip()
            contact_number = self.contact_number_var.get().strip()
            student_number = self.student_number_var.get().strip()
            password = self.password_var.get().strip()
            
            # Attempt registration
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
            
            # Reset cursor
            self.verification_dialog.configure(cursor="")
            
            # Clean up camera
            if self.is_camera_active:
                self.stop_camera()
            
            if success:
                messagebox.showinfo(
                    "Registration Successful",
                    "Your account has been created! You can now log in.",
                    parent=self.verification_dialog
                )
                
                # Close dialog
                self.verification_dialog.destroy()
                
                # Call success handler
                self.on_registration_success(email)
            else:
                messagebox.showerror("Registration Failed", result, parent=self.verification_dialog)
                
        except Exception as e:
            self.verification_dialog.configure(cursor="")
            messagebox.showerror("Registration Error", f"An unexpected error occurred: {str(e)}", parent=self.verification_dialog)
            import traceback
            traceback.print_exc()

    def on_verification_dialog_closing(self):
        """Handle verification dialog closing"""
        try:
            # Stop camera and clean up
            if self.is_camera_active:
                self.stop_camera()
            
            # Destroy dialog
            if self.verification_dialog:
                self.verification_dialog.destroy()
                
        except Exception as e:
            print(f"Error while closing verification dialog: {str(e)}")
            
    def _update_ui_after_camera_close(self):
        """Update UI after camera window is closed"""
        self.camera_button.configure(text="Open Camera")
        self.capture_button.configure(state="disabled")
        if not self.face_image:
            self.preview_label = ctk.CTkLabel(
                self.face_preview_frame,
                text="Camera will appear here\nClick 'Open Camera' to begin",
                font=ctk.CTkFont("Roboto", 12),
                text_color="#a0a0a0"
            )
            self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

    def retake_photo(self):
        """Retake photo - restart camera"""
        self.face_image = None
        self.face_image_data = None
        self.register_button.configure(state="disabled")
        self.retake_button.configure(state="disabled")
        
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
            
            # Enable buttons
            self.register_button.configure(state="normal")
            self.retake_button.configure(state="normal")
            
            messagebox.showinfo("Success", "Face image captured successfully! You can now proceed with registration.", parent=self.verification_dialog)
            
        except Exception as e:
            print(f"Capture error: {e}")
            messagebox.showerror("Error", f"Failed to capture image: {str(e)}", parent=self.verification_dialog)