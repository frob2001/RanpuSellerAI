import requests
from flask import Flask, request, render_template, redirect, url_for, session, flash, send_file
from chatgpt import obtener_respuesta_chatgpt, conversacion_historial, tiempo_restante
import logging
import os
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFilter
import io

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")  # Cambia por un valor seguro

# Datos de prueba
TEST_USER = {
    "email": "ranpumetatest@ranpuoficial.com",
    "password": "kJy2119$u"
}

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Datos de tu aplicación
app_id = os.getenv("FACEBOOK_APP_ID") #SE ENCUENTRAN EN EL SERVIDOR
app_secret = os.getenv("FACEBOOK_APP_SECRET")
user_access_token = os.getenv("USER_ACCESS_TOKEN")

# Variables globales para el token de acceso y el ID de Instagram
page_access_token = '' #SE GENERA AUTOMATICAMENTE DEPENDE DE USER_ACCESS_TOKEN
instagram_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")


graph_api_version = 'v21.0'
messages_url = f'https://graph.facebook.com/{graph_api_version}/me/messages'
accounts_url = f'https://graph.facebook.com/{graph_api_version}/me/accounts'

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
                        # Llama a obtener_respuesta_chatgpt pasando sender_id para mantener la conversación
                        respuesta_chatgpt = obtener_respuesta_chatgpt(message_text, sender_id)
                        enviar_mensaje(sender_id, respuesta_chatgpt)
        return "OK", 200
    else:
        logger.warning("Datos inválidos recibidos en el webhook.")
        return "Error: No se pudo procesar el webhook", 400


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validación de credenciales
        if email == TEST_USER["email"] and password == TEST_USER["password"]:
            session['user'] = email  # Almacenar el usuario en la sesión
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for('console'))
        else:
            flash("Credenciales incorrectas.", "danger")
            return redirect(url_for('login'))
    
    return render_template('login.html')  # Muestra un formulario de inicio de sesión

@app.route('/logout')
def logout():
    session.pop('user', None)  # Eliminar el usuario de la sesión
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for('login'))

@app.route('/console')
def console():
    if 'user' not in session:  # Verifica si el usuario está autenticado
        flash("Debes iniciar sesión para acceder a esta página.", "warning")
        return redirect(url_for('login'))
    
    tiempo_para_borrado = tiempo_restante()  # Calcula el tiempo restante
    return render_template(
        'console.html',
        historial_global=conversacion_historial,
        tiempo_para_borrado=tiempo_para_borrado
    )


# Función para aplicar la litofanía sin luz (como un dibujo a mano con trazos negros sutiles)
def apply_lithophane_no_light(image):
    """
    Simula una litofanía sin luz de fondo, con trazos negros sutiles, similar a un dibujo a mano.
    """
    # Convertir a escala de grises
    grayscale = ImageOps.grayscale(image)

    # Aplicar un filtro de detección de bordes para resaltar contornos
    edges = grayscale.filter(ImageFilter.FIND_EDGES)

    # Invertir los colores para que los bordes sean negros sobre un fondo blanco
    inverted = ImageOps.invert(edges)

    # Aclarar la imagen para hacer los trazos más sutiles
    brightness_enhancer = ImageEnhance.Brightness(inverted)
    very_bright = brightness_enhancer.enhance(1.5)

    # Reducir el contraste para que los trazos sean apenas visibles
    contrast_enhancer = ImageEnhance.Contrast(very_bright)
    low_contrast = contrast_enhancer.enhance(0.5)

    return low_contrast


def apply_lithophane_with_light(image):
    """
    Simula una litofanía con luz de fondo, creando un degradado circular amarillo desde el centro.
    """
    # Convertir a escala de grises
    grayscale = ImageOps.grayscale(image)

    # Aumentar brillo para un efecto de luz de fondo
    enhancer = ImageEnhance.Brightness(grayscale)
    brighter = enhancer.enhance(1.5)

    # Obtener tamaño de la imagen
    width, height = brighter.size

    # Crear un degradado radial que comienza amarillo en el centro y se aclara hacia los bordes
    gradient = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(gradient)

    center_x, center_y = width // 2, height // 2
    max_radius = (width**2 + height**2) ** 0.5

    for y in range(height):
        for x in range(width):
            # Calcular la distancia del pixel al centro
            distance_to_center = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            # Calcular el factor de degradado (entre 1.0 y 0.0)
            gradient_factor = 1.0 - (distance_to_center / max_radius)
            gradient_factor = max(0, gradient_factor)  # Asegurarse de que esté entre 0 y 1

            # Mezclar entre amarillo y blanco
            r = int(255 * gradient_factor + 255 * (1 - gradient_factor))
            g = int(255 * gradient_factor + 255 * (1 - gradient_factor))
            b = int(0 * gradient_factor + 255 * (1 - gradient_factor))

            draw.point((x, y), (r, g, b))

    # Combinar la imagen aclarada con el degradado para simular la luz en el centro
    combined = Image.blend(brighter.convert('RGB'), gradient, alpha=0.5)

    return combined

@app.route('/convert/no-light', methods=['POST'])
def convert_image_no_light():
    if 'image' not in request.files:
        return {"error": "No image file provided"}, 400

    # Leer la imagen del archivo enviado
    image_file = request.files['image']
    image = Image.open(image_file)

    # Aplicar filtro sin luz
    no_light_image = apply_lithophane_no_light(image)

    # Guardar la imagen en memoria
    img_io = io.BytesIO()
    no_light_image.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

@app.route('/convert/with-light', methods=['POST'])
def convert_image_with_light():
    if 'image' not in request.files:
        return {"error": "No image file provided"}, 400

    # Leer la imagen del archivo enviado
    image_file = request.files['image']
    image = Image.open(image_file)

    # Aplicar filtro con luz
    with_light_image = apply_lithophane_with_light(image)

    # Guardar la imagen en memoria
    img_io = io.BytesIO()
    with_light_image.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')


# Página principal
@app.route('/')
def home():
    return render_template('index.html')

# Llamada inicial para obtener Page Access Token
def inicializar_tokens():
    if obtener_page_access_token():
        logger.info("Inicialización de tokens completada.")
    else:
        logger.error("Fallo al obtener el Page Access Token durante la inicialización.")

if __name__ == '__main__':
    inicializar_tokens()  # Inicializar los tokens al iniciar la aplicación
    if page_access_token:
        app.run(port=5000)
    else:
        logger.critical("No se pudo inicializar el Page Access Token. La aplicación no se iniciará.")
