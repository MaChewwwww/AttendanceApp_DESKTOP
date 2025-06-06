import customtkinter as ctk

class EditProgramPopup(ctk.CTkToplevel):
    def __init__(self, parent, program_data=None):
        super().__init__(parent)
        self.program_data = program_data or {}
        self.title("Update Program")
        self.geometry("320x450")
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
        self.name_var = ctk.StringVar(value=self.program_data.get('name', ''))
        ctk.CTkEntry(self, textvariable=self.name_var, fg_color="#fff", border_color="#BDBDBD", border_width=1, text_color="#222", font=ctk.CTkFont(size=13), height=36).pack(anchor="w", padx=24, pady=(0, 10), fill="x")

        # Row for Acronym and Code (side by side)
        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.pack(fill="x", padx=24, pady=(0, 10))

        # Column for Acronym
        acronym_col = ctk.CTkFrame(row1, fg_color="transparent")
        acronym_col.pack(side="left", padx=(0, 10), anchor="n")

        ctk.CTkLabel(acronym_col, text="Acronym", font=ctk.CTkFont(size=13, weight="bold"), text_color="#222").pack(anchor="w", pady=(0, 2))
        self.acronym_var = ctk.StringVar(value=self.program_data.get('acronym', ''))
        ctk.CTkEntry(acronym_col, textvariable=self.acronym_var, fg_color="#fff", border_color="#BDBDBD", border_width=1, text_color="#222", font=ctk.CTkFont(size=13), width=120, height=36).pack(anchor="w")

        # Column for Code
        code_col = ctk.CTkFrame(row1, fg_color="transparent")
        code_col.pack(side="left", anchor="n")

        ctk.CTkLabel(code_col, text="Code", font=ctk.CTkFont(size=13, weight="bold"), text_color="#222").pack(anchor="w", pady=(0, 2))
        self.code_var = ctk.StringVar(value=self.program_data.get('code', ''))
        ctk.CTkEntry(code_col, textvariable=self.code_var, fg_color="#fff", border_color="#BDBDBD", border_width=1, text_color="#222", font=ctk.CTkFont(size=13), width=120, height=36).pack(anchor="w")

        # Description
        ctk.CTkLabel(self, text="Description", font=ctk.CTkFont(size=13, weight="bold"), text_color="#222").pack(anchor="w", padx=24, pady=(0, 2))
        description_entry = ctk.CTkTextbox(self, fg_color="#fff", border_color="#BDBDBD", border_width=1, text_color="#222", font=ctk.CTkFont(size=13), height=80)
        description_entry.pack(anchor="w", padx=24, pady=(0, 18), fill="x")
        description_entry.insert("1.0", self.program_data.get('description', ''))
        self.description_textbox = description_entry

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

        update_btn = ctk.CTkButton(
            button_frame,
            text="Update",
            fg_color="#1E3A8A",
            hover_color="#1D4ED8",
            text_color="#fff",
            width=120,
            height=36,
            command=self.update_program
        )
        update_btn.pack(side="right", padx=(8, 0))

    def update_program(self):
        # TODO: Implement update logic
        # Get values from form
        name = self.name_var.get()
        acronym = self.acronym_var.get()
        code = self.code_var.get()
        description = self.description_textbox.get("1.0", "end-1c")
        
        # Validate required fields
        if not name or not acronym or not code:
            # TODO: Show error message
            return
        
        # TODO: Call backend service to update program
        print(f"Updating program: {name} ({acronym}) - {code}")
        
        self.destroy()
