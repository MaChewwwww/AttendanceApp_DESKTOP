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
        
        # Load dropdown options from backend
        self.load_dropdown_options()
        
        # Main form frame
        form_frame = ctk.CTkFrame(self, fg_color="#fff")
        form_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))
        
        # Row 1: First Name - Last Name
        fname_lname_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fname_lname_frame.pack(fill="x", pady=(20, 15))
        fname_lname_frame.grid_columnconfigure(0, weight=1)
        fname_lname_frame.grid_columnconfigure(1, weight=1)
        
        # First Name (left side)
        fname_container = ctk.CTkFrame(fname_lname_frame, fg_color="transparent")
        fname_container.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(fname_container, text="First Name", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
        self.form_fields['first_name'] = ctk.CTkEntry(fname_container, width=220, fg_color="#fff", text_color="#000")
        self.form_fields['first_name'].pack(fill="x", pady=(0, 10))
        
        # Last Name (right side)
        lname_container = ctk.CTkFrame(fname_lname_frame, fg_color="transparent")
        lname_container.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(lname_container, text="Last Name", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
        self.form_fields['last_name'] = ctk.CTkEntry(lname_container, width=220, fg_color="#fff", text_color="#000")
        self.form_fields['last_name'].pack(fill="x", pady=(0, 10))
        
        # Row 2: Email - Contact Number
        email_contact_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        email_contact_frame.pack(fill="x", pady=(0, 15))
        email_contact_frame.grid_columnconfigure(0, weight=1)
        email_contact_frame.grid_columnconfigure(1, weight=1)
        
        # Email (left side)
        email_container = ctk.CTkFrame(email_contact_frame, fg_color="transparent")
        email_container.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(email_container, text="Email", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
        self.form_fields['email'] = ctk.CTkEntry(email_container, width=220, fg_color="#fff", text_color="#000")
        self.form_fields['email'].pack(fill="x", pady=(0, 10))
        
        # Contact Number (right side)
        contact_container = ctk.CTkFrame(email_contact_frame, fg_color="transparent")
        contact_container.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(contact_container, text="Contact Number", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
        self.form_fields['contact_number'] = ctk.CTkEntry(contact_container, width=220, fg_color="#fff", text_color="#000")
        self.form_fields['contact_number'].pack(fill="x", pady=(0, 10))
        
        # Row 3: Program - Section
        program_section_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        program_section_frame.pack(fill="x", pady=(0, 15))
        program_section_frame.grid_columnconfigure(0, weight=1)
        program_section_frame.grid_columnconfigure(1, weight=1)
        
        # Program (left side)
        program_container = ctk.CTkFrame(program_section_frame, fg_color="transparent")
        program_container.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(program_container, text="Program", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
        
        # Program dropdown - wrapped in container for border
        program_dropdown_container = ctk.CTkFrame(
            program_container,
            fg_color="#fff",
            border_width=2,
            border_color="#d1d1d1",
            corner_radius=6,
            height=36
        )
        program_dropdown_container.pack(fill="x", pady=(0, 10))
        program_dropdown_container.pack_propagate(False)
        
        # Use backend data for program options
        program_options = [p['abbreviation'] for p in self.dropdown_data.get('programs', [])]
        if not program_options:
            program_options = ["BSIT", "BSCS", "BSIS"]  # Fallback
        
        # Always include "Not Yet Assigned" option for users without programs
        if "Not Yet Assigned" not in program_options:
            program_options.insert(0, "Not Yet Assigned")
        
        self.form_fields['program'] = ctk.CTkOptionMenu(
            program_dropdown_container,
            fg_color="#fff",
            text_color="#000",
            button_color="#fff",
            button_hover_color="#f0f0f0",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#f0f0f0",
            dropdown_text_color="#000",
            values=program_options,
            font=ctk.CTkFont(size=13),
            corner_radius=4,
            anchor="w",
            height=32,
            command=self.on_program_change
        )
        self.form_fields['program'].pack(fill="both", expand=True, padx=1, pady=1)
        self.form_fields['program'].set("Not Yet Assigned")  # Default to not assigned
        
        # Section (right side)
        section_container = ctk.CTkFrame(program_section_frame, fg_color="transparent")
        section_container.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(section_container, text="Section", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
        
        # Section dropdown - wrapped in container for border
        section_dropdown_container = ctk.CTkFrame(
            section_container,
            fg_color="#fff",
            border_width=2,
            border_color="#d1d1d1",
            corner_radius=6,
            height=36
        )
        section_dropdown_container.pack(fill="x", pady=(0, 10))
        section_dropdown_container.pack_propagate(False)
        
        # Initially, section should be locked until program is selected
        self.form_fields['section'] = ctk.CTkOptionMenu(
            section_dropdown_container,
            fg_color="#f5f5f5",  # Disabled appearance
            text_color="#999999",  # Grayed out text
            button_color="#f5f5f5",
            button_hover_color="#f5f5f5",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#f0f0f0",
            dropdown_text_color="#000",
            values=["Select Program First"],  # Placeholder message
            font=ctk.CTkFont(size=13),
            corner_radius=4,
            anchor="w",
            height=32,
            state="disabled"  # Initially disabled
        )
        self.form_fields['section'].pack(fill="both", expand=True, padx=1, pady=1)
        self.form_fields['section'].set("Select Program First")

        # Row 4: New Password - Status
        password_status_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_status_frame.pack(fill="x", pady=(0, 15))
        password_status_frame.grid_columnconfigure(0, weight=1)
        password_status_frame.grid_columnconfigure(1, weight=1)
        
        # New Password (left side)
        password_container = ctk.CTkFrame(password_status_frame, fg_color="transparent")
        password_container.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(password_container, text="New Password (Optional)", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
        self.form_fields['password'] = ctk.CTkEntry(password_container, width=200, fg_color="#fff", text_color="#000", show="*", placeholder_text="Leave blank to keep current")
        self.form_fields['password'].pack(fill="x", pady=(0, 10))
        
        # Status (right side)
        status_container = ctk.CTkFrame(password_status_frame, fg_color="transparent")
        status_container.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(status_container, text="Status", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
        
        # Status dropdown - wrapped in container for border
        status_dropdown_container = ctk.CTkFrame(
            status_container,
            fg_color="#fff",
            border_width=2,
            border_color="#d1d1d1",
            corner_radius=6,
            height=36
        )
        status_dropdown_container.pack(fill="x", pady=(0, 10))
        status_dropdown_container.pack_propagate(False)
        
        # Status dropdown - placeholder options for now
        if self.user_type == "student":
            status_options = [s['name'] for s in self.dropdown_data.get('statuses', []) if s.get('name')]
            if not status_options:
                status_options = ["Enrolled", "Graduated", "Dropout", "On Leave", "Suspended"]  # Fallback
        else:
            status_options = [s['name'] for s in self.dropdown_data.get('statuses', []) if s.get('name')]
            if not status_options:
                status_options = ["Active", "Inactive", "Retired", "Probationary", "Tenure Track", "Tenured"]  # Fallback
        
        self.form_fields['status'] = ctk.CTkOptionMenu(
            status_dropdown_container,
            fg_color="#fff",
            text_color="#000",
            button_color="#fff",
            button_hover_color="#f0f0f0",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#f0f0f0",
            dropdown_text_color="#000",
            values=status_options,
            font=ctk.CTkFont(size=13),
            corner_radius=4,
            anchor="w",
            height=32
        )
        self.form_fields['status'].pack(fill="both", expand=True, padx=1, pady=1)
        self.form_fields['status'].set(status_options[0])
        
        # Row 5: Face Recognition Button (Centered)
        fr_button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fr_button_frame.pack(fill="x", pady=(0, 25))
        
        # Face Recognition Button
        fr_btn = ctk.CTkButton(
            fr_button_frame, 
            text="📷 Take Photo", 
            fg_color="#1E3A8A", 
            hover_color="#1D4ED8", 
            text_color="#fff", 
            height=40, 
            width=200,
            corner_radius=10, 
            font=ctk.CTkFont(size=13, weight="normal"),
            command=self.open_facial_recognition
        )
        fr_btn.pack(anchor="center")
        
        # Face data status (centered)
        self.face_status_frame = ctk.CTkFrame(form_frame, fg_color="#fff", height=50)
        self.face_status_frame.pack(fill="x", pady=(0, 10))
        self.face_status_frame.pack_propagate(False)
        
        self.face_status_label = ctk.CTkLabel(
            self.face_status_frame, 
            text="No Face Data", 
            font=ctk.CTkFont(size=13, weight="bold"), 
            text_color="#757575",
            anchor="center"
        )
        self.face_status_label.pack(expand=True, fill="both")
        
        # Bottom buttons in same row
        btns_frame = ctk.CTkFrame(self, fg_color="#fff")
        btns_frame.pack(fill="x", padx=30, pady=(10, 20))
        btns_frame.grid_columnconfigure(0, weight=1)
        btns_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(
            btns_frame, 
            text="Cancel", 
            fg_color="#E5E7EB", 
            text_color="#000", 
            hover_color="#D1D5DB", 
            width=285, 
            height=36, 
            corner_radius=8, 
            command=self.destroy
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        ctk.CTkButton(
            btns_frame, 
            text="Save Changes", 
            fg_color="#1E3A8A", 
            hover_color="#1E3A8A", 
            text_color="#fff", 
            width=285, 
            height=36, 
            corner_radius=8, 
            command=self.save_changes
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def create_form_field(self, parent, label_text, show=None):
        """Create a form field with label and entry"""
        ctk.CTkLabel(parent, text=label_text, anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
        entry = ctk.CTkEntry(parent, width=220, fg_color="#fff", text_color="#000", show=show)
        entry.pack(fill="x", pady=(0, 10))
        return entry

    def load_dropdown_options(self):
        """Load dropdown options from backend"""
        try:
            # Get dropdown options for this user type
            success, dropdown_data = self.db_manager.get_dropdown_options_for_user_type(self.user_type)
            
            if success:
                self.dropdown_data = dropdown_data
                print(f"Loaded dropdown options: {len(dropdown_data.get('programs', []))} programs, {len(dropdown_data.get('sections', []))} sections, {len(dropdown_data.get('statuses', []))} statuses")
            else:
                print(f"Error loading dropdown options: {dropdown_data}")
                self.dropdown_data = {'programs': [], 'sections': [], 'statuses': []}
                
        except Exception as e:
            print(f"Error in load_dropdown_options: {e}")
            self.dropdown_data = {'programs': [], 'sections': [], 'statuses': []}

    def on_program_change(self, selected_program):
        """Handle program selection change to filter sections"""
        try:
            if selected_program == "Not Yet Assigned":
                # Lock section dropdown when no program is selected
                self.form_fields['section'].configure(
                    values=["Select Program First"],
                    fg_color="#f5f5f5",
                    text_color="#999999",
                    button_color="#f5f5f5",
                    button_hover_color="#f5f5f5",
                    state="disabled"
                )
                self.form_fields['section'].set("Select Program First")
                return
            
            # Find the program ID for the selected abbreviation
            selected_program_id = None
            for program in self.dropdown_data.get('programs', []):
                if program['abbreviation'] == selected_program:
                    selected_program_id = program['id']
                    break
            
            if selected_program_id:
                # Filter sections by program
                filtered_sections = [
                    s['name'] for s in self.dropdown_data.get('sections', [])
                    if s.get('program_id') == selected_program_id
                ]
                
                # Always include "Not Yet Assigned" option
                if "Not Yet Assigned" not in filtered_sections:
                    filtered_sections.insert(0, "Not Yet Assigned")
                
                if filtered_sections:
                    # Enable and update section dropdown with filtered options
                    self.form_fields['section'].configure(
                        values=filtered_sections,
                        fg_color="#fff",
                        text_color="#000",
                        button_color="#fff",
                        button_hover_color="#f0f0f0",
                        state="normal"
                    )
                    # Set to "Not Yet Assigned" by default when program changes
                    self.form_fields['section'].set("Not Yet Assigned")
                else:
                    # No sections found for this program, show only "Not Yet Assigned"
                    self.form_fields['section'].configure(
                        values=["Not Yet Assigned"],
                        fg_color="#fff",
                        text_color="#000",
                        button_color="#fff",
                        button_hover_color="#f0f0f0",
                        state="normal"
                    )
                    self.form_fields['section'].set("Not Yet Assigned")
            else:
                # If no valid program selected, lock section dropdown
                self.form_fields['section'].configure(
                    values=["Select Program First"],
                    fg_color="#f5f5f5",
                    text_color="#999999",
                    button_color="#f5f5f5",
                    button_hover_color="#f5f5f5",
                    state="disabled"
                )
                self.form_fields['section'].set("Select Program First")
            
        except Exception as e:
            print(f"Error handling program change: {e}")
            # Fallback to locked state on error
            self.form_fields['section'].configure(
                values=["Select Program First"],
                fg_color="#f5f5f5",
                text_color="#999999",
                state="disabled"
            )
            self.form_fields['section'].set("Select Program First")

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
        
        # Set program dropdown based on user data
        program_set = False
        if 'program' in self.form_fields:
            program_name = self.user_data.get('program_name')
            
            if program_name and program_name.strip():
                # User has a program - find matching abbreviation
                for program in self.dropdown_data.get('programs', []):
                    if program['name'] == program_name or program['abbreviation'] in program_name:
                        self.form_fields['program'].set(program['abbreviation'])
                        # Trigger section filtering for this program
                        self.on_program_change(program['abbreviation'])
                        program_set = True
                        break
            
            if not program_set:
                # User has no program or program not found - set to "Not Yet Assigned"
                self.form_fields['program'].set("Not Yet Assigned")
                # This will trigger the program change handler to lock sections
                self.on_program_change("Not Yet Assigned")
        
        # Set section after program filtering is applied
        if 'section' in self.form_fields and program_set:
            section_name = self.user_data.get('section_name')
            if section_name and section_name.strip():
                # Check if section exists in current dropdown options
                current_sections = self.form_fields['section'].cget("values")
                if section_name in current_sections:
                    self.form_fields['section'].set(section_name)
                else:
                    # Section not available for selected program, set to "Not Yet Assigned"
                    self.form_fields['section'].set("Not Yet Assigned")
            else:
                # User has no section, set to "Not Yet Assigned"
                self.form_fields['section'].set("Not Yet Assigned")
        
        if 'status' in self.form_fields and self.user_data.get('status_name'):
            status_name = self.user_data['status_name']
            # Check if status exists in dropdown options
            current_statuses = self.form_fields['status'].cget("values")
            if status_name in current_statuses:
                self.form_fields['status'].set(status_name)
        
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

    def save_changes(self):
        """Save the edited user data"""
        try:
            # Collect form data
            form_data = {}
            
            # Get basic fields
            form_data['first_name'] = self.form_fields['first_name'].get().strip()
            form_data['last_name'] = self.form_fields['last_name'].get().strip()
            form_data['email'] = self.form_fields['email'].get().strip()
            form_data['contact_number'] = self.form_fields['contact_number'].get().strip()
            
            # Get password (optional)
            new_password = self.form_fields['password'].get().strip()
            if new_password:
                form_data['password'] = new_password
            
            # Get dropdown values - handle "Not Yet Assigned" properly
            program_value = self.form_fields['program'].get()
            section_value = self.form_fields['section'].get()
            
            # Convert "Not Yet Assigned" to None for database storage
            form_data['program'] = None if program_value == "Not Yet Assigned" else program_value
            form_data['section'] = None if section_value in ["Not Yet Assigned", "Select Program First"] else section_value
            form_data['status'] = self.form_fields['status'].get()
            
            # Add face image data if available
            if hasattr(self, 'face_image_data') and self.face_image_data:
                form_data['face_image'] = self.face_image_data
            
            # Validate required fields
            if not form_data['first_name'] or not form_data['last_name'] or not form_data['email']:
                messagebox.showerror("Error", "First name, last name, and email are required.")
                return
            
            # Show what will be saved (for debugging)
            print(f"Form data to save: {form_data}")
            
            # Show confirmation with special handling for unassigned values
            program_display = form_data['program'] or "Not Yet Assigned"
            section_display = form_data['section'] or "Not Yet Assigned"
            
            confirmation_msg = f"Save changes for {form_data['first_name']} {form_data['last_name']}?\n\n"
            confirmation_msg += f"Program: {program_display}\n"
            confirmation_msg += f"Section: {section_display}\n"
            confirmation_msg += f"Status: {form_data['status']}"
            
            if messagebox.askyesno("Confirm Changes", confirmation_msg):
                # TODO: Call the database update method when ready
                # success, message = self.update_user_in_database(form_data)
                
                # For now, just show success message
                messagebox.showinfo("Success", "User data saved successfully!\n\n(Database update will be implemented next)")
                
                # Refresh the parent view if possible
                if hasattr(self.master, 'load_filtered_data'):
                    self.master.load_filtered_data()
                
                self.destroy()
                
        except Exception as e:
            print(f"Error saving changes: {e}")
            messagebox.showerror("Error", f"An error occurred while saving: {str(e)}")

class IndependentFacialRecognitionWindow:
    """Facial recognition window using CustomTkinter to match register.py exactly"""
    
    def __init__(self, parent_edit):
        self.parent_edit = parent_edit
        
        # Create CustomTkinter toplevel window
        self.verification_dialog = ctk.CTkToplevel()
        self.verification_dialog.title("Facial Recognition")
        self.verification_dialog.geometry("454x450")
        self.verification_dialog.resizable(False, False)
        self.verification_dialog.configure(fg_color="#222222")
        
        # Set minimum and maximum size
        self.verification_dialog.minsize(454, 450)
        self.verification_dialog.maxsize(454, 450)
        
        # Camera variables
        self.camera = None
        self.is_camera_active = False
        self.camera_thread = None
        self.current_frame = None
        self.face_image = None
        self.face_image_data = None
        self.camera_canvas = None
        self.current_photo = None
        
        # Make it stay on top
        self.verification_dialog.attributes('-topmost', True)
        
        # Handle parent grab
        try:
            if hasattr(parent_edit, 'grab_release'):
                parent_edit.grab_release()
        except Exception as e:
            print(f"Could not release parent grab: {e}")
        
        # Center window
        self._center_window()
        
        # Setup UI content
        self._create_verification_dialog_content()
        
        # Handle close
        self.verification_dialog.protocol("WM_DELETE_WINDOW", self.on_verification_dialog_closing)
        
        # Focus and grab
        self.verification_dialog.focus_force()
        self.verification_dialog.after(200, self._try_set_grab)

    def _try_set_grab(self):
        """Try to set grab with error handling"""
        try:
            self.verification_dialog.grab_set()
            print("Successfully set grab")
        except Exception as e:
            print(f"Could not set grab: {e}")

    def _center_window(self):
        """Center the window on screen"""
        self.verification_dialog.update_idletasks()
        screen_width = self.verification_dialog.winfo_screenwidth()
        screen_height = self.verification_dialog.winfo_screenheight()
        x = (screen_width - 454) // 2
        y = (screen_height - 450) // 2
        self.verification_dialog.geometry(f"454x450+{x}+{y}")

    def _create_verification_dialog_content(self):
        """Create content for the face verification dialog - exact copy from register.py"""
        # Card Frame with explicit sizing
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
        
        # Ensure card maintains its size
        self.card.grid_propagate(False)

        # Info icon (top right)
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

        # Camera Preview Frame with explicit sizing
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

        # Default Preview Label (centered)
        self.preview_label = ctk.CTkLabel(
            self.face_preview_frame,
            text="Camera will appear here\nClick 'Open Camera' to begin",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#a0a0a0"
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Open Camera Button with explicit sizing
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

        # Retake and Capture Buttons with explicit sizing
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

        # Save Button with explicit sizing (renamed from register_button)
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
        """Start camera capture with embedded display"""
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
            
            # Create canvas for camera display with explicit sizing
            self.camera_canvas = tk.Canvas(
                self.face_preview_frame,
                width=410,
                height=240,
                bg="#fafafa",
                highlightthickness=0
            )
            self.camera_canvas.place(x=0, y=0, width=410, height=240)
            
            # Initialize photo reference
            self.current_photo = None
            
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
        
        # Clean up camera display and resources
        self._cleanup_camera_window()
        self._update_ui_after_camera_close()

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

                    # Draw face positioning guide rectangle
                    rect_w, rect_h = 160, 180
                    cv2.rectangle(frame_rgb, 
                                 (center_x - rect_w//2, center_y - rect_h//2),
                                 (center_x + rect_w//2, center_y + rect_h//2),
                                 (0, 255, 0), 2)
                    
                    # Convert to PIL Image
                    try:
                        pil_image = Image.fromarray(frame_rgb)
                        
                        # Schedule UI update on main thread
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
                                        self.camera_canvas.create_image(205, 120, image=photo, anchor="center")
                                        
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
                self.camera_thread.join(0.5)
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
            
            # Convert to RGB and store
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.face_image = Image.fromarray(frame_rgb)
            
            # Convert to bytes for storage
            img_byte_arr = io.BytesIO()
            self.face_image.save(img_byte_arr, format='PNG')
            self.face_image_data = img_byte_arr.getvalue()

            # Check image size
            if len(self.face_image_data) > 5 * 1024 * 1024:
                messagebox.showwarning("Warning", "The captured image exceeds the 5MB limit. Please try again.", parent=self.verification_dialog)
                self.face_image = None
                self.face_image_data = None
                return

            # Stop camera and show preview
            self.stop_camera()
            self.show_face_preview()
            
            # Update button states after successful capture
            self._update_buttons_after_capture()
            
            messagebox.showinfo("Success", "Face image captured successfully!", parent=self.verification_dialog)
            
        except Exception as e:
            print(f"Capture error: {e}")
            messagebox.showerror("Error", f"Failed to capture image: {str(e)}", parent=self.verification_dialog)

    def show_face_preview(self):
        """Show face image preview"""
        try:
            # Clear existing widgets in preview frame
            for widget in self.face_preview_frame.winfo_children():
                widget.destroy()
            
            if self.face_image:
                # Create canvas for displaying captured image
                preview_canvas = tk.Canvas(
                    self.face_preview_frame,
                    width=410,
                    height=240,
                    bg="#fafafa",
                    highlightthickness=0
                )
                preview_canvas.place(x=0, y=0, width=410, height=240)
                
                # Convert image to PhotoImage and display
                preview_img = self.face_image.copy()
                preview_img.thumbnail((410, 240), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(preview_img)
                
                preview_canvas.create_image(205, 120, image=photo, anchor="center")
                
                # Keep reference to prevent garbage collection
                preview_canvas.image = photo
            else:
                # Show success message
                preview_text = ctk.CTkLabel(
                    self.face_preview_frame,
                    text="✓ Photo Captured Successfully!\nReady for saving",
                    font=ctk.CTkFont("Roboto", 14, "bold"),
                    text_color="#4CAF50"
                )
                preview_text.place(relx=0.5, rely=0.5, anchor="center")
            
        except Exception as e:
            print(f"Error showing face preview: {e}")

    def _update_buttons_after_capture(self):
        """Update button states after successful face capture"""
        # Disable camera button and capture button since face is already captured
        self.camera_button.configure(
            state="disabled",
            text="Photo Captured",
            fg_color="#e5e5e5",
            text_color="#707070"
        )
        
        self.capture_button.configure(state="disabled", fg_color="#cccccc", text_color="#999999")
        
        # Enable save button
        self.save_button.configure(state="normal")
        
        # Enable and style retake button
        self.retake_button.configure(
            state="normal",
            fg_color="#dc2626",  # Red color for retake
            text_color="#ffffff"
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
            text="Close Camera",
            fg_color="#ffffff",
            text_color="#222"
        )
        
        # Disable save button since no face is captured
        self.save_button.configure(state="disabled")
        
        # Disable and reset retake button
        self.retake_button.configure(
            state="disabled",
            fg_color="#e5e5e5",
            text_color="#707070"
        )

    def complete_registration(self):
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
                
                messagebox.showinfo("Success", "Face image saved successfully!", parent=self.verification_dialog)
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
            
            # Wait for camera thread to finish
            if self.camera_thread and self.camera_thread.is_alive():
                self.camera_thread.join(timeout=1.0)
            
            # Release camera
            if self.camera:
                self.camera.release()
                self.camera = None
            
            # Release grab safely
            try:
                self.verification_dialog.grab_release()
            except Exception as e:
                print(f"Could not release grab: {e}")
            
            # Re-enable parent grab if possible
            try:
                if (hasattr(self.parent_edit, 'grab_set') and 
                    hasattr(self.parent_edit, 'winfo_exists') and 
                    self.parent_edit.winfo_exists()):
                    self.parent_edit.grab_set()
                    self.parent_edit.focus_force()
            except Exception as e:
                print(f"Could not restore parent grab: {e}")
            
            # Destroy window
            try:
                self.verification_dialog.destroy()
            except Exception as e:
                print(f"Could not destroy window: {e}")
            
        except Exception as e:
            print(f"Error closing window: {e}")
            # Force destroy as last resort
            try:
                self.verification_dialog.destroy()
            except:
                pass
