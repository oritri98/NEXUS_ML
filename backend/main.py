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

