from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.pedidos import Pedidos
from ..models.pedidos_usuario import PedidosUsuario
from ..schemas.pedidos_schema import PedidosSchema
from ..database import db

# Crear el Blueprint para pedidos
pedidos_bp = Blueprint('pedidos', __name__)

# Instancias del schema
pedido_schema = PedidosSchema()
multiple_pedidos_schema = PedidosSchema(many=True)

@pedidos_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Pedidos'],
    'summary': 'Listar pedidos',
    'description': 'Obtiene todos los pedidos registrados en la base de datos, incluyendo detalles de impuestos, direcciones, estados de pedido y el usuario asociado.',
    'responses': {
        200: {
            'description': 'Lista de pedidos',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'pedido_id': {'type': 'integer', 'example': 1},
                        'fecha_envio': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T10:00:00'},
                        'fecha_entrega': {'type': 'string', 'format': 'date-time', 'example': '2023-01-05T10:00:00'},
                        'fecha_pago': {'type': 'string', 'format': 'date-time', 'example': '2023-01-02T10:00:00'},
                        'estado_pedido_id': {'type': 'integer', 'example': 1},
                        'direccion_id': {'type': 'integer', 'example': 1},
                        'precio': {'type': 'string', 'example': '100.00'},
                        'impuesto_id': {'type': 'integer', 'example': 1},
                        'precio_final': {'type': 'string', 'example': '112.00'},
                        'pago_id': {'type': 'string', 'example': 'PAY123'},
                        'usuario_id': {'type': 'integer', 'example': 1}
                    }
                }
            }
        }
    }
})
def get_pedidos():
    """Obtener todos los pedidos"""
    pedidos = Pedidos.query.all()
    resultado = []
    for pedido in pedidos:
        data = pedido.to_dict()
        usuario = PedidosUsuario.query.filter_by(pedido_id=pedido.pedido_id).first()
        if usuario:
            data["usuario_id"] = usuario.usuario_id
        resultado.append(data)
    return jsonify(resultado), 200

@pedidos_bp.route('/usuario/<int:usuario_id>', methods=['GET'])
@swag_from({
    'tags': ['Pedidos'],
    'summary': 'Listar pedidos por usuario',
    'description': 'Obtiene todos los pedidos asociados a un usuario específico.',
    'parameters': [
        {
            'name': 'usuario_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del usuario'
        }
    ],
    'responses': {
        200: {
            'description': 'Lista de pedidos del usuario',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'pedido_id': {'type': 'integer', 'example': 1},
                        'fecha_envio': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T10:00:00'},
                        'fecha_entrega': {'type': 'string', 'format': 'date-time', 'example': '2023-01-05T10:00:00'},
                        'fecha_pago': {'type': 'string', 'format': 'date-time', 'example': '2023-01-02T10:00:00'},
                        'estado_pedido_id': {'type': 'integer', 'example': 1},
                        'direccion_id': {'type': 'integer', 'example': 1},
                        'precio': {'type': 'string', 'example': '100.00'},
                        'impuesto_id': {'type': 'integer', 'example': 1},
                        'precio_final': {'type': 'string', 'example': '112.00'},
                        'pago_id': {'type': 'string', 'example': 'PAY123'}
                    }
                }
            }
        },
        404: {'description': 'Usuario no tiene pedidos'}
    }
})
def get_pedidos_por_usuario(usuario_id):
    """Obtener pedidos por usuario"""
    pedidos_usuario = PedidosUsuario.query.filter_by(usuario_id=usuario_id).all()
    if not pedidos_usuario:
        return jsonify({"message": "No hay pedidos para este usuario"}), 404

    resultado = []
    for relacion in pedidos_usuario:
        pedido = Pedidos.query.get(relacion.pedido_id)
        if pedido:
            resultado.append(pedido.to_dict())
    return jsonify(resultado), 200

