from flask import Flask, request, jsonify

app = Flask(__name__)

# Verificación inicial del webhook
@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == 'mi_token_de_verificacion':  # Token de verificación
        return challenge, 200
    else:
        return "Error de verificación", 403

# Manejo de notificaciones de mensajes de Instagram (POST)
@app.route('/webhook', methods=['POST'])
def webhook():
    print("Solicitud POST recibida")
    data = request.json  # Captura el JSON recibido
    print(f"Datos recibidos: {data}")  # Imprime los datos recibidos para verlos en los logs

    if data and 'entry' in data:
        for entry in data['entry']:
            for change in entry.get('changes', []):
                if change.get('field') == 'messages':
                    sender_id = change['value']['sender']['id']
                    message_text = change['value']['message']['text']
                    print(f"Nuevo mensaje de {sender_id}: {message_text}")
        return "OK", 200
    else:
        return "Error: No se pudo procesar el webhook", 400

if __name__ == '__main__':
    app.run(port=5000)
