from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pydub import AudioSegment
import numpy as np
import os
import wave
import Vokaturi

# Cargar la librería Vokaturi
Vokaturi.load("OpenVokaturi-3-3-linux64.so")

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

    # Convertir OGG a WAV mono 48kHz
    wav_path = ruta_completa.replace(".ogg", ".wav")
    try:
        audio = AudioSegment.from_file(ruta_completa)
        audio = audio.set_channels(1).set_frame_rate(48000)
        audio.export(wav_path, format="wav")
    except Exception as e:
        return jsonify({"error": f"Error al convertir audio: {str(e)}"}), 500

    # Procesar con Vokaturi
    try:
        with wave.open(wav_path, "rb") as archivo_wav:
            nframes = archivo_wav.getnframes()
            contenido = archivo_wav.readframes(nframes)
            muestras = np.frombuffer(contenido, dtype=np.int16)
            muestras = muestras.astype(np.float32) / 32768.0

            voz = Vokaturi.Voice(48000, len(muestras))
            voz.fill(muestras)

            calidad, emociones = voz.extract()
            voz.destroy()

            if calidad < 0.5:
                emocion_detectada = "no confiable"
            else:
                emocion_detectada = max(emociones, key=emociones.get)
    except Exception as e:
        return jsonify({"error": f"Error al analizar emoción: {str(e)}"}), 500

    return jsonify({"emocion": emocion_detectada})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
