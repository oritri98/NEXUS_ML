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

