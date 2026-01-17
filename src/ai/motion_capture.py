import cv2
import mediapipe as mp
import json
import os
from datetime import datetime

class MotionCapture:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        self.animations_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'animations')
        os.makedirs(self.animations_dir, exist_ok=True)

    def capture_motion(self):
        """
        Opens webcam, tracks pose, records when 'r' pressed, saves on 's' or stop.
        """
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open webcam")
            return None

        recording = False
        frames = []

        print("Press 'r' to start/stop recording, 'q' to quit and save")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process pose
            results = self.pose.process(rgb_frame)

            # Draw landmarks
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

                if recording:
                    # Record landmarks
                    landmarks = []
                    for lm in results.pose_landmarks.landmark:
                        landmarks.append([lm.x, lm.y, lm.z])
                    frames.append(landmarks)

            # Display recording status
            status = "Recording" if recording else "Not Recording"
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if recording else (0, 0, 255), 2)

            cv2.imshow('Motion Capture', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('r'):
                recording = not recording
                if recording:
                    frames = []  # Reset on start
                else:
                    # Save on stop
                    if frames:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"motion_capture_{timestamp}.json"
                        filepath = os.path.join(self.animations_dir, filename)
                        data = {"frames": frames, "fps": 30}
                        with open(filepath, 'w') as f:
                            json.dump(data, f)
                        print(f"Saved motion capture to {filepath}")
                        return filepath
            elif key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return None

if __name__ == "__main__":
    mc = MotionCapture()
    mc.capture_motion()