import customtkinter as ctk
from PIL import Image
import os
from tkinter import font
from datetime import datetime
import tkinter as tk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, switch_view_callback, **kwargs):
        kwargs.update({"corner_radius": 0, "border_width": 0})
        super().__init__(master, **kwargs)
        self._switch_view_callback = switch_view_callback
        
        # Define fonts and colors
        self.normal_font = ctk.CTkFont(family="Inter", size=14)
        self.bold_font = ctk.CTkFont(family="Inter", size=14, weight="bold")
        self.active_color = "#FFFFFF"
        
        self.load_inter_font()
        self.configure(fg_color="#1E3A8A")
        self.width = 250
        self.current_view = None
        self.grid_propagate(False)
        
        # Initialize storage for icons and button references
        self.icon_images = {}  # Store the PIL Image objects
        self.icons = {}        # Store the CTkImage objects
        self.buttons = {}      # Store button references
        
        # Load all icons first
        self._load_icons()
        
        # Header with app title and logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons", "white-logo.png")
        if os.path.exists(logo_path):
            logo_img = ctk.CTkImage(light_image=Image.open(logo_path), dark_image=Image.open(logo_path), size=(48, 48))
        else:
            logo_img = None
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.header_frame.pack(fill="x", padx=10, pady=(20, 10))
        # Logo and text in a row
        logo_label = ctk.CTkLabel(self.header_frame, image=logo_img, text="", width=52)
        logo_label.pack(side="left", padx=(0, 8), pady=0)
        text_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="y")
        self.title_label = ctk.CTkLabel(text_frame, text="Attendify", font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
        self.title_label.pack(anchor="w")
        self.subtitle_label = ctk.CTkLabel(text_frame, text="Admin", font=ctk.CTkFont(size=15, weight="normal"), text_color="#D1D5DB")
        self.subtitle_label.pack(anchor="w", pady=(0, 0))
        
        # Create separator
        separator = ctk.CTkFrame(self, height=1, fg_color="#ffffff", corner_radius=0)
        separator.pack(fill="x", padx=10, pady=10)
        
        # Menu frame
        self.menu_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.menu_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create menu items with explicit icon keys
        menu_items = [
            {"name": "Dashboard", "view": "dashboard", "icon_key": "dashboard", "icon_active_key": "dashboard_active"},
            {"name": "Programs", "view": "programs", "icon_key": "book_open", "icon_active_key": "book_open_active"},
            {"name": "Courses", "view": "courses", "icon_key": "graduation_cap", "icon_active_key": "graduation_cap_active"},
            {"name": "Sections", "view": "sections", "icon_key": "folder", "icon_active_key": "folder_active"},
            {"name": "Users", "view": "users", "icon_key": "users", "icon_active_key": "users_active"}
        ]
        
        # Create menu buttons
        for item in menu_items:
            self._create_menu_button(item)
            
        # Bottom frame for logout
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        bottom_frame.pack(fill="x", side="bottom", padx=10, pady=20)
        
        # Create logout button
        self._create_logout_button(bottom_frame, switch_view_callback)
        
        # Set initial active view
        self.set_active("dashboard")
        
    def _create_menu_button(self, item):
        icon = self.icons.get(item["icon_key"])
        btn = ctk.CTkButton(
            self.menu_frame,
            text=f"  {item['name']}",
            image=icon,
            compound="left",
            anchor="w",
            fg_color="transparent",
            hover_color="#f5f5f5",
            text_color="white",
            height=40,
            corner_radius=0,
            command=lambda view=item["view"]: self.handle_view_switch(view, self._switch_view_callback)
        )
        btn.pack(fill="x", pady=5)
        
        # Store button reference with its associated data
        self.buttons[item["view"]] = {
            "button": btn,
            "icon_key": item["icon_key"],
            "icon_active_key": item["icon_active_key"],
            "name": item["name"]
        }
        
        # Bind hover events
        btn.bind("<Enter>", lambda e, v=item["view"]: self.on_button_hover(v, True))
        btn.bind("<Leave>", lambda e, v=item["view"]: self.on_button_hover(v, False))
        
    def _create_logout_button(self, parent_frame, callback):
        logout_icon = self.icons.get("logout")
        self.logout_button = ctk.CTkButton(
            parent_frame,
            text="  Logout",
            image=logout_icon,
            compound="left",
            anchor="w",
            fg_color="#1E3A8A",
            hover_color="#F5F5F5",
            text_color="white",
            height=40,
            corner_radius=0,
            command=lambda: callback("logout")
        )
        self.logout_button.pack(fill="x")
        
        # Use the same hover system as other navigation items
        self.logout_button.bind("<Enter>", lambda event: 
            self.on_button_hover("logout", True))
        self.logout_button.bind("<Leave>", lambda event: 
            self.on_button_hover("logout", False))
        
        # Store logout button reference
        self.buttons["logout"] = {
            "button": self.logout_button,
            "icon": logout_icon,
            "name": "Logout"
        }
        
    def _load_icons(self):
        """Load icons from assets directory, including active variants"""
        try:
            current_file = os.path.abspath(__file__)
            components_dir = os.path.dirname(current_file)
            admin_dir = os.path.dirname(components_dir)
            icons_dir = os.path.join(admin_dir, "assets", "icons")
            # Icon file mapping (default and active)
            icon_files = {
                "dashboard": "bar-chart-3.png",
                "dashboard_active": "bar-chart-3-active.png",
                "users": "users.png",
                "users_active": "users-active.png",
                "graduation_cap": "graduation-cap.png",
                "graduation_cap_active": "graduation-cap-active.png",
                "folder": "folder.png",
                "folder_active": "folder-active.png",
                "book_open": "book-open.png",
                "book_open_active": "book-open-active.png",
                "logout": "log-out.png"
            }
            for key, filename in icon_files.items():
                icon_path = os.path.join(icons_dir, filename)
                if os.path.exists(icon_path):
                    self.icon_images[key] = Image.open(icon_path)
                    self.icons[key] = ctk.CTkImage(
                        light_image=self.icon_images[key],
                        dark_image=self.icon_images[key],
                        size=(20, 20)
                    )
                else:
                    self.icons[key] = None
                    self.icon_images[key] = None
        except Exception as e:
            print(f"Error loading icons: {e}")
            for k in [
                "dashboard", "dashboard_active", "users", "users_active",
                "graduation_cap", "graduation_cap_active", "folder", "folder_active",
                "book_open", "book_open_active", "logout"
            ]:
                self.icons[k] = None
                self.icon_images[k] = None

    def handle_view_switch(self, view, callback):
        """Handle switching between views"""
        if view != self.current_view:
            self.set_active(view)
            callback(view)
            
    def set_active(self, view_name):
        """Set the active state of a button and update icons"""
        for view, data in self.buttons.items():
            button = data["button"]
            icon_key = data.get("icon_key", view)
            icon_active_key = data.get("icon_active_key", f"{view}_active")
            # Always set the icon, fallback to default if active icon is missing
            if view == view_name:
                icon = self.icons.get(icon_active_key) or self.icons.get(icon_key)
                button.configure(
                    fg_color="#ffffff",
                    text_color="#1E3A8A",
                    font=self.bold_font,
                    corner_radius=5,
                    image=icon
                )
            else:
                icon = self.icons.get(icon_key)
                button.configure(
                    fg_color="transparent",
                    text_color="white",
                    font=self.normal_font,
                    corner_radius=0,
                    image=icon
                )
        self.current_view = view_name
        
    def on_button_hover(self, view, is_hover):
        """Handle button hover states"""
        if view in self.buttons:
            button = self.buttons[view]["button"]
            is_active = (view == self.current_view)
            
            if is_active:
                button.configure(
                    text_color="black",
                    font=self.bold_font
                )
            else:
                if is_hover:
                    button.configure(text_color="white", font=self.bold_font)
                else:
                    button.configure(text_color="white", font=self.normal_font)

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
            widgets_to_clean = list(self.buttons.values()) + [self.logout_button]
            
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