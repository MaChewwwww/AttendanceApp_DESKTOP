import customtkinter as ctk
import tkinter as tk
from PIL import Image
import os

class InitialScreen(ctk.CTkFrame):
    def __init__(self, parent, on_student_click=None):
        super().__init__(parent, fg_color="transparent")
        
        self.on_student_click = on_student_click
        self.terms_modal = None
        
        # Create main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        # Left panel
        self.left_panel = ctk.CTkFrame(
            self.main_container,
            width=370,
            fg_color="#001143",
            corner_radius=0
        )
        self.left_panel.pack(side="left", fill="y")
        self.left_panel.pack_propagate(False)
        
        # Center container for logo and text
        center_container = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        center_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Load and display logo
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "Logo.png")
        if os.path.exists(logo_path):
            # Load the image using CTkImage for better HighDPI support
            logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(120, 120)
            )
            
            # Create label for logo
            logo_label = ctk.CTkLabel(
                center_container,
                image=logo_image,
                text=""
            )
            logo_label.pack(pady=(0, 20))
        
        ctk.CTkLabel(
            center_container,
            text="Attendify",
            font=ctk.CTkFont("Inter", 32, "bold"),
            text_color="#ffffff"
        ).pack()
        
        # Right panel
        self.right_panel = ctk.CTkFrame(
            self.main_container,
            fg_color="#f5f5f5",
            corner_radius=0
        )
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        # Content container
        container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Card
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
        
        padding_frame = ctk.CTkFrame(card, fg_color="transparent")
        padding_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            padding_frame,
            text="Sign in",
            font=ctk.CTkFont("Inter", 24, "bold"),
            text_color="#000000"
        ).pack(pady=(30, 10))
        
        divider_container = ctk.CTkFrame(padding_frame, fg_color="transparent", height=3)
        divider_container.pack(fill="x")
        divider_container.pack_propagate(False)
        
        center_frame = ctk.CTkFrame(divider_container, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        left_divider = ctk.CTkFrame(
            center_frame,
            fg_color="#1E3A8A",
            width=20.5,
            height=3
        )
        left_divider.pack(side="left")
        
        right_divider = ctk.CTkFrame(
            center_frame,
            fg_color="#10B981",
            width=20.5,
            height=3
        )
        right_divider.pack(side="left")
        
        self.student_btn = ctk.CTkButton(
            padding_frame,
            text="Admin",
            width=325,
            height=27,
            corner_radius=8,
            font=ctk.CTkFont("Source Sans 3", 12),
            fg_color="#1E3A8A",
            hover_color="#1E3A8A",
            command=lambda: self.on_student_click(False) if self.on_student_click else None
        )
        self.student_btn.pack(pady=10)
        
        terms_container = ctk.CTkFrame(padding_frame, fg_color="transparent")
        terms_container.pack(pady=(15, 5))
        
        first_line = ctk.CTkLabel(
            terms_container,
            text="By using this service, you understand and agree to the",
            font=ctk.CTkFont("Source Sans 3", 11),
            text_color="#666666"
        )
        first_line.pack()
        
        second_line_container = ctk.CTkFrame(terms_container, fg_color="transparent")
        second_line_container.pack()
        
        terms_link = tk.Label(
            second_line_container,
            text="Terms of Use",
            font=("Source Sans 3", 10),
            fg="#1E3A8A",
            cursor="hand2",
            bg="#ffffff"
        )
        terms_link.pack(side="left")
        terms_link.bind("<Button-1>", lambda e: self.open_terms_modal())
        
        and_label = ctk.CTkLabel(
            second_line_container,
            text=" and ",
            font=ctk.CTkFont("Source Sans 3", 11),
            text_color="#666666"
        )
        and_label.pack(side="left")
        
        privacy_link = tk.Label(
            second_line_container,
            text="Privacy Statement",
            font=("Source Sans 3", 10),
            fg="#1E3A8A",
            cursor="hand2",
            bg="#ffffff"
        )
        privacy_link.pack(side="left")
        privacy_link.bind("<Button-1>", lambda e: self.open_terms_modal())
        
        second_divider_container = ctk.CTkFrame(padding_frame, fg_color="transparent", height=1)
        second_divider_container.pack(fill="x", pady=(15, 15))
        second_divider_container.pack_propagate(False)
        
        second_center_frame = ctk.CTkFrame(second_divider_container, fg_color="transparent")
        second_center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        second_divider = ctk.CTkFrame(
            second_center_frame,
            fg_color="#1E3A8A",
            width=325,
            height=2
        )
        second_divider.pack()
        
        signup_container = ctk.CTkFrame(padding_frame, fg_color="transparent")
        signup_container.pack(pady=(0, 15))
        
        account_label = ctk.CTkLabel(
            signup_container,
            text="Need to register a student?",
            font=ctk.CTkFont("Source Sans 3", 11),
            text_color="#666666"
        )
        account_label.pack()
        
        signup_frame = ctk.CTkFrame(signup_container, fg_color="transparent")
        signup_frame.pack(pady=(2, 0))
        
        signup_label = tk.Label(
            signup_frame,
            text="Register Student",
            font=("Source Sans 3", 10, "underline"),
            fg="#000000",
            cursor="hand2",
            bg="#ffffff"
        )
        signup_label.pack()
        signup_label.bind("<Button-1>", lambda e: self.on_student_click(True) if self.on_student_click else None)
    
    def open_terms_modal(self):
        """Open the Terms of Use & Privacy Statement modal"""
        # Create modal dialog
        self.terms_modal = ctk.CTkToplevel(self)
        self.terms_modal.title("Terms of Use & Privacy Statement")
        self.terms_modal.geometry("700x600")  # Increased size for better readability
        self.terms_modal.resizable(False, False)  # Disable resizing to prevent fullscreen
        self.terms_modal.configure(fg_color="#ffffff")
        
        # Make modal and center it
        self.terms_modal.grab_set()
        self.terms_modal.update_idletasks()
        
        # Center the modal
        width = self.terms_modal.winfo_width()
        height = self.terms_modal.winfo_height()
        x = (self.terms_modal.winfo_screenwidth() // 2) - (width // 2)
        y = (self.terms_modal.winfo_screenheight() // 2) - (height // 2)
        self.terms_modal.geometry(f"{width}x{height}+{x}+{y}")
        
        # Header
        header_frame = ctk.CTkFrame(self.terms_modal, fg_color="transparent", height=50)
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="Terms of Use & Privacy Statement",
            font=ctk.CTkFont("Roboto", 20, "bold"),
            text_color="#1E3A8A"
        ).pack(anchor="w")
        
        # Scrollable text frame
        text_frame = ctk.CTkScrollableFrame(
            self.terms_modal,
            width=660,  # Increased width
            height=450,  # Increased height
            fg_color="#f8f9fa",
            border_width=1,
            border_color="#e9ecef"
        )
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Terms and Conditions Content
        terms_content = """
FACIAL RECOGNITION ATTENDANCE SYSTEM - ATTENDIFY

Terms of Use

1. Acceptance of Terms
By accessing or using the Facial Recognition Attendance System Attendify, you agree to be bound by these Terms of Use. If you do not agree to these Terms, you are not authorized to access nor use the system.

2. Purpose of the System
The system is developed to streamline and automate attendance tracking through facial recognition technology. It is intended solely for authorized use by organizations, administrators, and approved users for attendance monitoring and management.

3. User Responsibilities
By using the System, you agree to:
• Use the System only for its intended purpose and in accordance with applicable laws and regulations.
• Refrain from attempting to reverse-engineer, modify, disrupt, or misuse the System or any data it processes.
• Maintain the confidentiality of any account credentials provided to you and promptly notify us of any unauthorized use.

4. Intellectual Property
The System, including all software, algorithms, designs, and associated intellectual property, is owned by Attendify or its licensors. You may not copy, reproduce, distribute, or create derivative works from the System without prior written consent from Attendify.

5. Termination
Attendify reserves the right to suspend or terminate your access to the System at any time, with or without notice, if you violate these Terms or engage in unlawful or unauthorized activities.

6. Limitation of Liability
The System is provided "as is" without warranties of any kind. Attendify shall not be liable for any damages arising from the use or inability to use the System, including but not limited to system errors, data loss, or downtime.

7. Changes to Terms
We may update these Terms at any time. Continued use of the System after changes constitutes your acceptance of the revised Terms.

Privacy Statement

1. Information We Collect
The Facial Recognition Attendance System collects the following personal information:
• Biometric Data: Facial images or templates used for attendance tracking.
• Personal Information: Name, employee ID, or other identifiers linked to attendance records.
• Usage Data: Logs of system interactions, such as timestamps of attendance records.

2. How We Use Your Information
We collect and use data to:
• Authenticate identities and record attendance.
• Enhance the System's reliability, performance, and accuracy.
• Comply with legal obligations or organizational policies.

3. Data Storage and Security
All biometric data is encrypted and stored securely to prevent unauthorized access. Personal and usage data are stored with industry-standard security measures. We retain data only as long as necessary to fulfill attendance purposes or legal obligations.

4. Data Sharing
We do not share your data with third parties unless:
• You have given explicit consent.
• It is required by law or a valid legal request.
• It is shared with trusted service providers under strict confidentiality agreements to help operate or support the System.

5. Your Rights
You may have the right, in accordance with applicable laws, to:
• Access, review, correct, or request deletion of your personal data.
• Request information about how your data is collected and used.

6. Data Retention
Biometric and personal data are deleted once they are no longer needed for attendance tracking or as required by applicable law. You may request earlier deletion of your data where legally permitted.

7. Contact Us
For any questions, concerns, or requests related to these Terms or our Privacy Statement, please contact us at:
📧 attendify.attendancesystem@gmail.com

8. Changes to Privacy Statement
This Privacy Statement may be updated periodically. Any significant changes will be communicated through the System or via other appropriate means.

By using this service, you acknowledge that you have read, understood, and agree to be bound by these Terms of Use and Privacy Statement.
        """
        
        # Add terms content to scrollable frame
        terms_label = ctk.CTkLabel(
            text_frame,
            text=terms_content.strip(),
            font=ctk.CTkFont("Source Sans 3", 11),
            text_color="#333333",
            justify="left",
            wraplength=620  # Increased wrap length
        )
        terms_label.pack(anchor="w", padx=10, pady=10)
        
        # Button frame for centering
        button_frame = ctk.CTkFrame(self.terms_modal, fg_color="transparent", height=60)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        button_frame.pack_propagate(False)
        
        # Close button (centered)
        close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            width=120,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont("Source Sans 3", 12, "bold"),
            fg_color="#666666",
            hover_color="#555555",
            command=self.close_terms_modal
        )
        close_button.pack(anchor="center")
        
        # Handle modal close
        self.terms_modal.protocol("WM_DELETE_WINDOW", self.close_terms_modal)
    
    def close_terms_modal(self):
        """Close the terms modal"""
        if hasattr(self, 'terms_modal') and self.terms_modal:
            self.terms_modal.destroy()
            self.terms_modal = None