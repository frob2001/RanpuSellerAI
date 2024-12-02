import requests
from flask import Flask, request, render_template
import logging
from config import config
from routes import lithophane_bp
from services import get_chatgpt_response

# Inicialización de la aplicación Flask
app = Flask(__name__)
app.config.from_object(config['production'])

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables de entorno
user_access_token = app.config['USER_ACCESS_TOKEN']
instagram_account_id = app.config['INSTAGRAM_ACCOUNT_ID']
graph_api_version = app.config['GRAPH_API_VERSION']

# URLs de la API de Facebook Graph
accounts_url = f'https://graph.facebook.com/{graph_api_version}/me/accounts'
messages_url = f'https://graph.facebook.com/{graph_api_version}/me/messages'

# Variable global para el Page Access Token
page_access_token = ''

def obtener_page_access_token():
    """Obtiene y actualiza el Page Access Token."""
    global page_access_token
    try:
        response = requests.get(accounts_url, params={'access_token': user_access_token})
        response.raise_for_status()
        for account in response.json().get('data', []):
            if account['id'] == instagram_account_id:
                page_access_token = account.get('access_token')
                logger.info("Page Access Token actualizado exitosamente.")
                return True
        logger.error("Cuenta de Instagram no encontrada en me/accounts.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener Page Access Token: {e}")
    return False

def enviar_mensaje(recipient_id, message_text):
    """Envía un mensaje al destinatario especificado."""
    headers = {
        'Authorization': f'Bearer {page_access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text},
        'messaging_type': 'RESPONSE'
    }
    try:
        response = requests.post(messages_url, headers=headers, json=data)
        if response.status_code == 200:
            logger.info(f"Mensaje enviado a {recipient_id}")
        else:
            logger.warning(f"Error {response.status_code} al enviar mensaje: {response.text}")
            if response.status_code in [401, 403]:
                logger.info("Intentando renovar el Page Access Token...")
                if obtener_page_access_token():
                    headers['Authorization'] = f'Bearer {page_access_token}'
                    retry_response = requests.post(messages_url, headers=headers, json=data)
                    if retry_response.status_code == 200:
                        logger.info(f"Mensaje reenviado exitosamente a {recipient_id}")
                    else:
                        logger.error(f"Error tras renovar el token: {retry_response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al enviar mensaje: {e}")

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verifica el webhook para la integración."""
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == 'mi_token_de_verificacion':
        logger.info("Webhook verificado exitosamente.")
        return request.args.get('hub.challenge'), 200
    logger.warning("Error en la verificación del webhook.")
    return "Error de verificación", 403

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Maneja los eventos recibidos desde el webhook."""
    data = request.json
    if data and 'entry' in data:
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                sender_id = messaging_event.get('sender', {}).get('id')
                if sender_id and sender_id != "17841451060597045" and 'message' in messaging_event:
                    message_text = messaging_event['message'].get('text')
                    if message_text:
                        logger.info(f"Nuevo mensaje de {sender_id}: {message_text}")
                        respuesta = get_chatgpt_response(message_text, sender_id)
                        enviar_mensaje(sender_id, respuesta)
        return "OK", 200
    logger.warning("Datos inválidos recibidos en el webhook.")
    return "Error: No se pudo procesar el webhook", 400

@app.route('/')
def home():
    """Renderiza la página principal."""
    return render_template('index.html')

# Registro de rutas adicionales
app.register_blueprint(lithophane_bp)

if __name__ == '__main__':
    if obtener_page_access_token():
        app.run(port=5000)
    else:
        logger.critical("No se pudo inicializar el Page Access Token. La aplicación no se iniciará.")
