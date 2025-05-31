import customtkinter as ctk
from app.ui.admin.components.sidebar import DateTimePill

class ProgramsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.setup_ui()

    def setup_ui(self):
        # Top bar for the DateTimePill
        topbar = ctk.CTkFrame(self, fg_color="transparent")
        topbar.pack(fill="x", pady=(10, 0), padx=10)
        topbar.grid_columnconfigure(0, weight=1)
        pill = DateTimePill(topbar)
        pill.grid(row=0, column=1, sticky="e")

        label = ctk.CTkLabel(
            self,
            text="Programs",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="black"
        )
        label.pack(anchor="w", padx=20, pady=20) 