@pedidos_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Pedidos'],
    'summary': 'Crear pedido',
    'description': 'Crea un nuevo pedido en la base de datos, incluyendo el usuario asociado.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'fecha_envio': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T10:00:00'},
                    'fecha_entrega': {'type': 'string', 'format': 'date-time', 'example': '2023-01-05T10:00:00'},
                    'fecha_pago': {'type': 'string', 'format': 'date-time', 'example': '2023-01-02T10:00:00'},
                    'estado_pedido_id': {'type': 'integer', 'example': 1},
                    'direccion_id': {'type': 'integer', 'example': 1},
                    'precio': {'type': 'string', 'example': '100.00'},
                    'impuesto_id': {'type': 'integer', 'example': 1},
                    'precio_final': {'type': 'string', 'example': '112.00'},
                    'pago_id': {'type': 'string', 'example': 'PAY123'},
                    'usuario_id': {'type': 'integer', 'example': 1}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Pedido creado exitosamente'}
    }
})
def create_pedido():
    """Crear un nuevo pedido"""
    data = request.get_json()
    usuario_id = data.pop('usuario_id', None)
    if not usuario_id:
        return jsonify({"error": "Falta el usuario_id"}), 400
    try:
        pedido = pedido_schema.load(data, session=db.session)
        db.session.add(pedido)
        db.session.commit()

        pedido_usuario = PedidosUsuario(pedido_id=pedido.pedido_id, usuario_id=usuario_id)
        db.session.add(pedido_usuario)
        db.session.commit()

        return jsonify(pedido_schema.dump(pedido)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@pedidos_bp.route('/<int:pedido_id>', methods=['PUT'])
@swag_from({
    'tags': ['Pedidos'],
    'summary': 'Actualizar pedido',
    'description': 'Actualiza los datos de un pedido existente, incluyendo el usuario asociado.',
    'parameters': [
        {
            'name': 'pedido_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del pedido'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'fecha_envio': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T10:00:00'},
                    'fecha_entrega': {'type': 'string', 'format': 'date-time', 'example': '2023-01-05T10:00:00'},
                    'fecha_pago': {'type': 'string', 'format': 'date-time', 'example': '2023-01-02T10:00:00'},
                    'estado_pedido_id': {'type': 'integer', 'example': 1},
                    'direccion_id': {'type': 'integer', 'example': 1},
                    'precio': {'type': 'string', 'example': '100.00'},
                    'impuesto_id': {'type': 'integer', 'example': 1},
                    'precio_final': {'type': 'string', 'example': '112.00'},
                    'pago_id': {'type': 'string', 'example': 'PAY123'},
                    'usuario_id': {'type': 'integer', 'example': 1}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Pedido actualizado exitosamente'},
        400: {'description': 'Error al actualizar el pedido'}
    }
})
def update_pedido(pedido_id):
    """Actualizar un pedido existente"""
    data = request.get_json()
    usuario_id = data.pop('usuario_id', None)
    try:
        pedido = Pedidos.query.get_or_404(pedido_id)
        for key, value in data.items():
            setattr(pedido, key, value)
        db.session.commit()

        if usuario_id:
            pedidos_usuario = PedidosUsuario.query.filter_by(pedido_id=pedido_id).first()
            if pedidos_usuario:
                pedidos_usuario.usuario_id = usuario_id
            else:
                nuevo_usuario = PedidosUsuario(pedido_id=pedido_id, usuario_id=usuario_id)
                db.session.add(nuevo_usuario)
            db.session.commit()

        return jsonify(pedido_schema.dump(pedido)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@pedidos_bp.route('/<int:pedido_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Pedidos'],
    'summary': 'Eliminar pedido',
    'description': 'Elimina un pedido y su asociación con un usuario si existe.',
    'parameters': [
        {
            'name': 'pedido_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del pedido'
        }
    ],
    'responses': {
        200: {'description': 'Pedido eliminado exitosamente'},
        400: {'description': 'Error al eliminar el pedido'}
    }
})
def delete_pedido(pedido_id):
    """Eliminar un pedido"""
    try:
        pedido = Pedidos.query.get_or_404(pedido_id)
        PedidosUsuario.query.filter_by(pedido_id=pedido_id).delete()
        db.session.delete(pedido)
        db.session.commit()
        return jsonify({"message": "Pedido eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
