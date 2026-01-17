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
        self.audio_path = None
        self.use_ai_voice = False

        # Blender path selection frame
        blender_frame = ctk.CTkFrame(self)
        blender_frame.pack(pady=10, padx=10, fill="x")
        blender_label = ctk.CTkLabel(blender_frame, text="Blender Executable Path:")
        blender_label.pack(side="left", padx=10)
        self.blender_entry = ctk.CTkEntry(blender_frame, placeholder_text="Select blender.exe from USB")
        self.blender_entry.pack(side="left", padx=10, fill="x", expand=True)
        browse_button = ctk.CTkButton(blender_frame, text="Browse", command=self.browse_blender)
        browse_button.pack(side="right", padx=10)

        # Voice options frame
        voice_frame = ctk.CTkFrame(self)
        voice_frame.pack(pady=10, padx=10, fill="x")
        voice_label = ctk.CTkLabel(voice_frame, text="Voice Options:")
        voice_label.pack(side="left", padx=10)
        self.ai_voice_switch = ctk.CTkSwitch(voice_frame, text="AI Voice", command=self.toggle_ai_voice)
        self.ai_voice_switch.pack(side="left", padx=10)
        self.record_button = ctk.CTkButton(voice_frame, text="Record Voice", command=self.record_voice)
        self.record_button.pack(side="right", padx=10)

        # Asset selection frame
        asset_frame = ctk.CTkFrame(self)
        asset_frame.pack(pady=10, padx=10, fill="x")
        env_label = ctk.CTkLabel(asset_frame, text="Select Environment:")
        env_label.pack(side="left", padx=10)
        from blender.assets_manager import get_available_environments, get_available_characters
        self.env_combo = ctk.CTkComboBox(asset_frame, values=get_available_environments())
        self.env_combo.pack(side="left", padx=10)
        char_label = ctk.CTkLabel(asset_frame, text="Select Character:")
        char_label.pack(side="left", padx=10)
        self.char_combo = ctk.CTkComboBox(asset_frame, values=get_available_characters())
        self.char_combo.pack(side="left", padx=10)

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

    def toggle_ai_voice(self):
        self.use_ai_voice = self.ai_voice_switch.get()
        if self.use_ai_voice:
            self.record_button.pack_forget()
        else:
            self.record_button.pack(side="right", padx=10)

    def record_voice(self):
        from audio.voice_engine import VoiceEngine
        ve = VoiceEngine()
        self.audio_path = ve.record_voice()
        print(f"Voice recorded: {self.audio_path}")

    def generate(self):
        script = self.textbox.get("1.0", "end").strip()
        if not script or not self.blender_path:
            return
        if not self.use_ai_voice and self.audio_path is None:
            # Maybe show a message
            print("Please record voice or enable AI voice")
            return
        self.progress.set(0.2)
        # Import and call AI processor
        from ai.processor import process_script
        description = process_script(script)
        self.progress.set(0.5)
        if self.use_ai_voice:
            from audio.voice_engine import VoiceEngine
            ve = VoiceEngine()
            self.audio_path = ve.generate_ai_voice(script)
        # Import and call Blender scene generator
        from blender.scene_generator import render_scene
        env_name = self.env_combo.get()
        char_name = self.char_combo.get()
        output_file = render_scene(description, self.blender_path, self.audio_path, script, env_name, char_name)
        self.progress.set(1.0)