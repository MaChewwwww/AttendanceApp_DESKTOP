import customtkinter as ctk
from app.ui.admin.components.sidebar import DateTimePill
import tkinter as tk
from app.ui.admin.components.modals import DeleteModal, SuccessModal
from .programs_add import CreateProgramPopup
from .programs_edit import EditProgramPopup
from .programs_view import ViewProgramPopup
from PIL import Image
import os

class ProgramsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._open_menu = None  # Track open menu widget
        self._open_menu_card = None  # Track which card the menu is for
        self.programs_data = self.load_programs_data()
        self.setup_ui()

    def load_programs_data(self):
        # Load from database instead of hardcoded data
        try:
            from app.db_manager import DatabaseManager
            db = DatabaseManager()
            success, programs = db.get_programs()
            
            if success:
                return programs
            else:
                print(f"Error loading programs: {programs}")
                return []
        except Exception as e:
            print(f"Error loading programs data: {e}")
            # Fallback to hardcoded data if database fails
            return [
                {
                    'id': 1,
                    'name': 'Bachelor of Science in Information Technology',
                    'acronym': 'BSIT',
                    'code': 'IT-001',
                    'description': 'A comprehensive program focusing on information technology and computer systems',
                    'color': '#3B82F6'  # Blue
                },
                {
                    'id': 2,
                    'name': 'Bachelor of Science in Computer Science',
                    'acronym': 'BSCS',
                    'code': 'CS-001',
                    'description': 'A program emphasizing theoretical foundations of computation and practical software engineering',
                    'color': '#10B981'  # Green
                },
                {
                    'id': 3,
                    'name': 'Bachelor of Science in Information Systems',
                    'acronym': 'BSIS',
                    'code': 'IS-001',
                    'description': 'A program combining business processes with information technology solutions',
                    'color': '#F59E0B'  # Orange
                }
            ]

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

        # Create cards from programs data
        for idx, program in enumerate(self.programs_data):
            row = idx // cols
            col = idx % cols
            card = ctk.CTkFrame(card_grid, fg_color="#fff", width=175, height=175, corner_radius=12)
            card.grid(row=row, column=col, padx=16, pady=16)
            card.pack_propagate(False)
            card.grid_propagate(False)
            
            # Store program data in card for reference
            card.program_data = program
            
            # Add program image or placeholder
            self._add_program_image(card, program)
            
            # Program acronym at the bottom
            ctk.CTkLabel(
                card, 
                text=program['acronym'], 
                font=ctk.CTkFont(size=13, weight="bold"), 
                text_color="#222"
            ).pack(side="bottom", anchor="w", padx=16, pady=12)
            
            # 3-dot menu top right
            menu_btn = ctk.CTkButton(
                card, 
                text="⋮", 
                width=24, 
                height=24, 
                fg_color="#fff", 
                text_color="#222", 
                hover_color="#F3F4F6", 
                border_width=0, 
                font=ctk.CTkFont(size=18), 
                command=lambda c=card: self.show_card_menu(c)
            )
            menu_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-8, y=8)

        # Floating '+' button (bottom right)
        plus_btn = ctk.CTkButton(
            self,
            text="+",
            width=56,
            height=56,
            corner_radius=28,  # Half of width/height
            fg_color="#1E3A8A",
            text_color="#fff",
            font=ctk.CTkFont(size=32, weight="bold"),
            hover_color="#274690",
            border_width=0,
            command=self.create_program
        )
        plus_btn.place(relx=1.0, rely=1.0, anchor="se", x=-32, y=-32)

    def _add_program_image(self, card, program):
        """Add program color background or placeholder to card"""
        try:
            color = program.get('color', '#6B7280')  # Default gray if no color
            
            # Create a colored frame as background
            color_frame = ctk.CTkFrame(
                card, 
                fg_color=color,
                width=120, 
                height=80, 
                corner_radius=8
            )
            color_frame.pack(pady=(16, 8))
            
            # Add program acronym on the colored background
            acronym_label = ctk.CTkLabel(
                color_frame,
                text=program.get('acronym', '?'),
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="white"
            )
            acronym_label.place(relx=0.5, rely=0.5, anchor="center")
                
        except Exception as e:
            print(f"Error creating color background for {program.get('name', 'Unknown')}: {e}")
            # Fallback to emoji placeholder
            fallback_label = ctk.CTkLabel(
                card, 
                text="📚", 
                font=ctk.CTkFont(size=40), 
                text_color="#666"
            )
            fallback_label.pack(pady=(16, 8))

    def show_card_menu(self, card):
        # Toggle: if menu is open for this card, close it
        if hasattr(self, '_open_menu') and self._open_menu is not None and self._open_menu_card is card:
            self._open_menu.destroy()
            self._open_menu = None
            self._open_menu_card = None
            return
        
        # Remove any existing menu
        if hasattr(self, '_open_menu') and self._open_menu is not None:
            self._open_menu.destroy()
            self._open_menu = None
            self._open_menu_card = None
        
        # Calculate menu position
        card.update_idletasks()
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
            menu_x = card.winfo_rootx() - card.master.winfo_rootx() + card.winfo_width() - 88
            menu_y = card.winfo_rooty() - card.master.winfo_rooty() + 36
        
        # Create dropdown menu
        menu = ctk.CTkFrame(self, fg_color="#fff", border_color="#E5E7EB", border_width=1, corner_radius=8)
        menu.place(x=menu_x, y=menu_y)
        
        def close_menu():
            menu.destroy()
            self._open_menu = None
            self._open_menu_card = None
        
        def edit_program():
            close_menu()
            EditProgramPopup(self, card.program_data)
        
        def view_program():
            close_menu()
            ViewProgramPopup(self, card.program_data)
        
        def delete_program():
            close_menu()
            def on_delete():
                # TODO: Implement actual deletion
                SuccessModal(self)
            DeleteModal(self, on_delete=on_delete)
        
        ctk.CTkButton(menu, text="Edit", fg_color="#fff", text_color="#222", hover_color="#F3F4F6", width=80, height=28, command=edit_program).pack(fill="x")
        ctk.CTkButton(menu, text="View", fg_color="#fff", text_color="#222", hover_color="#F3F4F6", width=80, height=28, command=view_program).pack(fill="x")
        ctk.CTkButton(menu, text="Delete", fg_color="#fff", text_color="#EF4444", hover_color="#F3F4F6", width=80, height=28, command=delete_program).pack(fill="x")
        
        self._open_menu = menu
        self._open_menu_card = card

    def create_program(self):
        CreateProgramPopup(self)

    def refresh_programs(self):
        # TODO: Reload programs data and refresh UI
        self.programs_data = self.load_programs_data()
        # Refresh the UI components