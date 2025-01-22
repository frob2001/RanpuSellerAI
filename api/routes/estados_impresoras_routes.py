from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.estados_impresoras import EstadosImpresoras
from ..schemas.estados_impresoras_schema import EstadosImpresorasSchema
from ..database import db

# Middleware protections
from api.middlewares.origin_middleware import validate_origin

# Crear el Blueprint para estados_impresoras
estados_impresoras_bp = Blueprint('estados_impresoras', __name__)

# Instancias del esquema
estado_impresora_schema = EstadosImpresorasSchema()
estados_impresoras_schema = EstadosImpresorasSchema(many=True)

@estados_impresoras_bp.route('/', methods=['GET'])
@validate_origin()
@swag_from({
    'tags': ['EstadosImpresoras'],
    'summary': 'Obtener todos los estados de impresoras',
    'description': 'Obtiene una lista de todos los estados de impresoras registrados.',
    'responses': {
        200: {
            'description': 'Lista de estados de impresoras',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'estado_impresora_id': {'type': 'integer', 'example': 1},
                        'nombre': {'type': 'string', 'example': 'Disponible'}
                    }
                }
            }
        }
    }
})
def get_todos_estados_impresoras():
    """Obtener todos los estados de impresoras registrados."""
    estados = EstadosImpresoras.query.all()
    return jsonify(estados_impresoras_schema.dump(estados)), 200

@estados_impresoras_bp.route('/<int:estado_impresora_id>', methods=['GET'])
@validate_origin()
@swag_from({
    'tags': ['EstadosImpresoras'],
    'summary': 'Obtener un estado de impresora por ID',
    'description': 'Obtiene un estado de impresora específico por su ID.',
    'parameters': [
        {
            'name': 'estado_impresora_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del estado de impresora a obtener'
        }
    ],
    'responses': {
        200: {'description': 'Estado de impresora encontrado'},
        404: {'description': 'Estado de impresora no encontrado'}
    }
})
def get_estado_impresora_por_id(estado_impresora_id):
    """Obtener un estado de impresora específico por su ID."""
    estado = EstadosImpresoras.query.get(estado_impresora_id)
    if not estado:
        return jsonify({"message": "Estado de impresora no encontrado"}), 404
    return jsonify(estado_impresora_schema.dump(estado)), 200

@estados_impresoras_bp.route('/', methods=['POST'])
@validate_origin()
@swag_from({
    'tags': ['EstadosImpresoras'],
    'summary': 'Crear un nuevo estado de impresora',
    'description': 'Registra un nuevo estado de impresora.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'example': 'En mantenimiento'}
                },
                'required': ['nombre']
            }
        }
    ],
    'responses': {
        201: {'description': 'Estado de impresora creado exitosamente'},
        400: {'description': 'Datos inválidos en la solicitud'}
    }
})
def create_estado_impresora():
    """Crear un nuevo estado de impresora."""
    data = request.get_json()
    try:
        nuevo_estado = estado_impresora_schema.load(data, session=db.session)
        db.session.add(nuevo_estado)
        db.session.commit()
        return jsonify(estado_impresora_schema.dump(nuevo_estado)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al crear el estado de impresora", "error": str(e)}), 500

@estados_impresoras_bp.route('/<int:estado_impresora_id>', methods=['PUT'])
@validate_origin()
@swag_from({
    'tags': ['EstadosImpresoras'],
    'summary': 'Actualizar un estado de impresora existente',
    'description': 'Actualiza los datos de un estado de impresora existente.',
    'parameters': [
        {
            'name': 'estado_impresora_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del estado de impresora a actualizar'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'example': 'No disponible'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Estado de impresora actualizado exitosamente'},
        404: {'description': 'Estado de impresora no encontrado'},
        400: {'description': 'Datos inválidos en la solicitud'}
    }
})
def update_estado_impresora(estado_impresora_id):
    """Actualizar un estado de impresora existente."""
    estado = EstadosImpresoras.query.get(estado_impresora_id)
    if not estado:
        return jsonify({"message": "Estado de impresora no encontrado"}), 404
    data = request.get_json()
    try:
        for key, value in data.items():
            setattr(estado, key, value)
        db.session.commit()
        return jsonify(estado_impresora_schema.dump(estado)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al actualizar el estado de impresora", "error": str(e)}), 500

@estados_impresoras_bp.route('/<int:estado_impresora_id>', methods=['DELETE'])
@validate_origin()
@swag_from({
    'tags': ['EstadosImpresoras'],
    'summary': 'Eliminar un estado de impresora existente',
    'description': 'Elimina un estado de impresora específico por su ID.',
    'parameters': [
        {
            'name': 'estado_impresora_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del estado de impresora a eliminar'
        }
    ],
    'responses': {
        200: {'description': 'Estado de impresora eliminado exitosamente'},
        404: {'description': 'Estado de impresora no encontrado'}
    }
})
def delete_estado_impresora(estado_impresora_id):
    """Eliminar un estado de impresora existente."""
    estado = EstadosImpresoras.query.get(estado_impresora_id)
    if not estado:
        return jsonify({"message": "Estado de impresora no encontrado"}), 404
    try:
        db.session.delete(estado)
        db.session.commit()
        return jsonify({"estado_impresora_id": estado_impresora_id, "message": "Estado de impresora eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al eliminar el estado de impresora", "error": str(e)}), 500
