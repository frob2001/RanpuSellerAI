import openai
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de la clave de API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Función para obtener la respuesta de ChatGPT
def obtener_respuesta_chatgpt(mensaje_usuario):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
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
            )},
            {"role": "user", "content": mensaje_usuario}
        ],
        max_tokens=50
    )
    return response.choices[0].message["content"]
