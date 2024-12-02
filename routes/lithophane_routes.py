import requests
import logging
from config import config
from flask import Blueprint, request
from services import get_chatgpt_response

webhook_bp = Blueprint('webhook', __name__)
webhook_bp.config.from_object(config['production'])

# Logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#Enviroment variables from config
app_id = webhook_bp.config['FACEBOOK_APP_ID']
app_secret = webhook_bp.config['FACEBOOK_APP_SECRET']
user_access_token = webhook_bp.config['USER_ACCESS_TOKEN']
instagram_account_id = webhook_bp.config['INSTAGRAM_ACCOUNT_ID']
graph_api_version = webhook_bp.config['GRAPH_API_VERSION']

# URLs for Facebook Graph API
messages_url = f'https://graph.facebook.com/{graph_api_version}/me/messages'
accounts_url = f'https://graph.facebook.com/{graph_api_version}/me/accounts'

# Variables globales para el token de acceso y el ID de Instagram
page_access_token = '' #SE GENERA AUTOMATICAMENTE DEPENDE DE USER_ACCESS_TOKEN

def obtener_page_access_token():
    global page_access_token
    params = {
        'access_token': user_access_token
    }
    try:
        response = requests.get(accounts_url, params=params)
        response.raise_for_status()
        accounts_data = response.json()
        for account in accounts_data.get('data', []):
            if account['id'] == instagram_account_id:
                new_page_access_token = account.get('access_token')
                if new_page_access_token:
                    page_access_token = new_page_access_token
                    logger.info("Page Access Token actualizado exitosamente.")
                    return True
        logger.error("No se encontró la cuenta de Instagram especificada en me/accounts.")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Solicitud fallida al obtener Page Access Token: {e}")
        return False

# Función para renovar el Page Access Token
def renovar_page_access_token():
    if obtener_page_access_token():
        logger.info("Renovación de Page Access Token completada.")
        return True
    logger.error("No se pudo renovar el Page Access Token.")
    return False

# Verificación inicial del webhook
@webhook_bp.route('/webhook', methods=['GET'])
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

# Función para enviar mensajes
def enviar_mensaje(recipient_id, message_text):
    global page_access_token
    
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
            logger.info(f"Mensaje enviado correctamente a {recipient_id}")
        elif response.status_code in [400, 401, 403]:
            logger.warning(f"Error al enviar mensaje: {response.status_code}, {response.text} a {recipient_id}")
            logger.info("Intentando renovar el Page Access Token...")
            if renovar_page_access_token():
                # Reintentar enviar el mensaje con el nuevo token
                headers['Authorization'] = f'Bearer {page_access_token}'
                retry_response = requests.post(messages_url, headers=headers, json=data)
                if retry_response.status_code == 200:
                    logger.info(f"Mensaje enviado correctamente a {recipient_id} tras renovar el token.")
                else:
                    logger.error(f"Error al enviar mensaje tras renovar el token: {retry_response.status_code}, {retry_response.text}")
            else:
                logger.error("No se pudo renovar el Page Access Token.")
        else:
            logger.error(f"Error inesperado al enviar mensaje: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Solicitud fallida al enviar mensaje: {e}")

# Manejo de notificaciones de mensajes de Instagram (POST)
# Función que maneja la recepción de mensajes de Instagram
@webhook_bp.route('/webhook', methods=['POST'])
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


# Llamada inicial para obtener Page Access Token
def inicializar_tokens():
    if obtener_page_access_token():
        logger.info("Inicialización de tokens completada.")
    else:
        logger.error("Fallo al obtener el Page Access Token durante la inicialización.")