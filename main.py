from flask import Flask

# Crear la app Flask
app = Flask(__name__)

# Ruta de prueba
@app.route("/")
def home():
    return "🚀 ¡Hola Render desde Flask!"

# Objeto que Gunicorn usará
application = app

# Solo se usa si corres localmente con `python main.py`
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



