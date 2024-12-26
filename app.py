import requests
from flask import Flask, request, render_template, jsonify, redirect, session
import logging
from config import config
from routes import lithophane_bp
from services import (
    #Chatgpt Service
    get_chatgpt_response,
    conversation_history
)
from flask_cors import CORS

#API 
from api.database import init_db
from api.swagger import init_swagger

#API ROUTES
from api.routes import (
    usuarios_bp, 
    estados_pedidos_bp, 
    impuestos_bp,
    direcciones_bp,
    categorias_productos_bp,
    productos_bp,
    pedidos_bp,
    modelos_bp,
    estados_impresoras_bp,
    categorias_filamentos_bp,
    filamentos_bp,
    impresoras_bp
)

app = Flask(__name__)

# Configuración de CORS
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

init_db(app)
init_swagger(app)

#Blueprints for APIs
app.register_blueprint(usuarios_bp, url_prefix="/api/usuarios")
app.register_blueprint(estados_pedidos_bp, url_prefix="/api/estados_pedidos")
app.register_blueprint(impuestos_bp, url_prefix="/api/impuestos")
app.register_blueprint(direcciones_bp, url_prefix="/api/direcciones")
app.register_blueprint(categorias_productos_bp, url_prefix="/api/categorias_productos")
app.register_blueprint(productos_bp, url_prefix="/api/productos")
app.register_blueprint(pedidos_bp, url_prefix="/api/pedidos")
app.register_blueprint(modelos_bp, url_prefix="/api/modelos")
app.register_blueprint(estados_impresoras_bp, url_prefix="/api/estados_impresoras")
app.register_blueprint(categorias_filamentos_bp, url_prefix="/api/categorias_filamentos")
app.register_blueprint(filamentos_bp, url_prefix="/api/filamentos")
app.register_blueprint(impresoras_bp, url_prefix="/api/impresoras")

# Configuration in production mode
app.config.from_object(config['production'])

# Logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#Enviroment variables from config
app_id = app.config['FACEBOOK_APP_ID']
app_secret = app.config['FACEBOOK_APP_SECRET']
user_access_token = app.config['USER_ACCESS_TOKEN']
instagram_account_id = app.config['INSTAGRAM_ACCOUNT_ID']
graph_api_version = app.config['GRAPH_API_VERSION']

# URLs for Facebook Graph API
messages_url = f'https://graph.facebook.com/{graph_api_version}/me/messages'
accounts_url = f'https://graph.facebook.com/{graph_api_version}/me/accounts'

# Variables globales para el token de acceso y el ID de Instagram
page_access_token = '' #SE GENERA AUTOMATICAMENTE DEPENDE DE USER_ACCESS_TOKEN

