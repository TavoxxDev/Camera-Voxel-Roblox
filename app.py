from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import threading
import time
import requests

app = Flask(__name__)
CORS(app)

GRID = 96
FPS = 20
MODE = "color"
TIMEOUT = 2

FALLBACK_URL = "https://raw.githubusercontent.com/SrBolasGrandes/Camera-Voxel-Roblox/refs/heads/main/262%20Sem%20T%C3%ADtulo_20260101105003.png"

frame_data = {
    "ready": False,
    "data": []
}

last_frame_time = 0
lock = threading.Lock()

def image_to_pixels(img):
    img = cv2.resize(img, (GRID, GRID))
    pixels = []
    for y in range(GRID):
        for x in range(GRID):
            b, g, r = img[y, x]
            pixels.append([int(r), int(g), int(b)])
    return pixels

def load_fallback():
    r = requests.get(FALLBACK_URL)
    img = np.frombuffer(r.content, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    return image_to_pixels(img)

FALLBACK_PIXELS = load_fallback()

def watchdog():
    global frame_data
    while True:
        time.sleep(0.1)
        with lock:
            if time.time() - last_frame_time > TIMEOUT:
                frame_data["data"] = FALLBACK_PIXELS
                frame_data["ready"] = False

threading.Thread(target=watchdog, daemon=True).start()

def process_frame(frame):
    frame = cv2.resize(frame, (GRID, GRID))
    if MODE == "bw":
        g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    return image_to_pixels(frame)

@app.route("/camera")
def camera():
    return render_template("camera.html")

@app.route("/video")
def video():
    return render_template("video.html")

@app.route("/setMode", methods=["POST"])
def set_mode():
    global MODE
    MODE = request.json["mode"]
    return jsonify(ok=True)

@app.route("/pushFrame", methods=["POST"])
def push_frame():
    global frame_data, last_frame_time
    img = np.frombuffer(request.data, np.uint8)
    frame = cv2.imdecode(img, cv2.IMREAD_COLOR)
    pixels = process_frame(frame)
    with lock:
        frame_data["data"] = pixels
        frame_data["ready"] = True
        last_frame_time = time.time()
    return "ok"

@app.route("/cameraGet")
def camera_get():
    with lock:
        return jsonify(frame_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
