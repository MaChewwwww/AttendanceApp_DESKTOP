import customtkinter as ctk
from PIL import Image
import os
from tkinter import font
from datetime import datetime
import tkinter as tk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, switch_view_callback, **kwargs):
        # Remove border radius and border width for clean edges
        kwargs.update({"corner_radius": 0, "border_width": 0})
        super().__init__(master, **kwargs)

        self.load_inter_font()
        
        # Set the background color to blue
        self.configure(fg_color="#1E3A8A")  # A nice material blue color
        
        # Fixed width of 250px
        self.width = 250
        self.current_view = None  # Track current active view
        
        # Configure the containing frame to maintain width
        self.grid_propagate(False)
        
        # Load icons immediately but safely
        self.icons = {}
        self.load_icons()
        
        # Header with app title
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.header_frame.pack(fill="x", padx=10, pady=(20, 10))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Attendify", 
                                       font=ctk.CTkFont(size=20, weight="bold"),
                                       text_color="white")
        self.title_label.pack(side="left", padx=10)
        
        # Create a separator
        separator = ctk.CTkFrame(self, height=1, fg_color="#ffffff", corner_radius=0)
        separator.pack(fill="x", padx=10, pady=10)
        
        # Menu options with corresponding icons - Updated order
        menu_items = [
            {"name": "Dashboard", "view": "dashboard", "icon": self.icons.get("dashboard", "■")},
            {"name": "Programs", "view": "programs", "icon": self.icons.get("book_open", "■")},
            {"name": "Courses", "view": "courses", "icon": self.icons.get("graduation_cap", "■")},
            {"name": "Sections", "view": "sections", "icon": self.icons.get("folder", "■")},
            {"name": "Users", "view": "users", "icon": self.icons.get("users", "■")}
        ]
        
        # Menu buttons container
        self.menu_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.menu_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Define colors and fonts for buttons
        self.normal_font = ctk.CTkFont(family="Inter", size=14)
        self.bold_font = ctk.CTkFont(family="Inter", size=14, weight="bold")
        self.active_color = "#FFFFFF"  # White for active button
        self.active_text_color = "#1E3A8A"  # Blue text on white background
        
        # Create menu buttons with text icons
        self.menu_buttons = {}
        for item in menu_items:
            btn = ctk.CTkButton(
                self.menu_frame,
                text=f"{item['icon']}  {item['name']}",  # Combine icon and text
                anchor="w",
                fg_color="transparent",
                hover_color="#f5f5f5",
                text_color="white",
                height=40,
                corner_radius=0,
                command=lambda view=item["view"]: self.handle_view_switch(view, switch_view_callback)
            )
            btn.pack(fill="x", pady=5)
            btn._original_text = f"{item['icon']}  {item['name']}"  # Store original text with icon
            btn._icon = item['icon']  # Store just the icon
            btn._name = item['name']  # Store just the name
            self.menu_buttons[item["view"]] = btn
            
            # Update hover bindings with proper active state checking
            btn.bind("<Enter>", lambda event, b=btn, v=item["view"]: 
                 self.on_button_hover(b, v, True))
                 
            btn.bind("<Leave>", lambda event, b=btn, v=item["view"]: 
                 self.on_button_hover(b, v, False))

        # Create logout button at the bottom with icon
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        bottom_frame.pack(fill="x", side="bottom", padx=10, pady=20)
        
        self.logout_button = ctk.CTkButton(
            bottom_frame,
            text=f"{self.icons.get('logout', '■')}  Logout",  # Combine icon and text
            anchor="w",
            fg_color="#1E3A8A",
            hover_color="#F5F5F5",
            text_color="white",
            height=40,
            corner_radius=0,
            command=lambda: switch_view_callback("logout")
        )
        self.logout_button.pack(fill="x")
        
        # Update hover bindings for the logout button to keep text white
        self.logout_button.bind("<Enter>", lambda event: 
            self.logout_button.configure(text_color="white", font=self.bold_font))
        self.logout_button.bind("<Leave>", lambda event: 
            self.logout_button.configure(text_color="white", font=self.normal_font))
        
        # Set initial active view
        self.set_active("dashboard")

    def load_icons(self):
        """Load icons from assets folder - using dummy text icons for now"""
        try:
            print("Using dummy text icons")
            
            # Create simple text-based icons using Unicode symbols
            self.icons = {
                "dashboard": "📊",
                "users": "👥", 
                "graduation_cap": "🎓",
                "folder": "📁",
                "book_open": "📖",
                "logout": "🚪"
            }
            
            print("Successfully loaded dummy icons")
                    
        except Exception as e:
            print(f"Error in load_icons: {e}")
            # Fallback to simple text
            self.icons = {
                "dashboard": "■",
                "users": "■",
                "graduation_cap": "■",
                "folder": "■",
                "book_open": "■",
                "logout": "■"
            }

    def handle_view_switch(self, view, switch_view_callback):
        """Handle switching views and update active state"""
        if view != self.current_view:
            self.set_active(view)
            switch_view_callback(view)
    
    def set_active(self, view_name):
        """Set the active state for the selected view"""
        # Reset all buttons to inactive state
        for view, btn in self.menu_buttons.items():
            if view == view_name:
                # Set active button with 5px border radius and bold font
                btn.configure(
                    fg_color=self.active_color,
                    text_color="black",  # Text becomes black when active
                    font=self.bold_font,  # This makes the text bold
                    corner_radius=5
                )
            else:
                # Set inactive button with normal (non-bold) font
                btn.configure(
                    fg_color="transparent",
                    text_color="white", 
                    font=self.normal_font,
                    corner_radius=0
                )
    
        # Also ensure the logout button has normal font
        self.logout_button.configure(font=self.normal_font)
        
        self.current_view = view_name

    def on_button_hover(self, button, view, is_hover):
        """Handle hover state while respecting active state"""
        is_active = (view == self.current_view)
        
        if is_active:
            # Always keep active buttons with black text and bold font
            button.configure(
                text_color="black", 
                font=self.bold_font
            )
        else:
            # For inactive buttons, make bold on hover but keep text white
            if is_hover:
                button.configure(text_color="white", font=self.bold_font)
            else:
                button.configure(text_color="white", font=self.normal_font)

    def get_icon_name_for_view(self, view):
        """Helper method to get icon name for a view"""
        icon_mapping = {
            "dashboard": "dashboard",
            "users": "users",
            "courses": "graduation_cap",
            "sections": "folder",
            "programs": "book_open"
        }
        return icon_mapping.get(view, "dashboard")  # Default to dashboard if not found
    
    def load_inter_font(self):
        """Check if Inter font is available or add it from file"""
        try:
            available_fonts = font.families()
            
            # Check if Inter is already available in the system
            if "Inter" not in available_fonts:
                # Try to load Inter font from fonts directory
                try:
                    # Define the path to your Inter font files (adjust as needed)
                    font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")
                    
                    # Note: You'll need to ensure these files exist
                    # You can download Inter from https://fonts.google.com/specimen/Inter
                    font_paths = [
                        os.path.join(font_dir, "Inter-Regular.ttf"),
                        os.path.join(font_dir, "Inter-Bold.ttf")
                    ]
                    
                    for font_path in font_paths:
                        if os.path.exists(font_path):
                            font.families().append("Inter")
                            break
                except Exception as e:
                    print(f"Could not load Inter font: {e}")
                    print("Using system default font instead")
        except Exception as e:
            print(f"Font loading issue: {e}")

    def cleanup(self):
        """Clean up any pending animations or callbacks"""
        try:
            # Simply disable all interactive widgets to prevent new animations
            widgets_to_clean = list(self.menu_buttons.values()) + [self.logout_button]
            
            for widget in widgets_to_clean:
                if widget and widget.winfo_exists():
                    try:
                        # Set hover color to a solid color (not transparent)
                        widget.configure(hover_color="#1E3A8A")  # Use the sidebar color
                        
                        # Disable the widget to prevent interactions
                        widget.configure(state="disabled")
                        
                        # Unbind hover events
                        widget.unbind("<Enter>")
                        widget.unbind("<Leave>")
                        
                    except Exception as e:
                        # If individual widget cleanup fails, just disable it
                        try:
                            widget.configure(state="disabled")
                        except:
                            pass
                            
        except Exception as e:
            print(f"Error during sidebar cleanup: {e}")
    
    def destroy(self):
        """Override destroy to cleanup first"""
        try:
            self.cleanup()
        except:
            pass
        super().destroy()

