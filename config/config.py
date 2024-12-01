import os

# Clase base para la configuración de la aplicación
class Config:
    # Clave secreta utilizada por Flask para manejar sesiones y datos firmados
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "supersecretkey")
    # Clave API para la integración con OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # ID de la aplicación de Facebook para autenticación e integración
    FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
    # Secreto de la aplicación de Facebook (clave privada asociada al ID)
    FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
    # Token de acceso del usuario para integrar Facebook e Instagram a la página de Ranpu
    USER_ACCESS_TOKEN = os.getenv("USER_ACCESS_TOKEN")
    # ID de la cuenta de Instagram vinculada para acceder a sus datos (Se usa para actualizar automáticamente el Token de Graph)
    INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
    # Versión de la API de Facebook Graph que se utilizará
    GRAPH_API_VERSION = 'v21.0'
    # Indica si la aplicación está en modo depuración (útil para desarrollo)
    DEBUG = True

# Clase de configuración para el entorno de producción
class ProductionConfig(Config):
    # Desactiva el modo depuración para producción (importante por seguridad)
    DEBUG = False

# Clase de configuración para el entorno de desarrollo
class DevelopmentConfig(Config):
    # Activa el modo depuración para facilitar pruebas y desarrollo
    DEBUG = True

# Diccionario que mapea los nombres de entorno con sus configuraciones respectivas
config = {
    'development': DevelopmentConfig,  # Configuración para desarrollo
    'production': ProductionConfig     # Configuración para producción
}
