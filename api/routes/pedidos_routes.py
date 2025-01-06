from flask import Blueprint, request, jsonify
from flasgger import swag_from
from firebase_admin import db as firebase_db
from sqlalchemy import and_, or_
from datetime import datetime
import pytz
from datetime import datetime
from ..models.pedidos import Pedidos
from ..models.pedidos_usuario import PedidosUsuario
from ..models.productos_pedidos import ProductosPedidos
from ..models.direcciones import Direcciones
from ..models.impuestos import Impuestos
from ..models.productos import Productos
from ..schemas.pedidos_schema import PedidosSchema
from ..models.usuarios import Usuarios
from ..database import db

ECUADOR_TZ = pytz.timezone("America/Guayaquil")
MONTHS_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]
MONTHS_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# Crear el Blueprint para pedidos
pedidos_bp = Blueprint('pedidos', __name__)

# Instancias del schema
pedido_schema = PedidosSchema()
multiple_pedidos_schema = PedidosSchema(many=True)

def format_date_spanish(dt: datetime) -> str:
    """Example output: 15 de noviembre, 2023."""
    if dt is None:
        return ""

    # 1) Interpret dt as UTC (attach tzinfo=UTC)
    dt_utc = dt.replace(tzinfo=pytz.utc)
    # 2) Convert to Ecuador time (UTC-5)
    local_dt = dt_utc.astimezone(ECUADOR_TZ)

    day = local_dt.day
    month = MONTHS_ES[local_dt.month - 1]
    year = local_dt.year
    return f"{day} de {month}, {year}"

def format_date_english(dt: datetime) -> str:
    """Example output: November 15, 2023."""
    if dt is None:
        return ""

    # 1) Interpret dt as UTC
    dt_utc = dt.replace(tzinfo=pytz.utc)
    # 2) Convert to Ecuador time (UTC-5)
    local_dt = dt_utc.astimezone(ECUADOR_TZ)

    day = local_dt.day
    month = MONTHS_EN[local_dt.month - 1]
    year = local_dt.year
    return f"{month} {day}, {year}"

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

