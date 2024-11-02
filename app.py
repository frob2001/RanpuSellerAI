import requests
from flask import Flask, request, render_template
from chatgpt import obtener_respuesta_chatgpt 
import logging

app = Flask(__name__)

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Datos de tu aplicación
app_id = '1560936227863673'
app_secret = '432eda601cb78df51bc55d2bf79d9f3e'
app_access_token = 'EAAWLqclgZCHkBOZBZBrasdB3PiUgo2bwmbTY8Ox9ZCskHw2s7raqTMf9ZC2HxiwrT1bNyZCMY6vcoHRq7Ao4zg2SeiU5yslBIqW01O0KmWu4TZC1Xn5ZB9ZABEGIjvwq0rDTuZAYIEQDSsAXtDdm4ZBisMwASxrlZBHl50PV4f2oVqfUOMERrs0o87qZAV0WB9MGHxWJW0Sp9C5wb7rJLKJBuio8ZD'

# Variables globales para el token de acceso y el ID de Instagram
page_access_token = 'EAAWLqclgZCHkBO0Oyy3veuu6dfZCLWp4DtR6ZCl4ccZA7NJBH1TH5vJFm0GHmZBxyFwSkncXWC8MjN2KOICzwNcP1FPIhtPRfge9IYjrgyFBE6dAnyZA7bZCfAaa2QBDnT7fSqYYEvnCgx66BZC8Lip2MNZCn5duXNAoYtvf0LGKxwzUbnoZAfz4jwC3Q5S5jMnZC878k6E8Ix4JH36Yc5pzTpc2IZB3QJ6y'
instagram_account_id = '108165015152868'
url = f'https://graph.facebook.com/v12.0/me/messages'

# Función para obtener un token de larga duración
def get_long_lived_token():
    global page_access_token
    token_url = "https://graph.facebook.com/v12.0/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': app_access_token
    }
    try:
        response = requests.get(token_url, params=params)
        response.raise_for_status()
        token_data = response.json()

        if 'access_token' in token_data:
            page_access_token = token_data['access_token']
            logger.info("Nuevo token de larga duración obtenido.")
        else:
            logger.error(f"Error al obtener el token de larga duración: {token_data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Solicitud fallida al obtener el token de larga duración: {e}")

# Función para obtener el Page Access Token desde me/accounts
def obtener_page_access_token():
    global page_access_token
    accounts_url = "https://graph.facebook.com/v12.0/me/accounts"
    params = {
        'access_token': page_access_token
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
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            logger.info(f"Mensaje enviado correctamente a {recipient_id}")
        elif response.status_code in [400, 401, 403]:
            logger.warning(f"Error al enviar mensaje: {response.status_code}, {response.text}")
            logger.info("Intentando renovar el Page Access Token...")
            if renovar_page_access_token():
                # Reintentar enviar el mensaje con el nuevo token
                headers['Authorization'] = f'Bearer {page_access_token}'
                retry_response = requests.post(url, headers=headers, json=data)
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

# Función para renovar el Page Access Token
def renovar_page_access_token():
    """
    Renueva el Page Access Token obteniendo uno nuevo desde me/accounts.
    """
    # Primero, obtener un token de larga duración
    get_long_lived_token()
    
    # Luego, obtener el nuevo Page Access Token
    return obtener_page_access_token()

# Manejo de notificaciones de mensajes de Instagram (POST)
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
                if sender_id and 'message' in messaging_event:
                    message = messaging_event['message']
                    message_text = message.get('text')
                    if message_text:
                        logger.info(f"Nuevo mensaje de {sender_id}: {message_text}")
                        respuesta_chatgpt = obtener_respuesta_chatgpt(message_text)
                        enviar_mensaje(sender_id, respuesta_chatgpt)
        return "OK", 200
    else:
        logger.warning("Datos inválidos recibidos en el webhook.")
        return "Error: No se pudo procesar el webhook", 400

# Página principal
@app.route('/')
def home():
    return render_template('index.html')

# Llamada inicial para obtener el token de larga duración y el Page Access Token
def inicializar_tokens():
    get_long_lived_token()  # Obtener el token de larga duración
    if obtener_page_access_token():  # Obtener el Page Access Token
        logger.info("Inicialización de tokens completada.")
    else:
        logger.error("Fallo en la inicialización de tokens.")

if __name__ == '__main__':
    inicializar_tokens()  # Inicializar los tokens al iniciar la aplicación
    if page_access_token:
        app.run(port=5000)
    else:
        logger.critical("No se pudo inicializar el Page Access Token. La aplicación no se iniciará.")
