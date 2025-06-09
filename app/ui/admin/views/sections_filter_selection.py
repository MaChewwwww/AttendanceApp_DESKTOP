import customtkinter as ctk
import tkinter as tk
import winsound  # For Windows system sounds

class FilterPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_view = parent
        self.title("Filter Sections")
        self.geometry("400x600")  # Increased height for semester filter
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
            text="Filter Sections",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="black"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Filter options
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Get current filter values from parent
        current_filters = self.parent_view.current_filters
        
        # Academic Year filter (NEW)
        ctk.CTkLabel(filter_frame, text="Academic Year", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
        self.academic_year_var = tk.StringVar(value=current_filters.get('academic_year', 'All Years'))
        
        # Get available academic years from database
        academic_year_options = ["All Years"]
        try:
            if self.parent_view.db_manager:
                success, years = self.parent_view.db_manager.get_available_academic_years()
                if success and years:
                    academic_year_options.extend(years)
        except Exception as e:
            print(f"Error loading academic years: {e}")
            academic_year_options.extend(["2024-2025", "2023-2024"])
        
        academic_year_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=academic_year_options,
            variable=self.academic_year_var,
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222"
        )
        academic_year_menu.pack(fill="x", pady=(0, 15))
        
        # Semester filter (NEW)
        ctk.CTkLabel(filter_frame, text="Semester", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
        self.semester_var = tk.StringVar(value=current_filters.get('semester', 'All Semesters'))
        
        # Get available semesters from database
        semester_options = ["All Semesters"]
        try:
            if self.parent_view.db_manager:
                success, semesters = self.parent_view.db_manager.get_available_semesters()
                if success and semesters:
                    semester_options.extend(semesters)
        except Exception as e:
            print(f"Error loading semesters: {e}")
            semester_options.extend(["1st Semester", "2nd Semester", "Summer"])
        
        semester_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=semester_options,
            variable=self.semester_var,
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222"
        )
        semester_menu.pack(fill="x", pady=(0, 15))
        
        # Program filter - load from database
        ctk.CTkLabel(filter_frame, text="Program", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
        self.program_var = tk.StringVar(value=current_filters.get('program', 'All'))
        
        program_options = ["All"]
        try:
            if self.parent_view.db_manager:
                success, programs = self.parent_view.db_manager.get_available_programs()
                if success and programs:
                    program_options.extend(programs)
        except Exception as e:
            print(f"Error loading programs: {e}")
            program_options.extend(["BSIT", "BSCS", "BSIS"])
        
        program_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=program_options,
            variable=self.program_var,
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222"
        )
        program_menu.pack(fill="x", pady=(0, 15))
        
        # Year filter
        ctk.CTkLabel(filter_frame, text="Year", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
        self.year_var = tk.StringVar(value=current_filters.get('year', 'All'))
        year_options = ["All", "1st Year", "2nd Year", "3rd Year", "4th Year"]
        year_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=year_options,
            variable=self.year_var,
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222"
        )
        year_menu.pack(fill="x", pady=(0, 15))
        
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
        """Apply filters and update the parent view"""
        filter_values = {}
        
        # Academic year filter
        academic_year_value = self.academic_year_var.get().strip()
        if academic_year_value and academic_year_value != "All Years":
            filter_values['academic_year'] = academic_year_value
        
        # Semester filter
        semester_value = self.semester_var.get().strip()
        if semester_value and semester_value != "All Semesters":
            filter_values['semester'] = semester_value
        
        program_value = self.program_var.get().strip()
        if program_value and program_value != "All":
            filter_values['program'] = program_value
            
        year_value = self.year_var.get().strip()
        if year_value and year_value != "All":
            filter_values['year'] = year_value
        
        # Apply filters to parent view
        self.parent_view.apply_filters(filter_values)
        self.destroy()
    
    def reset_filters(self):
        """Reset all filters to default values"""
        self.academic_year_var.set("All Years")
        self.semester_var.set("All Semesters")
        self.program_var.set("All")
        self.year_var.set("All")
        
        # Apply reset filters
        self.parent_view.reset_filters()
        self.destroy()

