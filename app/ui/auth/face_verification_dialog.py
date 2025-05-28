import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import cv2
import threading
import time
import io
import os

class FaceVerificationDialog:
    def __init__(self, parent, db_manager=None):
        self.parent = parent
        self.db_manager = db_manager
        self.dialog = None
        self.camera = None
        self.is_camera_active = False
        self.face_image = None
        self.face_image_data = None
        
        # Create the dialog
        self.create_dialog()
        
    def create_dialog(self):
        """Create the face verification dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Complete Registration")
        self.dialog.geometry("500x700")
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

        self._create_dialog_content()
        
        # Bind dialog close to cleanup
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_dialog_closing)

    def _create_dialog_content(self):
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

        # Camera Controls Frame
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
        
        # Submit Button
        self.submit_button = ctk.CTkButton(
            inner_frame,
            text="Submit Registration",
            width=200,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12, "bold"),
            fg_color="#4CAF50",
            hover_color="#388E3C",
            command=self.handle_register
        )
        self.submit_button.pack(pady=15)

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
                messagebox.showerror("Camera Error", "Could not open camera. Please check your camera connection.", parent=self.dialog)
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
            messagebox.showerror("Camera Error", f"Error starting camera: {str(e)}", parent=self.dialog)
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
            # Get form data from parent
            form_data = self.parent.get_form_data()
            if not form_data:
                messagebox.showwarning("Registration Failed", "Form data not available.", parent=self.dialog)
                return

            first_name = form_data.get('first_name', '').strip()
            last_name = form_data.get('last_name', '').strip()
            middle_name = form_data.get('middle_name', '').strip()
            email = form_data.get('email', '').strip()
            contact_number = form_data.get('contact_number', '').strip()
            student_number = form_data.get('student_number', '').strip()
            password = form_data.get('password', '').strip()
            confirm_password = form_data.get('confirm_password', '').strip()

            # Validate required fields
            if not first_name or not last_name or not email or not contact_number or not student_number or not password:
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
            
            self.dialog.config(cursor="wait")
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
                
                try:
                    self.dialog.destroy()
                except Exception:
                    pass
                    
                self.parent.on_registration_success(email)
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
            
            if self.dialog:
                self.dialog.destroy()
                
        except Exception as e:
            print(f"Error while closing dialog: {str(e)}") 