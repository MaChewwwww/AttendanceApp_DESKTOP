import customtkinter as ctk
import tkinter as tk
from app.ui.admin.components.sidebar import DateTimePill  # adjust path if needed

class FilterPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Filter Users")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Set background color to white
        self.configure(fg_color="#fff")
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        ctk.CTkLabel(
            self,
            text="Filter Users",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="black"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Filter options
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Year filter
        ctk.CTkLabel(filter_frame, text="Year", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
        year_var = tk.StringVar(value="All")
        year_options = ["All", "1st Year", "2nd Year", "3rd Year", "4th Year"]
        year_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=year_options,
            variable=year_var,
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222"
        )
        year_menu.pack(fill="x", pady=(0, 15))
        
        # Section filter
        ctk.CTkLabel(filter_frame, text="Section", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
        section_var = tk.StringVar(value="All")
        section_options = ["All", "1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]
        section_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=section_options,
            variable=section_var,
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222"
        )
        section_menu.pack(fill="x", pady=(0, 15))
        
        # Status filter
        ctk.CTkLabel(filter_frame, text="Status", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
        status_var = tk.StringVar(value="All")
        status_options = ["All", "Active", "Inactive"]
        status_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=status_options,
            variable=status_var,
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222"
        )
        status_menu.pack(fill="x", pady=(0, 15))
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Apply Filters",
            command=self.apply_filters,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="white"
        ).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Reset",
            command=self.reset_filters,
            fg_color="#F3F4F6",
            text_color="#222",
            hover_color="#E5E7EB"
        ).pack(side="right")
    
    def apply_filters(self):
        # TODO: Implement filter logic
        self.destroy()
    
    def reset_filters(self):
        # TODO: Implement reset logic
        self.destroy()

class ActionPopup(ctk.CTkToplevel):
    def __init__(self, parent, action, user_data):
        super().__init__(parent)
        self.title(f"{action} User")
        self.geometry("350x220")
        self.resizable(False, False)
        self.configure(fg_color="#fff")
        self.transient(parent)
        self.grab_set()
        self.action = action
        self.user_data = user_data
        self.setup_ui()

    def setup_ui(self):
        action = self.action
        name, year, section, status = self.user_data
        ctk.CTkLabel(self, text=f"{action} User", font=ctk.CTkFont(size=18, weight="bold"), text_color="#2563EB").pack(pady=(20, 10))
        ctk.CTkLabel(self, text=f"Name: {name}", font=ctk.CTkFont(size=14), text_color="#222").pack(anchor="w", padx=30, pady=(5, 0))
        ctk.CTkLabel(self, text=f"Year: {year}", font=ctk.CTkFont(size=14), text_color="#222").pack(anchor="w", padx=30, pady=(5, 0))
        ctk.CTkLabel(self, text=f"Section: {section}", font=ctk.CTkFont(size=14), text_color="#222").pack(anchor="w", padx=30, pady=(5, 0))
        ctk.CTkLabel(self, text=f"Status: {status}", font=ctk.CTkFont(size=14), text_color="#222").pack(anchor="w", padx=30, pady=(5, 10))
        if action == "Delete":
            ctk.CTkLabel(self, text="Are you sure you want to delete this user?", text_color="#B91C1C").pack(pady=(5, 10))
            btn_frame = ctk.CTkFrame(self, fg_color="transparent")
            btn_frame.pack(pady=10)
            ctk.CTkButton(btn_frame, text="Cancel", fg_color="#F3F4F6", text_color="#222", hover_color="#E5E7EB", command=self.destroy).pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="Delete", fg_color="#DC2626", hover_color="#B91C1C", text_color="#fff", command=self.destroy).pack(side="left", padx=10)
        else:
            ctk.CTkButton(self, text="Close", fg_color="#2563EB", hover_color="#1D4ED8", text_color="#fff", command=self.destroy).pack(pady=20)

