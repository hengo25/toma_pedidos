from app import app as application # importa tu aplicación web
from api import server as application  # importa tu API REST

# ⚡ Combinar: montar la API dentro de la app principal
app.wsgi_app = server.wsgi_app

# 👉 Este será el objeto que Gunicorn usará
application = app

