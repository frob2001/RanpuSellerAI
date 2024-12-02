from flask import Flask, render_template
import logging
from config import config
from routes import lithophane_bp, webhook_bp
from services import get_chatgpt_response

app = Flask(__name__)

# Configuración en modo producción
app.config.from_object(config['production'])

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Registro de Blueprints
app.register_blueprint(lithophane_bp)
app.register_blueprint(webhook_bp)

# Página principal
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5000)
