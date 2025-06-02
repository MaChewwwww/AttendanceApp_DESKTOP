import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

class UsersEditModal(ctk.CTkToplevel):
    def __init__(self, parent, user_data, user_type="student"):
        super().__init__(parent)
        self.user_data = user_data
        self.user_type = user_type
        self.title(f"Edit User")
        self.geometry("640x720")
        self.resizable(False, False)
        self.configure(fg_color="#fff")
        self.transient(parent)
        self.grab_set()
        self._center_window(640, 720)
        self.setup_ui()

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
        self.create_form_field(left_col, "First Name")
        self.create_form_field(left_col, "Last Name")
        self.create_form_field(left_col, "Email")
        self.create_form_field(left_col, "Password", show="*")
        
        # Right column entries
        self.create_form_field(right_col, "Middle Name")
        self.create_form_field(right_col, "Suffix Name")
        
        if self.user_type == "student":
            self.create_form_field(right_col, "Section")
        else:
            self.create_form_field(right_col, "Employee Number")
        
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
        preview_frame = ctk.CTkFrame(right_col, fg_color="#fff")
        preview_frame.pack(fill="x", pady=(0, 10))
        
        img_frame = ctk.CTkFrame(preview_frame, fg_color="#222", width=40, height=40, corner_radius=6)
        img_frame.pack(side="left", pady=(0, 0), padx=(0, 8))
        img_frame.pack_propagate(False)
        ctk.CTkLabel(img_frame, text="", fg_color="#222").pack(expand=True, fill="both")
        
        file_info = ctk.CTkFrame(preview_frame, fg_color="#fff")
        file_info.pack(fill="x", pady=(0, 0))
        ctk.CTkLabel(file_info, text="img.name", font=ctk.CTkFont(size=13, weight="bold"), text_color="#000").pack(anchor="w")
        ctk.CTkLabel(file_info, text=".jpeg", font=ctk.CTkFont(size=11), text_color="#757575").pack(anchor="w")
        
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

    def open_facial_recognition(self):
        """Open facial recognition popup"""
        from .users_modals import FacialRecognitionPopup
        FacialRecognitionPopup(self)

    def show_caution_modal(self):
        """Show caution modal before saving"""
        def on_continue():
            print('Changes saved!')
            # Place your save logic here
        
        from .users_modals import CautionModal
        CautionModal(self, on_continue=on_continue)
