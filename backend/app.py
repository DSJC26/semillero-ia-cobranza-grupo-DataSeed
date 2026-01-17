from flask import Flask, request, jsonify
from flask_cors import CORS
from agente_promesas import ejecutar_agente
import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # aquí la lees
app = Flask(__name__)
CORS(app)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    mensaje = data.get("message", "").strip()

    if not mensaje:
        return jsonify({"error": "Mensaje vacío"}), 400

    try:
        reply = ejecutar_agente(mensaje)
        return jsonify({"reply": reply})
    except Exception as e:
        # Para debug en local
        print("Error en ejecutar_agente:", e)
        return jsonify({"error": "Error interno en el agente"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
