import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from app.ui.admin.components.modals import SuccessModal

class CreateCoursePopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_view = parent
        self.title("Create Course")
        self.geometry("360x400")
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
        ctk.CTkOptionMenu(
            self,
            variable=self.program_var,
            values=[
                "Bachelor of Science in Information Technology",
                "Bachelor of Science in Computer Science", 
                "Bachelor of Science in Information Systems"
            ],
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
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # Course Subject
        ctk.CTkLabel(
            self,
            text="Course Subject",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=24, pady=(0, 4))
        self.subject_var = ctk.StringVar(value="Choose a course subject")
        ctk.CTkOptionMenu(
            self,
            variable=self.subject_var,
            values=["Ethics 101", "Programming 1", "Data Structures", "Capstone"],
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
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # Year (entry with calendar icon)
        ctk.CTkLabel(
            self,
            text="Year",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=24, pady=(0, 4))
        year_frame = ctk.CTkFrame(self, fg_color="#fff", border_color="#BDBDBD", border_width=1, height=32)
        year_frame.pack(anchor="w", padx=24, pady=(0, 24), fill="x")
        year_frame.pack_propagate(False)
        self.year_var = ctk.StringVar(value="Enter/Select year")
        year_entry = ctk.CTkEntry(year_frame, textvariable=self.year_var, fg_color="#fff", border_width=0, text_color="#222", font=ctk.CTkFont(size=10), height=16, width=280)
        year_entry.pack(side="left", padx=(8, 0), pady=0)
        calendar_icon = ctk.CTkLabel(year_frame, text="\U0001F4C5", font=ctk.CTkFont(size=14), text_color="#757575", fg_color="#fff", width=24)
        calendar_icon.pack(side="right", padx=(0, 4), pady=0)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="#FAFAFA")
        button_frame.pack(side="bottom", fill="x", padx=24, pady=(10, 24))
        cancel_btn = ctk.CTkButton(
            button_frame,
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
            button_frame,
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
        # TODO: Implement creation logic with database
        print("Creating course...")
        # Store parent reference before destroying
        parent_ref = self.parent_view
        
        # Destroy this modal
        self.destroy()
        
        # Refresh parent view and show success
        parent_ref.after(100, lambda: parent_ref.refresh_courses())
        parent_ref.after(200, lambda: SuccessModal(parent_ref))
