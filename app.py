from flask import Flask, request

app = Flask(__name__)

# Verificación inicial del webhook
@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    # Verifica que el token sea correcto
    if mode == 'subscribe' and token == 'tu_token_de_verificacion':
        return challenge, 200
    else:
        return "Error de verificación", 403

# Manejar notificaciones de mensajes de Instagram
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data and 'entry' in data:
        for entry in data['entry']:
            for message in entry.get('messaging', []):
                sender_id = message['sender']['id']
                message_text = message.get('message', {}).get('text')
                print(f"Nuevo mensaje de {sender_id}: {message_text}")
        return "OK", 200
    else:
        return "Error: No se pudo procesar el webhook", 400

if __name__ == '__main__':
    app.run(port=5000)