class DateTimePill(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, fg_color="transparent", *args, **kwargs)
        self.configure(bg_color="transparent")
        self.build_ui()
        self.update_time()

    def build_ui(self):
        # Date/time pill
        self.pill = ctk.CTkFrame(
            self, fg_color="#fff", corner_radius=20,
            border_width=1, border_color="#D1D5DB"
        )
        self.pill.pack(side="left", padx=(0, 10), pady=5)

        self.date_label = ctk.CTkLabel(
            self.pill,
            text="",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color="#222"
        )
        self.date_label.pack(padx=16, pady=4)

        # Bell icon button (emoji)
        self.bell_btn = ctk.CTkButton(
            self,
            width=36, height=36,
            fg_color="#fff",
            corner_radius=18,
            text="🔔",
            font=ctk.CTkFont(size=18),
            hover_color="#E5E7EB",
            border_width=1,
            border_color="#D1D5DB"
        )
        self.bell_btn.pack(side="left", padx=(0, 10))

        # User icon button (emoji)
        self.user_btn = ctk.CTkButton(
            self,
            width=36, height=36,
            fg_color="#1E3A8A",
            corner_radius=18,
            text="👤",
            font=ctk.CTkFont(size=18),
            text_color="#fff",
            hover_color="#1E40AF"
        )
        self.user_btn.pack(side="left")

    def update_time(self):
        now = datetime.now()
        formatted = now.strftime("%B %#d, %Y  %#I:%M %p")
        self.date_label.configure(text=formatted)
        self.after(1000, self.update_time)