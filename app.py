from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import base64, io, time, requests, threading

app = Flask(__name__)
CORS(app)

GRID = 64
FPS = 10
TIMEOUT = 5

camera_frame = None
anime_frame = None
camera_time = 0
anime_time = 0

fallback_pixels = None

FALLBACK_IMG = "https://raw.githubusercontent.com/SrBolasGrandes/Camera-Voxel-Roblox/main/262%20Sem%20T%C3%ADtulo_20260101105003.png"

def img_to_pixels(img):
    img = img.resize((GRID, GRID))
    return list(img.getdata())

def load_fallback_once():
    global fallback_pixels
    r = requests.get(FALLBACK_IMG, timeout=10)
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    fallback_pixels = img_to_pixels(img)

load_fallback_once()

@app.route("/")
def camera_page():
    return render_template("camera.html")

@app.route("/anime")
def anime_page():
    return render_template("anime.html")

@app.route("/camera", methods=["POST"])
def camera_post():
    global camera_frame, camera_time
    raw = base64.b64decode(request.json["image"])
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    camera_frame = img_to_pixels(img)
    camera_time = time.time()
    return jsonify(ok=True)

@app.route("/animeFrame", methods=["POST"])
def anime_post():
    global anime_frame, anime_time
    raw = base64.b64decode(request.json["image"])
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    anime_frame = img_to_pixels(img)
    anime_time = time.time()
    return jsonify(ok=True)

@app.route("/cameraGet")
def camera_get():
    if camera_frame and time.time() - camera_time < TIMEOUT:
        return jsonify(size=GRID, data=camera_frame)
    return jsonify(size=GRID, data=fallback_pixels)

@app.route("/animeGet")
def anime_get():
    if anime_frame and time.time() - anime_time < TIMEOUT:
        return jsonify(size=GRID, data=anime_frame)
    return jsonify(size=GRID, data=fallback_pixels)

if __name__ == "__main__":
    app.run()
