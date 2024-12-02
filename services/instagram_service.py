import requests
import logging
from config import config

# Logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables from config
app_id = config['production']['FACEBOOK_APP_ID']
app_secret = config['production']['FACEBOOK_APP_SECRET']
user_access_token = config['production']['USER_ACCESS_TOKEN']
instagram_account_id = config['production']['INSTAGRAM_ACCOUNT_ID']
graph_api_version = config['production']['GRAPH_API_VERSION']

# URLs for Facebook Graph API
messages_url = f'https://graph.facebook.com/{graph_api_version}/me/messages'
accounts_url = f'https://graph.facebook.com/{graph_api_version}/me/accounts'

# Global variables
page_access_token = ''  # This is dynamically updated


def obtener_page_access_token():
    global page_access_token
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
        logger.error(f"Solicitud fallida al obtener Page Access Token: {e}")
        return False


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
            logger.warning(f"Error al enviar mensaje: {response.status_code}, {response.text}")
            logger.info("Intentando renovar el Page Access Token...")
            if renovar_page_access_token():
                headers['Authorization'] = f'Bearer {page_access_token}'
                retry_response = requests.post(messages_url, headers=headers, json=data)
                if retry_response.status_code == 200:
                    logger.info(f"Mensaje enviado correctamente tras renovar el token a {recipient_id}.")
                else:
                    logger.error(f"Error al enviar mensaje tras renovar el token: {retry_response.status_code}")
            else:
                logger.error("No se pudo renovar el Page Access Token.")
        else:
            logger.error(f"Error inesperado al enviar mensaje: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Solicitud fallida al enviar mensaje: {e}")


def renovar_page_access_token():
    if obtener_page_access_token():
        logger.info("Renovación de Page Access Token completada.")
        return True
    logger.error("No se pudo renovar el Page Access Token.")
    return False
