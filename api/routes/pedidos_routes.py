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
    'summary': 'Obtener todos los pedidos',
    'description': 'Obtiene una lista de todos los pedidos, incluyendo sus detalles de estado, dirección, impuesto y productos relacionados.',
    'responses': {
        200: {
            'description': 'Lista de pedidos',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'pedido_id': {'type': 'integer', 'example': 1},
                        'fecha_envio': {'type': 'string', 'example': '2024-12-19T14:30:00'},
                        'fecha_entrega': {'type': 'string', 'example': '2024-12-22T10:00:00'},
                        'fecha_pago': {'type': 'string', 'example': '2024-12-18T12:00:00'},
                        'estado_pedido': {'type': 'object', 'example': {'estado_pedido_id': 1, 'nombre': 'Enviado'}},
                        'direccion': {'type': 'object', 'example': {'direccion_id': 1, 'calle_principal': 'Av. Siempre Viva', 'ciudad': 'Springfield'}},
                        'impuesto': {'type': 'object', 'example': {'impuesto_id': 1, 'nombre': 'IVA', 'porcentaje': 12.00}},
                        'productos': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'producto_id': {'type': 'integer', 'example': 1},
                                    'nombre': {'type': 'string', 'example': 'Lámpara Redonda'},
                                    'cantidad': {'type': 'integer', 'example': 2}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_todos_pedidos():
    """Obtener todos los pedidos, incluyendo detalles y productos relacionados."""
    pedidos = Pedidos.query.all()
    response = []
    for pedido in pedidos:
        productos_pedidos = [
            {
                "producto_id": item.producto.producto_id,
                "nombre": item.producto.nombre,
                "cantidad": item.cantidad
            } for item in pedido.productos_pedidos_list
        ]

        pedido_dict = pedido.to_dict()
        pedido_dict["estado_pedido"] = pedido.estado_pedido.to_dict() if pedido.estado_pedido else None
        pedido_dict["direccion"] = pedido.direcciones.to_dict() if pedido.direcciones else None
        pedido_dict["impuesto"] = pedido.impuesto.to_dict() if pedido.impuesto else None
        pedido_dict["productos"] = productos_pedidos
        response.append(pedido_dict)

    return jsonify(response), 200


@pedidos_bp.route('/<int:pedido_id>', methods=['GET'])
@swag_from({
    'tags': ['Pedidos'],
    'summary': 'Obtener un pedido por ID',
    'description': 'Obtiene un pedido específico por su ID, incluyendo los detalles de estado, dirección, impuesto y productos relacionados.',
    'parameters': [
        {
            'name': 'pedido_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del pedido a obtener'
        }
    ],
    'responses': {
        200: {
            'description': 'Pedido encontrado',
            'schema': {
                'type': 'object',
                'properties': {
                    'pedido_id': {'type': 'integer', 'example': 1},
                    'fecha_envio': {'type': 'string', 'example': '2024-12-19T14:30:00'},
                    'fecha_entrega': {'type': 'string', 'example': '2024-12-22T10:00:00'},
                    'fecha_pago': {'type': 'string', 'example': '2024-12-18T12:00:00'},
                    'estado_pedido': {'type': 'object', 'example': {'estado_pedido_id': 1, 'nombre': 'Enviado'}},
                    'direccion': {'type': 'object', 'example': {'direccion_id': 1, 'calle_principal': 'Av. Siempre Viva', 'ciudad': 'Springfield'}},
                    'impuesto': {'type': 'object', 'example': {'impuesto_id': 1, 'nombre': 'IVA', 'porcentaje': 12.00}},
                    'productos': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'producto_id': {'type': 'integer', 'example': 1},
                                'nombre': {'type': 'string', 'example': 'Lámpara Redonda'},
                                'cantidad': {'type': 'integer', 'example': 2}
                            }
                        }
                    }
                }
            }
        },
        404: {'description': 'Pedido no encontrado'}
    }
})
def get_pedido_por_id(pedido_id):
    """Obtener un pedido por su ID, incluyendo detalles y productos relacionados."""
    pedido = Pedidos.query.get(pedido_id)
    if not pedido:
        return jsonify({"message": "Pedido no encontrado"}), 404

    productos_pedidos = [
        {
            "producto_id": item.producto.producto_id,
            "nombre": item.producto.nombre,
            "cantidad": item.cantidad
        } for item in pedido.productos_pedidos_list
    ]

    response = pedido.to_dict()
    response["estado_pedido"] = pedido.estado_pedido.to_dict() if pedido.estado_pedido else None
    response["direccion"] = pedido.direcciones.to_dict() if pedido.direcciones else None
    response["impuesto"] = pedido.impuesto.to_dict() if pedido.impuesto else None
    response["productos"] = productos_pedidos

    return jsonify(response), 200
