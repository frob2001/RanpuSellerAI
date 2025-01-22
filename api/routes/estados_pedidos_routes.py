from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.estados_pedidos import EstadosPedidos
from ..schemas.estados_pedidos_schema import EstadosPedidosSchema
from ..database import db

# Middleware protections
from api.middlewares.origin_middleware import validate_origin
from api.middlewares.firebase_auth_middleware import firebase_auth_required

estados_pedidos_bp = Blueprint('estados_pedidos', __name__)

# Instancias de los schemas
estados_pedidos_schema = EstadosPedidosSchema()
multiple_estados_pedidos_schema = EstadosPedidosSchema(many=True)

@estados_pedidos_bp.route('/', methods=['GET'])
@validate_origin()
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
                        'orden': {'type': 'integer', 'example': '1'},
                        'nombre': {'type': 'string', 'example': 'Esperando pago'},
                        'nombre_ingles': {'type': 'string', 'example': 'Waiting for payment'}
                    }
                }
            }
        }
    }
})
def get_estados_pedidos():
    """Obtener todos los estados de pedidos ordenados por el campo 'orden'"""
    estados = EstadosPedidos.query.order_by(EstadosPedidos.orden.asc()).all()
    return jsonify(multiple_estados_pedidos_schema.dump(estados)), 200

@estados_pedidos_bp.route('/', methods=['POST'])
@validate_origin()
@firebase_auth_required
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
        estado = estados_pedidos_schema.load(data, session=db.session)
        db.session.add(estado)
        db.session.commit()
        return jsonify(estados_pedidos_schema.dump(estado)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@estados_pedidos_bp.route('/<int:estado_pedido_id>', methods=['GET'])
@validate_origin()
@firebase_auth_required
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
    return jsonify(estados_pedidos_schema.dump(estado)), 200

@estados_pedidos_bp.route('/<int:estado_pedido_id>', methods=['PUT'])
@validate_origin()
@firebase_auth_required
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
        estado = estados_pedidos_schema.load(data, instance=estado, session=db.session)
        db.session.commit()
        return jsonify(estados_pedidos_schema.dump(estado)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@estados_pedidos_bp.route('/<int:estado_pedido_id>', methods=['DELETE'])
@validate_origin()
@firebase_auth_required
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