@pedidos_bp.route('/usuario/<string:usuario_id>', methods=['GET'])
@swag_from({
    'tags': ['Pedidos'],
    'summary': 'Obtener pedidos por ID de usuario (con filtros y paginación)',
    'description': (
        'Obtiene una lista de pedidos asociados a un usuario específico. '
        'Permite filtrar por fechas de creación (start_date, end_date) y estado del pedido (estado_pedido_id). '
        'Los resultados se paginan y se pueden controlar mediante los parámetros page y per_page.'
    ),
    'parameters': [
        {
            'name': 'usuario_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': 'Firebase UID del usuario cuyos pedidos se desean obtener'
        },
        {
            'name': 'start_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'description': 'Filtra pedidos a partir de esta fecha (formato: YYYY-MM-DD). Si no se especifica, no se aplica filtro inicial.'
        },
        {
            'name': 'end_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'description': 'Filtra pedidos hasta esta fecha (formato: YYYY-MM-DD). Si no se especifica, no se aplica filtro final.'
        },
        {
            'name': 'estado_pedido_id',
            'in': 'query',
            'type': 'integer',
            'description': 'Filtra por el estado del pedido. Si no se especifica, devuelve pedidos de todos los estados.'
        },
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'description': 'Número de página para la paginación. Por defecto es 1.'
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'description': 'Cantidad de elementos por página. El valor predeterminado es 10.'
        }
    ],
    'responses': {
        200: {
            'description': 'Lista de pedidos paginados con fechas formateadas, estado en ES/EN, productos y thumbnail',
            'schema': {
                'type': 'object',
                'properties': {
                    'pedidos': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'pedido_id': {
                                    'type': 'integer',
                                    'example': 123
                                },
                                'fecha_creacion': {
                                    'type': 'string',
                                    'example': '2025-01-20T15:32:00'
                                },
                                'fecha_creacion_es': {
                                    'type': 'string',
                                    'example': '20 de enero, 2025'
                                },
                                'fecha_creacion_en': {
                                    'type': 'string',
                                    'example': 'January 20, 2025'
                                },
                                'estado': {
                                    'type': 'object',
                                    'properties': {
                                        'nombre': {
                                            'type': 'string',
                                            'example': 'Pagado'
                                        },
                                        'nombre_ingles': {
                                            'type': 'string',
                                            'example': 'Paid'
                                        }
                                    }
                                },
                                'productos_nombres': {
                                    'type': 'string',
                                    'example': 'RanpuLamp, Lámpara curva'
                                },
                                'cantidad_total': {
                                    'type': 'integer',
                                    'example': 2
                                },
                                'thumbnail': {
                                    'type': 'string',
                                    'example': 'https://mybucket.s3.amazonaws.com/image1.jpg'
                                }
                            }
                        }
                    },
                    'total_items': {
                        'type': 'integer',
                        'example': 45
                    },
                    'total_pages': {
                        'type': 'integer',
                        'example': 5
                    },
                    'current_page': {
                        'type': 'integer',
                        'example': 2
                    },
                    'per_page': {
                        'type': 'integer',
                        'example': 10
                    }
                }
            }
        },
        404: {
            'description': 'Usuario no encontrado o sin pedidos'
        }
    }
})
def get_pedidos_por_usuario(usuario_id):
    """Obtener todos los pedidos asociados a un usuario con filtros y paginación."""
    
    user = Usuarios.query.filter_by(firebase_uid=usuario_id).first()
    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404

    # Fetch search params from the request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    estado_pedido_id = request.args.get('estado_pedido_id')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Base query for pedidos_usuario
    query = Pedidos.query.join(PedidosUsuario).filter(
        PedidosUsuario.usuario_id == user.usuario_id
    )

    # Apply filters conditionally
    filters = []
    if start_date:
        filters.append(Pedidos.fecha_creacion >= start_date)
    if end_date:
        filters.append(Pedidos.fecha_creacion <= end_date)
    if estado_pedido_id:
        filters.append(Pedidos.estado_pedido_id == estado_pedido_id)

    # Apply all filters to the query
    if filters:
        query = query.filter(and_(*filters))

    # Paginate the query
    paginated_pedidos = query.paginate(page=page, per_page=per_page, error_out=False)
    pedidos = paginated_pedidos.items

    if not pedidos:
        return jsonify({"message": "Usuario sin pedidos en el rango especificado"}), 404

    # Build response
    response = []
    for pedido in pedidos:
        pp_items = ProductosPedidos.query.filter_by(pedido_id=pedido.pedido_id).all()

        product_names = []
        total_cantidad = 0
        thumbnail = None

        for idx, pp_item in enumerate(pp_items):
            product_names.append(pp_item.producto.nombre)
            total_cantidad += pp_item.cantidad

            if idx == 0:
                # Find the thumbnail image
                thumb_image = next(
                    (img for img in pp_item.producto.imagenes if img.is_thumbnail),
                    None
                )
                thumbnail = thumb_image.ubicacion if thumb_image else (
                    pp_item.producto.imagenes[0].ubicacion if pp_item.producto.imagenes else None
                )

        product_names_str = ", ".join(product_names)

        fecha_creacion = pedido.fecha_pago or pedido.fecha_creacion
        fecha_creacion_es = format_date_spanish(fecha_creacion)
        fecha_creacion_en = format_date_english(fecha_creacion)

        pedido_dict = {
            "pedido_id": pedido.pedido_id,
            "fecha_creacion": fecha_creacion.isoformat(),
            "fecha_creacion_es": fecha_creacion_es,
            "fecha_creacion_en": fecha_creacion_en,
            "estado": {
                "nombre": pedido.estado_pedido.nombre,
                "nombre_ingles": pedido.estado_pedido.nombre_ingles
            },
            "productos_nombres": product_names_str,
            "cantidad_total": total_cantidad,
            "thumbnail": thumbnail,
        }
        response.append(pedido_dict)

    # Return paginated response with metadata
    return jsonify({
        "pedidos": response,
        "total_items": paginated_pedidos.total,
        "total_pages": paginated_pedidos.pages,
        "current_page": paginated_pedidos.page,
        "per_page": paginated_pedidos.per_page
    }), 200

