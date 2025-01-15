from flask import Blueprint, request, jsonify
from flasgger import swag_from
from firebase_admin import storage
from urllib.parse import urlparse, parse_qs, unquote
import datetime

# Crear el Blueprint para firebase_images
firebase_images_bp = Blueprint('firebase_images', __name__)

@firebase_images_bp.route('/get_signed_url', methods=['GET'])
@swag_from({
    'tags': ['Firebase Images'],
    'summary': 'Obtener una URL firmada para acceder a una imagen en Firebase Storage.',
    'description': 'Genera una URL firmada para permitir acceso temporal a una imagen específica almacenada en Firebase Storage.',
    'parameters': [
        {
            'name': 'userId',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'El ID del usuario propietario de la imagen.'
        },
        {
            'name': 'imagePath',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'El path de la imagen dentro del bucket de Firebase Storage.'
        }
    ],
    'responses': {
        200: {
            'description': 'URL firmada generada con éxito.',
            'schema': {
                'type': 'object',
                'properties': {
                    'url': {'type': 'string', 'example': 'https://example.com/signed-url'}
                }
            }
        },
        400: {'description': 'Solicitud inválida.'},
        500: {'description': 'Error interno del servidor.'}
    }
})
def get_signed_url():
    """Generar una URL firmada para acceder a una imagen en Firebase Storage."""
    user_id = request.args.get('userId')
    image_url = request.args.get('imagePath')

    if not user_id or not image_url:
        return jsonify({"message": "userId e imagePath son requeridos."}), 400

    try:
        # Extract object path from the full URL
        parsed_url = urlparse(image_url)
        # Decode the path and remove leading "/v0/b/<bucket_name>/o/"
        object_path = unquote(parsed_url.path).split('/o/')[-1]

        bucket = storage.bucket()
        blob = bucket.blob(object_path)

        url = blob.generate_signed_url(
            expiration=datetime.timedelta(minutes=15),
            method="GET"
        )

        return jsonify({"url": url}), 200

    except Exception as e:
        return jsonify({"message": "Error al generar la URL firmada.", "error": str(e)}), 500
