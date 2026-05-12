"""
face_mesh.py
Thin wrapper around MediaPipe FaceLandmarker (Task API).
Runs face detection and returns normalized landmarks.

Optimisation: processes every Nth frame (default: 2) to halve CPU load.
"""
import os
import cv2
import mediapipe as mp
from mediapipe.tasks.python.vision import FaceLandmarker, FaceLandmarkerOptions, RunningMode
from mediapipe.tasks.python.core.base_options import BaseOptions
import numpy as np
from typing import Optional

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models", "face_landmarker.task"
)
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
)

def _ensure_model():
    if not os.path.exists(MODEL_PATH):
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        print(f"[FaceMesh] Downloading face landmark model to {MODEL_PATH} ...")
        import urllib.request
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("[FaceMesh] Download complete.")


class FaceMesh:
    def __init__(self, process_every_n: int = 2):
        _ensure_model()
        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._detector = FaceLandmarker.create_from_options(options)
        self._process_every = process_every_n
        self._frame_idx     = 0
        self._last_landmarks: Optional[list] = None

    def process(self, bgr_frame: np.ndarray) -> tuple[Optional[list], np.ndarray]:
        """
        Process one webcam frame.

        Returns:
            landmarks: list of 478 [x, y, z] points, or None if no face found
            annotated: BGR frame with face mesh overlay drawn on it
        """
        self._frame_idx += 1

        if self._frame_idx % self._process_every != 0:
            return self._last_landmarks, bgr_frame

        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self._detector.detect(mp_image)

        annotated = bgr_frame.copy()

        if not result.face_landmarks:
            self._last_landmarks = None
            return None, annotated

        face = result.face_landmarks[0]
        h, w = bgr_frame.shape[:2]

        # Draw mesh dots (first 468 landmarks)
        for lm in face[:468]:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(annotated, (cx, cy), 1, (0, 200, 120), -1)

        # Draw iris landmarks (indices 468-477)
        for lm in face[468:]:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(annotated, (cx, cy), 3, (0, 120, 255), -1)

        landmarks = [[lm.x, lm.y, lm.z] for lm in face]
        self._last_landmarks = landmarks

        return landmarks, annotated

    def close(self):
        self._detector.close()
