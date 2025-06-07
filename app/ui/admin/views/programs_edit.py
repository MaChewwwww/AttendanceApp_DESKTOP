import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, colorchooser
import re
from app.ui.admin.components.modals import SuccessModal

class EditProgramPopup(ctk.CTkToplevel):
    def __init__(self, parent, program_data=None):
        super().__init__(parent)
        self.parent_view = parent
        self.program_data = program_data or {}
        self.title("Update Program")
        self.geometry("500x550")  # Same size as create modal
        self.resizable(False, False)
        
        # Set background color to white
        self.configure(fg_color="#fff")
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Center the window
        self.center_window()
        
        # Initialize form field references and color variable
        self.name_entry = None
        self.acronym_entry = None
        self.code_entry = None
        self.description_text = None
        self.color_var = tk.StringVar(value=self.program_data.get('color', '#3B82F6'))
        
        self.setup_ui()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Update Program",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="black"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header_frame,
            text="Modify the program details as needed",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color="#6B7280"
        ).pack(anchor="w", pady=(5, 0))
        
        # Form content
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # Program Name
        self.name_entry = self.create_form_field(
            form_frame, 
            "Program Name *", 
            placeholder="e.g., Bachelor of Science in Information Technology",
            initial_value=self.program_data.get('name', '')
        )
        
        # Acronym and Code in same row
        row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 15))
        
        # Acronym (left side)
        acronym_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        acronym_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            acronym_frame,
            text="Acronym *",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#374151",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        self.acronym_entry = ctk.CTkEntry(
            acronym_frame,
            placeholder_text="e.g., BSIT",
            height=40,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color="#F9FAFB",
            border_color="#D1D5DB",
            text_color="#111827"
        )
        self.acronym_entry.pack(fill="x")
        # Ensure acronym is properly set
        acronym_value = self.program_data.get('acronym', '')
        if acronym_value:
            self.acronym_entry.insert(0, acronym_value)
        
        # Code (right side)
        code_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        code_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            code_frame,
            text="Program Code *",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#374151",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        self.code_entry = ctk.CTkEntry(
            code_frame,
            placeholder_text="e.g., IT-001",
            height=40,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color="#F9FAFB",
            border_color="#D1D5DB",
            text_color="#111827"
        )
        self.code_entry.pack(fill="x")
        # Ensure code is properly set
        code_value = self.program_data.get('code', '')
        if code_value:
            self.code_entry.insert(0, code_value)
        
        # Description
        field_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        field_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            field_frame,
            text="Description",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#374151",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        self.description_text = ctk.CTkTextbox(
            field_frame,
            height=60,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color="#F9FAFB",
            border_color="#D1D5DB",
            text_color="#111827"
        )
        self.description_text.pack(fill="x")
        
        # Insert existing description or default text
        existing_description = self.program_data.get('description', '').strip()
        if existing_description:
            self.description_text.insert("1.0", existing_description)
        else:
            self.description_text.insert("1.0", "Brief description of the program...")
        
        # Color picker
        self.create_color_picker(form_frame)
        
        # Fixed button frame at bottom
        button_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        button_frame.pack(fill="x", side="bottom", padx=20, pady=20)
        button_frame.pack_propagate(False)
        
        # Center container for buttons
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(expand=True, anchor="center")
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_container,
            text="Cancel",
            width=120,
            height=40,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color="#F3F4F6",
            text_color="#374151",
            hover_color="#E5E7EB",
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        # Update button
        update_btn = ctk.CTkButton(
            button_container,
            text="Update Program",
            width=140,
            height=40,
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#1E3A8A",
            text_color="#fff",
            hover_color="#1D4ED8",
            command=self.update_program
        )
        update_btn.pack(side="left")

    def create_form_field(self, parent, label_text, placeholder="", initial_value=""):
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=(0, 15))
        
        # Label
        ctk.CTkLabel(
            field_frame,
            text=label_text,
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#374151",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        # Entry
        entry = ctk.CTkEntry(
            field_frame,
            placeholder_text=placeholder,
            height=40,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color="#F9FAFB",
            border_color="#D1D5DB",
            text_color="#111827"
        )
        entry.pack(fill="x")
        
        # Insert initial value if provided
        if initial_value:
            entry.insert(0, initial_value)
        
        return entry
    
    def create_color_picker(self, parent):
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=(0, 5))
        
        # Label
        ctk.CTkLabel(
            field_frame,
            text="Program Color",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#374151",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        # Color container
        color_container = ctk.CTkFrame(field_frame, fg_color="transparent", height=35)
        color_container.pack(fill="x")
        color_container.pack_propagate(False)
        
        # Predefined colors
        colors = [
            "#3B82F6",  # Blue
            "#10B981",  # Green
            "#F59E0B",  # Yellow
            "#EF4444",  # Red
            "#8B5CF6",  # Purple
            "#EC4899",  # Pink
            "#14B8A6",  # Teal
            "#F97316"   # Orange
        ]
        
        # Store color buttons for later reference
        self.color_buttons = []
        
        # Color buttons frame
        colors_frame = ctk.CTkFrame(color_container, fg_color="transparent")
        colors_frame.pack(side="left", pady=3)
        
        for i, color in enumerate(colors):
            color_btn = ctk.CTkButton(
                colors_frame,
                text="",
                width=28,
                height=28,
                fg_color=color,
                hover_color=color,
                border_width=2,
                border_color="#374151" if color == self.color_var.get() else "#E5E7EB",
                corner_radius=14,
                command=lambda c=color: self.select_color(c)
            )
            color_btn.grid(row=0, column=i, padx=2, pady=0)
            self.color_buttons.append((color_btn, color))
        
        # Custom color section
        custom_frame = ctk.CTkFrame(color_container, fg_color="transparent")
        custom_frame.pack(side="right", padx=(10, 0), pady=3)
        
        # Custom color display
        self.custom_color_display = ctk.CTkFrame(
            custom_frame,
            width=28,
            height=28,
            fg_color=self.color_var.get(),
            border_width=2,
            border_color="#374151",
            corner_radius=14
        )
        self.custom_color_display.pack(side="left", padx=(0, 5))
        
        # Pick color button
        self.color_picker_btn = ctk.CTkButton(
            custom_frame,
            text="Pick Color",
            width=80,
            height=28,
            font=ctk.CTkFont(family="Inter", size=11),
            fg_color="#F3F4F6",
            text_color="#374151",
            hover_color="#E5E7EB",
            border_width=1,
            border_color="#D1D5DB",
            corner_radius=6,
            command=self.open_color_picker
        )
        self.color_picker_btn.pack(side="left")
        
        # Update initial color selection
        self.update_color_buttons()

    def open_color_picker(self):
        """Open system color picker dialog"""
        try:
            current_color = self.color_var.get() or "#3B82F6"
            color = colorchooser.askcolor(
                color=current_color,
                title="Choose Program Color",
                parent=self
            )
            
            if color[1]:
                self.select_color(color[1])
                
        except Exception as e:
            print(f"Error opening color picker: {e}")

    def select_color(self, color):
        self.color_var.set(color)
        self.update_color_buttons()
        self.update_custom_color_display()

    def update_color_buttons(self):
        """Update color button borders based on selection"""
        selected_color = self.color_var.get()
        for color_btn, color in self.color_buttons:
            if color == selected_color:
                color_btn.configure(border_color="#374151", border_width=2)
            else:
                color_btn.configure(border_color="#E5E7EB", border_width=2)

    def update_custom_color_display(self):
        """Update the custom color display circle"""
        selected_color = self.color_var.get()
        if selected_color:
            self.custom_color_display.configure(fg_color=selected_color)

    def is_valid_hex_color(self, color):
        """Validate hex color format"""
        pattern = r'^#[0-9A-Fa-f]{6}$'
        return re.match(pattern, color) is not None

    def validate_form(self):
        """Validate form inputs"""
        name = self.name_entry.get().strip() if self.name_entry else ""
        acronym = self.acronym_entry.get().strip() if self.acronym_entry else ""
        code = self.code_entry.get().strip() if self.code_entry else ""
        color = self.color_var.get().strip()
        
        # Required field validation
        if not name:
            messagebox.showerror("Validation Error", "Program name is required.", parent=self)
            return False
        
        if not acronym:
            messagebox.showerror("Validation Error", "Program acronym is required.", parent=self)
            return False
        
        if not code:
            messagebox.showerror("Validation Error", "Program code is required.", parent=self)
            return False
        
        # Format validation
        if len(acronym) > 10:
            messagebox.showerror("Validation Error", "Acronym must be 10 characters or less.", parent=self)
            return False
        
        if len(code) > 20:
            messagebox.showerror("Validation Error", "Program code must be 20 characters or less.", parent=self)
            return False
        
        if color and not self.is_valid_hex_color(color):
            messagebox.showerror("Validation Error", "Please enter a valid hex color code (e.g., #FF5733).", parent=self)
            return False
        
        return True

    def update_program(self):
        """Update the program after validation"""
        if not self.validate_form():
            return
        
        try:
            from app.db_manager import DatabaseManager
            
            # Get form data
            description_content = self.description_text.get("1.0", tk.END).strip()
            
            # Remove the placeholder text if it's still there
            if description_content == "Brief description of the program...":
                description_content = ""
            
            # Explicitly get each field value
            name_value = self.name_entry.get().strip()
            acronym_value = self.acronym_entry.get().strip().upper()
            code_value = self.code_entry.get().strip().upper()
            color_value = self.color_var.get().strip()
            
            program_data = {
                'name': name_value,
                'acronym': acronym_value,
                'code': code_value,
                'description': description_content,
                'color': color_value
            }
            
            # Update program in database
            db = DatabaseManager()
            program_id = self.program_data.get('id')
            
            if not program_id:
                messagebox.showerror("Error", "Program ID not found.", parent=self)
                return
            
            success, result = db.update_program(program_id, program_data)
            
            if success:
                # Store parent reference before destroying
                parent_ref = self.parent_view
                
                # Destroy this modal first
                self.destroy()
                
                # Refresh parent view after a small delay
                parent_ref.after(100, lambda: parent_ref.refresh_programs())
                
                # Show success modal with a delay
                parent_ref.after(200, lambda: SuccessModal(parent_ref))
            else:
                messagebox.showerror("Error", f"Failed to update program: {result}", parent=self)
                
        except Exception as e:
            print(f"Exception in update_program: {e}")
            import traceback
            traceback.print_exc()
            try:
                if self.winfo_exists():
                    messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}", parent=self)
                else:
                    print(f"Could not show error dialog: window destroyed")
            except:
                print(f"Could not show error dialog: {str(e)}")
