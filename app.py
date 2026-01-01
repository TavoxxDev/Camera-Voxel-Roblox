from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import base64, io, time, requests

app = Flask(__name__)
CORS(app)

GRID = 96
TIMEOUT = 2.0

last_frame = None
last_time = 0
last_smile = False

FALLBACK_IMAGE_URL = "https://raw.githubusercontent.com/SrBolasGrandes/Camera-Voxel-Roblox/refs/heads/main/262%20Sem%20T%C3%ADtulo_20260101105003.png"

def load_fallback():
    global last_frame
    r = requests.get(FALLBACK_IMAGE_URL, timeout=5)
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    img = img.resize((GRID, GRID), Image.BILINEAR)
    last_frame = list(img.getdata())

@app.route("/")
def home():
    return render_template("camera.html")

@app.route("/camera", methods=["POST"])
def camera():
    global last_frame, last_time, last_smile

    mode = request.json.get("mode", "color")
    smiling = request.json.get("smiling", False)
    raw = base64.b64decode(request.json["image"])

    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img = img.resize((GRID, GRID), Image.BILINEAR)

    pixels = list(img.getdata())

    if mode == "bw":
        pixels = [
            (l := int(r*0.299 + g*0.587 + b*0.114), l, l)
            for r, g, b in pixels
        ]

    last_frame = pixels
    last_smile = smiling
    last_time = time.time()

    return jsonify(ok=True)

@app.route("/cameraGet")
def camera_get():
    global last_frame

    if last_frame is None or time.time() - last_time > TIMEOUT:
        load_fallback()

    if last_frame is None:
        return jsonify(ready=False)

    return jsonify(
        ready=True,
        size=GRID,
        data=last_frame,
        smiling=last_smile
    )

if __name__ == "__main__":
    app.run()
