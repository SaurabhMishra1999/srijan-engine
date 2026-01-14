from tkinter import filedialog
import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Srijan Engine")
        self.geometry("1200x800")  # Optimized for 8GB RAM with larger window
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")  # Hacker-style green theme

        self.blender_path = ""

        # Blender path selection frame
        blender_frame = ctk.CTkFrame(self)
        blender_frame.pack(pady=10, padx=10, fill="x")
        blender_label = ctk.CTkLabel(blender_frame, text="Blender Executable Path:")
        blender_label.pack(side="left", padx=10)
        self.blender_entry = ctk.CTkEntry(blender_frame, placeholder_text="Select blender.exe from USB")
        self.blender_entry.pack(side="left", padx=10, fill="x", expand=True)
        browse_button = ctk.CTkButton(blender_frame, text="Browse", command=self.browse_blender)
        browse_button.pack(side="right", padx=10)

        # Movie Script text area
        script_label = ctk.CTkLabel(self, text="Movie Script", font=("Courier", 16))
        script_label.pack(pady=10)
        self.textbox = ctk.CTkTextbox(self, font=("Courier", 12))
        self.textbox.pack(pady=10, padx=20, fill="both", expand=True)

        # Progress bar
        self.progress = ctk.CTkProgressBar(self, mode="determinate")
        self.progress.pack(pady=10, padx=20, fill="x")
        self.progress.set(0)

        # Big orange SRIJAN MAGIC button
        self.magic_button = ctk.CTkButton(self, text="SRIJAN MAGIC", fg_color="orange", font=("Arial", 20, "bold"), height=60, command=self.generate)
        self.magic_button.pack(pady=20)

    def browse_blender(self):
        path = filedialog.askopenfilename(title="Select Blender Executable", filetypes=[("Executable", "*.exe")])
        if path:
            self.blender_entry.delete(0, "end")
            self.blender_entry.insert(0, path)
            self.blender_path = path

    def generate(self):
        script = self.textbox.get("1.0", "end").strip()
        if not script or not self.blender_path:
            return
        self.progress.set(0.2)
        # Import and call AI processor
        from ai.processor import process_script
        description = process_script(script)
        self.progress.set(0.5)
        # Import and call Blender scene generator
        from blender.scene_generator import render_scene
        output_file = render_scene(description, self.blender_path)
        self.progress.set(1.0)