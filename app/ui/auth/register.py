import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from customtkinter.windows.widgets.image import CTkImage
import cv2
import threading
import time
import io
import numpy as np
import os
from .face_verification_dialog import FaceVerificationDialog

class RegisterForm(ctk.CTkFrame):
    def __init__(self, parent, db_manager=None):
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        
        # Initialize variables
        self.camera = None
        self.is_camera_active = False
        self.face_image = None
        self.face_image_data = None
        
        # Create StringVar for form fields
        self.first_name_var = tk.StringVar(value="")
        self.middle_name_var = tk.StringVar(value="")
        self.last_name_var = tk.StringVar(value="")
        self.email_var = tk.StringVar(value="")
        self.contact_number_var = tk.StringVar(value="")
        self.student_number_var = tk.StringVar(value="")
        self.password_var = tk.StringVar(value="")
        self.confirm_password_var = tk.StringVar(value="")
        
        # Create the registration form
        self._create_register_form()
        
        # Add trace to monitor changes
        self.first_name_var.trace_add("write", lambda *args: print(f"First Name changed to: {self.first_name_var.get()}"))
        self.last_name_var.trace_add("write", lambda *args: print(f"Last Name changed to: {self.last_name_var.get()}"))
        self.email_var.trace_add("write", lambda *args: print(f"Email changed to: {self.email_var.get()}"))
        self.contact_number_var.trace_add("write", lambda *args: print(f"Contact Number changed to: {self.contact_number_var.get()}"))
        self.student_number_var.trace_add("write", lambda *args: print(f"Student Number changed to: {self.student_number_var.get()}"))
        self.password_var.trace_add("write", lambda *args: print(f"Password changed to: {self.password_var.get()}"))
        self.confirm_password_var.trace_add("write", lambda *args: print(f"Confirm Password changed to: {self.confirm_password_var.get()}"))
        
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
        
        # Sign Up Button
        self.signup_button = ctk.CTkButton(
            card_frame,
            text="Next",
            width=120,
            height=27,
            corner_radius=10,
            border_width=1,
            font=ctk.CTkFont("Roboto", 12, "bold"),
            fg_color="#1E3A8A",
            hover_color="#152a63",
            command=self.open_verification_dialog
        )
        self.signup_button.place(x=315, y=450)

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
        # Reset form fields
        self.first_name_var.set("")
        self.middle_name_var.set("")
        self.last_name_var.set("")
        self.email_var.set("")
        self.contact_number_var.set("")
        self.student_number_var.set("")
        self.password_var.set("")
        self.confirm_password_var.set("")
        
        # Show login screen
        self.master.show_login()
        
        # Set remembered email
        if email:
            self.after(100, lambda e=email: self.email_var.set(e))

    def open_verification_dialog(self):
        """Open dialog for face verification during registration"""
        FaceVerificationDialog(self, self.db_manager)

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
            self.is_camera_active = False
            if hasattr(self, 'camera') and self.camera and self.camera.isOpened():
                self.camera.release()
                self.camera = None

    def start_camera(self):
        """Start camera capture"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                parent = self.dialog if hasattr(self, 'dialog') and self.dialog else self.master
                messagebox.showerror("Camera Error", "Could not open camera. Please check your camera connection.", parent=parent)
                return False

            self.is_camera_active = True

            if hasattr(self, 'preview_label') and self.preview_label.winfo_exists():
                self.preview_label.destroy()

            self.camera_label = ctk.CTkLabel(self.face_preview_frame, text="")
            self.camera_label.place(x=0, y=0)

            self.camera_thread = threading.Thread(target=self.update_camera_feed)
            self.camera_thread.daemon = True
            self.camera_thread.start()

            return True
        except Exception as e:
            parent = self.dialog if hasattr(self, 'dialog') and self.dialog else self.master
            messagebox.showerror("Camera Error", f"Error starting camera: {str(e)}", parent=parent)
            return False

    def update_camera_feed(self):
        """Update camera feed display"""
        while self.is_camera_active:
            try:
                ret, frame = self.camera.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    
                    img_ctk = ctk.CTkImage(
                        light_image=img, 
                        dark_image=img, 
                        size=(320, 240)
                    )
                    
                    if (hasattr(self, 'camera_label') and 
                        self.camera_label and 
                        self.camera_label.winfo_exists()):
                        try:
                            self.camera_label.configure(image=img_ctk)
                        except tk.TclError:
                            break
                    else:
                        break
            except Exception as e:
                print(f"Error updating camera feed: {e}")
                break

            time.sleep(0.03)
        
        self.is_camera_active = False

    def stop_camera(self):
        """Stop camera capture"""
        try:
            self.is_camera_active = False
            
            if hasattr(self, 'camera_thread') and self.camera_thread.is_alive():
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

            if hasattr(self, 'camera_label') and self.camera_label:
                try:
                    if self.camera_label.winfo_exists():
                        self.camera_label.destroy()
                except Exception:
                    pass
                finally:
                    self.camera_label = None

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

            self.face_image = Image.fromarray(frame_rgb)
            img_byte_arr = io.BytesIO()
            self.face_image.save(img_byte_arr, format='PNG')
            self.face_image_data = img_byte_arr.getvalue()

            if len(self.face_image_data) > 5 * 1024 * 1024:
                messagebox.showwarning(
                    "Image Too Large",
                    "The captured image exceeds the 5MB limit. Please try again with a smaller resolution.",
                    parent=self.dialog
                )
                self.face_image = None
                self.face_image_data = None
                return

            self.stop_camera()
            self.camera_button.configure(text="Open Camera")
            self.capture_button.configure(state="disabled")
            
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
            
            preview_img = image.copy()
            img_ctk = ctk.CTkImage(
                light_image=preview_img, 
                dark_image=preview_img, 
                size=(320, 240)
            )
            
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
            
            # Debug prints
            print("Form Values:")
            print(f"First Name: '{first_name}'")
            print(f"Last Name: '{last_name}'")
            print(f"Email: '{email}'")
            print(f"Contact Number: '{contact_number}'")
            print(f"Student Number: '{student_number}'")
            print(f"Password: '{password}'")
            print(f"Confirm Password: '{confirm_password}'")

            # Validate required fields
            if not first_name or not last_name or not email or not contact_number or not student_number or not password:
                print("Validation failed - missing fields:")
                if not first_name: print("First Name is empty")
                if not last_name: print("Last Name is empty")
                if not email: print("Email is empty")
                if not contact_number: print("Contact Number is empty")
                if not student_number: print("Student Number is empty")
                if not password: print("Password is empty")
                messagebox.showwarning("Registration Failed", "Please fill in all required fields.", parent=self.dialog)
                return

            if password != confirm_password:
                messagebox.showwarning("Registration Failed", "Passwords do not match.", parent=self.dialog)
                return

            if not self.face_image_data or len(self.face_image_data) == 0:
                messagebox.showwarning(
                    "Face Image Required", 
                    "A face image is required for registration. Please capture your face using the camera.",
                    parent=self.dialog
                )
                return
            
            self.master.config(cursor="wait")
            if hasattr(self, 'dialog') and self.dialog:
                self.dialog.config(cursor="wait")
            self.master.update_idletasks()
            if hasattr(self, 'dialog') and self.dialog:
                self.dialog.update_idletasks()
            
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
            
            self.master.config(cursor="")
            if hasattr(self, 'dialog') and self.dialog:
                self.dialog.config(cursor="")
            
            if self.is_camera_active:
                self.is_camera_active = False
                if self.camera and self.camera.isOpened():
                    self.camera.release()
                    self.camera = None
            
            if success:
                messagebox.showinfo(
                    "Registration Successful",
                    "Your account has been created! You can now log in.",
                    parent=self.dialog
                )
                
                if hasattr(self, 'dialog') and self.dialog:
                    try:
                        self.dialog.destroy()
                    except Exception:
                        pass
                    
                remembered_email = email
                
                self.first_name_var = tk.StringVar(value="")
                self.middle_name_var = tk.StringVar(value="")
                self.last_name_var = tk.StringVar(value="")
                self.email_var = tk.StringVar(value="")
                self.student_number_var = tk.StringVar(value="")
                self.password_var = tk.StringVar(value="")
                self.confirm_password_var = tk.StringVar(value="")
                
                self.master.show_login()
                
                if remembered_email:
                    self.after(100, lambda e=remembered_email: self.email_var.set(e))
            else:
                messagebox.showerror("Registration Failed", result, parent=self.dialog)
                
        except Exception as e:
            messagebox.showerror("Registration Error", f"An unexpected error occurred: {str(e)}", parent=self.dialog)
            import traceback
            traceback.print_exc()

    def on_dialog_closing(self):
        """Handle dialog closing"""
        try:
            if self.is_camera_active:
                self.is_camera_active = False
                if self.camera and self.camera.isOpened():
                    self.camera.release()
                    self.camera = None
            
            if hasattr(self, 'dialog') and self.dialog:
                self.dialog.destroy()
                
        except Exception as e:
            print(f"Error while closing dialog: {str(e)}") 