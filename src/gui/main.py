import customtkinter as ctk
import os
from datetime import datetime

# Set dark theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class SrijanEngineApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Srijan Engine - AI Text-to-Movie")
        self.geometry("900x700")

        # Header
        self.header = ctk.CTkLabel(self, text="Srijan Engine", font=("Courier", 24, "bold"))
        self.header.pack(pady=20)

        # Script input
        self.script_label = ctk.CTkLabel(self, text="Enter your script:", font=("Courier", 14))
        self.script_label.pack(pady=5)
        self.script_textbox = ctk.CTkTextbox(self, width=800, height=300, font=("Courier", 12))
        self.script_textbox.pack(pady=10)

        # Generate button
        self.generate_button = ctk.CTkButton(self, text="Generate Movie", command=self.generate_movie, font=("Courier", 16))
        self.generate_button.pack(pady=20)

        # Status label
        self.status_label = ctk.CTkLabel(self, text="Ready", font=("Courier", 12))
        self.status_label.pack(pady=10)

        # Processing log label
        self.processing_log_label = ctk.CTkLabel(self, text="", font=("Courier", 10), text_color="gray")
        self.processing_log_label.pack(pady=5)

    def generate_movie(self):
        script = self.script_textbox.get("1.0", "end").strip()
        if not script:
            self.status_label.configure(text="Error: Please enter a script.")
            return

        self.status_label.configure(text="Processing script with AI...")
        try:
            # Parse script with AI to extract scene descriptions, camera angles, etc.
            from src.ai.script_processor import ScriptProcessor
            processor = ScriptProcessor()
            scene_config = processor.parse_script_to_scenes(script)
            self.processing_log_label.configure(text=f"✓ Parsed {len(scene_config.get('scenes', []))} scenes")
        except ImportError:
            scene_config = self._create_default_scene_config(script)
            self.status_label.configure(text="Using default scene configuration")
        except Exception as e:
            self.status_label.configure(text=f"Error parsing script: {str(e)}")
            return

        self.status_label.configure(text="Generating 3D scene with Blender...")
        try:
            # Call Blender to render the scene
            from src.blender.scene_generator import SceneGenerator
            from src.blender.renderer import BlenderRenderer
            
            generator = SceneGenerator()
            renderer = BlenderRenderer()
            
            # Generate scene based on parsed config
            blend_file = generator.create_scene_from_config(scene_config)
            
            # Render to video frames
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'output'
            )
            os.makedirs(output_dir, exist_ok=True)
            
            rendered_video = renderer.render_to_video(blend_file, output_dir, fps=30)
            self.processing_log_label.configure(text=f"✓ Rendered video: {os.path.basename(rendered_video)}")
            
        except ImportError:
            self.status_label.configure(text="Blender not configured. Continuing with audio generation...")
            rendered_video = None
        except Exception as e:
            self.status_label.configure(text=f"Blender rendering error: {str(e)}")
            rendered_video = None

        self.status_label.configure(text="Generating AI narration...")
        try:
            # Generate emotional voice narration
            from src.audio.emotional_voice_engine import EmotionalVoiceEngine
            
            engine = EmotionalVoiceEngine()
            narration_audio = engine.generate_emotional_voice(script[:500], emotion="happy")
            self.processing_log_label.configure(text=f"✓ Generated narration: {os.path.basename(narration_audio)}")
            
        except Exception as e:
            self.status_label.configure(text=f"Narration error: {str(e)}")
            narration_audio = None

        self.status_label.configure(text="Applying VFX and audio effects...")
        try:
            # Apply visual effects if video exists
            if rendered_video and narration_audio:
                from src.audio.audio_visual_merger import AudioVisualMerger
                
                merger = AudioVisualMerger()
                
                # Add audio effects
                merger.add_audio_track(narration_audio, "Narration", volume=1.0)
                mixed_audio = merger.mix_audio_tracks(os.path.join(output_dir, "final_audio.wav"))
                
                # Apply visual effects
                merger.add_visual_effect('color_grade', 0.7, 0, 9999, {'color_temp': 'warm'})
                merger.add_visual_effect('grain', 0.05, 0, 9999)
                
                final_video = merger.process_video_with_effects(
                    rendered_video,
                    os.path.join(output_dir, f"movie_with_vfx_{datetime.now().timestamp()}.mp4")
                )
                
                # Merge video and audio
                final_output = merger.merge_video_and_audio(
                    final_video,
                    mixed_audio,
                    os.path.join(output_dir, f"movie_final_{datetime.now().timestamp()}.mp4")
                )
                
                self.processing_log_label.configure(text=f"✓ Final video: {os.path.basename(final_output)}")
            
        except Exception as e:
            self.status_label.configure(text=f"VFX error: {str(e)}")

        self.status_label.configure(text="Movie generated successfully! Check output folder.")

    def _create_default_scene_config(self, script):
        """Create a default scene configuration from script text."""
        return {
            'scenes': [
                {
                    'description': script[:200],
                    'duration': 5,
                    'camera_angle': 'wide',
                    'lighting': 'default'
                }
            ],
            'fps': 30,
            'resolution': '1920x1080'
        }


if __name__ == "__main__":
    app = SrijanEngineApp()
    app.mainloop()