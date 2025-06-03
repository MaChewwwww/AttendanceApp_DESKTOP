import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import cv2
import threading
import time
import io
from PIL import Image, ImageTk
import os
import numpy as np

class IndependentFacialRecognitionWindow:
    """Completely independent facial recognition window"""
    
    def __init__(self, parent_callback):
        self.parent_callback = parent_callback
        
        # Create completely independent root window
        self.verification_dialog = ctk.CTkToplevel()
        self.verification_dialog.title("Facial Recognition")
        self.verification_dialog.geometry("454x450")
        self.verification_dialog.resizable(False, False)
        self.verification_dialog.configure(fg_color="#222222")
        
        # Make it completely independent - DO NOT SET TOPMOST INITIALLY
        # This can interfere with grab
        
        # Camera variables
        self.camera = None
        self.is_camera_active = False
        self.camera_thread = None
        self.current_frame = None
        self.face_image = None
        self.face_image_data = None
        self.camera_canvas = None
        self.current_photo = None
        
        # Center window
        self._center_window()
        
        # Setup UI content
        self._create_verification_dialog_content()
        
        # Handle close
        self.verification_dialog.protocol("WM_DELETE_WINDOW", self.on_verification_dialog_closing)
        
        # Set grab AFTER everything is initialized and delay to ensure proper grab
        self.verification_dialog.after(200, self._set_grab_and_focus)

    def _set_grab_and_focus(self):
        """Set grab and focus after window is fully initialized"""
        try:
            # First focus the window
            self.verification_dialog.focus_force()
            self.verification_dialog.lift()
            
            # Then set grab
            self.verification_dialog.grab_set()
            
            # Make it topmost AFTER grab is set
            self.verification_dialog.attributes('-topmost', True)
            
            print("Successfully set grab on camera dialog")
        except Exception as e:
            print(f"Could not set grab on camera dialog: {e}")
            # Continue without grab - dialog will still work

    def _center_window(self):
        """Center the window on screen"""
        self.verification_dialog.update_idletasks()
        screen_width = self.verification_dialog.winfo_screenwidth()
        screen_height = self.verification_dialog.winfo_screenheight()
        x = (screen_width - 454) // 2
        y = (screen_height - 450) // 2
        self.verification_dialog.geometry(f"454x450+{x}+{y}")

    def _create_verification_dialog_content(self):
        """Create content for the face verification dialog"""
        # Card Frame
        self.card = ctk.CTkFrame(
            self.verification_dialog, 
            width=454, 
            height=450, 
            corner_radius=12, 
            fg_color="#ffffff", 
            border_width=0
        )
        self.card.place(x=0, y=0)
        self.card.pack_propagate(False)
        self.card.grid_propagate(False)

        # Info icon
        info_btn = ctk.CTkButton(
            self.card, 
            text="i", 
            width=24, 
            height=24, 
            corner_radius=12, 
            fg_color="#f5f5f5", 
            text_color="#222", 
            font=ctk.CTkFont("Roboto", 14, "bold"), 
            hover_color="#e0e0e0", 
            command=lambda: messagebox.showinfo("Camera Info", "Please ensure you're in a well-lit environment before capturing your photo for the best image quality", parent=self.verification_dialog)
        )
        info_btn.place(x=420, y=10)

        # Camera Preview Frame
        self.face_preview_frame = ctk.CTkFrame(
            self.card, 
            width=410, 
            height=240, 
            fg_color="#fafafa", 
            border_width=1, 
            border_color="#d1d1d1"
        )
        self.face_preview_frame.place(x=22, y=38)
        self.face_preview_frame.pack_propagate(False)
        self.face_preview_frame.grid_propagate(False)

        # Default Preview Label
        self.preview_label = ctk.CTkLabel(
            self.face_preview_frame,
            text="Camera will appear here\nClick 'Open Camera' to begin",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#a0a0a0"
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Open Camera Button
        self.camera_button = ctk.CTkButton(
            self.card,
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

        # Retake and Capture Buttons
        self.retake_button = ctk.CTkButton(
            self.card,
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
            self.card,
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

        # Save Button
        self.save_button = ctk.CTkButton(
            self.card,
            text="Save Photo",
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
        self.save_button.place(x=22, y=385)

    def toggle_camera(self):
        """Toggle camera on/off"""
        if self.is_camera_active:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        """Start camera capture"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                messagebox.showerror("Error", "Could not open camera. Please check your camera connection.", parent=self.verification_dialog)
                return False

            self.is_camera_active = True
            self.camera_button.configure(text="Close Camera")
            self.capture_button.configure(state="normal")
            
            # Hide the placeholder
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
            messagebox.showerror("Error", f"Error starting camera: {str(e)}", parent=self.verification_dialog)
            return False

    def stop_camera(self):
        """Stop camera capture"""
        self.is_camera_active = False
        self._cleanup_camera_window()
        self._update_ui_after_camera_close()

    def _update_camera_display(self):
        """Update camera feed display"""
        while self.is_camera_active:
            try:
                ret, frame = self.camera.read()
                if ret:
                    self.current_frame = frame.copy()
                    frame_resized = cv2.resize(frame, (410, 240))
                    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                    
                    # Add face guide
                    h, w = frame_rgb.shape[:2]
                    center_x, center_y = w // 2, h // 2
                    rect_w, rect_h = 160, 180
                    cv2.rectangle(frame_rgb, 
                                 (center_x - rect_w//2, center_y - rect_h//2),
                                 (center_x + rect_w//2, center_y + rect_h//2),
                                 (0, 255, 0), 2)
                    
                    try:
                        pil_image = Image.fromarray(frame_rgb)
                        
                        if (hasattr(self, 'camera_canvas') and 
                            self.camera_canvas and 
                            self.verification_dialog and 
                            self.verification_dialog.winfo_exists()):

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

                            self.verification_dialog.after(0, update_canvas)
                        else:
                            break

                    except Exception as img_error:
                        print(f"Image processing error: {img_error}")
                        break
                        
            except Exception as e:
                print(f"Camera display error: {e}")
                break

            time.sleep(0.03)
        
        self.is_camera_active = False

    def _cleanup_camera_window(self):
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
        """Update UI after camera close"""
        if not self.face_image:
            self.camera_button.configure(text="Open Camera")
            self.capture_button.configure(state="disabled")
            
            self.preview_label = ctk.CTkLabel(
                self.face_preview_frame,
                text="Camera will appear here\nClick 'Open Camera' to begin",
                font=ctk.CTkFont("Roboto", 12),
                text_color="#a0a0a0"
            )
            self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

    def capture_face(self):
        """Capture current frame"""
        if not self.is_camera_active:
            messagebox.showwarning("Warning", "Camera is not active. Please open camera first.", parent=self.verification_dialog)
            return
        
        if not hasattr(self, 'current_frame') or self.current_frame is None:
            messagebox.showwarning("Warning", "No frame available. Please wait for camera to initialize.", parent=self.verification_dialog)
            return
        
        try:
            frame = self.current_frame.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.face_image = Image.fromarray(frame_rgb)
            
            img_byte_arr = io.BytesIO()
            self.face_image.save(img_byte_arr, format='PNG')
            self.face_image_data = img_byte_arr.getvalue()

            if len(self.face_image_data) > 5 * 1024 * 1024:
                messagebox.showwarning("Warning", "The captured image exceeds the 5MB limit. Please try again.", parent=self.verification_dialog)
                self.face_image = None
                self.face_image_data = None
                return

            # Validate face image
            is_valid, message = self.validate_face_image(frame)
            
            if not is_valid:
                messagebox.showwarning("Face Validation Failed", message, parent=self.verification_dialog)
                self.face_image = None
                self.face_image_data = None
                return
            
            self.stop_camera()
            self.show_face_preview()
            self._update_buttons_after_capture()
            
            messagebox.showinfo("Success", "Face image captured successfully!", parent=self.verification_dialog)
            
        except Exception as e:
            print(f"Capture error: {e}")
            messagebox.showerror("Error", f"Failed to capture image: {str(e)}", parent=self.verification_dialog)

    def show_face_preview(self):
        """Show captured face preview"""
        try:
            for widget in self.face_preview_frame.winfo_children():
                widget.destroy()
            
            if self.face_image:
                preview_canvas = tk.Canvas(
                    self.face_preview_frame,
                    width=410,
                    height=240,
                    bg="#fafafa",
                    highlightthickness=0
                )
                preview_canvas.place(x=0, y=0, width=410, height=240)
                
                preview_img = self.face_image.copy()
                preview_img.thumbnail((410, 240), Image.Resampling.LANCZOS)
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
        
        self.capture_button.configure(state="disabled", fg_color="#cccccc", text_color="#999999")
        self.save_button.configure(state="normal")
        
        self.retake_button.configure(
            state="normal",
            fg_color="#dc2626",
            text_color="#ffffff"
        )

    def retake_photo(self):
        """Retake photo"""
        self.face_image = None
        self.face_image_data = None
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
        """Reset button states for retake"""
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

    def complete_registration(self):
        """Complete registration and save photo"""
        try:
            if self.face_image and self.face_image_data:
                # Send data to parent callback
                if self.parent_callback:
                    self.parent_callback(self.face_image, self.face_image_data)
                
                self.on_verification_dialog_closing()
            else:
                messagebox.showwarning("Warning", "No face image to save.", parent=self.verification_dialog)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save photo: {str(e)}", parent=self.verification_dialog)

    def on_verification_dialog_closing(self):
        """Handle window closing"""
        try:
            # Stop camera first
            self.is_camera_active = False
            
            if self.camera_thread and self.camera_thread.is_alive():
                self.camera_thread.join(timeout=1.0)
            
            if self.camera:
                self.camera.release()
                self.camera = None
            
            # Remove topmost before releasing grab
            try:
                self.verification_dialog.attributes('-topmost', False)
            except Exception:
                pass
            
            # Release grab
            try:
                self.verification_dialog.grab_release()
            except Exception as e:
                print(f"Could not release grab: {e}")
            
            # Destroy window
            try:
                self.verification_dialog.destroy()
            except Exception as e:
                print(f"Could not destroy window: {e}")
            
        except Exception as e:
            print(f"Error closing window: {e}")
            try:
                self.verification_dialog.destroy()
            except:
                pass

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
