from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)

# Sécurité : Restreindre les origines CORS (déjà bien configuré)
CORS(app, origins=[
    "https://azizabada10.github.io",
    "http://localhost",
    "http://127.0.0.1"
])

# Sécurité : Limiter la taille maximale d'upload (ex: 5 Mo)
# Cela protège contre les attaques de déni de service (DoS) par saturation d'espace
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

UPLOAD_FOLDER = "images"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload():
    # Vérification de la présence du fichier dans la requête
    if 'image' not in request.files:
        return jsonify({"error": "Aucun fichier envoyé"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "Aucun fichier sélectionné"}), 400

    if file and allowed_file(file.filename):
        # Sécurité : nettoyer le nom du fichier d'origine
        original_filename = secure_filename(file.filename)
        
        # Optimisation & Sécurité : Utiliser un UUID pour renommer le fichier
        # Cela évite les collisions (écrasement de fichiers du même nom) et masque les noms originaux
        extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_filename = f"{uuid.uuid4().hex}.{extension}"
        
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)

        return jsonify({
            "message": "Image téléchargée avec succès",
            "url": f"/images/{unique_filename}",
            "original_name": original_filename
        }), 201
    else:
        return jsonify({"error": "Type de fichier non autorisé"}), 400

@app.route("/images", methods=["GET"])
def list_images():
    try:
        files = os.listdir(UPLOAD_FOLDER)
        # Sécurité : Ne lister que les fichiers avec une extension autorisée
        images = [f for f in files if allowed_file(f)]
        return jsonify(images)
    except Exception as e:
        return jsonify({"error": "Erreur lors de la récupération des images"}), 500

@app.route("/images/<filename>", methods=["GET"])
def get_image(filename):
    # Sécurité : send_from_directory empêche déjà la faille de Path Traversal
    # Ajout d'une vérification d'extension pour plus de sécurité
    if allowed_file(filename):
         return send_from_directory(UPLOAD_FOLDER, filename)
    return jsonify({"error": "Fichier non trouvé ou non autorisé"}), 404

# Gestionnaire d'erreur si la taille du fichier dépasse MAX_CONTENT_LENGTH
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "Le fichier est trop volumineux (limite : 5MB)"}), 413

if __name__ == "__main__":
    app.run(
        host="10.66.66.84",
        port=5000,
        ssl_context="adhoc"   
    )