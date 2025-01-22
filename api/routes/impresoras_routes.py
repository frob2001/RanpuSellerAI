from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.impresoras import Impresoras
from ..schemas.impresoras_schema import ImpresorasSchema
from ..database import db

# Middleware protections
from api.middlewares.origin_middleware import validate_origin

# Crear el Blueprint para impresoras
impresoras_bp = Blueprint('impresoras', __name__)

# Instancias del schema
impresora_schema = ImpresorasSchema()
impresoras_schema = ImpresorasSchema(many=True)

@impresoras_bp.route('/', methods=['GET'])
@validate_origin()
@swag_from({
    'tags': ['Impresoras'],
    'summary': 'Obtener todas las impresoras',
    'description': 'Obtiene una lista de todas las impresoras.',
    'responses': {
        200: {
            'description': 'Lista de impresoras',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'impresora_id': {'type': 'integer', 'example': 1},
                        'marca': {'type': 'string', 'example': 'Creality'},
                        'estado_impresora': {
                            'type': 'object',
                            'properties': {
                                'estado_impresora_id': {'type': 'integer', 'example': 1},
                                'nombre': {'type': 'string', 'example': 'Disponible'}
                            }
                        },
                        'alto_area': {'type': 'string', 'example': '250.00'},
                        'ancho_area': {'type': 'string', 'example': '220.00'},
                        'largo_area': {'type': 'string', 'example': '220.00'},
                        'max_temp_cama': {'type': 'string', 'example': '100.00'},
                        'max_temp_extrusor': {'type': 'string', 'example': '260.00'},
                        'diametro_extrusor': {'type': 'integer', 'example': 1},
                        'consumo_electrico': {'type': 'string', 'example': '350.00'},
                        'filamento': {
                            'type': 'object',
                            'properties': {
                                'filamento_id': {'type': 'integer', 'example': 1},
                                'color': {'type': 'string', 'example': 'Rojo'},
                                'marca': {'type': 'string', 'example': 'Esun'}
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_todas_impresoras():
    """Obtener todas las impresoras."""
    impresoras = Impresoras.query.all()
    result = []
    for impresora in impresoras:
        data = impresora_schema.dump(impresora)
        data['estado_impresora'] = impresora.estado_impresora.to_dict() if impresora.estado_impresora else None
        data['filamento'] = impresora.filamento.to_dict() if impresora.filamento else None
        result.append(data)
    return jsonify(result), 200

@impresoras_bp.route('/<int:impresora_id>', methods=['GET'])
@validate_origin()
@swag_from({
    'tags': ['Impresoras'],
    'summary': 'Obtener una impresora por ID',
    'description': 'Obtiene una impresora específica por su ID.',
    'parameters': [
        {
            'name': 'impresora_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID de la impresora a obtener'
        }
    ],
    'responses': {
        200: {
            'description': 'Impresora encontrada',
            'schema': {
                'type': 'object',
                'properties': {
                    'impresora_id': {'type': 'integer', 'example': 1},
                    'marca': {'type': 'string', 'example': 'Creality'},
                    'estado_impresora': {
                        'type': 'object',
                        'properties': {
                            'estado_impresora_id': {'type': 'integer', 'example': 1},
                            'nombre': {'type': 'string', 'example': 'Disponible'}
                        }
                    },
                    'alto_area': {'type': 'string', 'example': '250.00'},
                    'ancho_area': {'type': 'string', 'example': '220.00'},
                    'largo_area': {'type': 'string', 'example': '220.00'},
                    'max_temp_cama': {'type': 'string', 'example': '100.00'},
                    'max_temp_extrusor': {'type': 'string', 'example': '260.00'},
                    'diametro_extrusor': {'type': 'integer', 'example': 1},
                    'consumo_electrico': {'type': 'string', 'example': '350.00'},
                    'filamento': {
                        'type': 'object',
                        'properties': {
                            'filamento_id': {'type': 'integer', 'example': 1},
                            'color': {'type': 'string', 'example': 'Rojo'},
                            'marca': {'type': 'string', 'example': 'Esun'}
                        }
                    }
                }
            }
        },
        404: {'description': 'Impresora no encontrada'}
    }
})
def get_impresora_por_id(impresora_id):
    """Obtener una impresora por ID."""
    impresora = Impresoras.query.get(impresora_id)
    if not impresora:
        return jsonify({"message": "Impresora no encontrada"}), 404
    data = impresora_schema.dump(impresora)
    data['estado_impresora'] = impresora.estado_impresora.to_dict() if impresora.estado_impresora else None
    data['filamento'] = impresora.filamento.to_dict() if impresora.filamento else None
    return jsonify(data), 200

@impresoras_bp.route('/', methods=['POST'])
@validate_origin()
@swag_from({
    'tags': ['Impresoras'],
    'summary': 'Crear una nueva impresora',
    'description': 'Registra una nueva impresora con todos sus atributos.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'marca': {'type': 'string', 'example': 'Creality'},
                    'estado_impresora_id': {'type': 'integer', 'example': 1},
                    'alto_area': {'type': 'number', 'example': 250.00},
                    'ancho_area': {'type': 'number', 'example': 220.00},
                    'largo_area': {'type': 'string', 'example': '220.00'},
                    'max_temp_cama': {'type': 'number', 'example': 100.00},
                    'max_temp_extrusor': {'type': 'number', 'example': 260.00},
                    'diametro_extrusor': {'type': 'integer', 'example': 1},
                    'consumo_electrico': {'type': 'number', 'example': 350.00},
                    'filamento_id': {'type': 'integer', 'example': 1}
                },
                'required': [
                    'marca', 'estado_impresora_id', 'alto_area', 'ancho_area',
                    'largo_area', 'max_temp_cama', 'max_temp_extrusor',
                    'diametro_extrusor', 'consumo_electrico', 'filamento_id'
                ]
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Impresora creada exitosamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'impresora_id': {'type': 'integer', 'example': 1},
                    'marca': {'type': 'string', 'example': 'Creality'},
                    'estado_impresora_id': {'type': 'integer', 'example': 1},
                    'alto_area': {'type': 'number', 'example': 250.00},
                    'ancho_area': {'type': 'number', 'example': 220.00},
                    'largo_area': {'type': 'string', 'example': '220.00'},
                    'max_temp_cama': {'type': 'number', 'example': 100.00},
                    'max_temp_extrusor': {'type': 'number', 'example': 260.00},
                    'diametro_extrusor': {'type': 'integer', 'example': 1},
                    'consumo_electrico': {'type': 'number', 'example': 350.00},
                    'filamento_id': {'type': 'integer', 'example': 1}
                }
            }
        },
        400: {'description': 'Datos inválidos en la solicitud'},
        500: {'description': 'Error interno del servidor'}
    }
})
def create_impresora():
    """Crear una nueva impresora."""
    data = request.get_json()

    try:
        # Validar y cargar los datos con el esquema
        nueva_impresora = impresora_schema.load(data, session=db.session)
        db.session.add(nueva_impresora)
        db.session.commit()

        # Devolver la nueva impresora creada
        return jsonify(impresora_schema.dump(nueva_impresora)), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al crear la impresora", "error": str(e)}), 500

@impresoras_bp.route('/<int:impresora_id>', methods=['PUT'])
@validate_origin()
@swag_from({
    'tags': ['Impresoras'],
    'summary': 'Actualizar una impresora',
    'description': 'Actualiza los datos de una impresora existente.',
    'parameters': [
        {
            'name': 'impresora_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID de la impresora a actualizar'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'marca': {'type': 'string', 'example': 'Creality'},
                    'estado_impresora_id': {'type': 'integer', 'example': 1},
                    'alto_area': {'type': 'number', 'example': 250.00},
                    'ancho_area': {'type': 'number', 'example': 220.00},
                    'largo_area': {'type': 'string', 'example': '220.00'},
                    'max_temp_cama': {'type': 'number', 'example': 100.00},
                    'max_temp_extrusor': {'type': 'number', 'example': 260.00},
                    'diametro_extrusor': {'type': 'integer', 'example': 1},
                    'consumo_electrico': {'type': 'number', 'example': 350.00},
                    'filamento_id': {'type': 'integer', 'example': 1}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Impresora actualizada exitosamente'},
        404: {'description': 'Impresora no encontrada'},
        400: {'description': 'Datos inválidos en la solicitud'},
        500: {'description': 'Error interno del servidor'}
    }
})
def update_impresora(impresora_id):
    """Actualizar una impresora."""
    data = request.get_json()
    impresora = Impresoras.query.get(impresora_id)

    if not impresora:
        return jsonify({"message": "Impresora no encontrada"}), 404

    try:
        # Actualizar los datos de la impresora existente
        for key, value in data.items():
            if hasattr(impresora, key):
                setattr(impresora, key, value)

        db.session.commit()
        return jsonify(impresora_schema.dump(impresora)), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al actualizar la impresora", "error": str(e)}), 500

@impresoras_bp.route('/<int:impresora_id>', methods=['DELETE'])
@validate_origin()
@swag_from({
    'tags': ['Impresoras'],
    'summary': 'Eliminar una impresora',
    'description': 'Elimina una impresora existente por su ID.',
    'parameters': [
        {
            'name': 'impresora_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID de la impresora a eliminar'
        }
    ],
    'responses': {
        200: {'description': 'Impresora eliminada exitosamente'},
        404: {'description': 'Impresora no encontrada'},
        500: {'description': 'Error interno del servidor'}
    }
})
def delete_impresora(impresora_id):
    """Eliminar una impresora."""
    impresora = Impresoras.query.get(impresora_id)

    if not impresora:
        return jsonify({"message": "Impresora no encontrada"}), 404

    try:
        db.session.delete(impresora)
        db.session.commit()
        return jsonify({"message": "Impresora eliminada exitosamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al eliminar la impresora", "error": str(e)}), 500
