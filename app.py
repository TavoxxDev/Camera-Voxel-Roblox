from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import cv2, threading, time, requests, numpy as np

app = Flask(__name__)
CORS(app)

GRID = 96
FPS = 20
MODE = "color"
TIMEOUT = 2

GITHUB_USER = "SrBolasGrandes"
GITHUB_REPO = "Camera-Voxel-Roblox"
VIDEOS_PATH = "videos"
BRANCH = "main"

FALLBACK_URL = "https://raw.githubusercontent.com/SrBolasGrandes/Camera-Voxel-Roblox/refs/heads/main/262%20Sem%20T%C3%ADtulo_20260101105003.png"

frame_data = {"ready": False, "data": []}
last_frame_time = 0
lock = threading.Lock()
video_cap = None
video_paused = False

def image_to_pixels(img):
    img = cv2.resize(img, (GRID, GRID))
    out = []
    for y in range(GRID):
        for x in range(GRID):
            b, g, r = img[y, x]
            out.append([int(r), int(g), int(b)])
    return out

def load_fallback():
    r = requests.get(FALLBACK_URL)
    img = np.frombuffer(r.content, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    return image_to_pixels(img)

FALLBACK_PIXELS = load_fallback()

def watchdog():
    while True:
        time.sleep(0.1)
        with lock:
            if time.time() - last_frame_time > TIMEOUT:
                frame_data["data"] = FALLBACK_PIXELS
                frame_data["ready"] = False

threading.Thread(target=watchdog, daemon=True).start()

def process_frame(frame):
    if MODE == "bw":
        g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    return image_to_pixels(frame)

def video_loop():
    global video_cap, video_paused, last_frame_time
    while True:
        time.sleep(1 / FPS)
        if video_cap and not video_paused:
            ok, frame = video_cap.read()
            if not ok:
                video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            pixels = process_frame(frame)
            with lock:
                frame_data["data"] = pixels
                frame_data["ready"] = True
                last_frame_time = time.time()

threading.Thread(target=video_loop, daemon=True).start()

@app.route("/camera")
def camera():
    return render_template("camera.html")

@app.route("/video")
def video():
    return render_template("video.html")

@app.route("/videosList")
def videos_list():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{VIDEOS_PATH}?ref={BRANCH}"
    r = requests.get(url).json()
    videos = []
    for f in r:
        if f["name"].lower().endswith((".mp4", ".webm", ".mov", ".avi")):
            videos.append({
                "name": f["name"],
                "url": f["download_url"]
            })
    return jsonify(videos)

@app.route("/playVideo", methods=["POST"])
def play_video():
    global video_cap, video_paused
    video_paused = False
    video_cap = cv2.VideoCapture(request.json["url"])
    return "ok"

@app.route("/pauseVideo", methods=["POST"])
def pause_video():
    global video_paused
    video_paused = True
    return "ok"

@app.route("/resumeVideo", methods=["POST"])
def resume_video():
    global video_paused
    video_paused = False
    return "ok"

@app.route("/cameraGet")
def camera_get():
    with lock:
        return jsonify(frame_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
