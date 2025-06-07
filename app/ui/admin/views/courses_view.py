import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ViewCoursePopup(ctk.CTkToplevel):
    def __init__(self, parent, course_data):
        super().__init__(parent)
        self.course_data = course_data
        
        course_name = course_data.get('name', 'Unknown Course')
        self.title(f"{course_name} View")
        self.geometry("640x720")
        self.resizable(False, False)
        self.configure(fg_color="#F5F5F5")
        self.transient(parent)
        self.grab_set()
        self.center_window()
        self.setup_ui()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        course_name = self.course_data.get('name', 'Unknown Course')
        program_name = self.course_data.get('program_name', 'Unknown Program')
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
        header_frame.pack(fill="x", padx=24, pady=(24, 0))
        ctk.CTkLabel(
            header_frame,
            text=course_name,
            font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
            text_color="#111"
        ).pack(side="left", anchor="n")
        
        # Current course info
        ctk.CTkLabel(
            self,
            text=f"Current: {course_name} - {program_name}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#1E3A8A"
        ).pack(anchor="w", padx=24, pady=(8, 0))
        
        # Academic year
        ctk.CTkLabel(
            self,
            text="S.Y 2025 - 2026",
            font=ctk.CTkFont(size=13),
            text_color="#222"
        ).pack(anchor="w", padx=24, pady=(0, 20))
        
        # Stat cards
        stat_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
        stat_frame.pack(fill="x", padx=24, pady=(0, 0))
        
        # Sample statistics data
        card_data = [
            ("99", "Total Absents"),
            ("12%", "Attendance Rate"), 
            ("10", "Number of Classes"),
            ("25", "Total Students")
        ]
        
        # First row: 3 cards
        row1 = ctk.CTkFrame(stat_frame, fg_color="#F5F5F5")
        row1.pack(fill="x")
        for value, label in card_data[:3]:
            card = ctk.CTkFrame(row1, fg_color="#fff", width=150, height=92, corner_radius=12)
            card.pack(side="left", padx=8, pady=0)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"), text_color="#222").pack(anchor="w", padx=16, pady=(16, 0))
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=13), text_color="#757575").pack(anchor="w", padx=16, pady=(0, 12))
            
        # Second row: 1 card on the left
        row2 = ctk.CTkFrame(stat_frame, fg_color="#F5F5F5")
        row2.pack(fill="x")
        card = ctk.CTkFrame(row2, fg_color="#fff", width=150, height=92, corner_radius=12)
        card.pack(side="left", padx=8, pady=8)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=card_data[3][0], font=ctk.CTkFont(size=22, weight="bold"), text_color="#222").pack(anchor="w", padx=16, pady=(16, 0))
        ctk.CTkLabel(card, text=card_data[3][1], font=ctk.CTkFont(size=13), text_color="#757575").pack(anchor="w", padx=16, pady=(0, 12))
        
        # Graph cards row
        graph_row = ctk.CTkFrame(self, fg_color="#F5F5F5")
        graph_row.pack(fill="both", expand=True, padx=24, pady=(24, 0))
        graph_row.grid_columnconfigure(0, weight=1)
        graph_row.grid_columnconfigure(1, weight=1)
        
        # Course Attendance Rate card
        graph1 = ctk.CTkFrame(graph_row, fg_color="#fff", corner_radius=12, border_width=1, border_color="#E5E7EB")
        graph1.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=0)
        ctk.CTkLabel(graph1, text="Course Attendance Rate", font=ctk.CTkFont(size=15, weight="bold"), text_color="#222").pack(anchor="w", padx=16, pady=(16, 0))
        ctk.CTkLabel(graph1, text="graph here", font=ctk.CTkFont(size=13), text_color="#757575", fg_color="#fff").pack(expand=True, fill="both", padx=16, pady=16)
        
        # Monthly Attendance card
        graph2 = ctk.CTkFrame(graph_row, fg_color="#fff", corner_radius=12, border_width=1, border_color="#E5E7EB")
        graph2.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=0)
        ctk.CTkLabel(graph2, text="Monthly Attendance", font=ctk.CTkFont(size=15, weight="bold"), text_color="#222").pack(anchor="w", padx=16, pady=(16, 0))
        ctk.CTkLabel(graph2, text="graph here", font=ctk.CTkFont(size=13), text_color="#757575", fg_color="#fff").pack(expand=True, fill="both", padx=16, pady=16)
