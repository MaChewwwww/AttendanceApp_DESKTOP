import customtkinter as ctk
import tkinter as tk

class InitialScreen(ctk.CTk):
    def __init__(self, on_student_click=None):
        super().__init__()
        
        self.on_student_click = on_student_click
        
        self.title("Attendify")
        self.geometry("1000x600")
        self.resizable(False, False)
        
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        self.left_panel = ctk.CTkFrame(
            self.main_container,
            width=370,
            fg_color="#001143",
            corner_radius=0
        )
        self.left_panel.pack(side="left", fill="y")
        self.left_panel.pack_propagate(False)
        
        ctk.CTkLabel(
            self.left_panel,
            text="Attendify",
            font=ctk.CTkFont("Roboto", 32, "bold"),
            text_color="#ffffff"
        ).pack(expand=True)
        
        self.right_panel = ctk.CTkFrame(
            self.main_container,
            fg_color="#f5f5f5",
            corner_radius=0
        )
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
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
            text="Sign in as",
            font=ctk.CTkFont("Roboto", 24, "bold"),
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
            text="Student",
            width=325,
            height=27,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#1E3A8A",
            hover_color="#1E3A8A",
            command=self.on_student_click
        )
        self.student_btn.pack(pady=10)
        
        terms_container = ctk.CTkFrame(padding_frame, fg_color="transparent")
        terms_container.pack(pady=(15, 5))
        
        first_line = ctk.CTkLabel(
            terms_container,
            text="By using this service, you understand and agree to the",
            font=ctk.CTkFont("Roboto", 11),
            text_color="#666666"
        )
        first_line.pack()
        
        second_line_container = ctk.CTkFrame(terms_container, fg_color="transparent")
        second_line_container.pack()
        
        terms_link = tk.Label(
            second_line_container,
            text="Terms of Use",
            font=("Roboto", 10),
            fg="#1E3A8A",
            cursor="hand2",
            bg="#ffffff"
        )
        terms_link.pack(side="left")
        
        and_label = ctk.CTkLabel(
            second_line_container,
            text=" and ",
            font=ctk.CTkFont("Roboto", 11),
            text_color="#666666"
        )
        and_label.pack(side="left")
        
        privacy_link = tk.Label(
            second_line_container,
            text="Privacy Statement",
            font=("Roboto", 10),
            fg="#1E3A8A",
            cursor="hand2",
            bg="#ffffff"
        )
        privacy_link.pack(side="left")
        
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
            text="Don't have an account yet?",
            font=ctk.CTkFont("Roboto", 11),
            text_color="#666666"
        )
        account_label.pack()
        
        signup_frame = ctk.CTkFrame(signup_container, fg_color="transparent")
        signup_frame.pack(pady=(2, 0))
        
        signup_label = tk.Label(
            signup_frame,
            text="Sign up here",
            font=("Roboto", 10, "underline"),
            fg="#000000",
            cursor="hand2",
            bg="#ffffff"
        )
        signup_label.pack()
        signup_label.bind("<Button-1>", lambda e: self.on_student_click(True)) 