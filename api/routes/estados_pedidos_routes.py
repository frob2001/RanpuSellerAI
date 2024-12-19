from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.estados_pedidos import EstadosPedidos
from ..database import db

estados_pedidos_bp = Blueprint('estados_pedidos', __name__)

@estados_pedidos_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['EstadosPedidos'],
    'summary': 'Listar estados de pedidos',
    'description': 'Obtiene todos los estados de pedidos registrados en la base de datos.',
    'responses': {
        200: {
            'description': 'Lista de estados de pedidos',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'estado_pedido_id': {'type': 'integer', 'example': 1},
                        'nombre': {'type': 'string', 'example': 'Pendiente'}
                    }
                }
            }
        }
    }
})
def get_estados_pedidos():
    """Obtener todos los estados de pedidos"""
    estados = EstadosPedidos.query.all()
    return jsonify([estado.to_dict() for estado in estados]), 200

@estados_pedidos_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['EstadosPedidos'],
    'summary': 'Crear estado de pedido',
    'description': 'Crea un nuevo estado de pedido en la base de datos.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'example': 'Pendiente'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Estado de pedido creado exitosamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'estado_pedido_id': {'type': 'integer', 'example': 1},
                    'nombre': {'type': 'string', 'example': 'Pendiente'}
                }
            }
        },
        400: {'description': 'Error al crear estado de pedido'}
    }
})
def create_estado_pedido():
    """Crear un nuevo estado de pedido"""
    data = request.get_json()
    try:
        estado = EstadosPedidos(nombre=data['nombre'])
        db.session.add(estado)
        db.session.commit()
        return jsonify(estado.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@estados_pedidos_bp.route('/<int:estado_pedido_id>', methods=['GET'])
@swag_from({
    'tags': ['EstadosPedidos'],
    'summary': 'Obtener estado de pedido',
    'description': 'Obtiene un estado de pedido por su ID.',
    'parameters': [
        {
            'name': 'estado_pedido_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del estado de pedido'
        }
    ],
    'responses': {
        200: {
            'description': 'Estado de pedido obtenido',
            'schema': {
                'type': 'object',
                'properties': {
                    'estado_pedido_id': {'type': 'integer', 'example': 1},
                    'nombre': {'type': 'string', 'example': 'Pendiente'}
                }
            }
        },
        404: {'description': 'Estado de pedido no encontrado'}
    }
})
def get_estado_pedido(estado_pedido_id):
    """Obtener un estado de pedido por ID"""
    estado = EstadosPedidos.query.get_or_404(estado_pedido_id)
    return jsonify(estado.to_dict()), 200

@estados_pedidos_bp.route('/<int:estado_pedido_id>', methods=['PUT'])
@swag_from({
    'tags': ['EstadosPedidos'],
    'summary': 'Actualizar estado de pedido',
    'description': 'Actualiza los datos de un estado de pedido existente.',
    'parameters': [
        {
            'name': 'estado_pedido_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del estado de pedido'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'example': 'Procesado'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Estado de pedido actualizado',
            'schema': {
                'type': 'object',
                'properties': {
                    'estado_pedido_id': {'type': 'integer', 'example': 1},
                    'nombre': {'type': 'string', 'example': 'Procesado'}
                }
            }
        },
        400: {'description': 'Error al actualizar estado de pedido'}
    }
})
def update_estado_pedido(estado_pedido_id):
    """Actualizar un estado de pedido existente"""
    estado = EstadosPedidos.query.get_or_404(estado_pedido_id)
    data = request.get_json()
    try:
        estado.nombre = data['nombre']
        db.session.commit()
        return jsonify(estado.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@estados_pedidos_bp.route('/<int:estado_pedido_id>', methods=['DELETE'])
@swag_from({
    'tags': ['EstadosPedidos'],
    'summary': 'Eliminar estado de pedido',
    'description': 'Elimina un estado de pedido por su ID.',
    'parameters': [
        {
            'name': 'estado_pedido_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del estado de pedido'
        }
    ],
    'responses': {
        200: {'description': 'Estado de pedido eliminado exitosamente'},
        400: {'description': 'Error al eliminar estado de pedido'}
    }
})
def delete_estado_pedido(estado_pedido_id):
    """Eliminar un estado de pedido"""
    estado = EstadosPedidos.query.get_or_404(estado_pedido_id)
    try:
        db.session.delete(estado)
        db.session.commit()
        return jsonify({"message": "Estado de pedido eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
