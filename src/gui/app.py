from tkinter import filedialog
import customtkinter as ctk

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Srijan Engine")
        self.geometry("1200x800")  # Optimized for 8GB RAM with larger window
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")  # Hacker-style green theme

        # Hardware check
        from engine.core import check_hardware_compatibility
        check_hardware_compatibility()

        self.blender_path = ""
        self.audio_path = None
        self.use_ai_voice = False
        self.enable_bgm = False
        self.voice_volume = 1.0
        self.bgm_volume = 0.3

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
        self.bgm_switch = ctk.CTkSwitch(voice_frame, text="Enable Background Music", command=self.toggle_bgm)
        self.bgm_switch.pack(side="left", padx=10)
        self.record_button = ctk.CTkButton(voice_frame, text="Record Voice", command=self.record_voice)
        self.record_button.pack(side="right", padx=10)

        # Audio mixing frame
        mixing_frame = ctk.CTkFrame(self)
        mixing_frame.pack(pady=10, padx=10, fill="x")
        mixing_label = ctk.CTkLabel(mixing_frame, text="Audio Mixing:")
        mixing_label.pack(side="left", padx=10)
        voice_vol_label = ctk.CTkLabel(mixing_frame, text="Voice Volume")
        voice_vol_label.pack(side="left", padx=5)
        self.voice_slider = ctk.CTkSlider(mixing_frame, from_=0.0, to=2.0, command=self.set_voice_volume)
        self.voice_slider.set(1.0)
        self.voice_slider.pack(side="left", padx=5)
        bgm_vol_label = ctk.CTkLabel(mixing_frame, text="BGM Volume")
        bgm_vol_label.pack(side="left", padx=5)
        self.bgm_slider = ctk.CTkSlider(mixing_frame, from_=0.0, to=2.0, command=self.set_bgm_volume)
        self.bgm_slider.set(0.3)
        self.bgm_slider.pack(side="left", padx=5)

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

        # Motion Capture frame
        mocap_frame = ctk.CTkFrame(self)
        mocap_frame.pack(pady=10, padx=10, fill="x")
        mocap_label = ctk.CTkLabel(mocap_frame, text="Motion Capture:")
        mocap_label.pack(side="left", padx=10)
        self.mocap_button = ctk.CTkButton(mocap_frame, text="Start MoCap", command=self.start_mocap)
        self.mocap_button.pack(side="left", padx=10)
        self.motion_capture_path = None

        # Scene List panel
        scene_list_frame = ctk.CTkFrame(self)
        scene_list_frame.pack(pady=10, padx=20, fill="x")
        scene_list_label = ctk.CTkLabel(scene_list_frame, text="Scene List", font=("Courier", 16))
        scene_list_label.pack(pady=5)
        self.scenes_frame = ctk.CTkScrollableFrame(scene_list_frame, height=200)
        self.scenes_frame.pack(pady=5, padx=10, fill="x")
        self.scenes = []
        add_scene_button = ctk.CTkButton(scene_list_frame, text="Add Scene", command=self.add_scene)
        add_scene_button.pack(pady=5)

        # Progress bar
        self.progress = ctk.CTkProgressBar(self, mode="determinate")
        self.progress.pack(pady=10, padx=20, fill="x")
        self.progress.set(0)

        # Hacker-style terminal logs
        terminal_frame = ctk.CTkFrame(self)
        terminal_frame.pack(pady=10, padx=20, fill="x")
        terminal_label = ctk.CTkLabel(terminal_frame, text="Rendering Logs", font=("Courier", 12))
        terminal_label.pack(pady=5)
        self.log_textbox = ctk.CTkTextbox(terminal_frame, font=("Courier", 10), fg_color="black", text_color="green", height=150)
        self.log_textbox.pack(pady=5, padx=10, fill="x")
        self.log_textbox.insert("0.0", "Srijan Engine initialized...\n")

        # Preview and Generate buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)
        self.preview_button = ctk.CTkButton(button_frame, text="Preview Scene", fg_color="blue", font=("Arial", 16), command=self.preview)
        self.preview_button.pack(side="left", padx=10)
        self.generate_button = ctk.CTkButton(button_frame, text="Generate Single Scene", fg_color="orange", font=("Arial", 16), command=self.generate)
        self.generate_button.pack(side="left", padx=10)
        self.compile_button = ctk.CTkButton(button_frame, text="Compile Full Movie", fg_color="green", font=("Arial", 18, "bold"), command=self.compile_movie)
        self.compile_button.pack(side="right", padx=10)

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

    def toggle_bgm(self):
        self.enable_bgm = self.bgm_switch.get()

    def set_voice_volume(self, value):
        self.voice_volume = value

    def set_bgm_volume(self, value):
        self.bgm_volume = value

    def record_voice(self):
        from audio.voice_engine import VoiceEngine
        ve = VoiceEngine()
        self.audio_path = ve.record_voice()
        print(f"Voice recorded: {self.audio_path}")

    def start_mocap(self):
        try:
            from ai.motion_capture import MotionCapture
            mc = MotionCapture()
            self.motion_capture_path = mc.capture_motion()
            if self.motion_capture_path:
                print(f"Motion capture saved: {self.motion_capture_path}")
        except Exception as e:
            print(f"MoCap failed: {e}. Make sure webcam is available.")

    def generate(self):
        if not self.scenes:
            return
        script = self.scenes[0].get("1.0", "end").strip()
        if not script or not self.blender_path:
            return
        if not self.use_ai_voice and self.audio_path is None:
            # Maybe show a message
            print("Please record voice or enable AI voice")
            return
        self.progress.set(0.2)
        # Import and call AI processor
        from engine.core import generate_blender_code
        description = generate_blender_code(script)
        self.progress.set(0.5)
        if self.use_ai_voice:
            from audio.voice_engine import VoiceEngine
            ve = VoiceEngine()
            self.audio_path = ve.generate_ai_voice(script)
        # Import and call Blender scene generator
        from blender.scene_generator import render_scene
        env_name = self.env_combo.get()
        char_name = self.char_combo.get()
        try:
            output_file = render_scene(description, self.blender_path, self.audio_path, script, env_name, char_name, self.motion_capture_path, self.enable_bgm, self.voice_volume, self.bgm_volume)
        except Exception as e:
            print(f"Rendering failed: {e}. Check Blender path and dependencies.")
            return
        self.progress.set(1.0)

    def preview(self):
        if not self.scenes:
            return
        script = self.scenes[0].get("1.0", "end").strip()
        if not script or not self.blender_path:
            return
        if not self.use_ai_voice and self.audio_path is None:
            print("Please record voice or enable AI voice")
            return
        self.progress.set(0.2)
        # Import and call AI processor
        from engine.core import generate_blender_code
        description = generate_blender_code(script)
        self.progress.set(0.5)
        if self.use_ai_voice:
            from audio.voice_engine import VoiceEngine
            ve = VoiceEngine()
            self.audio_path = ve.generate_ai_voice(script)
        self.progress.set(0.8)
        # Import and call Blender scene preview
        from blender.scene_generator import preview_scene
        env_name = self.env_combo.get()
        char_name = self.char_combo.get()
        try:
            screenshot_path = preview_scene(description, self.blender_path, self.audio_path, script, env_name, char_name, self.motion_capture_path, self.enable_bgm, self.voice_volume, self.bgm_volume)
        except Exception as e:
            print(f"Preview failed: {e}. Check Blender path.")
            return
        self.progress.set(1.0)
        # Show preview in popup
        if PIL_AVAILABLE and screenshot_path:
            try:
                image = Image.open(screenshot_path)
                photo = ImageTk.PhotoImage(image)
                popup = ctk.CTkToplevel(self)
                popup.title("Scene Preview")
                popup.geometry("900x500")
                label = ctk.CTkLabel(popup, image=photo, text="")
                label.pack()
                label.image = photo  # Keep reference
            except Exception as e:
                print(f"Error showing preview: {e}")
        else:
            print("PIL not available or no screenshot generated")

    def add_scene(self):
        scene_num = len(self.scenes) + 1
        frame = ctk.CTkFrame(self.scenes_frame)
        frame.pack(pady=5, fill="x")
        label = ctk.CTkLabel(frame, text=f"Scene {scene_num}:")
        label.pack(side="left", padx=5)
        textbox = ctk.CTkTextbox(frame, height=60)
        textbox.pack(side="left", fill="x", expand=True, padx=5)
        remove_button = ctk.CTkButton(frame, text="Remove", command=lambda: self.remove_scene(frame, textbox))
        remove_button.pack(side="right", padx=5)
        self.scenes.append(textbox)

    def remove_scene(self, frame, textbox):
        frame.destroy()
        self.scenes.remove(textbox)

    def compile_movie(self):
        if not self.scenes or not self.blender_path:
            return
        self.progress.set(0.1)
        from ai.processor import process_script
        scenes_data = []
        for textbox in self.scenes:
            script = textbox.get("1.0", "end").strip()
            if script:
                from engine.core import generate_blender_code
                description = generate_blender_code(script)
                scenes_data.append((description, script))
        if not scenes_data:
            return
        self.progress.set(0.3)
        # Render each scene
        temp_videos = []
        for i, (description, script) in enumerate(scenes_data):
            from blender.scene_generator import render_scene
            try:
                output_file = render_scene(description, self.blender_path, None, script, self.env_combo.get(), self.char_combo.get(), self.motion_capture_path, self.enable_bgm, self.voice_volume, self.bgm_volume)
                temp_videos.append(output_file)
            except Exception as e:
                print(f"Rendering scene {i+1} failed: {e}")
                continue
            self.progress.set(0.3 + 0.4 * (i+1) / len(scenes_data))
        if not temp_videos:
            print("No scenes rendered successfully.")
            return
        # Compile videos
        from blender.scene_generator import compile_videos
        try:
            final_output = compile_videos(temp_videos, self.blender_path)
        except Exception as e:
            print(f"Compiling movie failed: {e}")
            return
        self.progress.set(1.0)
        print(f"Full movie compiled: {final_output}")