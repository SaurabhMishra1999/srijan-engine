"""
Srijan Engine Advanced Audio-Visual Integration Example
Demonstrates how to use the new audio-visual modules together.
"""

import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_audio_processing():
    """
    Example 1: Advanced audio processing with emotional voice and lip-sync.
    """
    logger.info("=" * 60)
    logger.info("Example 1: Advanced Audio Processing")
    logger.info("=" * 60)
    
    from audio.emotional_voice_engine import EmotionalVoiceEngine
    from audio.lip_sync_engine import LipSyncEngine
    
    # Initialize engines
    voice_engine = EmotionalVoiceEngine()
    lipsync_engine = LipSyncEngine()
    
    # Generate emotional voice
    text = "Welcome to the Saipooja Warehouse! We have excellent medicine boxes in stock."
    
    # Generate with different emotions
    emotions_to_try = ['happy', 'neutral', 'concerned']
    
    for emotion in emotions_to_try:
        try:
            audio_path = voice_engine.generate_emotional_voice(
                text=text,
                emotion=emotion,
                filename=f"warehouse_welcome_{emotion}.wav"
            )
            logger.info(f"Generated emotional voice: {emotion}")
        except Exception as e:
            logger.error(f"Error generating voice for {emotion}: {e}")
    
    # Get available options
    logger.info(f"Available emotions: {voice_engine.get_available_emotions()}")
    logger.info(f"Available voices: {voice_engine.get_available_voices()}")


def example_audio_visual_merge():
    """
    Example 2: Merging audio and visual effects with ducking.
    """
    logger.info("=" * 60)
    logger.info("Example 2: Audio-Visual Merge with Ducking")
    logger.info("=" * 60)
    
    from audio.audio_visual_merger import AudioVisualMerger, AudioTrack
    from audio.emotional_voice_engine import EmotionalVoiceEngine
    
    # Initialize merger
    merger = AudioVisualMerger()
    
    # Generate voice track
    voice_engine = EmotionalVoiceEngine()
    voice_path = voice_engine.generate_emotional_voice(
        text="This is the main narration for the warehouse tour.",
        emotion="neutral",
        filename="narration.wav"
    )
    
    # Add tracks (assume background music and voice files exist)
    try:
        # Add voice track
        voice_track = merger.add_audio_track(
            audio_path=voice_path,
            name="Narration",
            volume=1.0,
            fade_in=0.5,
            fade_out=0.5
        )
        
        logger.info(f"Added voice track: {voice_track.name} ({voice_track.duration:.2f}s)")
        
        # Get processing log
        log = merger.get_processing_log()
        logger.info("Processing steps:")
        for step in log:
            logger.info(f"  - {step}")
        
        # Export report
        report_path = merger.export_processing_report()
        logger.info(f"Processing report saved: {report_path}")
        
    except Exception as e:
        logger.error(f"Error in merge example: {e}")


def example_vfx_processing():
    """
    Example 3: Visual effects processing.
    """
    logger.info("=" * 60)
    logger.info("Example 3: VFX Processing")
    logger.info("=" * 60)
    
    from blender.vfx_processor import VFXProcessor, BlenderParticleEffects
    
    # Initialize VFX processor
    vfx = VFXProcessor()
    
    # Log available color grading styles
    color_grades = ['teal_orange', 'blue_yellow', 'desaturated', 'warm']
    logger.info(f"Available color grading styles: {color_grades}")
    
    # Initialize Blender effects
    blender_effects = BlenderParticleEffects()
    
    # Generate Blender scripts for different effects
    output_dir = "output/blender_scripts"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Dust particles script
        dust_script = blender_effects.generate_dust_particles_script(
            output_script=os.path.join(output_dir, "dust_effects.py"),
            intensity=0.8,
            particle_count=5000
        )
        logger.info(f"Generated dust script: {dust_script}")
        
        # Smoke effects script
        smoke_script = blender_effects.generate_smoke_effects_script(
            output_script=os.path.join(output_dir, "smoke_effects.py"),
            intensity=0.6
        )
        logger.info(f"Generated smoke script: {smoke_script}")
        
        # Vehicle-specific effects
        truck_script = blender_effects.generate_vehicle_effects_script(
            output_script=os.path.join(output_dir, "truck_exhaust.py"),
            vehicle_type="truck",
            intensity=0.7
        )
        logger.info(f"Generated truck effects script: {truck_script}")
        
        forklift_script = blender_effects.generate_vehicle_effects_script(
            output_script=os.path.join(output_dir, "forklift_exhaust.py"),
            vehicle_type="forklift",
            intensity=0.5
        )
        logger.info(f"Generated forklift effects script: {forklift_script}")
        
    except Exception as e:
        logger.error(f"Error generating VFX scripts: {e}")


