import customtkinter as ctk

class ViewProgramPopup(ctk.CTkToplevel):
    def __init__(self, parent, program_data):
        super().__init__(parent)
        self.program_data = program_data
        program_name = program_data.get('name', 'Unknown Program')
        self.title(f"{program_name} View")
        self.geometry("730x600")
        self.resizable(False, False)
        self.configure(fg_color="#F5F5F5")
        self.transient(parent)
        self.grab_set()
        self.setup_ui()

    def setup_ui(self):
        program_name = self.program_data.get('name', 'Unknown Program')
        program_description = self.program_data.get('description', 'No description available')
        
        # Header row with program name, subtitle, and export button
        header_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
        header_frame.pack(fill="x", padx=24, pady=(16, 0))
        
        # Program name and subtitle (left)
        name_subtitle = ctk.CTkFrame(header_frame, fg_color="#F5F5F5")
        name_subtitle.pack(side="left", anchor="n")
        
        ctk.CTkLabel(
            name_subtitle,
            text=program_name,
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color="#222"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            name_subtitle,
            text=program_description.upper(),
            font=ctk.CTkFont(size=13),
            text_color="#757575"
        ).pack(anchor="w", pady=(0, 0))
        
        # Export button (right)
        ctk.CTkButton(
            header_frame,
            text="Export",
            fg_color="#1E3A8A",
            hover_color="#274690",
            text_color="#fff",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=90,
            height=32,
            corner_radius=16,
            command=self.export_data
        ).pack(side="right", anchor="n", padx=(0, 8), pady=(0, 8))

        # Stat cards row
        stat_row = ctk.CTkFrame(self, fg_color="#F5F5F5")
        stat_row.pack(fill="x", padx=24, pady=(18, 0))
        
        # TODO: Replace with actual data from backend
        card_data = [
            ("300", "Total Students"),
            ("90%", "Total Attendance Rate"),
            ("15", "Number of Courses"),
            ("99", "Total Absents")
        ]
        
        for value, label in card_data:
            card = ctk.CTkFrame(stat_row, fg_color="#fff", width=150, height=90, corner_radius=12)
            card.pack(side="left", padx=12, pady=0)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"), text_color="#222").pack(anchor="w", padx=16, pady=(16, 0))
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=10), text_color="#757575").pack(anchor="w", padx=16, pady=(0, 8))

        # Program details section
        details_frame = ctk.CTkFrame(self, fg_color="#fff", corner_radius=12)
        details_frame.pack(fill="both", expand=True, padx=24, pady=20)
        
        ctk.CTkLabel(
            details_frame,
            text="Program Details",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Details grid
        details_grid = ctk.CTkFrame(details_frame, fg_color="transparent")
        details_grid.pack(fill="x", padx=20, pady=(0, 20))
        
        details = [
            ("Acronym:", self.program_data.get('acronym', 'N/A')),
            ("Code:", self.program_data.get('code', 'N/A')),
            ("Created:", self.program_data.get('created_at', 'N/A')),
            ("Last Updated:", self.program_data.get('updated_at', 'N/A'))
        ]
        
        for i, (label, value) in enumerate(details):
            detail_row = ctk.CTkFrame(details_grid, fg_color="transparent")
            detail_row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                detail_row,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#222",
                width=100
            ).pack(side="left", anchor="w")
            
            ctk.CTkLabel(
                detail_row,
                text=value,
                font=ctk.CTkFont(size=13),
                text_color="#666"
            ).pack(side="left", anchor="w", padx=(20, 0))

    def export_data(self):
        # TODO: Implement export functionality
        print(f"Exporting data for program: {self.program_data.get('name', 'Unknown')}")
