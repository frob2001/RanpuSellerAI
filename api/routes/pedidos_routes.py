from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.pedidos import Pedidos
from ..models.pedidos_usuario import PedidosUsuario
from ..models.productos_pedidos import ProductosPedidos
from ..models.direcciones import Direcciones
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
    'description': 'Obtiene una lista de todos los pedidos, incluyendo detalles de estado, dirección, impuesto, productos relacionados y usuario asociado.',
    'responses': {
        200: {
            'description': 'Lista de pedidos',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'pedido_id': {'type': 'integer', 'example': 1},
                        'fecha_envio': {'type': 'string', 'example': '2024-12-10T10:00:00'},
                        'fecha_entrega': {'type': 'string', 'example': '2024-12-12T15:00:00'},
                        'fecha_pago': {'type': 'string', 'example': '2024-12-10T09:00:00'},
                        'estado_pedido': {
                            'type': 'object',
                            'properties': {
                                'estado_pedido_id': {'type': 'integer', 'example': 1},
                                'nombre': {'type': 'string', 'example': 'Imprimiendo'}
                            }
                        },
                        'direccion': {
                            'type': 'object',
                            'properties': {
                                'direccion_id': {'type': 'integer', 'example': 1},
                                'cedula': {'type': 'string', 'example': '1234567890'},
                                'nombre_completo': {'type': 'string', 'example': 'John Doe'},
                                'telefono': {'type': 'string', 'example': '+593999999999'},
                                'calle_principal': {'type': 'string', 'example': 'Av. Siempre Viva'},
                                'calle_secundaria': {'type': 'string', 'example': 'Calle Falsa'},
                                'ciudad': {'type': 'string', 'example': 'Springfield'},
                                'provincia': {'type': 'string', 'example': 'Pichincha'},
                                'numeracion': {'type': 'string', 'example': '123'},
                                'referencia': {'type': 'string', 'example': 'Frente al parque'},
                                'codigo_postal': {'type': 'string', 'example': '170123'}
                            }
                        },
                        'impuesto': {
                            'type': 'object',
                            'properties': {
                                'impuesto_id': {'type': 'integer', 'example': 1},
                                'nombre': {'type': 'string', 'example': 'IVA'},
                                'porcentaje': {'type': 'string', 'example': '15.00'}
                            }
                        },
                        'usuario_id': {'type': 'integer', 'example': 1},
                        'pago_id': {'type': 'string', 'example': 'PAY123'},
                        'precio': {'type': 'string', 'example': '100.00'},
                        'precio_final': {'type': 'string', 'example': '112.00'},
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
    """Obtener todos los pedidos, incluyendo detalles, productos relacionados y usuario asociado."""
    pedidos = Pedidos.query.all()
    response = []
    for pedido in pedidos:
        productos_pedidos = [
            {
                "producto_id": item.producto.producto_id,
                "nombre": item.producto.nombre,
                "cantidad": item.cantidad
            } for item in ProductosPedidos.query.filter_by(pedido_id=pedido.pedido_id).all()
        ]

        usuario_pedido = PedidosUsuario.query.filter_by(pedido_id=pedido.pedido_id).first()
        usuario_id = usuario_pedido.usuario_id if usuario_pedido else None

        pedido_dict = pedido.to_dict()
        pedido_dict.pop("estado_pedido_id", None)
        pedido_dict.pop("direccion_id", None)
        pedido_dict.pop("impuesto_id", None)

        pedido_dict["estado_pedido"] = pedido.estado_pedido.to_dict() if pedido.estado_pedido else None
        pedido_dict["direccion"] = pedido.direcciones.to_dict() if pedido.direcciones else None
        pedido_dict["impuesto"] = pedido.impuesto.to_dict() if pedido.impuesto else None
        pedido_dict["productos"] = productos_pedidos
        pedido_dict["usuario_id"] = usuario_id

        response.append(pedido_dict)

    return jsonify(response), 200


@pedidos_bp.route('/<int:pedido_id>', methods=['GET'])
@swag_from({
    'tags': ['Pedidos'],
    'summary': 'Obtener un pedido por ID',
    'description': 'Obtiene un pedido específico, incluyendo detalles, productos relacionados y usuario asociado.',
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
                    'fecha_envio': {'type': 'string', 'example': '2024-12-10T10:00:00'},
                    'fecha_entrega': {'type': 'string', 'example': '2024-12-12T15:00:00'},
                    'fecha_pago': {'type': 'string', 'example': '2024-12-10T09:00:00'},
                    'estado_pedido': {
                        'type': 'object',
                        'properties': {
                            'estado_pedido_id': {'type': 'integer', 'example': 1},
                            'nombre': {'type': 'string', 'example': 'Imprimiendo'}
                        }
                    },
                    'direccion': {
                        'type': 'object',
                        'properties': {
                            'direccion_id': {'type': 'integer', 'example': 1},
                            'cedula': {'type': 'string', 'example': '1234567890'},
                            'nombre_completo': {'type': 'string', 'example': 'John Doe'},
                            'telefono': {'type': 'string', 'example': '+593999999999'},
                            'calle_principal': {'type': 'string', 'example': 'Av. Siempre Viva'},
                            'calle_secundaria': {'type': 'string', 'example': 'Calle Falsa'},
                            'ciudad': {'type': 'string', 'example': 'Springfield'},
                            'provincia': {'type': 'string', 'example': 'Pichincha'},
                            'numeracion': {'type': 'string', 'example': '123'},
                            'referencia': {'type': 'string', 'example': 'Frente al parque'},
                            'codigo_postal': {'type': 'string', 'example': '170123'}
                        }
                    },
                    'impuesto': {
                        'type': 'object',
                        'properties': {
                            'impuesto_id': {'type': 'integer', 'example': 1},
                            'nombre': {'type': 'string', 'example': 'IVA'},
                            'porcentaje': {'type': 'string', 'example': '15.00'}
                        }
                    },
                    'usuario_id': {'type': 'integer', 'example': 1},
                    'pago_id': {'type': 'string', 'example': 'PAY123'},
                    'precio': {'type': 'string', 'example': '100.00'},
                    'precio_final': {'type': 'string', 'example': '112.00'},
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
    """Obtener un pedido por su ID, incluyendo detalles, productos relacionados y usuario asociado."""
    pedido = Pedidos.query.get(pedido_id)
    if not pedido:
        return jsonify({"message": "Pedido no encontrado"}), 404

    productos_pedidos = [
        {
            "producto_id": item.producto.producto_id,
            "nombre": item.producto.nombre,
            "cantidad": item.cantidad
        } for item in ProductosPedidos.query.filter_by(pedido_id=pedido.pedido_id).all()
    ]

    usuario_pedido = PedidosUsuario.query.filter_by(pedido_id=pedido.pedido_id).first()
    usuario_id = usuario_pedido.usuario_id if usuario_pedido else None

    response = pedido.to_dict()
    response.pop("estado_pedido_id", None)
    response.pop("direccion_id", None)
    response.pop("impuesto_id", None)

    response["estado_pedido"] = pedido.estado_pedido.to_dict() if pedido.estado_pedido else None
    response["direccion"] = pedido.direcciones.to_dict() if pedido.direcciones else None
    response["impuesto"] = pedido.impuesto.to_dict() if pedido.impuesto else None
    response["productos"] = productos_pedidos
    response["usuario_id"] = usuario_id

    return jsonify(response), 200


@pedidos_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Pedidos'],
    'summary': 'Crear un nuevo pedido con dirección y usuario',
    'description': 'Crea un nuevo pedido, incluyendo la dirección asociada, usuario, productos relacionados, estado e impuesto.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'fecha_envio': {'type': 'string', 'example': '2024-12-10T10:00:00'},
                    'fecha_entrega': {'type': 'string', 'example': '2024-12-12T15:00:00'},
                    'fecha_pago': {'type': 'string', 'example': '2024-12-10T09:00:00'},
                    'estado_pedido_id': {'type': 'integer', 'example': 1},
                    'impuesto_id': {'type': 'integer', 'example': 1},
                    'precio': {'type': 'string', 'example': '100.00'},
                    'precio_final': {'type': 'string', 'example': '112.00'},
                    'pago_id': {'type': 'string', 'example': 'PAY123'},
                    'usuario_id': {'type': 'integer', 'example': 1},
                    'direccion': {
                        'type': 'object',
                        'properties': {
                            'cedula': {'type': 'string', 'example': '1234567890'},
                            'nombre_completo': {'type': 'string', 'example': 'John Doe'},
                            'telefono': {'type': 'string', 'example': '+593999999999'},
                            'calle_principal': {'type': 'string', 'example': 'Av. Siempre Viva'},
                            'calle_secundaria': {'type': 'string', 'example': 'Calle Falsa'},
                            'ciudad': {'type': 'string', 'example': 'Springfield'},
                            'provincia': {'type': 'string', 'example': 'Pichincha'},
                            'numeracion': {'type': 'string', 'example': '123'},
                            'referencia': {'type': 'string', 'example': 'Frente al parque'},
                            'codigo_postal': {'type': 'string', 'example': '170123'}
                        },
                        'required': [
                            'cedula', 'nombre_completo', 'telefono',
                            'calle_principal', 'ciudad', 'provincia'
                        ]
                    },
                    'productos': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'producto_id': {'type': 'integer', 'example': 1},
                                'cantidad': {'type': 'integer', 'example': 2}
                            }
                        }
                    }
                },
                'required': [
                    'fecha_envio', 'fecha_entrega', 'fecha_pago',
                    'estado_pedido_id', 'impuesto_id', 'precio', 'precio_final',
                    'pago_id', 'usuario_id', 'direccion', 'productos'
                ]
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
                    'direccion_id': {'type': 'integer', 'example': 1},
                    'usuario_id': {'type': 'integer', 'example': 1},
                    'message': {'type': 'string', 'example': 'Pedido, dirección y usuario asociados exitosamente'}
                }
            }
        },
        400: {'description': 'Datos inválidos en la solicitud'},
        500: {'description': 'Error interno del servidor'}
    }
})
def create_pedido():
    """Crear un nuevo pedido con dirección, usuario y productos relacionados."""
    data = request.get_json()

    # Validar campos obligatorios
    required_fields = [
        'fecha_envio', 'fecha_entrega', 'fecha_pago',
        'estado_pedido_id', 'impuesto_id', 'precio', 'precio_final',
        'pago_id', 'usuario_id', 'direccion', 'productos'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"El campo '{field}' es obligatorio"}), 400

    try:
        # Crear la dirección
        direccion_data = data['direccion']
        nueva_direccion = Direcciones(
            cedula=direccion_data['cedula'],
            nombre_completo=direccion_data['nombre_completo'],
            telefono=direccion_data['telefono'],
            calle_principal=direccion_data['calle_principal'],
            calle_secundaria=direccion_data.get('calle_secundaria'),
            ciudad=direccion_data['ciudad'],
            provincia=direccion_data['provincia'],
            numeracion=direccion_data.get('numeracion'),
            referencia=direccion_data.get('referencia'),
            codigo_postal=direccion_data.get('codigo_postal')
        )
        db.session.add(nueva_direccion)
        db.session.flush()  # Obtener el direccion_id antes de confirmar

        # Crear el pedido
        nuevo_pedido = Pedidos(
            fecha_envio=data['fecha_envio'],
            fecha_entrega=data['fecha_entrega'],
            fecha_pago=data['fecha_pago'],
            estado_pedido_id=data['estado_pedido_id'],
            direccion_id=nueva_direccion.direccion_id,
            impuesto_id=data['impuesto_id'],
            precio=data['precio'],
            precio_final=data['precio_final'],
            pago_id=data['pago_id']
        )
        db.session.add(nuevo_pedido)
        db.session.flush()  # Obtener el pedido_id antes del commit

        # Asociar el pedido al usuario
        usuario_pedido = PedidosUsuario(
            pedido_id=nuevo_pedido.pedido_id,
            usuario_id=data['usuario_id']
        )
        db.session.add(usuario_pedido)

        # Agregar productos al pedido
        for producto in data['productos']:
            producto_pedido = ProductosPedidos(
                pedido_id=nuevo_pedido.pedido_id,
                producto_id=producto['producto_id'],
                cantidad=producto['cantidad']
            )
            db.session.add(producto_pedido)

        db.session.commit()

        # Respuesta exitosa
        return jsonify({
            "pedido_id": nuevo_pedido.pedido_id,
            "direccion_id": nueva_direccion.direccion_id,
            "usuario_id": data['usuario_id'],
            "message": "Pedido, dirección y usuario asociados exitosamente"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al crear el pedido", "error": str(e)}), 500