@pedidos_bp.route('', methods=['POST'], strict_slashes=False)
@swag_from({
    'tags': ['Pedidos'],
    'summary': 'Crear un nuevo pedido con dirección y usuario',
    'description': 'Crea un nuevo pedido, obteniendo impuestos activos y carrito del usuario desde Firebase.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
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
                    'usuario_id': {'type': 'integer', 'example': 1}
                },
                'required': ['direccion', 'usuario_id']
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
                    'message': {'type': 'string', 'example': 'Pedido creado exitosamente'}
                }
            }
        },
        500: {'description': 'Error interno del servidor'}
    }
})
def create_pedido():
    """Crear un nuevo pedido evitando duplicidad por temporal_cart_id y 'Esperando pago'."""
    data = request.get_json()

    usuario_id = data.get('usuario_id')
    direccion_data = data.get('direccion')

    # Validar que se haya recibido la dirección y el usuario
    if not direccion_data or not usuario_id:
        return jsonify({"message": "Dirección y usuario_id son obligatorios"}), 400

    try:

        # 1. Traer los pedidos del usuario
        user = Usuarios.query.filter_by(firebase_uid=usuario_id).first()

        if not user:
            new_user = Usuarios(firebase_uid=usuario_id)
            db.session.add(new_user)
            db.session.flush()  # Get the user ID without committing yet
            user = new_user

        pedido_usuario = PedidosUsuario.query.filter_by(usuario_id=user.usuario_id).all()
        pedido_ids = [p.pedido_id for p in pedido_usuario]

        # 2. Recuperar el carrito del usuario desde Firebase
        cart_ref = firebase_db.reference(f'/carts/{usuario_id}')
        cart_snapshot = cart_ref.get()

        if not cart_snapshot or 'items' not in cart_snapshot or not cart_snapshot['items']:
            return jsonify({"message": "El carrito está vacío o no existe"}), 400

        cart_items = cart_snapshot['items']
        temporal_cart_id = cart_snapshot.get('temporalId')

        # 3. Descartar que se quiera guardar un pedido exactamente igual a uno existente, pero actualizando la dirección de todas maneras
        existing_pedido = Pedidos.query.filter(
            Pedidos.pedido_id.in_(pedido_ids),
            Pedidos.temporal_cart_id == temporal_cart_id
        ).first()

        if existing_pedido:

            direccion_existente = Direcciones.query.get(existing_pedido.direccion_id)
            
            if direccion_existente:
                direccion_existente.cedula = direccion_data['cedula']
                direccion_existente.nombre_completo = direccion_data['nombre_completo']
                direccion_existente.telefono = direccion_data['telefono']
                direccion_existente.calle_principal = direccion_data['calle_principal']
                direccion_existente.ciudad = direccion_data['ciudad']
                direccion_existente.provincia = direccion_data['provincia']
                direccion_existente.calle_secundaria = direccion_data.get('calle_secundaria')
                direccion_existente.numeracion = direccion_data.get('numeracion')
                direccion_existente.referencia = direccion_data.get('referencia')
                direccion_existente.codigo_postal = direccion_data.get('codigo_postal')
                db.session.flush()
                db.session.commit()


            return jsonify({
                "message": "Pedido ya existe con este temporal_cart_id, dirección actualizada",
                "pedido_id": existing_pedido.pedido_id
            }), 201

        # 4. Calcular el precio total del carrito
        subtotal = 0

        for item in cart_items:
            producto_id = item.get('databaseProductId')  # Use the correct key
            quantity = item.get('quantity', 0)

            if not producto_id or not isinstance(quantity, int) or quantity <= 0:
                return jsonify({"message": f"ID de producto o cantidad inválida en el item: {item}"}), 400

            producto = Productos.query.get(producto_id)
            if not producto:
                return jsonify({"message": f"Producto con ID {producto_id} no encontrado"}), 404

            # Multiply price by quantity and accumulate in the subtotal
            subtotal += float(producto.precio) * quantity
        
        # 5. Obtener el impuesto activo
        active_tax = Impuestos.query.filter_by(activo=True).first()
        if not active_tax:
            return jsonify({"message": "No hay impuesto activo configurado"}), 400

        tax_percentage = float(active_tax.porcentaje) / 100
        calculated_tax = subtotal * tax_percentage
        shipping_fee = 2.00
        total_price = subtotal + calculated_tax + shipping_fee

        # 6. Verificar si ya existe un pedido con el estado 'Esperando pago'
        existing_pending_pedido = Pedidos.query.filter(
            Pedidos.pedido_id.in_(pedido_ids),
            Pedidos.estado_pedido_id == 8  # 'Esperando pago'
        ).first()

        if existing_pending_pedido:
            # Sobreescribir el pedido existente
            
            # 7. Actualizar la dirección existente
            direccion_existente = Direcciones.query.get(existing_pending_pedido.direccion_id)
            
            if direccion_existente:
                direccion_existente.cedula = direccion_data['cedula']
                direccion_existente.nombre_completo = direccion_data['nombre_completo']
                direccion_existente.telefono = direccion_data['telefono']
                direccion_existente.calle_principal = direccion_data['calle_principal']
                direccion_existente.ciudad = direccion_data['ciudad']
                direccion_existente.provincia = direccion_data['provincia']
                direccion_existente.calle_secundaria = direccion_data.get('calle_secundaria')
                direccion_existente.numeracion = direccion_data.get('numeracion')
                direccion_existente.referencia = direccion_data.get('referencia')
                direccion_existente.codigo_postal = direccion_data.get('codigo_postal')
                db.session.flush()
            else:
                nueva_direccion = Direcciones(
                    cedula=direccion_data['cedula'],
                    nombre_completo=direccion_data['nombre_completo'],
                    telefono=direccion_data['telefono'],
                    calle_principal=direccion_data['calle_principal'],
                    ciudad=direccion_data['ciudad'],
                    provincia=direccion_data['provincia'],
                    calle_secundaria=direccion_data.get('calle_secundaria'),
                    numeracion=direccion_data.get('numeracion'),
                    referencia=direccion_data.get('referencia'),
                    codigo_postal=direccion_data.get('codigo_postal')
                )
                db.session.add(nueva_direccion)
                db.session.flush()
                existing_pending_pedido.direccion_id = nueva_direccion.direccion_id

            # 8. Actualizar el pedido existente
            existing_pending_pedido.precio = subtotal
            existing_pending_pedido.precio_final = total_price
            existing_pending_pedido.impuesto_id = active_tax.impuesto_id
            existing_pending_pedido.temporal_cart_id = temporal_cart_id  # Actualizar temporal ID
            db.session.flush()

            # 9. Eliminar productos previos y agregar los nuevos
            ProductosPedidos.query.filter_by(pedido_id=existing_pending_pedido.pedido_id).delete()

            for item in cart_items:
                producto_pedido = ProductosPedidos(
                    pedido_id=existing_pending_pedido.pedido_id,
                    producto_id=item['databaseProductId'],
                    cantidad=item['quantity']
                )
                db.session.add(producto_pedido)

            db.session.commit()

            return jsonify({
                "pedido_id": existing_pending_pedido.pedido_id,
                "direccion_id": existing_pending_pedido.direccion_id,
                "usuario_id": user.usuario_id,
                "message": "Pedido actualizado exitosamente"
            }), 201

        else:
            # 7. Crear un nuevo pedido (caso en el que no haya uno existente 'Esperando pago')
            nueva_direccion = Direcciones(
                cedula=direccion_data['cedula'],
                nombre_completo=direccion_data['nombre_completo'],
                telefono=direccion_data['telefono'],
                calle_principal=direccion_data['calle_principal'],
                ciudad=direccion_data['ciudad'],
                provincia=direccion_data['provincia'],
                calle_secundaria=direccion_data.get('calle_secundaria'),
                numeracion=direccion_data.get('numeracion'),
                referencia=direccion_data.get('referencia'),
                codigo_postal=direccion_data.get('codigo_postal')
            )
            db.session.add(nueva_direccion)
            db.session.flush()

            nuevo_pedido = Pedidos(
                fecha_envio=None,
                fecha_entrega=None,
                fecha_pago=None,
                estado_pedido_id=8,
                direccion_id=nueva_direccion.direccion_id,
                impuesto_id=active_tax.impuesto_id,
                precio=subtotal,
                precio_final=total_price,
                pago_id=None,
                temporal_cart_id=temporal_cart_id
            )
            db.session.add(nuevo_pedido)
            db.session.flush()

            usuario_pedido = PedidosUsuario(
                pedido_id=nuevo_pedido.pedido_id,
                usuario_id=user.usuario_id
            )
            db.session.add(usuario_pedido)

            for item in cart_items:
                producto_pedido = ProductosPedidos(
                    pedido_id=nuevo_pedido.pedido_id,
                    producto_id=item['databaseProductId'],
                    cantidad=item['quantity']
                )
                db.session.add(producto_pedido)

            db.session.commit()

            return jsonify({
                "pedido_id": nuevo_pedido.pedido_id,
                "direccion_id": nueva_direccion.direccion_id,
                "usuario_id": user.usuario_id,
                "message": "Pedido creado exitosamente"
            }), 201


    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al crear el pedido", "error": str(e)}), 500

