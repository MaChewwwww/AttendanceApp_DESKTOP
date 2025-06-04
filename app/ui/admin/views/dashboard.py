import customtkinter as ctk
from app.ui.admin.components.sidebar import DateTimePill

class DashboardView(ctk.CTkFrame):
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
            text="Admin\nDashboard",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="black",
            anchor="w",
            justify="left"
        )
        label.pack(anchor="w", padx=20, pady=(10, 10))

        # Card grid for dashboard metrics (3+1 layout)
        card_grid = ctk.CTkFrame(self, fg_color="transparent")
        card_grid.pack(anchor="nw", padx=20, pady=0)
        cols = 3
        for c in range(cols):
            card_grid.grid_columnconfigure(c, weight=0)
        metrics = [
            ("20", "Students"),
            ("20", "Courses"),
            ("20", "Programs"),
            ("20", "Programs")
        ]
        # First row: 3 cards
        for idx in range(3):
            value, label_text = metrics[idx]
            card = ctk.CTkFrame(card_grid, fg_color="#fff", width=310, height=190, corner_radius=12)
            card.grid(row=0, column=idx, padx=16, pady=16)
            card.pack_propagate(False)
            # Bottom-left container for text
            text_frame = ctk.CTkFrame(card, fg_color="#fff")
            text_frame.pack(side="bottom", anchor="w", fill="x", padx=0, pady=0)
            ctk.CTkLabel(text_frame, text=value, font=ctk.CTkFont(size=32, weight="bold"), text_color="#222").pack(anchor="w", padx=24, pady=(0, 0))
            ctk.CTkLabel(text_frame, text=label_text, font=ctk.CTkFont(size=14), text_color="#757575").pack(anchor="w", padx=24, pady=(0, 24))
        # Second row: 1 card bottom-left
        value, label_text = metrics[3]
        card = ctk.CTkFrame(card_grid, fg_color="#fff", width=310, height=190, corner_radius=12)
        card.grid(row=1, column=0, padx=16, pady=16)
        card.pack_propagate(False)
        text_frame = ctk.CTkFrame(card, fg_color="#fff")
        text_frame.pack(side="bottom", anchor="w", fill="x", padx=0, pady=0)
        ctk.CTkLabel(text_frame, text=value, font=ctk.CTkFont(size=32, weight="bold"), text_color="#222").pack(anchor="w", padx=24, pady=(0, 0))
        ctk.CTkLabel(text_frame, text=label_text, font=ctk.CTkFont(size=14), text_color="#757575").pack(anchor="w", padx=24, pady=(0, 24)) 