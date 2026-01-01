from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import base64, io, time, requests

app = Flask(__name__)
CORS(app)

GRID = 96
TIMEOUT = 3

last_frame = None
last_time = 0

FALLBACK = "https://raw.githubusercontent.com/SrBolasGrandes/Camera-Voxel-Roblox/refs/heads/main/262%20Sem%20T%C3%ADtulo_20260101105003.png"

def load_fallback():
    global last_frame
    r = requests.get(FALLBACK)
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    img = img.resize((GRID,GRID))
    last_frame = list(img.getdata())

@app.route("/")
def home():
    return render_template("camera.html")

@app.route("/camera", methods=["POST"])
def camera():
    global last_frame, last_time

    raw = base64.b64decode(request.json["image"])
    mode = request.json.get("mode","color")

    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img = img.resize((GRID,GRID))
    pixels = list(img.getdata())

    if mode == "bw":
        pixels = [(l:=int(r*0.299+g*0.587+b*0.114),l,l) for r,g,b in pixels]

    last_frame = pixels
    last_time = time.time()

    return jsonify(ok=True)

@app.route("/cameraGet")
def get():
    global last_frame
    if last_frame is None or time.time() - last_time > TIMEOUT:
        load_fallback()

    return jsonify(
        ready=True,
        size=GRID,
        data=last_frame
    )

if __name__ == "__main__":
    app.run()