class CautionModal(ctk.CTkToplevel):
    def __init__(self, parent, on_continue=None):
        super().__init__(parent)
        self.title("Caution")
        self.geometry("340x210")
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
        self._center_window(340, 210)
        self.setup_ui()

    def _center_window(self, width, height):
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        # Card frame for rounded corners, responsive
        card = ctk.CTkFrame(self, fg_color="#fff", corner_radius=16)
        card.pack(expand=True, fill="both", padx=16, pady=16)
        card.pack_propagate(True)
        
        # Draw yellow circle with exclamation mark
        canvas = tk.Canvas(card, width=56, height=56, bg="#fff", highlightthickness=0)
        canvas.create_oval(4, 4, 52, 52, outline="#FBBF24", width=3)
        canvas.create_text(28, 28, text="!", font=("Segoe UI", 28, "bold"), fill="#FBBF24")
        canvas.pack(pady=(8, 0))
        
        # Title
        ctk.CTkLabel(card, text="Caution", font=ctk.CTkFont(size=16, weight="bold"), text_color="#222", fg_color="#fff").pack(pady=(4, 0))
        
        # Subtitle
        ctk.CTkLabel(card, text="Do you want to make changes to this?", font=ctk.CTkFont(size=13), text_color="#888", fg_color="#fff").pack(pady=(0, 8))
        
        # Buttons
        btns_frame = ctk.CTkFrame(card, fg_color="#fff")
        btns_frame.pack(side="bottom", fill="x", pady=(0, 16), padx=0)
        
        ctk.CTkButton(
            btns_frame,
            text="Cancel",
            fg_color="#D1D5DB",
            text_color="#444",
            hover_color="#BDBDBD",
            height=38,
            corner_radius=8,
            command=self.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))
        
        ctk.CTkButton(
            btns_frame,
            text="Continue",
            fg_color="#FBBF24",
            text_color="#fff",
            hover_color="#f59e1b",
            height=38,
            corner_radius=8,
            command=self.show_success_modal
        ).pack(side="left", expand=True, fill="x", padx=(8, 0))

    def show_success_modal(self):
        SuccessModal(self)


