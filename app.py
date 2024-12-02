from flask import Flask, render_template
from routes.webhooks_routes import webhook_bp, inicializar_tokens, page_access_token
from routes.lithophane_routes import lithophane_bp
from config import config

app = Flask(__name__)

# Cargar configuración de entorno
app.config.from_object(config['production'])

# Registrar Blueprints
app.register_blueprint(webhook_bp)
app.register_blueprint(lithophane_bp)

@app.route('/')
def home():
    """Página principal."""
    return render_template('index.html')

if __name__ == '__main__':
    inicializar_tokens()
    if page_access_token:
        app.run(port=5000)
    else:
        print("ERROR: No se pudo inicializar el Page Access Token. La aplicación no se iniciará.")
