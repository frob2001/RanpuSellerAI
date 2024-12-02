from flask import Blueprint, request, current_app
import requests
import logging
from services import get_chatgpt_response  # Importar tu servicio para ChatGPT

# Crear el Blueprint
webhook_bp = Blueprint('webhook', __name__)
logger = logging.getLogger(__name__)

# Función auxiliar para obtener el Page Access Token
def obtener_page_access_token():
    user_access_token = current_app.config['USER_ACCESS_TOKEN']
    instagram_account_id = current_app.config['INSTAGRAM_ACCOUNT_ID']
    accounts_url = f"https://graph.facebook.com/{current_app.config['GRAPH_API_VERSION']}/me/accounts"

    try:
        params = {'access_token': user_access_token}
        response = requests.get(accounts_url, params=params)
        response.raise_for_status()
        accounts_data = response.json()
        for account in accounts_data.get('data', []):
            if account['id'] == instagram_account_id:
                return account.get('access_token')
        logger.error("No se encontró la cuenta de Instagram especificada.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener Page Access Token: {e}")
    return None

# Ruta para la verificación inicial del webhook
@webhook_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == current_app.config.get('VERIFY_TOKEN'):
        logger.info("Webhook verificado exitosamente.")
        return challenge, 200
    else:
        logger.warning("Fallo en la verificación del webhook.")
        return "Error de verificación", 403

# Ruta para manejar eventos de mensajes
@webhook_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    logger.info("Solicitud POST recibida en /webhook")
    data = request.json
    logger.debug(f"Datos recibidos: {data}")

    if data and 'entry' in data:
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                sender = messaging_event.get('sender', {})
                sender_id = sender.get('id')

                # Ignorar mensajes provenientes del ID del bot
                if sender_id == current_app.config.get('BOT_ID'):
                    logger.warning(f"Mensaje recibido del bot (ID: {sender_id}). Ignorando...")
                    continue

                if sender_id and 'message' in messaging_event:
                    message = messaging_event['message']
                    message_text = message.get('text')
                    if message_text:
                        logger.info(f"Nuevo mensaje de {sender_id}: {message_text}")
                        respuesta_chatgpt = get_chatgpt_response(message_text, sender_id)
                        enviar_mensaje(sender_id, respuesta_chatgpt)
        return "OK", 200
    else:
        logger.warning("Datos inválidos recibidos en el webhook.")
        return "Error: No se pudo procesar el webhook", 400

# Función auxiliar para enviar mensajes
def enviar_mensaje(recipient_id, message_text):
    page_access_token = obtener_page_access_token()
    if not page_access_token:
        logger.error("No se pudo obtener el Page Access Token.")
        return

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
        response = requests.post(current_app.config['MESSAGES_URL'], headers=headers, json=data)
        if response.status_code == 200:
            logger.info(f"Mensaje enviado correctamente a {recipient_id}")
        else:
            logger.error(f"Error al enviar mensaje: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error en la solicitud para enviar mensaje: {e}")
