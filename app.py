from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import base64, io

app = Flask(__name__)
CORS(app)

GRID = 96
last_frame = None

@app.route("/")
def home():
    return render_template("camera.html")

@app.route("/camera", methods=["POST"])
def camera():
    global last_frame

    img_data = base64.b64decode(request.json["image"])
    img = Image.open(io.BytesIO(img_data)).convert("RGB")
    img = img.resize((GRID, GRID))

    last_frame = list(img.getdata())
    return jsonify({"ok": True})

@app.route("/cameraGet")
def camera_get():
    if last_frame is None:
        return jsonify({"ready": False})

    return jsonify({
        "ready": True,
        "size": GRID,
        "data": last_frame
    })

if __name__ == "__main__":
    app.run()
