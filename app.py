from flask import Flask, request, render_template
from routes import lithophane_bp, webhook_bp, inicializar_tokens, page_access_token

app = Flask(__name__)


# # Si necesitas valores específicos, accede directamente a las variables
# app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Función para obtener el Page Access Token desde me/accounts

#Rutas para litofanias
app.register_blueprint(webhook_bp)
app.register_blueprint(lithophane_bp)

# Página principal
@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    inicializar_tokens()  # Inicializar los tokens al iniciar la aplicación
    if page_access_token:
        app.run(port=5000)
    else:
        print("ERROR: No se pudo inicializar el Page Access Token. La aplicación no se iniciará.")
