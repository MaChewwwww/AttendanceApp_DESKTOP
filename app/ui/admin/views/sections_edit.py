import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from app.ui.admin.components.modals import SuccessModal

class SectionEditPopup(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, section_data, on_success=None):
        super().__init__(parent)
        self.parent_view = parent
        self.db_manager = db_manager
        self.section_data = section_data
        self.on_success = on_success
        self.programs_data = []
        self.load_programs_data()
        self.title("Update Section")
        self.geometry("450x420")
        self.resizable(False, False)
        self.configure(fg_color="#fff")
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
            if self.db_manager:
                success, programs = self.db_manager.get_programs()
                if success:
                    self.programs_data = programs
                else:
                    print(f"Error loading programs: {programs}")
                    self.programs_data = []
            else:
                # Try to get db_manager from parent if not available
                from app.db_manager import DatabaseManager
                self.db_manager = DatabaseManager()
                success, programs = self.db_manager.get_programs()
                if success:
                    self.programs_data = programs
                else:
                    self.programs_data = []
        except Exception as e:
            print(f"Error loading programs data: {e}")
            self.programs_data = []

    def setup_ui(self):
        # Header
        ctk.CTkLabel(
            self,
            text="Update Section",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="black"
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        ctk.CTkLabel(
            self,
            text="Modify the section details below",
            font=ctk.CTkFont(size=13),
            text_color="#6B7280"
        ).pack(anchor="w", padx=20, pady=(0, 20))

        # Form content
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Program selection
        ctk.CTkLabel(
            content_frame,
            text="Program *",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#374151"
        ).pack(anchor="w", pady=(0, 8))
        
        # Get programs from database
        program_names = [p['name'] for p in self.programs_data] if self.programs_data else ["No programs available"]
        
        # Set current program as default
        current_program = self.section_data.get('program_name', program_names[0] if program_names else "")
        
        self.program_var = tk.StringVar(value=current_program)
        self.program_menu = ctk.CTkOptionMenu(
            content_frame,
            variable=self.program_var,
            values=program_names,
            fg_color="#fff",
            text_color="#374151",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#F3F4F6",
            dropdown_text_color="#374151",
            width=360,
            height=40,
            font=ctk.CTkFont(size=14),
            corner_radius=6
        )
        self.program_menu.pack(fill="x", pady=(0, 20))

        # Section Name
        ctk.CTkLabel(
            content_frame,
            text="Section Name *",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#374151"
        ).pack(anchor="w", pady=(0, 8))
        
        self.section_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Enter section name (e.g., 1-1, 2-1A, 3-B)",
            width=360,
            height=40,
            fg_color="#fff",
            text_color="#374151",
            placeholder_text_color="#9CA3AF",
            border_color="#D1D5DB",
            border_width=1,
            font=ctk.CTkFont(size=14),
            corner_radius=6
        )
        # Set current section name
        self.section_entry.insert(0, self.section_data.get('name', ''))
        self.section_entry.pack(fill="x", pady=(0, 20))

        # Naming guidelines
        guidelines_frame = ctk.CTkFrame(content_frame, fg_color="#EFF6FF", corner_radius=6)
        guidelines_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            guidelines_frame,
            text="💡 Examples: 1-1, 2-1A, 3-B, 4-2C",
            font=ctk.CTkFont(size=12),
            text_color="#1E40AF"
        ).pack(padx=15, pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="#F3F4F6",
            text_color="#374151",
            hover_color="#E5E7EB",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=6,
            command=self.destroy
        )
        cancel_btn.pack(side="left")
        
        # Update button
        update_btn = ctk.CTkButton(
            button_frame,
            text="Update Section",
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="white",
            width=140,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=6,
            command=self.update_section
        )
        update_btn.pack(side="right")

    def validate_input(self):
        """Validate form input"""
        program_name = self.program_var.get().strip()
        section_name = self.section_entry.get().strip()
        
        if program_name == "Select a program" or not program_name or program_name == "No programs available":
            return False, "Please select a valid program"
        
        if not section_name:
            return False, "Please enter a section name"
        
        # Check for spaces in section name
        if " " in section_name:
            return False, "Section name cannot contain spaces. Use format like '2-1' not '2 - 1'"
        
        # Validate section name format: starts with single digit, followed by "-", then anything
        import re
        pattern = r'^[1-9]-.*$'  # Single digit 1-9, followed by hyphen, then anything
        
        if not re.match(pattern, section_name):
            return False, "Section name must start with a single digit (1-9) followed by '-' (e.g., '1-1', '2-A', '3-B1')"
        
        if len(section_name) > 50:
            return False, "Section name must be 50 characters or less"
        
        # Check if exactly same section name already exists for this program (excluding current section)
        if self.check_duplicate_section(program_name, section_name):
            return False, f"Section '{section_name}' already exists for program '{program_name}'"
        
        return True, ""

    def check_duplicate_section(self, program_name, section_name):
        """Check if exactly same section name exists for the program (excluding current section)"""
        try:
            if not self.db_manager:
                return False
            
            # Get all sections for this program
            sections = self.db_manager.get_sections_with_filters()
            if not sections:
                return False
            
            # Check for exact match in section name and program, excluding current section
            current_section_id = self.section_data.get('id')
            for section in sections:
                if (section.get('id') != current_section_id and
                    section.get('name', '').strip().lower() == section_name.lower() and 
                    section.get('program_name', '').strip() == program_name):
                    return True
            
            return False
        except Exception as e:
            print(f"Error checking duplicate section: {e}")
            return False

    def update_section(self):
        """Update section"""
        # Validate input
        is_valid, error_message = self.validate_input()
        if not is_valid:
            messagebox.showerror("Validation Error", error_message)
            return
        
        if not self.db_manager:
            messagebox.showerror("Error", "Database connection not available")
            return
        
        # Prepare section data
        updated_section_data = {
            'name': self.section_entry.get().strip(),
            'program': self.program_var.get().strip()
        }
        
        try:
            # Update section in database
            success, message = self.db_manager.update_section(
                self.section_data['id'], 
                updated_section_data
            )
            
            if success:
                # Close the popup
                self.destroy()
                
                # Show success modal
                try:
                    SuccessModal(self.master)
                except Exception as e:
                    print(f"Error showing success modal: {e}")
                    # Fallback to messagebox
                    messagebox.showinfo("Success", "Section updated successfully!")
                
                # Call success callback to refresh the parent view
                if self.on_success:
                    self.on_success()
            else:
                messagebox.showerror("Error", message)
                
        except Exception as e:
            print(f"Error updating section: {e}")
            messagebox.showerror("Error", "An unexpected error occurred. Please try again.")

    def destroy(self):
        """Override destroy to ensure proper cleanup"""
        try:
            super().destroy()
        except Exception as e:
            print(f"Error destroying section edit popup: {e}")
