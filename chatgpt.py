import openai
from dotenv import load_dotenv
import os
# Variables globales
from datetime import datetime, timedelta

FECHA_INICIO = datetime.now()
TIEMPO_MAXIMO_HISTORIAL = timedelta(days=1)

# Cargar variables de entorno
load_dotenv()

# Configuración de la clave de API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")


def tiempo_restante():
    global conversacion_historial, FECHA_INICIO  # Declara como global antes de usar
    ahora = datetime.now()
    tiempo_restante = TIEMPO_MAXIMO_HISTORIAL - (ahora - FECHA_INICIO)
    if tiempo_restante.total_seconds() > 0:
        return str(tiempo_restante).split('.')[0]  # Retorna formato HH:MM:SS
    else:
        # Limpia el historial si el tiempo ha expirado
        conversacion_historial.clear()  # Limpia el historial
        FECHA_INICIO = datetime.now()  # Reinicia el contador
        return "00:00:00"


# Diccionario para almacenar el historial de conversaciones por usuario
conversacion_historial = {}

# Función para obtener la respuesta de ChatGPT
def obtener_respuesta_chatgpt(mensaje_usuario, user_id):
    # Ignorar cualquier mensaje proveniente del ID del bot
    if user_id == "17841451060597045":
        return ""

    # Inicializar el historial de mensajes para el usuario si no existe
    if user_id not in conversacion_historial:
        conversacion_historial[user_id] = [
            {"role": "system", "content": (
                "Eres Ranpu, la inteligencia artificial de la empresa ecuatoriana de lámparas 3D personalizadas, Ranpu. "
                "Responde siempre con un tono amable y agrega emojis para hacer las respuestas amigables. "
                "Tus respuestas deben ser breves, precisas y con un estilo ecuatoriano. "
                "Usa modismos ecuatorianos de forma sutil para mantener cercanía sin perder la seriedad. "
                "No utilices ambos signos de interrogación o exclamación al inicio y al final de las oraciones. Solamente Pon el signo final de exclamación o interrogación. "
            )}
        ]

    # Agregar el mensaje del usuario al historial
    conversacion_historial[user_id].append({"role": "user", "content": mensaje_usuario})

    # Generar la respuesta del asistente
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversacion_historial[user_id],
        max_tokens=150,
        temperature=0.7
    )

    # Obtener la respuesta generada
    respuesta = response['choices'][0]['message']['content'].strip()

    # Agregar la respuesta del asistente al historial
    conversacion_historial[user_id].append({"role": "assistant", "content": respuesta})

    return respuesta

