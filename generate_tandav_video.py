#!/usr/bin/env python3
"""
Srijan Engine - Direct Video Generator
Generates videos without needing Flask server
"""

import cv2
import numpy as np
import os
from datetime import datetime
import json

OUTPUT_FOLDER = r"e:\Srijan_Engine\output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def create_tandav_video(duration=60):
    """Create TANDAV - Cosmic Dance of Shiva video"""
    
    output_path = os.path.join(OUTPUT_FOLDER, f"TANDAV_ShivasDance_{duration}sec.mp4")
    
    print(f"\n{'='*60}")
    print("TANDAV - COSMIC DANCE OF SHIVA")
    print(f"{'='*60}")
    print(f"Creating video: {output_path}")
    print(f"Duration: {duration} seconds")
    print(f"{'='*60}\n")
    
    # Video properties
    width, height = 1920, 1080
    fps = 30
    total_frames = duration * fps
    
    # Create video writer with MP4V codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        print("ERROR: MP4V codec failed, trying MJPG...")
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        output_path = output_path.replace('.mp4', '.avi')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        print("ERROR: Video writer could not be opened!")
        return None
    
    print(f"Generating {total_frames} frames...\n")
    
    # Generate frames
    for frame_num in range(total_frames):
        # Create frame with cosmic gradient
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Dark cosmic background
        for i in range(height):
            intensity = int(10 + (i / height) * 30)
            frame[i, :] = [intensity, intensity, intensity + 20]
        
        # Add multiple animated circles (cosmic energy)
        center_x1 = int(width/2 + 200 * np.sin(frame_num * 0.02))
        center_y1 = int(height/2 + 150 * np.cos(frame_num * 0.01))
        radius1 = 60 + int(40 * np.sin(frame_num * 0.05))
        
        center_x2 = int(width/2 - 150 * np.cos(frame_num * 0.015))
        center_y2 = int(height/2 + 100 * np.sin(frame_num * 0.025))
        radius2 = 80 + int(50 * np.cos(frame_num * 0.03))
        
        # Draw cosmic circles with cyan glow
        cv2.circle(frame, (center_x1, center_y1), radius1, (200, 100, 50), -1)
        cv2.circle(frame, (center_x1, center_y1), radius1 + 10, (0, 200, 255), 2)
        
        cv2.circle(frame, (center_x2, center_y2), radius2, (100, 150, 200), -1)
        cv2.circle(frame, (center_x2, center_y2), radius2 + 10, (0, 255, 200), 2)
        
        # Add rotating mandala effect
        angle = (frame_num * 2) % 360
        for i in range(8):
            angle_offset = i * 45
            x = int(width/2 + 250 * np.cos(np.radians(angle + angle_offset)))
            y = int(height/2 + 250 * np.sin(np.radians(angle + angle_offset)))
            cv2.circle(frame, (x, y), 30, (0, 212, 255), 2)
        
        # Add title
        cv2.putText(frame, "TANDAV", (150, 150), cv2.FONT_HERSHEY_DUPLEX, 4, (0, 212, 255), 3)
        cv2.putText(frame, "Cosmic Dance of Shiva", (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 200, 255), 2)
        
        # Add progress bar
        progress = int((frame_num / total_frames) * 100)
        bar_width = int((frame_num / total_frames) * (width - 300))
        cv2.rectangle(frame, (150, height - 100), (150 + bar_width, height - 60), (0, 212, 255), -1)
        cv2.rectangle(frame, (150, height - 100), (width - 150, height - 60), (100, 100, 100), 2)
        cv2.putText(frame, f"{progress}%", (width - 200, height - 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 212, 255), 2)
        
        # Write frame
        out.write(frame)
        
        # Progress indicator
        if (frame_num + 1) % 30 == 0:
            print(f"Progress: {progress}% ({frame_num + 1}/{total_frames} frames)")
    
    # Release the video writer
    out.release()
    
    # Verify file was created
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n{'='*60}")
        print(f"SUCCESS: Video created!")
        print(f"File: {os.path.basename(output_path)}")
        print(f"Size: {file_size:.2f} MB")
        print(f"Path: {output_path}")
        print(f"{'='*60}\n")
        return output_path
    else:
        print(f"\nERROR: Video file was not created")
        return None

if __name__ == "__main__":
    video_path = create_tandav_video(duration=60)
    if video_path:
        print("Ready to download at: http://localhost:5000/download/TANDAV_ShivasDance_60sec.mp4")
