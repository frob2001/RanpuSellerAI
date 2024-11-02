import requests
from flask import Flask, request, render_template
from chatgpt import obtener_respuesta_chatgpt 
import time

app = Flask(__name__)

# Datos de tu aplicación
app_id = '1560936227863673'
app_secret = '432eda601cb78df51bc55d2bf79d9f3e'
short_lived_token = 'EAAWLqclgZCHkBO49PeJbJqCSX7HFb9Y3XYMtCaz15nQ72wPQXVZBemm6KSryNIPUf8SsWEGDC2NGZATSMESbst9BszalMcjOwnDm1ZC0gz1pa7r2PGB5EPWpXw80worujbt32GFivrZBl80aO0hwBJc9GojBsjCMHzZBIK13y53w5Uyt7S7rudM1AB'

# Variables globales para el token de acceso y el ID de Instagram
access_token = 'EAAWLqclgZCHkBO7XxLWAz1FFnq6nM2vYWqpvpzYbM6klFeQLFf6EbbZBA9jQyZAFok9NS3sdIIHqnfV3NS9ZChyss6HZAw9g7hSCCMj88SAeyfjg6keZCwGX0FrqurzFZB9SWtfZA2kV1InJPAD1ZBWM1qkhIVRFiZBBJSHIQGMF3uOMEYQi7sQwRoSXqyQtgVYPbJExTNh8hagsIHdDeDuPjdTf8ZD'
instagram_account_id = '108165015152868'
url = f'https://graph.facebook.com/v12.0/me/messages'

# Variable para almacenar el tiempo de expiración del token
token_expiration_time = None

# Función para obtener un token de larga duración
def get_long_lived_token():
    global access_token, token_expiration_time
    token_url = f"https://graph.facebook.com/v12.0/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': short_lived_token
    }
    response = requests.get(token_url, params=params)
    token_data = response.json()

    if 'access_token' in token_data:
        access_token = token_data['access_token']
        # Supongamos que el token de larga duración expira en 60 días
        token_expiration_time = time.time() + 60 * 24 * 60 * 60  # 60 días en segundos
        print("Nuevo token obtenido:", access_token)
    else:
        print("Error al obtener el token de larga duración:", token_data)

# Verificación inicial del webhook
@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == 'mi_token_de_verificacion':
        return challenge, 200
    else:
        return "Error de verificación", 403

# Función para enviar mensajes
def enviar_mensaje(recipient_id, message_text, retry=True):
    global access_token, token_expiration_time
    
    # Verificar si el token ha expirado según nuestro registro
    if token_expiration_time and time.time() > token_expiration_time:
        print("Token expirado según el tiempo registrado. Obteniendo uno nuevo.")
        get_long_lived_token()

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text},
        'messaging_type': 'RESPONSE'
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"Mensaje enviado correctamente a {recipient_id}")
    elif response.status_code in [400, 401, 403] and retry:
        error_data = response.json()
        error_message = error_data.get('error', {}).get('message', '')
        print(f"Error al enviar mensaje: {response.status_code}, {response.text}")
        # Verificar si el error está relacionado con el token
        if 'invalid_token' in error_message or 'expired' in error_message:
            print("Token inválido o expirado. Intentando obtener uno nuevo.")
            get_long_lived_token()
            # Reintentar enviar el mensaje una vez
            enviar_mensaje(recipient_id, message_text, retry=False)
    else:
        print(f"Error al enviar mensaje: {response.status_code}, {response.text}")

# Manejo de notificaciones de mensajes de Instagram (POST)
@app.route('/webhook', methods=['POST'])
def webhook():
    print("Solicitud POST recibida")
    data = request.json
    print(f"Datos recibidos: {data}")

    if data and 'entry' in data:
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                if 'sender' in messaging_event and 'id' in messaging_event['sender']:
                    sender_id = messaging_event['sender']['id']
                    if 'message' in messaging_event:
                        message_text = messaging_event['message'].get('text')
                        print(f"Nuevo mensaje de {sender_id}: {message_text}")
                        respuesta_chatgpt = obtener_respuesta_chatgpt(message_text)
                        enviar_mensaje(sender_id, respuesta_chatgpt)
        return "OK", 200
    else:
        return "Error: No se pudo procesar el webhook", 400

# Página principal
@app.route('/')
def home():
    return render_template('index.html')

# Llamada inicial para obtener el token de larga duración
if __name__ == '__main__':
    get_long_lived_token()  # Obtener el token antes de iniciar la app
    app.run(port=5000)