@pedidos_bp.route('/<int:pedido_id>', methods=['PUT'])
@swag_from({
    'tags': ['Pedidos'],
    'summary': 'Actualizar un pedido existente',
    'description': 'Actualiza un pedido, incluyendo la dirección asociada, los productos relacionados, el estado, el impuesto y el usuario asociado.',
    'parameters': [
        {
            'name': 'pedido_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del pedido a actualizar'
        },
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
                        }
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
                    },
                    'usuario_id': {'type': 'integer', 'example': 1}
                },
                'required': [
                    'fecha_envio', 'fecha_entrega', 'fecha_pago',
                    'estado_pedido_id', 'impuesto_id', 'precio', 'precio_final', 'pago_id',
                    'direccion', 'productos', 'usuario_id'
                ]
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Pedido actualizado exitosamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'pedido_id': {'type': 'integer', 'example': 1},
                    'message': {'type': 'string', 'example': 'Pedido actualizado exitosamente'}
                }
            }
        },
        400: {'description': 'Datos inválidos en la solicitud'},
        404: {'description': 'Pedido no encontrado'},
        500: {'description': 'Error interno del servidor'}
    }
})
def update_pedido(pedido_id):
    """Actualizar un pedido existente, incluyendo dirección, productos y usuario asociado."""
    data = request.get_json()

    # Validar existencia del pedido
    pedido = Pedidos.query.get(pedido_id)
    if not pedido:
        return jsonify({"message": "Pedido no encontrado"}), 404

    try:
        # Actualizar dirección
        direccion_data = data['direccion']
        direccion = Direcciones.query.get(pedido.direccion_id)
        if direccion:
            direccion.cedula = direccion_data['cedula']
            direccion.nombre_completo = direccion_data['nombre_completo']
            direccion.telefono = direccion_data['telefono']
            direccion.calle_principal = direccion_data['calle_principal']
            direccion.calle_secundaria = direccion_data.get('calle_secundaria')
            direccion.ciudad = direccion_data['ciudad']
            direccion.provincia = direccion_data['provincia']
            direccion.numeracion = direccion_data.get('numeracion')
            direccion.referencia = direccion_data.get('referencia')
            direccion.codigo_postal = direccion_data.get('codigo_postal')

        # Actualizar datos del pedido
        pedido.fecha_envio = data['fecha_envio']
        pedido.fecha_entrega = data['fecha_entrega']
        pedido.fecha_pago = data['fecha_pago']
        pedido.estado_pedido_id = data['estado_pedido_id']
        pedido.impuesto_id = data['impuesto_id']
        pedido.precio = data['precio']
        pedido.precio_final = data['precio_final']
        pedido.pago_id = data['pago_id']

        # Actualizar usuario del pedido
        usuario_id = data['usuario_id']
        pedido_usuario = PedidosUsuario.query.filter_by(pedido_id=pedido_id).first()
        if pedido_usuario:
            pedido_usuario.usuario_id = usuario_id
        else:
            nuevo_pedido_usuario = PedidosUsuario(pedido_id=pedido_id, usuario_id=usuario_id)
            db.session.add(nuevo_pedido_usuario)

        # Actualizar productos del pedido
        nuevos_productos = data['productos']
        productos_existentes = ProductosPedidos.query.filter_by(pedido_id=pedido_id).all()

        # Eliminar productos que ya no están en la solicitud
        productos_a_eliminar = [
            producto for producto in productos_existentes
            if producto.producto_id not in [p['producto_id'] for p in nuevos_productos]
        ]
        for producto in productos_a_eliminar:
            db.session.delete(producto)

        # Agregar o actualizar productos existentes
        for nuevo_producto in nuevos_productos:
            producto_existente = next(
                (p for p in productos_existentes if p.producto_id == nuevo_producto['producto_id']), None
            )
            if producto_existente:
                producto_existente.cantidad = nuevo_producto['cantidad']
            else:
                nuevo_producto_pedido = ProductosPedidos(
                    pedido_id=pedido_id,
                    producto_id=nuevo_producto['producto_id'],
                    cantidad=nuevo_producto['cantidad']
                )
                db.session.add(nuevo_producto_pedido)

        db.session.commit()

        # Respuesta exitosa
        return jsonify({
            "pedido_id": pedido_id,
            "message": "Pedido actualizado exitosamente"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al actualizar el pedido", "error": str(e)}), 500

@pedidos_bp.route('/<int:pedido_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Pedidos'],
    'summary': 'Eliminar un pedido existente',
    'description': 'Elimina un pedido específico, incluyendo los productos relacionados, la dirección asociada y la relación con el usuario.',
    'parameters': [
        {
            'name': 'pedido_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del pedido a eliminar'
        }
    ],
    'responses': {
        200: {
            'description': 'Pedido eliminado exitosamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'pedido_id': {'type': 'integer', 'example': 1},
                    'message': {'type': 'string', 'example': 'Pedido eliminado exitosamente'}
                }
            }
        },
        404: {'description': 'Pedido no encontrado'},
        500: {'description': 'Error interno del servidor'}
    }
})
def delete_pedido(pedido_id):
    """Eliminar un pedido existente, incluyendo dirección, productos y relación con usuario."""
    # Validar existencia del pedido
    pedido = Pedidos.query.get(pedido_id)
    if not pedido:
        return jsonify({"message": "Pedido no encontrado"}), 404

    try:
        # Eliminar productos relacionados con el pedido
        productos_pedidos = ProductosPedidos.query.filter_by(pedido_id=pedido_id).all()
        for producto in productos_pedidos:
            db.session.delete(producto)

        # Eliminar la relación usuario-pedido
        pedido_usuario = PedidosUsuario.query.filter_by(pedido_id=pedido_id).first()
        if pedido_usuario:
            db.session.delete(pedido_usuario)

        # Eliminar la dirección asociada
        direccion = Direcciones.query.get(pedido.direccion_id)
        if direccion:
            db.session.delete(direccion)

        # Eliminar el pedido
        db.session.delete(pedido)

        db.session.commit()

        # Respuesta exitosa
        return jsonify({
            "pedido_id": pedido_id,
            "message": "Pedido eliminado exitosamente"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al eliminar el pedido", "error": str(e)}), 500
