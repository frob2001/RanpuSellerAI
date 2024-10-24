import requests
from flask import Flask, request, render_template
import time

app = Flask(__name__)

# Datos de tu aplicación
app_id = '1560936227863673'
app_secret = '432eda601cb78df51bc55d2bf79d9f3e'
short_lived_token = 'EAAWLqclgZCHkBO8ZBuqb0SGzZAZAe2vE5swRZBibsiHqP13fXMBCF6P13iqqL15NWXpZAd8Jxjc6uHqATPrwrXvfDHXbXrj3honQYtoXmbVvvIP9crmQNnJMHaPM4NAZB8EmK2BaiVfR1pbZAhog8ZAoeoicP0ZCXKyRbDHhqWAbsowlVFUVQnDdafifnBgSref5KZBkh6PJwOQFjoaTkZANwi3bF5xQX9gVv0hk27v0SqZACLVkZD'

# Variables globales para el token de acceso y el ID de Instagram
access_token = ''
instagram_account_id = '1961699064327445'
url = f'https://graph.facebook.com/v12.0/{instagram_account_id}/messages'


# Función para obtener un token de larga duración
def get_long_lived_token():
    global access_token
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
def enviar_mensaje(recipient_id, message_text):
    global access_token
    data = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text},
        'messaging_type': 'RESPONSE',
        'access_token': access_token
    }
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print(f"Mensaje enviado correctamente a {recipient_id}")
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
                sender_id = messaging_event['sender']['id']
                if 'message' in messaging_event:
                    message_text = messaging_event['message'].get('text')
                    print(f"Nuevo mensaje de {sender_id}: {message_text}")
                    enviar_mensaje(sender_id, "Soy un robot y este es un mensaje de prueba desde Ranpu")
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

