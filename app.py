from flask import Flask, request, jsonify
from PIL import Image
import base64
import io

app = Flask(__name__)
last_frame = None
GRID = 32

@app.route("/camera", methods=["POST"])
def camera():
    global last_frame
    data = request.json
    image_data = base64.b64decode(data["image"])
    img = Image.open(io.BytesIO(image_data))
    img = img.resize((GRID, GRID))
    img = img.convert("L")
    last_frame = list(img.getdata())
    return jsonify({"ok": True})

@app.route("/cameraGet", methods=["GET"])
def camera_get():
    if last_frame is None:
        return jsonify({"ready": False})

    data = []
    for v in last_frame:
        depth = int((255 - v) / 255 * 20)
        data.append([v, depth])

    return jsonify({
        "ready": True,
        "data": data
    })

app.run(host="0.0.0.0", port=5000)
