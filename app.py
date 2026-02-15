from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import base64, io, time, requests

app = Flask(__name__)
CORS(app)

GRID = 64
FPS_TIMEOUT = 3

GITHUB_USER = "SrBolasGrandes"
REPO = "Camera-Voxel-Roblox"
MEDIA_PATH = "videos"

FALLBACK_IMAGE = "https://raw.githubusercontent.com/SrBolasGrandes/Camera-Voxel-Roblox/refs/heads/main/262%20Sem%20T%C3%ADtulo_20260101105003.png"

last_frame = None
last_time = 0
current_audio = None

keys_state = {} 

def load_fallback():
    global last_frame
    r = requests.get(FALLBACK_IMAGE)
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    img = img.resize((GRID, GRID))
    last_frame = list(img.getdata())

@app.route("/")
def camera_page():
    return render_template("camera.html")

@app.route("/video")
def video_page():
    return render_template("video.html")

@app.route("/doom")
def doom_page():
    return render_template("doom.html")

@app.route("/videosList")
def videos_list():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/contents/{MEDIA_PATH}"
    r = requests.get(url).json()

    videos = []
    for f in r:
        if f["name"].endswith(".mp4"):
            videos.append({
                "name": f["name"],
                "url": f["download_url"]
            })
    return jsonify(videos)

@app.route("/camera", methods=["POST"])
def camera():
    global last_frame, last_time

    raw = base64.b64decode(request.json["image"])
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img = img.resize((GRID, GRID))

    last_frame = list(img.getdata())
    last_time = time.time()
    return jsonify(ok=True)

@app.route("/foto", methods=["POST"])
def foto():
    global last_frame, last_time

    if "image" not in request.files:
        return jsonify(error="Nenhuma imagem enviada"), 400

    img = Image.open(request.files["image"].stream).convert("RGB")
    img = img.resize((GRID, GRID))

    last_frame = list(img.getdata())
    last_time = time.time()
    return jsonify(ok=True)

@app.route("/cameraGet")
def camera_get():
    if last_frame is None or time.time() - last_time > FPS_TIMEOUT:
        load_fallback()

    return jsonify(
        ready=True,
        size=GRID,
        data=last_frame
    )

@app.route("/setAudio", methods=["POST"])
def set_audio():
    global current_audio
    current_audio = request.json["audio"]
    return jsonify(ok=True)

@app.route("/audioGet")
def audio_get():
    return jsonify(audio=current_audio)

@app.route("/keyDown", methods=["POST"])
def key_down():
    key = request.json.get("key")
    if not key:
        return jsonify(error="Sem tecla"), 400

    keys_state[key.upper()] = True
    return jsonify(ok=True)

@app.route("/keyUp", methods=["POST"])
def key_up():
    key = request.json.get("key")
    if not key:
        return jsonify(error="Sem tecla"), 400

    keys_state[key.upper()] = False
    return jsonify(ok=True)

@app.route("/keyboardGet")
def keyboard_get():
    return jsonify(keys=keys_state)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