# Función para obtener el Page Access Token desde me/accounts
def obtener_page_access_token():
    global page_access_token
    params = {
        'access_token': user_access_token
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
        response = requests.post(messages_url, headers=headers, json=data)
        if response.status_code == 200:
            logger.info(f"Mensaje enviado correctamente a {recipient_id}")
        elif response.status_code in [400, 401, 403]:
            logger.warning(f"Error al enviar mensaje: {response.status_code}, {response.text} a {recipient_id}")
            logger.info("Intentando renovar el Page Access Token...")
            if renovar_page_access_token():
                # Reintentar enviar el mensaje con el nuevo token
                headers['Authorization'] = f'Bearer {page_access_token}'
                retry_response = requests.post(messages_url, headers=headers, json=data)
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
    if obtener_page_access_token():
        logger.info("Renovación de Page Access Token completada.")
        return True
    logger.error("No se pudo renovar el Page Access Token.")
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

# Manejo de notificaciones de mensajes de Instagram (POST)
# Función que maneja la recepción de mensajes de Instagram
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

                # Ignorar mensajes provenientes del ID del bot
                if sender_id == "17841451060597045":
                    logger.warning(f"Mensaje recibido del bot (ID: {sender_id}). Ignorando...")
                    continue

                if sender_id and 'message' in messaging_event:
                    message = messaging_event['message']
                    message_text = message.get('text')
                    if message_text:
                        logger.info(f"Nuevo mensaje de {sender_id}: {message_text}")
                        # Llama a get_chatgpt_response pasando sender_id para mantener la conversación
                        respuesta_chatgpt = get_chatgpt_response(message_text, sender_id)
                        enviar_mensaje(sender_id, respuesta_chatgpt)
        return "OK", 200
    else:
        logger.warning("Datos inválidos recibidos en el webhook.")
        return "Error: No se pudo procesar el webhook", 400
    
# Configuración de Instagram (desde config.py o variables de entorno)
INSTAGRAM_CLIENT_ID = '996064988988485'
INSTAGRAM_CLIENT_SECRET = '4b6c06bbcc9f350a9dda641fd1a93974'
REDIRECT_URI = 'https://ranpusellerai.onrender.com/auth/instagram/callback'

# URLs de Instagram OAuth2
INSTAGRAM_AUTH_URL = 'https://api.instagram.com/oauth/authorize'
INSTAGRAM_TOKEN_URL = 'https://api.instagram.com/oauth/access_token'
INSTAGRAM_GRAPH_API_URL = 'https://graph.instagram.com'

### ---- 1. Endpoint para Iniciar el Login con Instagram ---- ###
@app.route('/auth/instagram')
def auth_instagram():
    auth_url = (
        f"{INSTAGRAM_AUTH_URL}"
        f"?client_id={INSTAGRAM_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=user_profile,user_media"
        f"&response_type=code"
    )
    return redirect(auth_url)


### ---- 2. Callback para Recibir el Código y Obtener el Token de Acceso ---- ###
@app.route('/auth/instagram/callback')
def instagram_callback():
    code = request.args.get('code')
    if not code:
        return "Error: No se recibió el código de autorización.", 400

    data = {
        "client_id": INSTAGRAM_CLIENT_ID,
        "client_secret": INSTAGRAM_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    try:
        # Intercambiar el código por un token de acceso
        response = requests.post(INSTAGRAM_TOKEN_URL, data=data)
        response.raise_for_status()
        access_data = response.json()

        # Guardar token de acceso y usuario en sesión
        session['instagram_access_token'] = access_data['access_token']
        session['user_id'] = access_data['user_id']

        logger.info("Inicio de sesión de Instagram exitoso.")
        return redirect('/profile')  # Redirigir a perfil
    except requests.exceptions.RequestException as e:
        logger.error(f"Error durante la autenticación de Instagram: {e}")
        return "Error al autenticar con Instagram.", 400


### ---- 3. Perfil del Usuario (Con Token) ---- ###
@app.route('/profile')
def profile():
    access_token = session.get('instagram_access_token')
    user_id = session.get('user_id')

    if not access_token:
        return redirect('/auth/instagram')

    # Obtener información básica del usuario
    user_info_url = (
        f"{INSTAGRAM_GRAPH_API_URL}/{user_id}"
        f"?fields=id,username,account_type"
        f"&access_token={access_token}"
    )
    response = requests.get(user_info_url)
    user_info = response.json()

    return render_template('profile.html', user=user_info)


### ---- 4. Logout (Cerrar Sesión) ---- ###
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


### ---- 5. Endpoint para Mostrar Conversaciones (Simulación) ---- ###
@app.route('/conversations', methods=['GET'])
def get_conversations():
    access_token = session.get('instagram_access_token')
    if not access_token:
        return redirect('/auth/instagram')

    # Simulación de conversaciones
    conversaciones = [
        {"from": "usuario1", "message": "Hola, ¿puedo personalizar una lámpara?"},
        {"from": "usuario2", "message": "¿Tienen envíos internacionales?"}
    ]
    return render_template('conversaciones.html', conversaciones=conversaciones)


#Rutas para litofanias
app.register_blueprint(lithophane_bp)


# Página principal
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    renovar_page_access_token()  # Inicializar los tokens al iniciar la aplicación
    if page_access_token:
        app.run(port=5000)
    else:
        logger.critical("No se pudo inicializar el Page Access Token. La aplicación no se iniciará.")

# if __name__ == '__main__':
#         app.run(port=5000)