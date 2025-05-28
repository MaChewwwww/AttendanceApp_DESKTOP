import customtkinter as ctk
from PIL import Image, ImageTk
import os
from tkinter import font

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
        self.collapsed_width = 50  
        self.is_collapsed = False
        self.current_view = None  # Track current active view
        
        # Configure the containing frame to maintain width
        self.grid_propagate(False)
        # self.configure(width=self.width)  # Remove fixed width configuration
        
        # Load all icons
        self.load_icons()
        
        # Header with app title
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.header_frame.pack(fill="x", padx=10, pady=(20, 10))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Iskoptrix", 
                                       font=ctk.CTkFont(size=20, weight="bold"),
                                       text_color="white")
        self.title_label.pack(side="left", padx=10)
        
        # Toggle button for sidebar collapse using backBtn icon
        self.toggle_button = ctk.CTkButton(self.header_frame, text="", width=30, 
                                          image=self.icons["back_btn"],  # Use back button icon
                                          fg_color="transparent", 
                                          hover_color="#1976D2",
                                          corner_radius=0, 
                                          text_color="white", 
                                          command=self.toggle_sidebar)
        self.toggle_button.pack(side="right")
        
        # Create a separator
        separator = ctk.CTkFrame(self, height=1, fg_color="#ffffff", corner_radius=0)
        separator.pack(fill="x", padx=10, pady=10)
        
        # Menu options with corresponding icons
        menu_items = [
            {"name": "Dashboard", "view": "dashboard", "icon": self.icons["dashboard"]},
            {"name": "Users", "view": "users", "icon": self.icons["users"]},
            {"name": "Courses", "view": "courses", "icon": self.icons["graduation_cap"]},
            {"name": "Sections", "view": "sections", "icon": self.icons["folder"]},
            {"name": "Programs", "view": "programs", "icon": self.icons["book_open"]}
        ]
        
        # Menu buttons container
        self.menu_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.menu_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Define colors and fonts for buttons
        self.normal_font = ctk.CTkFont(family="Inter", size=14)
        self.bold_font = ctk.CTkFont(family="Inter", size=14, weight="bold")
        self.active_color = "#FFFFFF"  # White for active button
        self.active_text_color = "#1E3A8A"  # Blue text on white background
        
        # Create menu buttons
        self.menu_buttons = {}
        for item in menu_items:
            btn = ctk.CTkButton(
                self.menu_frame,
                text=item["name"],
                image=item["icon"],
                anchor="w",
                fg_color="transparent",
                hover_color="#f5f5f5",
                text_color="white",
                height=40,
                corner_radius=0,
                compound="left",  # Place icon to the left of text
                command=lambda view=item["view"]: self.handle_view_switch(view, switch_view_callback)
            )
            btn.pack(fill="x", pady=5)
            btn._original_text = item["name"]  # Store original text
            self.menu_buttons[item["view"]] = btn
            
            # Update hover bindings with proper active state checking
            btn.bind("<Enter>", lambda event, b=btn, v=item["view"]: 
                 self.on_button_hover(b, v, True))
                 
            btn.bind("<Leave>", lambda event, b=btn, v=item["view"]: 
                 self.on_button_hover(b, v, False))

        # Create logout button at the bottom
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        bottom_frame.pack(fill="x", side="bottom", padx=10, pady=20)
        
        self.logout_button = ctk.CTkButton(
            bottom_frame,
            text="Logout",
            image=self.icons["logout"],
            anchor="w",
            fg_color="#1E3A8A",
            hover_color="#F5F5F5",
            text_color="white",
            height=40,
            corner_radius=0,
            compound="left",  # Place icon to the left of text
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
        """Load icons from assets folder"""
        # Path to the icons directory
        icon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons")
        
        # Define icon size
        icon_size = (20, 20)
        
        self.icons = {}
        
        # Define icon paths and names
        icon_files = {
            "dashboard": "bar-chart-3.png",
            "users": "users.png",
            "graduation_cap": "graduation-cap.png", 
            "folder": "folder.png",
            "book_open": "book-open.png",
            "logout": "log-out.png",
            "back_btn": "backBtn.png"  # Add the backBtn to your icons
        }
        
        # Load each icon
        for name, file in icon_files.items():
            try:
                icon_path = os.path.join(icon_dir, file)
                if os.path.exists(icon_path):
                    # Load and resize icon for normal state
                    icon_image = Image.open(icon_path).resize(icon_size)
                    
                    # Make sure back_btn icon is white
                    if name == "dashboard" or name == "back_btn":
                        # Process image to make sure it's white
                        # Convert to RGBA if not already
                        if icon_image.mode != 'RGBA':
                            icon_image = icon_image.convert('RGBA')
                        
                        # Create a white version of the image
                        data = icon_image.getdata()
                        new_data = []
                        for item in data:
                            # Change all non-transparent pixels to white
                            if item[3] > 0:  # If not completely transparent
                                new_data.append((255, 255, 255, item[3]))  # White with original alpha
                            else:
                                new_data.append(item)
                        
                        icon_image.putdata(new_data)
                    
                    self.icons[name] = ctk.CTkImage(light_image=icon_image, 
                                                  dark_image=icon_image,
                                                  size=icon_size)
                else:
                    print(f"Icon file not found: {icon_path}")
                    self.icons[name] = None
            except Exception as e:
                print(f"Error loading icon {name}: {e}")
                self.icons[name] = None

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
                
                # Get the icon name for this view
                icon_name = None
                for item in [
                    {"view": "dashboard", "icon": "dashboard"},
                    {"view": "users", "icon": "users"},
                    {"view": "courses", "icon": "graduation_cap"},
                    {"view": "sections", "icon": "folder"},
                    {"view": "programs", "icon": "book_open"}
                ]:
                    if item["view"] == view:
                        icon_name = item["icon"]
                        break
                
                # If we found the icon name, create a black version
                if icon_name:
                    # Get the original icon path
                    icon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons")
                    icon_file = None
                    if icon_name == "dashboard": icon_file = "bar-chart-3.png"
                    elif icon_name == "users": icon_file = "users.png"
                    elif icon_name == "graduation_cap": icon_file = "graduation-cap.png"
                    elif icon_name == "folder": icon_file = "folder.png"
                    elif icon_name == "book_open": icon_file = "book-open.png"
                    
                    if icon_file:
                        try:
                            icon_path = os.path.join(icon_dir, icon_file)
                            if os.path.exists(icon_path):
                                # Create a black version of the icon
                                icon_image = Image.open(icon_path).resize((20, 20))
                                
                                # Convert to RGBA if not already
                                if icon_image.mode != 'RGBA':
                                    icon_image = icon_image.convert('RGBA')
                                
                                # Create a black version
                                data = icon_image.getdata()
                                new_data = []
                                for item in data:
                                    # Change all non-transparent pixels to black
                                    if item[3] > 0:  # If not completely transparent
                                        new_data.append((0, 0, 0, item[3]))  # Black with original alpha
                                    else:
                                        new_data.append(item)
                                
                                icon_image.putdata(new_data)
                                
                                # Update the button's icon
                                black_icon = ctk.CTkImage(light_image=icon_image,
                                                        dark_image=icon_image,
                                                        size=(20, 20))
                                btn.configure(image=black_icon)
                        except Exception as e:
                            print(f"Error creating black icon: {e}")
            else:
                # Set inactive button with normal (non-bold) font
                btn.configure(
                    fg_color="transparent",
                    text_color="white", 
                    font=self.normal_font,  # This ensures non-active buttons use normal font
                    corner_radius=0,
                    image=self.icons[self.get_icon_name_for_view(view)]  # Reset to white icon
                )
    
        # Also ensure the logout button has normal font (not bold) since it's not selectable
        # as a view in the same way as other menu items
        self.logout_button.configure(font=self.normal_font)
        
        self.current_view = view_name

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

    def toggle_sidebar(self):
        if self.is_collapsed:
            # Expand sidebar
            self.configure(width=self.width)
            self.title_label.pack(side="left", padx=10)
            for btn in self.menu_buttons.values():
                btn.configure(text=btn._original_text)
            self.logout_button.configure(text="Logout") 
            self.toggle_button.configure(image=self.icons["back_btn"])
        else:
            # Collapse sidebar
            self.configure(width=self.collapsed_width)
            self.title_label.pack_forget()
            for btn in self.menu_buttons.values():
                btn.configure(text="")
            self.logout_button.configure(text="")  

            try:
                back_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                             "assets", "icons", "backBtn.png")
                if os.path.exists(back_icon_path):
                    icon_image = Image.open(back_icon_path).resize((20, 20))
                  
                    icon_image = icon_image.transpose(Image.FLIP_LEFT_RIGHT)
                   
                    if icon_image.mode != 'RGBA':
                        icon_image = icon_image.convert('RGBA')
                    data = icon_image.getdata()
                    new_data = []
                    for item in data:
                        if item[3] > 0:
                            new_data.append((255, 255, 255, item[3]))
                        else:
                            new_data.append(item)
                    icon_image.putdata(new_data)
                    rotated_icon = ctk.CTkImage(light_image=icon_image, 
                                              dark_image=icon_image,
                                              size=(20, 20))
                    self.toggle_button.configure(image=rotated_icon)
            except Exception as e:
                print(f"Error rotating icon: {e}")
        self.is_collapsed = not self.is_collapsed

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