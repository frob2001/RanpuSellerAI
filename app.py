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

if __name__ == '__main__':
    app.run(port=5000)