class SuccessModal(ctk.CTkToplevel):
    def __init__(self, parent, on_continue=None):
        super().__init__(parent)
        self.title("Success")
        self.geometry("340x210")
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
        
        # Play success sound
        self.play_success_sound()
        
        # Properly center the window on the actual screen
        self.update_idletasks()  # Ensure window is fully created
        self._center_window_on_screen()
        
        self._parent_modal = parent
        self.setup_ui()

    def play_success_sound(self):
        """Play a success sound notification"""
        try:
            # Use Windows system sound for success/information
            winsound.MessageBeep(winsound.MB_OK)
        except Exception as e:
            print(f"Could not play sound: {e}")
            # Fallback: try system bell
            try:
                self.bell()
            except:
                pass  # Silent fallback if no sound is available

    def _center_window_on_screen(self):
        """Center the window on the actual screen, not relative to parent"""
        # Wait for window to be fully created
        self.update_idletasks()
        
        # Get actual screen dimensions (not parent window dimensions)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Get window dimensions
        window_width = 340
        window_height = 210
        
        # Calculate absolute center position on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set absolute position on screen using +x+y format
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Force window to be on top and centered
        self.lift()
        self.focus_force()

    def setup_ui(self):
        # Card frame for rounded corners, responsive and matching other modals
        card = ctk.CTkFrame(self, fg_color="#fff", corner_radius=16)
        card.pack(expand=True, fill="both", padx=16, pady=16)
        card.pack_propagate(True)
        
        # Draw green circle with checkmark
        canvas = tk.Canvas(card, width=56, height=56, bg="#fff", highlightthickness=0)
        canvas.create_oval(4, 4, 52, 52, outline="#22C55E", width=3)
        # Draw checkmark
        canvas.create_line(18, 32, 27, 42, 40, 18, fill="#22C55E", width=4, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        canvas.pack(pady=(8, 0))
        
        # Title
        ctk.CTkLabel(card, text="Success!", font=ctk.CTkFont(size=16, weight="bold"), text_color="#222", fg_color="#fff").pack(pady=(4, 0))
        
        # Subtitle
        ctk.CTkLabel(card, text="Action is done successfully.", font=ctk.CTkFont(size=13), text_color="#888", fg_color="#fff").pack(pady=(0, 8))
        
        # Responsive Continue button (full width, bottom, fixed height)
        btns_frame = ctk.CTkFrame(card, fg_color="#fff", height=38)
        btns_frame.pack(side="bottom", fill="x", pady=(0, 16), padx=0)
        btns_frame.pack_propagate(False)
        
        ctk.CTkButton(
            btns_frame,
            text="Continue",
            fg_color="#22C55E",
            text_color="#fff",
            hover_color="#16a34a",
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=8,
            command=self._close_all
        ).pack(expand=True, fill="both", padx=0)

    def _close_all(self):
        self.destroy()
        try:
            self._parent_modal.destroy()
        except Exception:
            pass


class FacialRecognitionPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Facial Recognition")
        self.geometry("454x450")
        self.resizable(False, False)
        self.configure(fg_color="#222222")
        self.minsize(454, 450)
        self.maxsize(454, 450)
        self.transient(parent)
        self.grab_set()
        # Center the window
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 454) // 2
        y = (screen_height - 450) // 2
        self.geometry(f"454x450+{x}+{y}")
        self.update()
        self._create_verification_dialog_content()

    def _create_verification_dialog_content(self):
        """Create content for the face verification dialog (as main popup content)"""
        import tkinter.messagebox as messagebox
        # Card Frame with explicit sizing
        card = ctk.CTkFrame(
            self, 
            width=454, 
            height=450, 
            corner_radius=12, 
            fg_color="#ffffff", 
            border_width=0
        )
        card.place(x=0, y=0)
        card.pack_propagate(False)
        card.grid_propagate(False)

        # Info icon (top right)
        info_btn = ctk.CTkButton(
            card, 
            text="i", 
            width=24, 
            height=24, 
            corner_radius=12, 
            fg_color="#f5f5f5", 
            text_color="#222", 
            font=ctk.CTkFont("Roboto", 14, "bold"), 
            hover_color="#e0e0e0", 
            command=lambda: messagebox.showinfo("Info", "Please ensure you're in a well-lit environment before capturing your photo for the best image quality", parent=self)
        )
        info_btn.place(x=420, y=10)

        # Camera Preview Frame with explicit sizing
        self.face_preview_frame = ctk.CTkFrame(
            card, 
            width=410, 
            height=240, 
            fg_color="#fafafa", 
            border_width=1, 
            border_color="#d1d1d1"
        )
        self.face_preview_frame.place(x=22, y=38)
        self.face_preview_frame.pack_propagate(False)
        self.face_preview_frame.grid_propagate(False)

        # Default Preview Label (centered)
        self.preview_label = ctk.CTkLabel(
            self.face_preview_frame,
            text="Camera will appear here\nClick 'Open Camera' to begin",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#a0a0a0"
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Open Camera Button with explicit sizing
        self.camera_button = ctk.CTkButton(
            card,
            text="Open Camera",
            width=410,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont("Roboto", 13, "bold"),
            fg_color="#ffffff",
            text_color="#222",
            border_width=1,
            border_color="#d1d1d1",
            hover_color="#f5f5f5",
            command=self.toggle_camera if hasattr(self, 'toggle_camera') else None
        )
        self.camera_button.place(x=22, y=290)

        # Retake and Capture Buttons with explicit sizing
        self.retake_button = ctk.CTkButton(
            card,
            text="Retake",
            width=200,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 13, "bold"),
            fg_color="#e5e5e5",
            text_color="#707070",
            border_width=0,
            hover_color="#cccccc",
            state="disabled",
            command=self.retake_photo if hasattr(self, 'retake_photo') else None
        )
        self.retake_button.place(x=22, y=335)

        self.capture_button = ctk.CTkButton(
            card,
            text="Capture",
            width=200,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 13, "bold"),
            fg_color="#1E3A8A",
            text_color="#fff",
            border_width=0,
            hover_color="#152a63",
            state="disabled",
            command=self.capture_face if hasattr(self, 'capture_face') else None
        )
        self.capture_button.place(x=232, y=335)

        # Register Button with explicit sizing
        self.register_button = ctk.CTkButton(
            card,
            text="Next",
            width=410,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 13, "bold"),
            fg_color="#1E3A8A",
            text_color="#fff",
            border_width=0,
            hover_color="#152a63",
            command=self.complete_registration if hasattr(self, 'complete_registration') else None,
            state="disabled"
        )
        self.register_button.place(x=22, y=385)
