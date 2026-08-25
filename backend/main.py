import cv2
import mediapipe as mp
import pyautogui
import math
import time
import threading
import asyncio
import os
import json
import webbrowser
import tempfile
import speech_recognition as sr
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Initialize MediaPipe Hands Tasks API in the main thread scope
# This prevents thread-safety and dynamic lazy-loading issues inside child threads
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

base_options = mp_python.BaseOptions(model_asset_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "hand_landmarker.task")))
options = vision.HandLandmarkerOptions(base_options=base_options,
                                       num_hands=2,
                                       min_hand_detection_confidence=0.75,
                                       min_tracking_confidence=0.75)
detector = vision.HandLandmarker.create_from_options(options)

face_base_options = mp_python.BaseOptions(model_asset_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "face_landmarker.task")))
face_options = vision.FaceLandmarkerOptions(base_options=face_base_options,
                                            output_face_blendshapes=False,
                                            output_facial_transformation_matrixes=False,
                                            num_faces=1)
face_detector = vision.FaceLandmarker.create_from_options(face_options)

# Initialize FastAPI
app = FastAPI(title="Nexus Gesture Engine")

# Enable CORS for frontend web accessibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Database file location
DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "users.json"))

# Pydantic model for User Logins
class LoginRequest(BaseModel):
    name: str
    email: str
    password: str

# Static Telemetry State (shared between tracking thread and WebSocket thread)
telemetry = {
    "fps": 0,
    "current_action": "SYSTEM IDLE",
    "action_color": [0, 255, 255], # RGB format
    "cursor": {"x": 0, "y": 0},
    "volume": 50,
    "desktop_active": False,
    "landmarks": [],
    "screen_size": {"width": 1920, "height": 1080}
}

# Configuration settings (dynamic from frontend)
config = {
    "engine_active": True,
    "camera_index": 0,
    "smooth_closeness": 2.0,
    "blink_threshold": 0.22,
    "show_opencv_window": False,
    "modalities": {
        "hand_gestures": True,
        "face_tracking": True,
        "voice_commands": False
    },
    "gestures_enabled": {
        "hover": True,
        "left_click": True,
        "right_click": True,
        "click_drag": True,
        "minimize": True,
        "maximize": True,
        "screenshot": True,
        "volume_up": True,
        "volume_down": True,
        "enter_scroll": True,
        "scroll_up": True,
        "scroll_down": True,
        "exit_scroll": True
    }
}

# Screen coordinates setup
screen_w, screen_h = pyautogui.size()
telemetry["screen_size"] = {"width": screen_w, "height": screen_h}
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  

# Track WebSocket connections
connected_clients = set()

# Thread lock for telemetry object access
telemetry_lock = threading.Lock()

# Directory for screenshots
SCREENSHOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "screenshots"))
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def draw_hand_skeleton(frame, landmarks, w, h, color):
    connections = [
        (0,1), (1,2), (2,3), (3,4),
        (0,5), (5,6), (6,7), (7,8),
        (5,9), (9,10), (10,11), (11,12),
        (9,13), (13,14), (14,15), (15,16),
        (13,17), (0,17), (17,18), (18,19), (19,20)
    ]
    for start_idx, end_idx in connections:
        pt1 = (int(landmarks[start_idx].x * w), int(landmarks[start_idx].y * h))
        pt2 = (int(landmarks[end_idx].x * w), int(landmarks[end_idx].y * h))
        cv2.line(frame, pt1, pt2, color, 2)
    for lm in landmarks:
        pt = (int(lm.x * w), int(lm.y * h))
        cv2.circle(frame, pt, 4, color, -1)


def tracking_loop():
    global telemetry, config, screen_w, screen_h
    
    cap = None
    global detector, face_detector
    
    prev_x, prev_y = 0, 0
    prev_time = time.time()
    is_dragging = False
    desktop_active = False
    
    last_screenshot_time = 0
    last_right_click_time = 0
    last_boss_key_time = 0
    last_left_click_time = 0
    
    maximize_gesture_start = None
    minimize_gesture_start = None
    scroll_mode_active = False
    two_hands_open_start = None
    two_hands_closed_start = None
    last_both_open_time = 0
    last_both_closed_time = 0
    global_cooldown_until = 0

    # Face tracking variables
    last_left_turn_time = 0
    last_right_turn_time = 0
    is_head_currently_turned_left = False
    is_head_currently_turned_right = False

    PINCH_ENGAGE = 28
    PINCH_RELEASE = 40

    print("[SYSTEM] Core Tracking Thread Started.")

    current_camera_index = 0

    while True:
        try:
            target_camera_index = config.get("camera_index", 0)
            
            if cap is not None and cap.isOpened() and current_camera_index != target_camera_index:
                cap.release()
                print(f"[SYSTEM] Camera index changed to {target_camera_index}. Releasing old camera.")
                
            if not config.get("engine_active", True):
                if cap is not None and cap.isOpened():
                    cap.release()
                    cv2.destroyAllWindows()
                    print("[SYSTEM] Camera Released (Engine Standby).")
                time.sleep(0.2)
                continue
                
            if cap is None or not cap.isOpened():
                current_camera_index = target_camera_index
                cap = cv2.VideoCapture(current_camera_index)
                if not cap.isOpened():
                    time.sleep(1.0)
                    continue
                print(f"[SYSTEM] Camera {current_camera_index} Initialized (Engine Active).")
                
            success, frame = cap.read()
            if not success:
                time.sleep(0.01)
                continue
                
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape 
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            results = detector.detect(mp_image)
            face_results = face_detector.detect(mp_image)
            
            # Draw Face Mesh
            if face_results.face_landmarks and config["modalities"].get("face_tracking", True):
                for flm in face_results.face_landmarks[0]:
                    pt = (int(flm.x * w), int(flm.y * h))
                    cv2.circle(frame, pt, 1, (0, 255, 255), -1)
            
            current_action = "SYSTEM IDLE"
            action_color = [0, 255, 255] # Cyan
            normalized_lms = []
            
            right_hand_state = None
            left_hand_state = None
            hands_data = []

            if results.hand_landmarks and results.handedness:
                for idx, hand_landmarks in enumerate(results.hand_landmarks):
                    category = results.handedness[idx][0].category_name
                    is_right_hand = (category == "Left") # Mirrored camera
                    
                    lm = hand_landmarks
                    normalized_lms.extend([{"x": p.x, "y": p.y, "z": p.z} for p in lm])
                    draw_hand_skeleton(frame, lm, w, h, (0, 255, 0) if is_right_hand else (255, 0, 255))
                    
                    thumb, index, middle, ring, pinky = lm[4], lm[8], lm[12], lm[16], lm[20]
                    
                    is_index_up = index.y < lm[6].y
                    is_middle_up = middle.y < lm[10].y
                    is_ring_up = ring.y < lm[14].y
                    is_pinky_up = pinky.y < lm[18].y
                    
                    is_open_palm = is_index_up and is_middle_up and is_ring_up and is_pinky_up

                   