import requests
from flask import Flask, request, render_template
import logging
from config import config
from routes import lithophane_bp
from services import (
    #Chatgpt Service
    get_chatgpt_response,

    enviar_mensaje, 
    renovar_page_access_token
)

app = Flask(__name__)

# Configuration in production mode
app.config.from_object(config['production'])

# Logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#Enviroment variables from config
app_id = app.config['FACEBOOK_APP_ID']
app_secret = app.config['FACEBOOK_APP_SECRET']
user_access_token = app.config['USER_ACCESS_TOKEN']
instagram_account_id = app.config['INSTAGRAM_ACCOUNT_ID']
graph_api_version = app.config['GRAPH_API_VERSION']

# URLs for Facebook Graph API
messages_url = f'https://graph.facebook.com/{graph_api_version}/me/messages'
accounts_url = f'https://graph.facebook.com/{graph_api_version}/me/accounts'

# Variables globales para el token de acceso y el ID de Instagram
page_access_token = '' #SE GENERA AUTOMATICAMENTE DEPENDE DE USER_ACCESS_TOKEN

# Verificación inicial del webhook
@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == 'mi_token_de_verificacion':
        logger.info("Webhook verificado exitosamente.")
        return challenge, 200
    else:
        logger.warning("Fallo en la verificación del webhook.")
        return "Error de verificación", 403

# Manejo de notificaciones de mensajes de Instagram (POST)
# Función que maneja la recepción de mensajes de Instagram
@app.route('/webhook', methods=['POST'])
def webhook():
    logger.info("Solicitud POST recibida en /webhook")
    data = request.json
    logger.debug(f"Datos recibidos: {data}")

    if data and 'entry' in data:
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                sender = messaging_event.get('sender', {})
                sender_id = sender.get('id')

                # Ignorar mensajes provenientes del ID del bot
                if sender_id == "17841451060597045":
                    logger.warning(f"Mensaje recibido del bot (ID: {sender_id}). Ignorando...")
                    continue

                if sender_id and 'message' in messaging_event:
                    message = messaging_event['message']
                    message_text = message.get('text')
                    if message_text:
                        logger.info(f"Nuevo mensaje de {sender_id}: {message_text}")
                        # Llama a get_chatgpt_response pasando sender_id para mantener la conversación
                        respuesta_chatgpt = get_chatgpt_response(message_text, sender_id)
                        enviar_mensaje(sender_id, respuesta_chatgpt)
        return "OK", 200
    else:
        logger.warning("Datos inválidos recibidos en el webhook.")
        return "Error: No se pudo procesar el webhook", 400

#Rutas para litofanias
app.register_blueprint(lithophane_bp)

# Página principal
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    renovar_page_access_token()  # Inicializar los tokens al iniciar la aplicación
    if page_access_token:
        app.run(port=5000)
    else:
        logger.critical("No se pudo inicializar el Page Access Token. La aplicación no se iniciará.")
