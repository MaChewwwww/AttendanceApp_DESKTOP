import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

class LoginForm(ctk.CTkFrame):
    def __init__(self, master, db_manager=None, on_login_success=None):
        super().__init__(master, fg_color="transparent")
        
        self.db_manager = db_manager
        self.on_login_success = on_login_success
        
        # Initialize variables
        self.student_number = tk.StringVar()
        self.password = tk.StringVar()
        self.remember_me = tk.BooleanVar()
        
        # Create the login form
        self._create_login_form()
        
    def _create_login_form(self):
        # Create container frame
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Create card frame
        card = ctk.CTkFrame(
            container,
            fg_color="#ffffff",
            corner_radius=15,
            width=454,
            height=353,
            border_width=1,
            border_color="#d1d1d1"
        )
        card.pack(padx=20, pady=20)
        card.pack_propagate(False)
        
        # Create padding frame
        padding_frame = ctk.CTkFrame(card, fg_color="transparent")
        padding_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title
        ctk.CTkLabel(
            padding_frame,
            text="Sign in as",
            font=ctk.CTkFont("Roboto", 24, "bold"),
            text_color="#000000"
        ).pack(pady=(0, 2))
        
        # Student label
        ctk.CTkLabel(
            padding_frame,
            text="Student",
            font=ctk.CTkFont("Roboto", 24, "bold"),
            text_color="#1E3A8A"
        ).pack(pady=(0, 5))
        
        # Divider
        divider_container = ctk.CTkFrame(padding_frame, fg_color="transparent", height=2)
        divider_container.pack(fill="x", pady=(0, 15))
        divider_container.pack_propagate(False)
        
        divider = ctk.CTkFrame(
            divider_container,
            fg_color="#1E3A8A",
            width=50,
            height=2
        )
        divider.place(relx=0.5, rely=0.5, anchor="center")
        
        # Student Number
        ctk.CTkLabel(
            padding_frame,
            text="Student Number",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070"
        ).pack(anchor="w", padx=17, pady=(0, 3))
        
        student_number_entry = ctk.CTkEntry(
            padding_frame,
            textvariable=self.student_number,
            width=420,
            height=27,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000"
        )
        student_number_entry.pack(padx=17, pady=(0, 10))
        
        # Password
        ctk.CTkLabel(
            padding_frame,
            text="Password",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070"
        ).pack(anchor="w", padx=17, pady=(0, 3))
        
        password_entry = ctk.CTkEntry(
            padding_frame,
            textvariable=self.password,
            width=420,
            height=27,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            show="•"
        )
        password_entry.pack(padx=17, pady=(0, 10))
        
        # Remember me checkbox
        checkbox_frame = ctk.CTkFrame(padding_frame, fg_color="transparent")
        checkbox_frame.pack(fill="x", padx=17, pady=(0, 15))
        
        remember_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Remember me",
            variable=self.remember_me,
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070",
            checkbox_width=15,
            checkbox_height=15,
            corner_radius=4,
            border_width=1,
            fg_color="#1E3A8A",
            hover_color="#1E3A8A"
        )
        remember_checkbox.pack(side="left")
        
        # Sign in button
        signin_button = ctk.CTkButton(
            padding_frame,
            text="Sign in",
            width=120,
            height=27,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12, "bold"),
            fg_color="#1E3A8A",
            hover_color="#1E3A8A",
            command=self.handle_login
        )
        signin_button.pack(pady=(0, 8))
        
        # Forgot password link
        forgot_password = tk.Label(
            padding_frame,
            text="I forgot password",
            font=("Roboto", 10, "underline"),
            fg="#F87171",
            cursor="hand2",
            bg="#ffffff"
        )
        forgot_password.pack()
        
    def handle_login(self):
        """Handle login button click"""
        student_number = self.student_number.get().strip()
        password = self.password.get().strip()
        
        if not student_number or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        # TODO: Implement actual login logic with database
        if self.on_login_success:
            self.on_login_success({
                'student_number': student_number,
                'role': 'student'
            }) 