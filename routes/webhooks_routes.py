from flask import Blueprint, request, current_app
import requests
import logging
from services import get_chatgpt_response

# Crear el Blueprint
webhook_bp = Blueprint('webhook', __name__)

# Configuración de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables globales para el token de acceso y el ID de Instagram
page_access_token = ''  # Se genera automáticamente usando USER_ACCESS_TOKEN


def obtener_page_access_token():
    """Obtiene y actualiza el Page Access Token."""
    global page_access_token
    user_access_token = current_app.config['USER_ACCESS_TOKEN']
    instagram_account_id = current_app.config['INSTAGRAM_ACCOUNT_ID']
    accounts_url = f"https://graph.facebook.com/{current_app.config['GRAPH_API_VERSION']}/me/accounts"

    params = {'access_token': user_access_token}
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
        logger.error(f"Error al obtener Page Access Token: {e}")
        return False


def renovar_page_access_token():
    """Renueva el Page Access Token si es necesario."""
    if obtener_page_access_token():
        logger.info("Renovación de Page Access Token completada.")
        return True
    logger.error("No se pudo renovar el Page Access Token.")
    return False


@webhook_bp.route('/webhook', methods=['GET'])
def verify():
    """Verificación inicial del Webhook."""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == 'mi_token_de_verificacion':
        logger.info("Webhook verificado exitosamente.")
        return challenge, 200
    else:
        logger.warning("Fallo en la verificación del webhook.")
        return "Error de verificación", 403


@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """Manejo de notificaciones de mensajes de Instagram."""
    logger.info("Solicitud POST recibida en /webhook")
    data = request.json
    logger.debug(f"Datos recibidos: {data}")

    if data and 'entry' in data:
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                sender = messaging_event.get('sender', {}).get('id')
                if sender and sender != "17841451060597045":  # Ignorar mensajes del bot
                    message_text = messaging_event['message'].get('text')
                    if message_text:
                        respuesta_chatgpt = get_chatgpt_response(message_text, sender)
                        enviar_mensaje(sender, respuesta_chatgpt)
        return "OK", 200
    else:
        logger.warning("Datos inválidos recibidos en el webhook.")
        return "Error: No se pudo procesar el webhook", 400


def enviar_mensaje(recipient_id, message_text):
    """Envía un mensaje a un usuario de Instagram."""
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
        response = requests.post(
            f"https://graph.facebook.com/{current_app.config['GRAPH_API_VERSION']}/me/messages",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            logger.info(f"Mensaje enviado correctamente a {recipient_id}")
        else:
            logger.error(f"Error al enviar mensaje: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Solicitud fallida al enviar mensaje: {e}")


def inicializar_tokens():
    """Inicializa los tokens necesarios."""
    if obtener_page_access_token():
        logger.info("Tokens inicializados correctamente.")
    else:
        logger.error("Error al inicializar los tokens.")
