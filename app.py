import requests
from flask import Flask, request, render_template
from chatgpt import obtener_respuesta_chatgpt 
import time
import logging

app = Flask(__name__)

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Datos de tu aplicación
app_id = '1560936227863673'
app_secret = '432eda601cb78df51bc55d2bf79d9f3e'
short_lived_token = 'EAAWLqclgZCHkBOZBZBrasdB3PiUgo2bwmbTY8Ox9ZCskHw2s7raqTMf9ZC2HxiwrT1bNyZCMY6vcoHRq7Ao4zg2SeiU5yslBIqW01O0KmWu4TZC1Xn5ZB9ZABEGIjvwq0rDTuZAYIEQDSsAXtDdm4ZBisMwASxrlZBHl50PV4f2oVqfUOMERrs0o87qZAV0WB9MGHxWJW0Sp9C5wb7rJLKJBuio8ZD'

# Variables globales para el token de acceso y el ID de Instagram
access_token = None  # Inicialmente no definido
instagram_account_id = '108165015152868'
url = f'https://graph.facebook.com/v12.0/me/messages'

# Variable para almacenar el tiempo de expiración del token
token_expiration_time = None

def get_long_lived_token():
    """
    Obtiene un token de acceso de usuario a largo plazo utilizando el token de corto plazo.
    """
    global access_token, token_expiration_time
    logging.info("Intentando obtener un nuevo access_token de larga duración.")
    
    token_url = "https://graph.facebook.com/v12.0/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': short_lived_token
    }
    
    try:
        response = requests.get(token_url, params=params)
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP 4xx/5xx
        token_data = response.json()

        if 'access_token' in token_data:
            user_long_lived_token = token_data['access_token']
            # Supongamos que el token de larga duración expira en 60 días
            token_expiration_time = time.time() + 60 * 24 * 60 * 60  # 60 días en segundos
            logging.info("Nuevo access_token de usuario a largo plazo obtenido.")
            
            # Obtener el token de página utilizando el token de usuario a largo plazo
            get_page_access_token(user_long_lived_token)
        else:
            logging.error("Error al obtener el token de larga duración: %s", token_data)
            raise ValueError("No se obtuvo access_token en la respuesta.")
    except requests.exceptions.RequestException as e:
        logging.error("Excepción al obtener el access_token de larga duración: %s", e)
        raise

def get_page_access_token(user_access_token):
    """
    Obtiene el token de acceso de la página específica desde /me/accounts utilizando el token de usuario.
    """
    global access_token
    logging.info("Intentando obtener el access_token de la página desde /me/accounts.")

    accounts_url = "https://graph.facebook.com/v12.0/me/accounts"
    params = {
        'access_token': user_access_token
    }

    try:
        response = requests.get(accounts_url, params=params)
        response.raise_for_status()
        accounts_data = response.json()

        # Buscar la página con el ID específico
        pages = accounts_data.get('data', [])
        for page in pages:
            if page.get('id') == instagram_account_id:
                access_token = page.get('access_token')
                logging.info(f"Access token de la página obtenido: {access_token}")
                return

        logging.error(f"No se encontró una página con el ID {instagram_account_id}.")
        raise ValueError(f"No se encontró una página con el ID {instagram_account_id}.")
    except requests.exceptions.RequestException as e:
        logging.error("Excepción al obtener el access_token de la página: %s", e)
        raise

# Verificación inicial del webhook
@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == 'mi_token_de_verificacion':
        logging.info("Webhook verificado correctamente.")
        return challenge, 200
    else:
        logging.warning("Error de verificación del webhook.")
        return "Error de verificación", 403

# Función para enviar mensajes
def enviar_mensaje(recipient_id, message_text, retry=True):
    global access_token, token_expiration_time
    
    # Verificar si el token ha expirado según nuestro registro
    if token_expiration_time and time.time() > token_expiration_time:
        logging.info("Token expirado según el tiempo registrado. Obteniendo uno nuevo.")
        try:
            get_long_lived_token()
        except Exception as e:
            logging.error("No se pudo renovar el access_token: %s", e)
            return
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text},
        'messaging_type': 'RESPONSE'
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logging.info(f"Mensaje enviado correctamente a {recipient_id}")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error al enviar mensaje: {response.status_code}, {response.text}")
        if response.status_code in [400, 401, 403] and retry:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', '')
            if 'invalid_token' in error_message or 'expired' in error_message:
                logging.info("Token inválido o expirado. Intentando obtener uno nuevo.")
                try:
                    get_long_lived_token()
                    # Reintentar enviar el mensaje una vez
                    enviar_mensaje(recipient_id, message_text, retry=False)
                except Exception as e:
                    logging.error("No se pudo renovar el access_token tras el error: %s", e)
    except requests.exceptions.RequestException as e:
        logging.error(f"Excepción al enviar mensaje: {e}")

# Manejo de notificaciones de mensajes de Instagram (POST)
@app.route('/webhook', methods=['POST'])
def webhook():
    logging.info("Solicitud POST recibida en /webhook")
    data = request.json
    logging.debug(f"Datos recibidos: {data}")

    if data and 'entry' in data:
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                if 'sender' in messaging_event and 'id' in messaging_event['sender']:
                    sender_id = messaging_event['sender']['id']
                    if 'message' in messaging_event:
                        message_text = messaging_event['message'].get('text')
                        logging.info(f"Nuevo mensaje de {sender_id}: {message_text}")
                        try:
                            respuesta_chatgpt = obtener_respuesta_chatgpt(message_text)
                            enviar_mensaje(sender_id, respuesta_chatgpt)
                        except Exception as e:
                            logging.error(f"Error al procesar el mensaje: {e}")
        return "OK", 200
    else:
        logging.warning("Datos inválidos recibidos en el webhook.")
        return "Error: No se pudo procesar el webhook", 400

# Página principal
@app.route('/')
def home():
    return render_template('index.html')

# Llamada inicial para obtener el token de larga duración y el token de página
if __name__ == '__main__':
    try:
        get_long_lived_token()  # Obtener el token antes de iniciar la app
        app.run(port=5000)
    except Exception as e:
        logging.critical("La aplicación no pudo iniciarse debido a un error al obtener el access_token: %s", e)
