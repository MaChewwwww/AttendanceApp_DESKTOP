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

        # Floating '+' button (bottom right)
        plus_btn = ctk.CTkButton(self, text="+", width=56, height=56, corner_radius=28, fg_color="#1E3A8A", text_color="#fff", font=ctk.CTkFont(size=32, weight="bold"), hover_color="#274690", border_width=0, command=self.create_program)
        plus_btn.place(relx=1.0, rely=1.0, anchor="se", x=-32, y=-32)

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
        def edit_program():
            close_menu()
            EditProgramPopup(self)
        ctk.CTkButton(menu, text="Edit", fg_color="#fff", text_color="#222", hover_color="#F3F4F6", width=80, height=28, command=edit_program).pack(fill="x")
        ctk.CTkButton(menu, text="View", fg_color="#fff", text_color="#222", hover_color="#F3F4F6", width=80, height=28, command=close_menu).pack(fill="x")
        ctk.CTkButton(menu, text="Delete", fg_color="#fff", text_color="#EF4444", hover_color="#F3F4F6", width=80, height=28, command=close_menu).pack(fill="x")
        self._open_menu = menu
        self._open_menu_card = card

    def create_program(self):
        CreateProgramPopup(self)
    
    def edit_program(self):
        EditProgramPopup(self)

class CreateProgramPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Create Program")
        self.geometry("320x390")
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(
            self,
            text="Create Program",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="#111",
        ).pack(anchor="w", padx=24, pady=(24, 12))

       # Program Name
        ctk.CTkLabel(self, text="Program Name", font=ctk.CTkFont(size=13, weight="bold"), text_color="#222").pack(anchor="w", padx=24, pady=(0, 2))
        self.name_var = ctk.StringVar()
        ctk.CTkEntry(self, textvariable=self.name_var, fg_color="#fff", border_color="#BDBDBD", border_width=1, text_color="#222", font=ctk.CTkFont(size=13), height=36).pack(anchor="w", padx=24, pady=(0, 10), fill="x")

        # Row for Acronym and Year Levels (side by side)
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(0, 10))

        # Column for Acronym
        acronym_col = ctk.CTkFrame(row, fg_color="transparent")
        acronym_col.pack(side="left", padx=(0, 10), anchor="n")

        ctk.CTkLabel(acronym_col, text="Acronym", font=ctk.CTkFont(size=13, weight="bold"), text_color="#222").pack(anchor="w", pady=(0, 2))
        self.acronym_var = ctk.StringVar()
        ctk.CTkEntry(acronym_col, textvariable=self.acronym_var, fg_color="#fff", border_color="#BDBDBD", border_width=1, text_color="#222", font=ctk.CTkFont(size=13), width=120, height=36).pack(anchor="w")

        # Column for Year Levels
        year_col = ctk.CTkFrame(row, fg_color="transparent")
        year_col.pack(side="left", anchor="n")

        ctk.CTkLabel(year_col, text="Year Levels", font=ctk.CTkFont(size=13, weight="bold"), text_color="#222").pack(anchor="w", pady=(0, 2))
        self.year_var = ctk.StringVar(value="1")
        ctk.CTkOptionMenu(
            year_col,
            variable=self.year_var,
            values=[str(i) for i in range(1, 5)],
            fg_color="#fff",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            width=60,
            height=36,
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w")

        # Program Head
        ctk.CTkLabel(self, text="Program Head", font=ctk.CTkFont(size=13, weight="bold"), text_color="#222").pack(anchor="w", padx=24, pady=(0, 2))
        self.head_var = ctk.StringVar()
        ctk.CTkEntry(self, textvariable=self.head_var, fg_color="#fff", border_color="#BDBDBD", border_width=1, text_color="#222", font=ctk.CTkFont(size=13), height=36).pack(anchor="w", padx=24, pady=(0, 18), fill="x")

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="#FAFAFA")
        button_frame.pack(side="bottom", fill="x", padx=24, pady=(10, 20))

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="#BDBDBD",
            text_color="#222",
            hover_color="#A3A3A3",
            width=120,
            height=36,
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 8))

        create_btn = ctk.CTkButton(
            button_frame,
            text="Create",
            fg_color="#1E3A8A",
            hover_color="#1D4ED8",
            text_color="#fff",
            width=120,
            height=36,
            command=self.create_program
        )
        create_btn.pack(side="right", padx=(8, 0))

    def create_program(self):
        # TODO: Implement creation logic
        self.destroy() 

class EditProgramPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Update Program")
        self.geometry("320x390")
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(
            self,
            text="Update Program",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="#111",
        ).pack(anchor="w", padx=24, pady=(24, 12))

       # Program Name
        ctk.CTkLabel(self, text="Program Name", font=ctk.CTkFont(size=13, weight="bold"), text_color="#222").pack(anchor="w", padx=24, pady=(0, 2))
        self.name_var = ctk.StringVar()
        ctk.CTkEntry(self, textvariable=self.name_var, fg_color="#fff", border_color="#BDBDBD", border_width=1, text_color="#222", font=ctk.CTkFont(size=13), height=36).pack(anchor="w", padx=24, pady=(0, 10), fill="x")

        # Row for Acronym and Year Levels (side by side)
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(0, 10))

        # Column for Acronym
        acronym_col = ctk.CTkFrame(row, fg_color="transparent")
        acronym_col.pack(side="left", padx=(0, 10), anchor="n")

        ctk.CTkLabel(acronym_col, text="Acronym", font=ctk.CTkFont(size=13, weight="bold"), text_color="#222").pack(anchor="w", pady=(0, 2))
        self.acronym_var = ctk.StringVar()
        ctk.CTkEntry(acronym_col, textvariable=self.acronym_var, fg_color="#fff", border_color="#BDBDBD", border_width=1, text_color="#222", font=ctk.CTkFont(size=13), width=120, height=36).pack(anchor="w")

        # Column for Year Levels
        year_col = ctk.CTkFrame(row, fg_color="transparent")
        year_col.pack(side="left", anchor="n")

        ctk.CTkLabel(year_col, text="Year Levels", font=ctk.CTkFont(size=13, weight="bold"), text_color="#222").pack(anchor="w", pady=(0, 2))
        self.year_var = ctk.StringVar(value="1")
        ctk.CTkOptionMenu(
            year_col,
            variable=self.year_var,
            values=[str(i) for i in range(1, 5)],
            fg_color="#fff",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            width=60,
            height=36,
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w")

        # Program Head
        ctk.CTkLabel(self, text="Program Head", font=ctk.CTkFont(size=13, weight="bold"), text_color="#222").pack(anchor="w", padx=24, pady=(0, 2))
        self.head_var = ctk.StringVar()
        ctk.CTkEntry(self, textvariable=self.head_var, fg_color="#fff", border_color="#BDBDBD", border_width=1, text_color="#222", font=ctk.CTkFont(size=13), height=36).pack(anchor="w", padx=24, pady=(0, 18), fill="x")

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="#FAFAFA")
        button_frame.pack(side="bottom", fill="x", padx=24, pady=(10, 20))

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="#BDBDBD",
            text_color="#222",
            hover_color="#A3A3A3",
            width=120,
            height=36,
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 8))

        create_btn = ctk.CTkButton(
            button_frame,
            text="Update",
            fg_color="#1E3A8A",
            hover_color="#1D4ED8",
            text_color="#fff",
            width=120,
            height=36,
            command=self.update_program
        )
        create_btn.pack(side="right", padx=(8, 0))

    def update_program(self):
        # TODO: Implement creation logic
        self.destroy() 