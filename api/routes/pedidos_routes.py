from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.pedidos import Pedidos
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
    'description': 'Obtiene todos los pedidos registrados en la base de datos, incluyendo detalles de impuestos, direcciones y estados de pedido.',
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
                        'estado_pedido': {
                            'type': 'object',
                            'properties': {
                                'estado_pedido_id': {'type': 'integer', 'example': 1},
                                'nombre': {'type': 'string', 'example': 'Pendiente'}
                            }
                        },
                        'direccion': {
                            'type': 'object',
                            'properties': {
                                'direccion_id': {'type': 'integer', 'example': 1},
                                'cedula': {'type': 'string', 'example': '0102030405'},
                                'nombre_completo': {'type': 'string', 'example': 'Juan Perez'},
                                'telefono': {'type': 'string', 'example': '0987654321'},
                                'calle_principal': {'type': 'string', 'example': 'Calle Principal'},
                                'calle_secundaria': {'type': 'string', 'example': 'Calle Secundaria'},
                                'ciudad': {'type': 'string', 'example': 'Quito'},
                                'provincia': {'type': 'string', 'example': 'Pichincha'},
                                'codigo_postal': {'type': 'string', 'example': '170123'}
                            }
                        },
                        'impuesto': {
                            'type': 'object',
                            'properties': {
                                'impuesto_id': {'type': 'integer', 'example': 1},
                                'nombre': {'type': 'string', 'example': 'IVA'},
                                'porcentaje': {'type': 'string', 'example': '12.00'}
                            }
                        },
                        'precio': {'type': 'string', 'example': '100.00'},
                        'precio_final': {'type': 'string', 'example': '112.00'},
                        'pago_id': {'type': 'string', 'example': 'PAY123'}
                    }
                }
            }
        }
    }
})
def get_pedidos():
    """Obtener todos los pedidos"""
    pedidos = Pedidos.query.all()
    return jsonify(multiple_pedidos_schema.dump(pedidos)), 200

@pedidos_bp.route('/<int:pedido_id>', methods=['GET'])
@swag_from({
    'tags': ['Pedidos'],
    'summary': 'Obtener pedido',
    'description': 'Obtiene un pedido por su ID, incluyendo detalles de impuestos, direcciones y estados de pedido.',
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
        200: {
            'description': 'Pedido obtenido',
            'schema': {
                'type': 'object',
                'properties': {
                    'pedido_id': {'type': 'integer', 'example': 1},
                    'fecha_envio': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T10:00:00'},
                    'fecha_entrega': {'type': 'string', 'format': 'date-time', 'example': '2023-01-05T10:00:00'},
                    'fecha_pago': {'type': 'string', 'format': 'date-time', 'example': '2023-01-02T10:00:00'},
                    'estado_pedido': {
                        'type': 'object',
                        'properties': {
                            'estado_pedido_id': {'type': 'integer', 'example': 1},
                            'nombre': {'type': 'string', 'example': 'Pendiente'}
                        }
                    },
                    'direccion': {
                        'type': 'object',
                        'properties': {
                            'direccion_id': {'type': 'integer', 'example': 1},
                            'cedula': {'type': 'string', 'example': '0102030405'},
                            'nombre_completo': {'type': 'string', 'example': 'Juan Perez'},
                            'telefono': {'type': 'string', 'example': '0987654321'},
                            'calle_principal': {'type': 'string', 'example': 'Calle Principal'},
                            'calle_secundaria': {'type': 'string', 'example': 'Calle Secundaria'},
                            'ciudad': {'type': 'string', 'example': 'Quito'},
                            'provincia': {'type': 'string', 'example': 'Pichincha'},
                            'codigo_postal': {'type': 'string', 'example': '170123'}
                        }
                    },
                    'impuesto': {
                        'type': 'object',
                        'properties': {
                            'impuesto_id': {'type': 'integer', 'example': 1},
                            'nombre': {'type': 'string', 'example': 'IVA'},
                            'porcentaje': {'type': 'string', 'example': '12.00'}
                        }
                    },
                    'precio': {'type': 'string', 'example': '100.00'},
                    'precio_final': {'type': 'string', 'example': '112.00'},
                    'pago_id': {'type': 'string', 'example': 'PAY123'}
                }
            }
        },
        404: {'description': 'Pedido no encontrado'}
    }
})
def get_pedido(pedido_id):
    """Obtener un pedido por ID"""
    pedido = Pedidos.query.get_or_404(pedido_id)
    return jsonify(pedido_schema.dump(pedido)), 200

@pedidos_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Pedidos'],
    'summary': 'Crear pedido',
    'description': 'Crea un nuevo pedido en la base de datos.',
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
                    'pago_id': {'type': 'string', 'example': 'PAY123'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Pedido creado exitosamente',
            'schema': {
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
        },
        400: {'description': 'Error al crear el pedido'}
    }
})
def create_pedido():
    """Crear un nuevo pedido"""
    data = request.get_json()
    try:
        pedido = pedido_schema.load(data, session=db.session)
        db.session.add(pedido)
        db.session.commit()
        return jsonify(pedido_schema.dump(pedido)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
