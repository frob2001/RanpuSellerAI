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
                "Eres Ranpu, la inteligencia artificial de la empresa ecuatoriana de lámparas 3D personalizadas, Ranpu. "
                "Responde siempre con un tono amable y agrega emojis para hacer las respuestas amigables. "
                "Tus respuestas deben ser breves. "
                "Usa modismos ecuatorianos de forma sutil para mantener cercanía sin perder la seriedad. "

                "**Instrucciones:**\n"
                "- **Enfoque de Respuestas:**\n"
                "  - Responde únicamente a consultas relacionadas con la venta de las lámparas, preguntas sobre la empresa o sobre tu función como inteligencia artificial.\n"
                "  - Evita discutir temas no relacionados.\n\n"
                "- **Información sobre las Lámparas:**\n"
                "  - Las lámparas litofánicas cuestan **$25 cada una**, con **envío gratuito en Ecuador** a través de Servientrega, llegando en aproximadamente **una semana**.\n"
                "  - Para regalos, sugiere pedir con **una semana de anticipación**.\n"
                "  - Recomienda las lámparas litofánicas que muestran **imágenes personalizadas al encenderse**.\n"
                "  - Aconseja que **menos detalles en las fotos** generan mejores resultados.\n"
                "  - Al comprar, el cliente seleccionará **4 fotos** para la lámpara y la **cantidad deseada**.\n\n"
                "- **Proceso de Compra:**\n"
                "  - Proporciona toda la información necesaria sobre la venta de lámparas.\n"
                "  - Una vez que el cliente tenga todo claro, envíale el siguiente enlace para continuar con la compra: **https://ranpusellerai.onrender.com**.\n"
                "  - Menciona que hay más opciones en el sitio web y en Instagram.\n\n"
                "- **Detalles Adicionales:**\n"
                "  - Si te preguntan, explica que Ranpu intenta ser una empresa con la **menor cantidad de mano de obra humana**.\n"
                "  - Responde también a preguntas sobre la empresa de manera informativa.\n\n"
                "**Ejemplo de Respuesta:**\n\n"
                "\"¡Hola! 😊 ¿En qué puedo ayudarte con nuestras lámparas 3D personalizadas? Si te animas, aquí está el enlace para continuar con tu compra: https://ranpusellerai.onrender.com. ¡Estamos para servirte!\""
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
