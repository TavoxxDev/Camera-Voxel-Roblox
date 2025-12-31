from flask import Flask, request, jsonify
from PIL import Image, ImageEnhance
import base64, io

app = Flask(__name__)
last_frame = None
GRID = 32

@app.route("/camera", methods=["POST"])
def camera():
    global last_frame
    img_data = base64.b64decode(request.json["image"])
    img = Image.open(io.BytesIO(img_data))

    img = img.resize((GRID, GRID))
    img = img.convert("L")

    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.5)

    pixels = list(img.getdata())

    min_v = min(pixels)
    max_v = max(pixels)
    norm = []

    for v in pixels:
        if max_v - min_v == 0:
            n = 0
        else:
            n = int((v - min_v) / (max_v - min_v) * 255)
        norm.append(n)

    last_frame = norm
    return jsonify({"ok": True})

@app.route("/cameraGet", methods=["GET"])
def camera_get():
    if last_frame is None:
        return jsonify({"ready": False})

    data = []
    for v in last_frame:
        depth = int((255 - v) / 255 * 20)
        data.append([v, depth])

    return jsonify({"ready": True, "data": data})

app.run(host="0.0.0.0", port=5000)
