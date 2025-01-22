from flask import Blueprint, jsonify
from flasgger import swag_from
from sqlalchemy import func
from ..models.filamentos import Filamentos
from ..models.colores import Colores
from ..database import db

# Middleware protections
from api.middlewares.origin_middleware import validate_origin

# Crear el Blueprint para los colores disponibles
colors_bp = Blueprint('colors', __name__)

@colors_bp.route('/available-colors', methods=['GET'])
@validate_origin()
@swag_from({
    'tags': ['Colores'],
    'summary': 'Obtener colores disponibles',
    'description': 'Retorna una lista de colores junto con su disponibilidad basada en la suma de las longitudes actuales de los filamentos.',
    'responses': {
        200: {
            'description': 'Lista de colores con disponibilidad',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'color_id': {'type': 'integer', 'example': 1},
                        'nombre': {'type': 'string', 'example': 'Negro'},
                        'nombre_ingles': {'type': 'string', 'example': 'Black'},
                        'hexadecimal': {'type': 'string', 'example': '#FFFFFF'},
                        'available': {'type': 'boolean', 'example': True}
                    }
                }
            }
        },
        500: {
            'description': 'Error interno del servidor',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Error al obtener los colores disponibles'},
                    'error': {'type': 'string', 'example': 'Detalle del error'}
                }
            }
        }
    }
})
def get_available_colors():
    """Obtiene la disponibilidad de colores basado en la suma de la longitud_actual de los filamentos."""
    try:
        # Consulta para agrupar filamentos por color y sumar sus longitudes
        filamentos_suma = (
            db.session.query(
                Filamentos.color_id,
                func.sum(Filamentos.longitud_actual).label('total_length')
            )
            .group_by(Filamentos.color_id)
            .all()
        )

        # Convertir el resultado a un diccionario {color_id: total_length}
        filamentos_suma_dict = {
            fila.color_id: fila.total_length for fila in filamentos_suma
        }

        # Obtener todos los colores
        colores = Colores.query.all()

        # Crear la respuesta con disponibilidad
        result = []
        for color in colores:
            total_length = filamentos_suma_dict.get(color.color_id, 0)
            available = total_length >= 10  # Verificar si hay al menos 10 metros

            result.append({
                "color_id": color.color_id,
                "nombre": color.nombre,
                "nombre_ingles": color.nombre_ingles,
                "hexadecimal": color.hexadecimal,
                "available": available
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"message": "Error al obtener los colores disponibles", "error": str(e)}), 500
