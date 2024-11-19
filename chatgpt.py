import openai
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import threading
import time

# Cargar variables de entorno
load_dotenv()

# Configuración de la clave de API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Diccionario para almacenar el historial de conversaciones por usuario
conversacion_historial = {}
FECHA_INICIO = datetime.now()  # Registrar la fecha de inicio del sistema
TIEMPO_MAXIMO_HISTORIAL = timedelta(days=15)  # Tiempo máximo para resetear la variable


# Función para reiniciar el historial después de 15 días
def verificar_y_resetear_historial():
    global conversacion_historial, FECHA_INICIO
    ahora = datetime.now()
    
    # Si han pasado más de 15 días desde el inicio, reinicia la variable
    if ahora - FECHA_INICIO > TIEMPO_MAXIMO_HISTORIAL:
        conversacion_historial = {}  # Reinicia el historial completo
        FECHA_INICIO = datetime.now()  # Actualiza la fecha de inicio


# Función en un hilo separado para mostrar el tiempo restante cada minuto
def mostrar_tiempo_restante():
    global FECHA_INICIO, TIEMPO_MAXIMO_HISTORIAL
    while True:
        ahora = datetime.now()
        tiempo_restante = TIEMPO_MAXIMO_HISTORIAL - (ahora - FECHA_INICIO)
        
        if tiempo_restante.total_seconds() > 0:
            print(f"Tiempo restante para eliminar el historial: {tiempo_restante}")
        else:
            print("El historial ha sido eliminado. Reiniciando conteo.")
        
        time.sleep(60)  # Espera un minuto antes de volver a calcular


# Inicia el hilo para mostrar el tiempo restante
thread = threading.Thread(target=mostrar_tiempo_restante, daemon=True)
thread.start()

# Función para obtener la respuesta de ChatGPT
def obtener_respuesta_chatgpt(mensaje_usuario, user_id):
    # Verificar si es necesario reiniciar el historial completo
    verificar_y_resetear_historial()


    # Inicializar el historial de mensajes para el usuario si no existe
    if user_id not in conversacion_historial:
        conversacion_historial[user_id] = [
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
    conversacion_historial[user_id].append({"role": "user", "content": mensaje_usuario})

    # Enviar el historial completo a la API para mantener la conversación
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversacion_historial[user_id],
        max_tokens=150,
        temperature=0.7,
        n=1,
        stop=None
    )

    # Obtener la respuesta de ChatGPT
    respuesta = response['choices'][0]['message']['content'].strip()

    # Agregar la respuesta de ChatGPT al historial
    conversacion_historial[user_id].append({"role": "assistant", "content": respuesta})

    return respuesta