import customtkinter as ctk

class UsersView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.setup_ui()

    def setup_ui(self):
        label = ctk.CTkLabel(
            self,
            text="Users Management",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="black"
        )
        label.pack(pady=20) 