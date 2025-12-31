from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import base64, io

app = Flask(__name__)
CORS(app)

last_frame = None
GRID = 64

@app.route("/")
def home():
    return render_template("camera.html")

@app.route("/camera", methods=["POST"])
def camera():
    global last_frame
    try:
        print("FRAME RECEBIDO")
        img_data = base64.b64decode(request.json["image"])
        img = Image.open(io.BytesIO(img_data)).convert("L")
        img = img.resize((GRID, GRID))
        pixels = list(img.getdata())

        fixed = []
        for v in pixels:
            if v < 20:
                v = 20
            fixed.append(v)

        last_frame = fixed
        return jsonify({"ok": True})
    except Exception as e:
        print("ERRO:", e)
        return jsonify({"error": str(e)}), 400

@app.route("/cameraGet")
def camera_get():
    if last_frame is None:
        return jsonify({"ready": False})

    data = []
    for v in last_frame:
        depth = int((255 - v) / 255 * 20)
        data.append([v, depth])

    return jsonify({"ready": True, "data": data})