def example_warehouse_inventory():
    """
    Example 4: Warehouse inventory management and scene setup.
    """
    logger.info("=" * 60)
    logger.info("Example 4: Warehouse Inventory & Scene Setup")
    logger.info("=" * 60)
    
    from blender.warehouse_assets_manager import WarehouseAssetsManager, AssetType
    
    # Initialize manager
    assets_manager = WarehouseAssetsManager()
    
    # List all registered assets
    logger.info("Registered assets:")
    assets = assets_manager.list_all_assets()
    for asset in assets:
        logger.info(f"  - {asset['name']} ({asset['asset_id']}): {asset['asset_type']}")
    
    # Get asset statistics
    stats = assets_manager.get_asset_statistics()
    logger.info(f"Asset Statistics: {stats}")
    
    # Get assets by type
    forklifts = assets_manager.get_assets_by_type(AssetType.FORKLIFT)
    logger.info(f"Available forklifts: {len(forklifts)}")
    
    trucks = assets_manager.get_assets_by_type(AssetType.CONTAINER_TRUCK)
    logger.info(f"Available trucks: {len(trucks)}")
    
    # Create a warehouse scene
    try:
        scene = assets_manager.create_scene(
            scene_name="Warehouse Loading Dock",
            scene_id="loading_dock_001",
            description="A busy warehouse loading dock with trucks and forklifts"
        )
        
        # Add assets to scene
        assets_manager.add_asset_to_scene(
            scene_id="loading_dock_001",
            asset_id="container_truck_001",
            position=(0, 0, 0)
        )
        
        assets_manager.add_asset_to_scene(
            scene_id="loading_dock_001",
            asset_id="forklift_001",
            position=(5, 0, 0)
        )
        
        assets_manager.add_asset_to_scene(
            scene_id="loading_dock_001",
            asset_id="medicine_box_001",
            position=(3, 2, 0),
            scale=(1.5, 1.5, 1.5)
        )
        
        assets_manager.add_asset_to_scene(
            scene_id="loading_dock_001",
            asset_id="warehouse_shelf_001",
            position=(-5, 0, 0)
        )
        
        logger.info("Scene created with 4 assets")
        
        # List scenes
        scenes = assets_manager.list_all_scenes()
        logger.info(f"Available scenes: {scenes}")
        
        # Export scene config
        output_dir = "output/scene_configs"
        os.makedirs(output_dir, exist_ok=True)
        
        config_path = os.path.join(output_dir, "loading_dock_001.json")
        if assets_manager.export_scene_config("loading_dock_001", config_path):
            logger.info(f"Scene config exported: {config_path}")
        
        # Generate Blender setup script
        script_path = os.path.join(output_dir, "setup_loading_dock.py")
        if assets_manager.generate_blender_setup_script("loading_dock_001", script_path):
            logger.info(f"Blender setup script generated: {script_path}")
        
    except Exception as e:
        logger.error(f"Error creating warehouse scene: {e}")


def example_complete_workflow():
    """
    Example 5: Complete integrated workflow combining all modules.
    """
    logger.info("=" * 60)
    logger.info("Example 5: Complete Integrated Workflow")
    logger.info("=" * 60)
    
    from audio.emotional_voice_engine import EmotionalVoiceEngine
    from audio.audio_visual_merger import AudioVisualMerger
    from blender.warehouse_assets_manager import WarehouseAssetsManager
    
    try:
        # Step 1: Create warehouse scene
        logger.info("Step 1: Setting up warehouse scene...")
        assets_manager = WarehouseAssetsManager()
        
        scene = assets_manager.create_scene(
            scene_name="Full Warehouse Tour",
            scene_id="full_tour_001",
            description="Complete warehouse tour with narrative"
        )
        
        # Add warehouse assets
        for asset_id in ["container_truck_001", "forklift_001", "warehouse_shelf_001"]:
            assets_manager.add_asset_to_scene("full_tour_001", asset_id)
        
        logger.info("Scene setup complete")
        
        # Step 2: Generate narration with emotions
        logger.info("\nStep 2: Generating narration...")
        voice_engine = EmotionalVoiceEngine()
        
        narration = voice_engine.generate_emotional_voice(
            text="Welcome to the Saipooja Warehouse management system. We maintain a fleet of container trucks and forklifts for efficient logistics.",
            emotion="happy",
            filename="warehouse_tour_narration.wav"
        )
        logger.info(f"Narration generated: {narration}")
        
        # Step 3: Setup audio mixing
        logger.info("\nStep 3: Setting up audio mixing...")
        merger = AudioVisualMerger()
        
        # Add narration
        merger.add_audio_track(
            audio_path=narration,
            name="Narration",
            volume=1.0
        )
        
        logger.info("Audio tracks configured")
        
        # Step 4: Add visual effects
        logger.info("\nStep 4: Configuring visual effects...")
        
        # Add color grading
        merger.add_visual_effect(
            effect_type='color_grade',
            intensity=0.7,
            start_frame=0,
            end_frame=150,
            parameters={'color_temp': 'warm'}
        )
        
        # Add film grain
        merger.add_visual_effect(
            effect_type='grain',
            intensity=0.05,
            start_frame=0,
            end_frame=150
        )
        
        logger.info("Visual effects configured")
        
        # Step 5: Generate Blender setup
        logger.info("\nStep 5: Generating Blender setup...")
        output_dir = "output/complete_workflow"
        os.makedirs(output_dir, exist_ok=True)
        
        blender_script = os.path.join(output_dir, "scene_setup.py")
        assets_manager.generate_blender_setup_script("full_tour_001", blender_script)
        logger.info(f"Blender setup script: {blender_script}")
        
        # Export configuration
        config_path = os.path.join(output_dir, "scene_config.json")
        assets_manager.export_scene_config("full_tour_001", config_path)
        logger.info(f"Scene configuration: {config_path}")
        
        # Export processing report
        report_path = merger.export_processing_report(
            os.path.join(output_dir, "processing_report.json")
        )
        logger.info(f"Processing report: {report_path}")
        
        logger.info("\n✓ Complete workflow executed successfully!")
        
    except Exception as e:
        logger.error(f"Error in complete workflow: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    logger.info("Srijan Engine Advanced Audio-Visual Features Demo")
    logger.info("=" * 60)
    
    # Run examples
    try:
        example_audio_processing()
        example_audio_visual_merge()
        example_vfx_processing()
        example_warehouse_inventory()
        example_complete_workflow()
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("\n" + "=" * 60)
    logger.info("Demo completed!")
