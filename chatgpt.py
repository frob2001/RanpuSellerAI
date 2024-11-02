import openai
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de la clave de API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Diccionario para almacenar el historial de conversaciones por usuario
conversacion_historial = {}

# Función para obtener la respuesta de ChatGPT
def obtener_respuesta_chatgpt(mensaje_usuario, user_id):
    # Inicializar el historial de mensajes para el usuario si no existe
    if user_id not in conversacion_historial:
        conversacion_historial[user_id] = [
            {"role": "system", "content": (
                "Eres Ranpu, la inteligencia artificial de la empresa de lámparas 3D personalizadas. "
                "Responde siempre con un tono amable y agrega emojis para hacer las respuestas amigables. "
                "Las lámparas cuestan $25 cada una, con envío gratuito en Ecuador (por Servientrega) y llegan en una semana. "
                "Para regalos, sugiere pedir con una semana de anticipación 🎁. "
                "Recomienda las lámparas litofánicas, que muestran imágenes personalizadas al encenderse 💡. "
                "Menos detalles en la foto generan mejores resultados 📸. "
                "Al comprar, el cliente seleccionará 4 fotos para la lámpara y la cantidad deseada. "
                "Si se decide a comprar, proporciona este link: https://ranpusellerai.onrender.com. "
                "Recuerda también mencionar que hay más opciones en el sitio web y en Instagram."
            )}
        ]

    # Agregar el mensaje del usuario al historial
    conversacion_historial[user_id].append({"role": "user", "content": mensaje_usuario})

    # Enviar el historial completo a la API para mantener la conversación
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversacion_historial[user_id],
        max_tokens=50
    )

    # Obtener la respuesta de ChatGPT
    respuesta = response['choices'][0]['message']['content']

    # Agregar la respuesta de ChatGPT al historial
    conversacion_historial[user_id].append({"role": "assistant", "content": respuesta})

    return respuesta
