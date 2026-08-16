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

                                       

