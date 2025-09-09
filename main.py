from app import app
from api import server

# Montar la API dentro de la app principal
app.wsgi_app = server.wsgi_app

# Objeto que Gunicorn usará
application = app


