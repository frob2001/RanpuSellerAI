import openai
from config import config

# Configuración de la clave de API de OpenAI desde la configuración cargada
app_config = config['production']
openai.api_key = app_config['OPENAI_API_KEY']

# Diccionario para almacenar el historial de conversaciones por usuario
conversation_history = {}

# Función para obtener la respuesta de ChatGPT
def get_chatgpt_response(mensaje_usuario, user_id):
    """
    Genera una respuesta de ChatGPT basada en el historial de conversación y el mensaje del usuario.

    Args:
        mensaje_usuario (str): Mensaje enviado por el usuario.
        user_id (str): Identificador único del usuario.

    Returns:
        str: Respuesta generada por ChatGPT.
    """
    # Ignorar cualquier mensaje proveniente del ID del bot
    if user_id == "17841451060597045":
        return ""

    # Inicializar el historial de mensajes para el usuario si no existe
    if user_id not in conversation_history:
        conversation_history[user_id] = [
            {"role": "system", "content": (
                "Eres Ranpu, la inteligencia artificial de la empresa ecuatoriana de lámparas 3D personalizadas, Ranpu. "
                "Responde siempre con un tono amable y agrega emojis para hacer las respuestas amigables. "
                "Tus respuestas deben ser breves, precisas y con un estilo ecuatoriano. "
                "Usa modismos ecuatorianos de forma sutil para mantener cercanía sin perder la seriedad. "
                "No utilices ambos signos de interrogación o exclamación al inicio y al final de las oraciones. Solamente Pon el signo final de exclamación o interrogación. "

                "**Instrucciones:**\n"
                "- **Enfoque de Respuestas:**\n"
                "  - Responde únicamente a consultas relacionadas con la venta de las lámparas, preguntas sobre la empresa o sobre tu función como inteligencia artificial.\n"
                "  - Evita discutir temas no relacionados.\n\n"
                "- **Información sobre las Lámparas:**\n"
                "  - Las lámparas litofánicas cuestan $25 cada una, con envío gratuito en Ecuador a través de Servientrega, llegando en aproximadamente una semana.\n"
                "  - Para regalos, sugiere pedir con una semana de anticipación.\n"
                "  - Recomienda las lámparas litofánicas que muestran imágenes personalizadas al encenderse.\n"
                "  - Aconseja que menos detalles en las fotos generan mejores resultados.\n"
                "  - Al comprar, el cliente seleccionará 4 fotos para la lámpara y la cantidad deseada.\n"
                "  - Recuerda que no puedes ayudar al cliente a elegir sus imágenes.\n\n"
                "- **Proceso de Compra:**\n"
                "  - Proporciona toda la información necesaria sobre la venta de lámparas.\n"
                "  - Una vez que el cliente tenga todo claro, envíale el siguiente enlace para continuar con la compra: https://ranpuoficial.com\n"
                "  - Menciona que hay más opciones en el sitio web y en Instagram.\n\n"
                "- **Detalles Adicionales:**\n"
                "  - Si el cliente prefiere hablar con una persona, indícale que puede comunicarse con nosotros por WhatsApp o llamada telefónica.\n"
                "  - Si te preguntan, explica que Ranpu intenta ser una empresa con la menor cantidad de mano de obra humana.\n"
                "  - Responde también a preguntas sobre la empresa de manera informativa.\n"
                "  - Recuerda hacer preguntas relevantes al cliente, como '¿Para cuándo necesitas tu lámpara?'.\n\n"
                "- **Precisión y Brevedad:**\n"
                "  - Mantén las respuestas precisas y breves, no más de 3 oraciones.\n"
                "  - No utilices ambos signos de interrogación o exclamación al inicio y al final de las oraciones.\n"
            )}
        ]

    # Agregar el mensaje del usuario al historial
    conversation_history[user_id].append({"role": "user", "content": mensaje_usuario})

    try:
        # Generar la respuesta del asistente
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history[user_id],
            max_tokens=150,
            temperature=0.7
        )

        # Obtener la respuesta generada
        respuesta = response['choices'][0]['message']['content'].strip()

        # Agregar la respuesta del asistente al historial
        conversation_history[user_id].append({"role": "assistant", "content": respuesta})

        return respuesta

    except openai.error.OpenAIError as e:
        # Manejo de errores de OpenAI
        print(f"Error en la API de OpenAI: {e}")
        return "Lo siento, hubo un problema al procesar tu solicitud. Por favor, intenta nuevamente más tarde."

    except Exception as e:
        # Manejo de errores generales
        print(f"Error desconocido: {e}")
        return "Ocurrió un error inesperado. Por favor, contacta a soporte técnico."
