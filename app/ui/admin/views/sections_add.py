import customtkinter as ctk
import tkinter as tk
from app.ui.admin.components.modals import SuccessModal

class SectionCreatePopup(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, on_success=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.on_success = on_success
        self.title("Create Section")
        self.geometry("320x320")
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
        self.setup_ui()

    def setup_ui(self):
        # Title
        ctk.CTkLabel(
            self,
            text="Create Section",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#111",
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Program label and dropdown
        ctk.CTkLabel(
            self,
            text="Program",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=20, pady=(0, 4))
        
        # Get programs from database
        programs = self.db_manager.get_programs() if self.db_manager else []
        program_names = [p['name'] for p in programs] if programs else ["No programs available"]
        
        self.program_var = ctk.StringVar(value="Choose a program")
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
            width=260,
            height=38,
            font=ctk.CTkFont(size=13),
        )
        self.program_menu.pack(anchor="w", padx=20, pady=(0, 16))

        # Section Name label and entry
        ctk.CTkLabel(
            self,
            text="Section Name",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=20, pady=(0, 4))
        
        self.section_entry = ctk.CTkEntry(
            self,
            placeholder_text="e.g., 1-1, 2-3, 4-A",
            width=260,
            height=38,
            fg_color="#fff",
            text_color="#222",
            border_color="#E5E7EB",
            font=ctk.CTkFont(size=13)
        )
        self.section_entry.pack(anchor="w", padx=20, pady=(0, 24))

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="#FAFAFA")
        button_frame.pack(side="bottom", fill="x", padx=16, pady=(10, 16))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="#E5E7EB",
            text_color="#222",
            hover_color="#D1D5DB",
            width=120,
            height=36,
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 8))
        
        create_btn = ctk.CTkButton(
            button_frame,
            text="Create",
            fg_color="#1E3A8A",
            hover_color="#1D4ED8",
            text_color="#fff",
            width=120,
            height=36,
            command=self.create_section
        )
        create_btn.pack(side="right", padx=(8, 0))

    def create_section(self):
        if not self.db_manager:
            print("No database manager available")
            return
            
        program_name = self.program_var.get()
        section_name = self.section_entry.get().strip()
        
        # Validation
        if program_name == "Choose a program" or not program_name:
            self.show_error("Please select a program")
            return
        
        if not section_name:
            self.show_error("Please enter a section name")
            return
        
        # Create section data
        section_data = {
            'name': section_name,
            'program': program_name
        }
        
        # Call database manager to create section
        success, message = self.db_manager.create_section(section_data)
        
        if success:
            self.destroy()
            # Show success modal
            try:
                root = self.winfo_toplevel()
                SuccessModal(root, message="Section created successfully!")
            except Exception as e:
                print(f"Error showing success modal: {e}")
            
            # Call success callback if provided
            if self.on_success:
                self.on_success()
        else:
            self.show_error(message)

    def show_error(self, message):
        # Remove any existing error labels
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and hasattr(widget, '_error_label'):
                widget.destroy()
        
        # Show error message
        error_label = ctk.CTkLabel(
            self,
            text=message,
            text_color="red",
            font=ctk.CTkFont(size=12)
        )
        error_label._error_label = True  # Mark as error label
        error_label.pack(pady=5)
        # Remove error message after 3 seconds
        self.after(3000, error_label.destroy)
