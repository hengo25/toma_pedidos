from app import app   # importa tu aplicación web
from api import server   # importa tu API REST

# ⚡ Combinar: montar la API dentro de la app principal
app.wsgi_app = server.wsgi_app

# 👉 Este será el objeto que Gunicorn usará
application = app
