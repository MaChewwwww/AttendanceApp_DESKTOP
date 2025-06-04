import customtkinter as ctk
from app.ui.admin.components.sidebar import DateTimePill

class ProgramsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._open_menu = None  # Track open menu widget
        self._open_menu_card = None  # Track which card the menu is for
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

        # Card grid
        card_grid = ctk.CTkFrame(self, fg_color="transparent")
        card_grid.pack(fill="both", expand=True, padx=20, pady=0)
        cols = 4
        for c in range(cols):
            card_grid.grid_columnconfigure(c, weight=1)

        # Sample data
        programs = ["BSIT", "BSBA", "BTLED ICT", "BSIT", "BSIT", "BSIT", "BSIT", "BSIT"]
        for idx, prog in enumerate(programs):
            row = idx // cols
            col = idx % cols
            card = ctk.CTkFrame(card_grid, fg_color="#fff", width=175, height=175, corner_radius=12)
            card.grid(row=row, column=col, padx=16, pady=16)
            card.pack_propagate(False)
            card.grid_propagate(False)
            # Only program name at the very bottom, left-aligned
            ctk.CTkLabel(card, text=prog, font=ctk.CTkFont(size=13, weight="bold"), text_color="#222").pack(side="bottom", anchor="w", padx=16, pady=12)
            # 3-dot menu top right
            menu_btn = ctk.CTkButton(card, text="⋮", width=24, height=24, fg_color="#fff", text_color="#222", hover_color="#F3F4F6", border_width=0, font=ctk.CTkFont(size=18), command=lambda c=card, b=None: self.show_card_menu(c, b))
            menu_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-8, y=8)

    def show_card_menu(self, card, btn=None):
        # Toggle: if menu is open for this card, close it
        if hasattr(self, '_open_menu') and self._open_menu is not None and self._open_menu_card is card:
            self._open_menu.destroy()
            self._open_menu = None
            self._open_menu_card = None
            return
        # Remove any existing menu from self
        if hasattr(self, '_open_menu') and self._open_menu is not None:
            self._open_menu.destroy()
            self._open_menu = None
            self._open_menu_card = None
        # Get absolute position of card and menu_btn
        card.update_idletasks()
        # Find the menu_btn widget inside the card
        menu_btn = None
        for child in card.winfo_children():
            if isinstance(child, ctk.CTkButton):
                menu_btn = child
                break
        if menu_btn:
            bx = menu_btn.winfo_rootx() - self.winfo_rootx()
            by = menu_btn.winfo_rooty() - self.winfo_rooty()
            menu_x = bx + menu_btn.winfo_width() + 2
            menu_y = by
        else:
            # fallback to card position
            menu_x = card.winfo_rootx() - card.master.winfo_rootx() + card.winfo_width() - 88
            menu_y = card.winfo_rooty() - card.master.winfo_rooty() + 36
        # Dropdown menu as child of self
        menu = ctk.CTkFrame(self, fg_color="#fff", border_color="#E5E7EB", border_width=1, corner_radius=8)
        menu._is_menu = True
        menu.place(x=menu_x, y=menu_y)
        def close_menu():
            menu.destroy()
            self._open_menu = None
            self._open_menu_card = None
        ctk.CTkButton(menu, text="Edit", fg_color="#fff", text_color="#222", hover_color="#F3F4F6", width=80, height=28, command=close_menu).pack(fill="x")
        ctk.CTkButton(menu, text="Delete", fg_color="#fff", text_color="#EF4444", hover_color="#F3F4F6", width=80, height=28, command=close_menu).pack(fill="x")
        self._open_menu = menu
        self._open_menu_card = card 