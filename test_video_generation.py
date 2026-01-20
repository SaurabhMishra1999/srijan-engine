#!/usr/bin/env python3
"""
Srijan Engine - Video Generation Test Script
Comprehensive testing of all audio-visual features
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_imports():
    """Test if all modules can be imported"""
    logger.info("=" * 60)
    logger.info("TEST 1: Import All Modules")
    logger.info("=" * 60)
    
    try:
        from audio.emotional_voice_engine import EmotionalVoiceEngine
        logger.info("✓ EmotionalVoiceEngine imported")
        
        from audio.lip_sync_engine import LipSyncEngine
        logger.info("✓ LipSyncEngine imported")
        
        from audio.audio_visual_merger import AudioVisualMerger
        logger.info("✓ AudioVisualMerger imported")
        
        from blender.vfx_processor import VFXProcessor, BlenderParticleEffects
        logger.info("✓ VFXProcessor imported")
        logger.info("✓ BlenderParticleEffects imported")
        
        from blender.warehouse_assets_manager import WarehouseAssetsManager
        logger.info("✓ WarehouseAssetsManager imported")
        
        logger.info("✅ All imports successful!\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}\n")
        return False


def test_emotional_voice():
    """Test emotional voice generation"""
    logger.info("=" * 60)
    logger.info("TEST 2: Generate Emotional Voice Audio")
    logger.info("=" * 60)
    
    try:
        from audio.emotional_voice_engine import EmotionalVoiceEngine
        
        engine = EmotionalVoiceEngine()
        logger.info(f"✓ Engine initialized")
        
        # Test different emotions
        emotions = ['happy', 'sad', 'neutral']
        generated_files = []
        
        for emotion in emotions:
            text = f"This is a {emotion} voice test for Srijan Engine"
            audio_path = engine.generate_emotional_voice(
                text=text,
                emotion=emotion,
                filename=f"test_voice_{emotion}.wav"
            )
            
            if os.path.exists(audio_path):
                size_kb = os.path.getsize(audio_path) / 1024
                logger.info(f"✓ Generated {emotion} voice: {audio_path} ({size_kb:.1f} KB)")
                generated_files.append(audio_path)
            else:
                logger.error(f"❌ File not created: {audio_path}")
                return False
        
        logger.info(f"✅ Generated {len(generated_files)} voice files!\n")
        return True, generated_files
        
    except Exception as e:
        logger.error(f"❌ Voice generation failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False, []


def test_audio_mixing():
    """Test audio mixing and ducking"""
    logger.info("=" * 60)
    logger.info("TEST 3: Audio Mixing with Ducking")
    logger.info("=" * 60)
    
    try:
        from audio.emotional_voice_engine import EmotionalVoiceEngine
        from audio.audio_visual_merger import AudioVisualMerger
        
        # Generate voice
        engine = EmotionalVoiceEngine()
        voice_path = engine.generate_emotional_voice(
            "Welcome to Srijan Engine warehouse system",
            emotion="happy",
            filename="test_narration.wav"
        )
        logger.info(f"✓ Generated narration: {voice_path}")
        
        # Test mixer
        merger = AudioVisualMerger()
        logger.info("✓ AudioVisualMerger initialized")
        
        # Add voice track
        merger.add_audio_track(
            audio_path=voice_path,
            name="Narration",
            volume=1.0,
            fade_in=0.5
        )
        logger.info("✓ Added audio track")
        
        # Mix audio
        output_audio = merger.mix_audio_tracks("test_mixed_audio.wav")
        
        if os.path.exists(output_audio):
            size_kb = os.path.getsize(output_audio) / 1024
            logger.info(f"✓ Mixed audio created: {output_audio} ({size_kb:.1f} KB)")
            logger.info("✅ Audio mixing successful!\n")
            return True, output_audio
        else:
            logger.error(f"❌ Mixed audio file not created")
            return False, None
            
    except Exception as e:
        logger.error(f"❌ Audio mixing failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False, None


def test_vfx_generation():
    """Test VFX and particle effects script generation"""
    logger.info("=" * 60)
    logger.info("TEST 4: VFX and Particle Effects")
    logger.info("=" * 60)
    
    try:
        from blender.vfx_processor import VFXProcessor, BlenderParticleEffects
        
        vfx = VFXProcessor()
        logger.info("✓ VFXProcessor initialized")
        
        blender_fx = BlenderParticleEffects()
        logger.info("✓ BlenderParticleEffects initialized")
        
        # Create output directory
        os.makedirs("output/blender_scripts", exist_ok=True)
        
        # Generate particle scripts
        scripts_generated = []
        
        # Dust particles
        dust_script = blender_fx.generate_dust_particles_script(
            "output/blender_scripts/test_dust.py",
            intensity=0.8,
            particle_count=5000
        )
        if os.path.exists(dust_script):
            logger.info(f"✓ Dust particles script: {dust_script}")
            scripts_generated.append(dust_script)
        
        # Smoke effects
        smoke_script = blender_fx.generate_smoke_effects_script(
            "output/blender_scripts/test_smoke.py",
            intensity=0.6
        )
        if os.path.exists(smoke_script):
            logger.info(f"✓ Smoke effects script: {smoke_script}")
            scripts_generated.append(smoke_script)
        
        # Vehicle effects
        truck_script = blender_fx.generate_vehicle_effects_script(
            "output/blender_scripts/test_truck_fx.py",
            vehicle_type="truck",
            intensity=0.7
        )
        if os.path.exists(truck_script):
            logger.info(f"✓ Truck effects script: {truck_script}")
            scripts_generated.append(truck_script)
        
        logger.info(f"✅ Generated {len(scripts_generated)} effect scripts!\n")
        return True, scripts_generated
        
    except Exception as e:
        logger.error(f"❌ VFX generation failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False, []


def test_warehouse_assets():
    """Test warehouse asset management"""
    logger.info("=" * 60)
    logger.info("TEST 5: Warehouse Asset Management")
    logger.info("=" * 60)
    
    try:
        from blender.warehouse_assets_manager import WarehouseAssetsManager
        
        manager = WarehouseAssetsManager()
        logger.info("✓ WarehouseAssetsManager initialized")
        
        # Get asset statistics
        stats = manager.get_asset_statistics()
        logger.info(f"✓ Total assets in inventory: {stats['total_assets']}")
        for asset_type, count in stats['by_type'].items():
            logger.info(f"  - {asset_type}: {count}")
        
        # Create test scene
        scene = manager.create_scene(
            scene_name="Test Warehouse",
            scene_id="test_wh_001",
            description="Test warehouse scene"
        )
        logger.info(f"✓ Created scene: {scene.scene_name}")
        
        # Add assets to scene
        manager.add_asset_to_scene("test_wh_001", "forklift_001", position=(0, 0, 0))
        logger.info("✓ Added forklift to scene")
        
        manager.add_asset_to_scene("test_wh_001", "container_truck_001", position=(5, 0, 0))
        logger.info("✓ Added container truck to scene")
        
        # Export configuration
        os.makedirs("output/scene_configs", exist_ok=True)
        config_path = "output/scene_configs/test_warehouse_scene.json"
        
        if manager.export_scene_config("test_wh_001", config_path):
            logger.info(f"✓ Exported scene config: {config_path}")
        
        # Generate Blender script
        script_path = "output/scene_configs/test_warehouse_setup.py"
        if manager.generate_blender_setup_script("test_wh_001", script_path):
            logger.info(f"✓ Generated Blender setup script: {script_path}")
        
        logger.info("✅ Warehouse asset management successful!\n")
        return True, config_path
        
    except Exception as e:
        logger.error(f"❌ Warehouse assets test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False, None


def test_lip_sync():
    """Test lip-sync engine initialization"""
    logger.info("=" * 60)
    logger.info("TEST 6: Lip-Sync Engine")
    logger.info("=" * 60)
    
    try:
        from audio.lip_sync_engine import LipSyncEngine
        
        engine = LipSyncEngine()
        logger.info("✓ LipSyncEngine initialized")
        
        logger.info(f"✓ Upper lip points: {len(engine.upper_lip_indices)}")
        logger.info(f"✓ Lower lip points: {len(engine.lower_lip_indices)}")
        
        logger.info("✅ Lip-sync engine ready!\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Lip-sync test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_complete_workflow():
    """Test complete integrated workflow"""
    logger.info("=" * 60)
    logger.info("TEST 7: Complete Integrated Workflow")
    logger.info("=" * 60)
    
    try:
        from audio.emotional_voice_engine import EmotionalVoiceEngine
        from audio.audio_visual_merger import AudioVisualMerger
        from blender.warehouse_assets_manager import WarehouseAssetsManager
        
        # Step 1: Generate narration
        logger.info("→ Step 1: Generating narration...")
        voice_engine = EmotionalVoiceEngine()
        narration = voice_engine.generate_emotional_voice(
            "This is a complete workflow test for the Srijan Engine with advanced audio-visual features",
            emotion="happy",
            filename="test_complete_narration.wav"
        )
        logger.info(f"  ✓ Narration: {narration}")
        
        # Step 2: Setup audio mixing
        logger.info("→ Step 2: Setting up audio mixing...")
        merger = AudioVisualMerger()
        merger.add_audio_track(narration, "Narration", volume=1.0)
        logger.info("  ✓ Audio tracks added")
        
        # Step 3: Create warehouse scene
        logger.info("→ Step 3: Creating warehouse scene...")
        manager = WarehouseAssetsManager()
        scene = manager.create_scene(
            "Complete Test Scene",
            "complete_test_001",
            "Full workflow test"
        )
        manager.add_asset_to_scene("complete_test_001", "forklift_001")
        manager.add_asset_to_scene("complete_test_001", "container_truck_001")
        logger.info("  ✓ Scene created with assets")
        
        # Step 4: Export configurations
        logger.info("→ Step 4: Exporting configurations...")
        os.makedirs("output/complete_test", exist_ok=True)
        
        config_path = "output/complete_test/complete_test_config.json"
        manager.export_scene_config("complete_test_001", config_path)
        logger.info(f"  ✓ Scene config: {config_path}")
        
        blender_script = "output/complete_test/complete_test_setup.py"
        manager.generate_blender_setup_script("complete_test_001", blender_script)
        logger.info(f"  ✓ Blender script: {blender_script}")
        
        # Step 5: Export audio and report
        logger.info("→ Step 5: Finalizing...")
        report = "output/complete_test/processing_report.json"
        merger.export_processing_report(report)
        logger.info(f"  ✓ Processing report: {report}")
        
        logger.info("✅ Complete workflow successful!\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Complete workflow test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    logger.info("\n" + "🎬" * 30)
    logger.info("SRIJAN ENGINE - COMPREHENSIVE TEST SUITE")
    logger.info("🎬" * 30 + "\n")
    
    results = {}
    
    # Test 1: Imports
    results['Imports'] = test_imports()
    
    # Test 2: Emotional Voice
    result, files = test_emotional_voice()
    results['Emotional Voice'] = result
    
    # Test 3: Audio Mixing
    result, output = test_audio_mixing()
    results['Audio Mixing'] = result
    
    # Test 4: VFX Generation
    result, scripts = test_vfx_generation()
    results['VFX Generation'] = result
    
    # Test 5: Warehouse Assets
    result, config = test_warehouse_assets()
    results['Warehouse Assets'] = result
    
    # Test 6: Lip-Sync
    results['Lip-Sync Engine'] = test_lip_sync()
    
    # Test 7: Complete Workflow
    results['Complete Workflow'] = test_complete_workflow()
    
    # Summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v is True)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result is True else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("=" * 60)
    logger.info(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("✅ ALL TESTS PASSED - SYSTEM READY FOR VIDEO GENERATION!")
    else:
        logger.info(f"⚠️ {total - passed} test(s) failed - Check errors above")
    
    logger.info("=" * 60)
    logger.info("\n📁 Output Files Location: output/")
    logger.info("📋 Check these directories:")
    logger.info("   - output/  (audio, configs, reports)")
    logger.info("   - output/blender_scripts/  (Blender effect scripts)")
    logger.info("   - output/scene_configs/  (Scene configurations)")
    logger.info("   - assets/audio/  (Generated voice files)")
    
    logger.info("\n" + "🎬" * 30)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
