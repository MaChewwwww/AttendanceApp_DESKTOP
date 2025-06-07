import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from app.ui.admin.components.modals import SuccessModal

class CreateCoursePopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_view = parent
        self.db_manager = None
        self.programs_data = []
        self.load_programs_data()
        self.title("Create Course")
        self.geometry("360x520")  # Increased height to show all components properly
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
        self.center_window()
        self.setup_ui()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def load_programs_data(self):
        """Load programs data from database"""
        try:
            from app.db_manager import DatabaseManager
            self.db_manager = DatabaseManager()
            success, programs = self.db_manager.get_programs()
            
            if success:
                self.programs_data = programs
            else:
                print(f"Error loading programs: {programs}")
                # Fallback to sample data
                self.programs_data = [
                    {"id": 1, "name": "Bachelor of Science in Information Technology"},
                    {"id": 2, "name": "Bachelor of Science in Computer Science"},
                    {"id": 3, "name": "Bachelor of Science in Information Systems"}
                ]
        except Exception as e:
            print(f"Error loading programs data: {e}")
            # Fallback to sample data
            self.programs_data = [
                {"id": 1, "name": "Bachelor of Science in Information Technology"},
                {"id": 2, "name": "Bachelor of Science in Computer Science"},
                {"id": 3, "name": "Bachelor of Science in Information Systems"}
            ]

    def setup_ui(self):
        ctk.CTkLabel(
            self,
            text="Create Course",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="#111",
        ).pack(anchor="w", padx=24, pady=(24, 12))

        # Program
        ctk.CTkLabel(
            self,
            text="Program",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=24, pady=(0, 4))
        self.program_var = ctk.StringVar(value="Choose a program")
        program_names = [program["name"] for program in self.programs_data]
        if not program_names:
            program_names = ["No programs available"]
        self.program_menu = ctk.CTkOptionMenu(
            self,
            variable=self.program_var,
            values=program_names,
            fg_color="#fff",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            width=300,
            height=38,
            font=ctk.CTkFont(size=13),
        )
        self.program_menu.pack(anchor="w", padx=24, pady=(0, 16))

        # Course Subject
        ctk.CTkLabel(
            self,
            text="Course Subject",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=24, pady=(0, 4))
        self.subject_var = ctk.StringVar(value="")
        self.subject_entry = ctk.CTkEntry(
            self,
            textvariable=self.subject_var,
            placeholder_text="Enter course subject (e.g., Programming 1)",
            fg_color="#fff",
            text_color="#222",
            border_color="#BDBDBD",
            border_width=1,
            width=300,
            height=38,
            font=ctk.CTkFont(size=13),
        )
        self.subject_entry.pack(anchor="w", padx=24, pady=(0, 16))

        # Course Code
        ctk.CTkLabel(
            self,
            text="Course Code",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=24, pady=(0, 4))
        self.code_var = ctk.StringVar(value="")
        self.code_entry = ctk.CTkEntry(
            self,
            textvariable=self.code_var,
            placeholder_text="Enter course code (e.g., CS101)",
            fg_color="#fff",
            text_color="#222",
            border_color="#BDBDBD",
            border_width=1,
            width=300,
            height=38,
            font=ctk.CTkFont(size=13),
        )
        self.code_entry.pack(anchor="w", padx=24, pady=(0, 16))

        # Description - Scrollable textbox only
        ctk.CTkLabel(
            self,
            text="Description",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=24, pady=(0, 4))
        self.description_textbox = ctk.CTkTextbox(
            self,
            fg_color="#fff",
            text_color="#222",
            border_color="#BDBDBD",
            border_width=1,
            width=300,
            height=80,
            font=ctk.CTkFont(size=13),
        )
        self.description_textbox.pack(anchor="w", padx=24, pady=(0, 16))
        self.description_textbox.insert("1.0", "Enter course description...")

        # Buttons - Fixed positioning
        button_frame = ctk.CTkFrame(self, fg_color="#FAFAFA")
        button_frame.pack(side="bottom", fill="x", padx=0, pady=0)
        
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(fill="x", padx=24, pady=16)
        
        cancel_btn = ctk.CTkButton(
            button_container,
            text="Cancel",
            fg_color="#D1D5DB",
            text_color="#222",
            hover_color="#BDBDBD",
            width=140,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 8))
        
        create_btn = ctk.CTkButton(
            button_container,
            text="Create",
            fg_color="#1E3A8A",
            hover_color="#1D4ED8",
            text_color="#fff",
            width=140,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.create_course
        )
        create_btn.pack(side="right", padx=(8, 0))

    def create_course(self):
        """Create a new course with database integration"""
        try:
            # Get values directly from widgets
            subject = self.subject_entry.get().strip()
            code = self.code_entry.get().strip()
            selected_program = self.program_var.get()
            description = self.description_textbox.get("1.0", "end-1c").strip()
            
            # Remove placeholder text
            if description == "Enter course description...":
                description = ""
            
            if not subject:
                messagebox.showerror("Error", "Course subject is required")
                return
            
            if not description:
                messagebox.showerror("Error", "Course description is required")
                return
            
            if selected_program == "Choose a program" or selected_program == "No programs available":
                messagebox.showerror("Error", "Please select a program")
                return
            
            # Find program ID
            program_id = None
            for program in self.programs_data:
                if program["name"] == selected_program:
                    program_id = program["id"]
                    break
            
            if not program_id:
                messagebox.showerror("Error", "Invalid program selected")
                return
            
            # Prepare course data
            course_data = {
                'name': subject,
                'code': code if code else None,
                'description': description,  # Now required, so always has a value
                'program_id': program_id
            }
            
            # Create course in database
            if self.db_manager:
                success, result = self.db_manager.create_course(course_data)
                
                if success:
                    # Store parent reference before destroying
                    parent_ref = self.parent_view
                    
                    # Destroy this modal
                    self.destroy()
                    
                    # Refresh parent view and show success
                    parent_ref.after(100, lambda: parent_ref.refresh_courses())
                    parent_ref.after(200, lambda: SuccessModal(parent_ref))
                else:
                    messagebox.showerror("Error", f"Failed to create course: {result}")
            else:
                messagebox.showerror("Error", "Database connection not available")
                
        except Exception as e:
            print(f"Error creating course: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
