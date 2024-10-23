import requests
from flask import Flask, request

app = Flask(__name__)


access_token = 'EAAWLqclgZCHkBO6do8MBtZCNrQCWpb45fQkdNLPgZAumEuJvbUlur2CnWApDESDLGsZCNGHkZAplBrYQFg3yFPCe7aiSN5ZCirXZA5xSJioczMraxKj4TSyFYYbhyPpQKX4u8Q8uaz1lPWGtfEMhzVEg5jv5sQZBaHNTeKJzeLCfDEaoPXHT41ovVeWl38NcthrrkbGUd3Bj3AZCfKDxpPgYqSOZCPxZBkZD'
instagram_account_id = '1961699064327445'  # El ID de la cuenta de Instagram
url = f'https://graph.facebook.com/v12.0/{instagram_account_id}/messages'

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

def enviar_mensaje(recipient_id, message_text):
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
    data = request.json  # Captura el JSON recibido
    print(f"Datos recibidos: {data}")  # Imprime los datos recibidos para verlos en los logs

    if data and 'entry' in data:
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                sender_id = messaging_event['sender']['id']
                if 'message' in messaging_event:
                    message_text = messaging_event['message'].get('text')
                    print(f"Nuevo mensaje de {sender_id}: {message_text}")
                    enviar_mensaje(sender_id, "EAAWLqclgZCHkBO6do8MBtZCNrQCWpb45fQkdNLPgZAumEuJvbUlur2CnWApDESDLGsZCNGHkZAplBrYQFg3yFPCe7aiSN5ZCirXZA5xSJioczMraxKj4TSyFYYbhyPpQKX4u8Q8uaz1lPWGtfEMhzVEg5jv5sQZBaHNTeKJzeLCfDEaoPXHT41ovVeWl38NcthrrkbGUd3Bj3AZCfKDxpPgYqSOZCPxZBkZD")  # Token de acceso
        return "OK", 200
    else:
        return "Error: No se pudo procesar el webhook", 400

if __name__ == '__main__':
    app.run(port=5000)