class UsersView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.setup_ui()

    def setup_ui(self):
        # Top bar with date pill
        topbar = ctk.CTkFrame(self, fg_color="transparent")
        topbar.pack(fill="x", pady=(10, 0), padx=10)
        topbar.grid_columnconfigure(0, weight=1)
        DateTimePill(topbar).grid(row=0, column=1, sticky="e")

        # Header
        ctk.CTkLabel(
            self,
            text="Users",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="black"
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Search and filter bar (side by side, both with border, no corner radius, flush)
        search_bar_container = ctk.CTkFrame(self, fg_color="#fff")
        search_bar_container.pack(pady=(0, 10), padx=20, anchor="w")

        # Search entry with icon inside (frame height 36, icon and entry height 28, centered vertically, consistent color)
        search_entry_frame = ctk.CTkFrame(search_bar_container, fg_color="#fff", border_color="#BDBDBD", border_width=1, corner_radius=0, height=36)
        search_entry_frame.pack(side="left", pady=0, padx=0)
        search_entry_frame.pack_propagate(False)
        search_icon = ctk.CTkLabel(search_entry_frame, text="\U0001F50D", font=ctk.CTkFont(size=16), text_color="#757575", fg_color="#fff", width=28, height=28)
        search_icon.pack(side="left", padx=(8, 0), pady=4)
        search_entry = ctk.CTkEntry(search_entry_frame, placeholder_text="", width=160, fg_color="#fff",
                                    border_color="#fff", border_width=0, text_color="#222", font=ctk.CTkFont(size=15), height=28)
        search_entry.pack(side="left", padx=(2, 8), pady=4)

        # Filter button (flush, no corner radius, border on all sides, same height)
        filter_btn = ctk.CTkButton(
            search_bar_container,
            text="Filters",
            width=80,
            height=36,
            fg_color="#fff",
            text_color="#757575",
            hover_color="#F3F4F6",
            border_width=1,
            border_color="#BDBDBD",
            corner_radius=0,
            font=ctk.CTkFont(size=13),
            command=self.show_filter_popup
        )
        filter_btn.pack(side="left", padx=0, pady=0)

        # Table
        table_frame = ctk.CTkFrame(self, fg_color="#fff", corner_radius=8, border_width=1, border_color="#E5E7EB")
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Columns
        columns = ["Student Name", "Year", "Section", "Status", "Actions"]
        col_widths = [10, 1, 1, 1, 1]  # weight for grid columns
        for i, weight in enumerate(col_widths):
            table_frame.grid_columnconfigure(i, weight=weight)

        # Header row
        for i, col in enumerate(columns):
            ctk.CTkLabel(
                table_frame,
                text=col,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#6B7280",
                anchor="w"
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")

        # Sample data
        sample_data = [
            ("Shadrack Castro", "1st Year", "1-1", "Active"),
            ("Jerlee Alipio", "2nd Year", "2-3", "Inactive"),
            ("Steven Masangcay", "3rd Year", "3-2", "Active"),
            ("John Mathew Parocha", "4th Year", "4-1", "Active"),
        ]

        for idx, (name, year, section, status) in enumerate(sample_data, start=1):
            bg = "#fff" if idx % 2 == 0 else "#F9FAFB"
            # Name
            ctk.CTkLabel(table_frame, text=name, font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color=bg, anchor="w").grid(row=idx, column=0, sticky="nsew", padx=10, pady=6)
            # Year
            ctk.CTkLabel(table_frame, text=year, font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color=bg, anchor="w").grid(row=idx, column=1, sticky="nsew", padx=10, pady=6)
            # Section
            ctk.CTkLabel(table_frame, text=section, font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color=bg, anchor="w").grid(row=idx, column=2, sticky="nsew", padx=10, pady=6)
            # Status
            ctk.CTkLabel(table_frame, text=status, font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color=bg, anchor="w").grid(row=idx, column=3, sticky="nsew", padx=10, pady=6)
            # Actions dropdown styled as button
            action_var = tk.StringVar(value="Edit")
            actions = ["Edit", "View", "Delete"]
            action_menu = ctk.CTkOptionMenu(
                table_frame,
                values=actions,
                variable=action_var,
                width=100,
                height=28,
                font=ctk.CTkFont(size=12),
                fg_color="#F3F4F6",
                text_color="#222",
                button_color="#E5E7EB",
                button_hover_color="#D1D5DB",
                dropdown_fg_color="#fff",
                dropdown_hover_color="#E5E7EB",
                dropdown_text_color="#222",
                command=lambda choice, data=(name, year, section, status): self.handle_action(choice, data)
            )
            action_menu.grid(row=idx, column=4, sticky="w", padx=10, pady=6)

    def show_filter_popup(self):
        FilterPopup(self)

    def show_action_menu(self, widget, data):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="View", command=lambda: print(f"Viewing {data[0]}"))
        menu.add_command(label="Edit", command=lambda: print(f"Editing {data[0]}"))
        menu.add_command(label="Delete", command=lambda: print(f"Deleting {data[0]}"))
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height()
        self.after(1, lambda: menu.tk_popup(x, y))

    def handle_action(self, action, data):
        ActionPopup(self, action, data)
