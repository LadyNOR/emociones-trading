from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/analizar-emocion", methods=["POST"])
def analizar_emocion():
    if "audio" not in request.files:
        return jsonify({"error": "No se proporcionó el archivo de audio"}), 400

    archivo = request.files["audio"]
    if archivo.filename == "":
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    nombre_seguro = secure_filename(archivo.filename)
    ruta_completa = os.path.join(UPLOAD_FOLDER, nombre_seguro)
    archivo.save(ruta_completa)

    emocion_detectada = "estrés"  # Simulación del análisis
    return jsonify({"emocion": emocion_detectada})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)