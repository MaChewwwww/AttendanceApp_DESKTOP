import customtkinter as ctk
from components.sidebar import Sidebar
from views.dashboard import DashboardView
from views.users import UsersView
from views.sections import SectionsView
from views.programs import ProgramsView

class AdminDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Admin Dashboard")
        self.geometry("1280x720")
        
        # Configure grid and set window background to match content
        self.configure(fg_color="#f5f5f5")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar with fixed width of 250px
        self.sidebar = Sidebar(self, self.switch_view, width=250)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Main content area with light gray background (#f5f5f5)
        self.content_frame = ctk.CTkFrame(
            self, 
            fg_color="#f5f5f5",
            corner_radius=0,
            border_width=0
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        
        # Initialize with dashboard view
        self.current_view = None
        self.switch_view("dashboard")
        
    def switch_view(self, view_name):
        # Clear current view
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Update current view
        self.current_view = view_name
        
        # Update sidebar active state
        self.sidebar.set_active(view_name)
        
        # Create new view based on selection
        if view_name == "dashboard":
            self.load_dashboard_view()
        elif view_name == "users":
            self.load_users_view()
        elif view_name == "sections":
            self.load_sections_view()
        elif view_name == "programs":
            self.load_programs_view()
        elif view_name == "logout":
            self.logout()
    
    def load_dashboard_view(self):
        view = DashboardView(self.content_frame)
        view.pack(fill="both", expand=True, padx=20, pady=20)
        
    def load_users_view(self):
        view = UsersView(self.content_frame)
        view.pack(fill="both", expand=True, padx=20, pady=20)
        
    def load_sections_view(self):
        view = SectionsView(self.content_frame)
        view.pack(fill="both", expand=True, padx=20, pady=20)
        
    def load_programs_view(self):
        view = ProgramsView(self.content_frame)
        view.pack(fill="both", expand=True, padx=20, pady=20)
        
    def logout(self):
        # Handle logout functionality
        self.quit()

if __name__ == "__main__":
    app = AdminDashboard()
    app.mainloop()