from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

CORS(app, origins=[
    "https://azizabada10.github.io",
    "http://localhost",
    "http://127.0.0.1"
])

UPLOAD_FOLDER = "images"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/upload", methods=["POST"])
def upload():
    if 'image' not in request.files:
        return jsonify({"error": "Aucun fichier envoyé"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "Aucun fichier sélectionné"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    return jsonify({
        "message": "image uploaded",
        "url": f"/images/{filename}"
    })

@app.route("/images", methods=["GET"])
def list_images():
    files = os.listdir(UPLOAD_FOLDER)
    images = [f for f in files if f.lower().endswith(('.png','.jpg','.jpeg','.gif','.webp'))]
    return jsonify(images)

@app.route("/images/<filename>", methods=["GET"])
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(
        host="10.66.66.84",
        port=5000,
        ssl_context="adhoc"   
    )