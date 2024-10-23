from flask import Flask, request
import os

app = Flask(__name__)

# Verificación inicial del webhook
@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == 'mi_token_de_verificacion':  # Asegúrate de que este token coincide
        return challenge, 200
    else:
        return "Error de verificación", 403

# Manejo de notificaciones de mensajes de Instagram (POST)
@app.route('/webhook', methods=['POST'])
def webhook():
    print("Solicitud POST recibida")
    data = request.json  # Captura el JSON recibido
    print(f"Datos recibidos: {data}")  # Imprime los datos para ver qué está llegando

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


@app.route('/webhook', methods=['POST', 'GET', 'PATCH', 'PUT', 'DELETE'])
def webhook():
    # Registra la solicitud completa en los logs
    print(f"Headers: {request.headers}")
    print(f"Body: {request.json}")
    print(f"Method: {request.method}")
    
    # Procesar el cuerpo si es necesario
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
    port = int(os.environ.get('PORT', 5000))  # Obtiene el puerto desde la variable de entorno PORT
    app.run(host='0.0.0.0', port=port)  # Asegura que Flask escuche en el puerto especificado
