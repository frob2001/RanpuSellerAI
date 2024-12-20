from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.productos import Productos
from ..models.categorias_productos import CategoriasProductos
from ..models.detalles_catalogo import DetallesCatalogo
from ..models.detalles_lamparas_ranpu import DetallesLamparasRanpu
from ..models.detalles_productos_ia import DetallesProductosIA
from ..models.imagenes_productos import ImagenesProductos
from ..models.impuestos import Impuestos
from ..database import db

productos_bp = Blueprint('productos', __name__)

@productos_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Productos'],
    'summary': 'Obtener todos los productos',
    'description': 'Obtiene todos los productos de la base de datos, incluyendo los detalles de categoría y las tablas relacionadas (detalles_catalogo, detalles_lamparas_ranpu y detalles_productos_ia) para cada producto.',
    'responses': {
        200: {
            'description': 'Lista de productos',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'producto_id': {'type': 'integer', 'example': 1},
                        'nombre': {'type': 'string', 'example': 'Lámpara Inteligente'},
                        'descripcion': {'type': 'string', 'example': 'Lámpara con diseño moderno y conexión Wi-Fi'},
                        'alto': {'type': 'string', 'example': '12.00'},
                        'ancho': {'type': 'string', 'example': '6.00'},
                        'largo': {'type': 'string', 'example': '9.00'},
                        'gbl': {'type': 'string', 'example': 'path/to/file.gbl'},
                        'precio': {'type': 'string', 'example': '29.99'},
                        'categoria_producto': {
                            'type': 'object',
                            'properties': {
                                'categoria_producto_id': {'type': 'integer', 'example': 1},
                                'nombre': {'type': 'string', 'example': 'Lámparas'}
                            }
                        },
                        'detalles_catalogo': {
                            'type': 'object',
                            'properties': {
                                'producto_id': {'type': 'integer', 'example': 1},
                                'detalles': {'type': 'string', 'example': 'Lámpara incluida en catálogo'}
                            }
                        },
                        'detalles_lamparas_ranpu': {
                            'type': 'object',
                            'properties': {
                                'producto_id': {'type': 'integer', 'example': 1},
                                'detalles': {'type': 'string', 'example': 'Detalles específicos de Ranpu'}
                            }
                        },
                        'detalles_productos_ia': {
                            'type': 'object',
                            'properties': {
                                'producto_id': {'type': 'integer', 'example': 1},
                                'detalles': {'type': 'string', 'example': 'Detalles generados por IA'}
                            }
                        },
                        'imagenes': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'imagen_producto_id': {'type': 'integer', 'example': 1},
                                    'descripcion': {'type': 'string', 'example': 'Vista frontal'},
                                    'ubicacion': {'type': 'string', 'example': '/images/product1_front.jpg'},
                                    'producto_id': {'type': 'integer', 'example': 1}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_productos():
    """Obtener todos los productos, incluyendo detalles y categoría."""
    productos = Productos.query.all()
    resultado = []

    for producto in productos:
        detalles_catalogo = DetallesCatalogo.query.filter_by(producto_id=producto.producto_id).first()
        detalles_lamparas = DetallesLamparasRanpu.query.filter_by(producto_id=producto.producto_id).first()
        detalles_ia = DetallesProductosIA.query.filter_by(producto_id=producto.producto_id).first()

        producto_dict = producto.to_dict()
        producto_dict["categoria_producto"] = (
            producto.categoria_producto.to_dict()
            if producto.categoria_producto else {"categoria_producto_id": producto.categoria_producto_id, "nombre": None}
        )
        producto_dict["detalles_catalogo"] = (
            {"producto_id": producto.producto_id, "detalles": detalles_catalogo.detalles}
            if detalles_catalogo else {"producto_id": producto.producto_id, "detalles": None}
        )
        producto_dict["detalles_lamparas_ranpu"] = (
            {"producto_id": producto.producto_id, "detalles": detalles_lamparas.detalles}
            if detalles_lamparas else {"producto_id": producto.producto_id, "detalles": None}
        )
        producto_dict["detalles_productos_ia"] = (
            {"producto_id": producto.producto_id, "detalles": detalles_ia.detalles}
            if detalles_ia else {"producto_id": producto.producto_id, "detalles": None}
        )

        producto_dict["imagenes"] = [
            imagen.to_dict() for imagen in producto.imagenes
        ]

        resultado.append(producto_dict)

    return jsonify(resultado), 200

@productos_bp.route('/<int:producto_id>', methods=['GET'])
@swag_from({
    'tags': ['Productos'],
    'summary': 'Obtener un producto por ID',
    'description': 'Obtiene un producto específico por su ID, incluyendo los detalles de categoría y las tablas relacionadas (detalles_catalogo, detalles_lamparas_ranpu y detalles_productos_ia).',
    'parameters': [
        {
            'name': 'producto_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del producto a obtener'
        }
    ],
    'responses': {
        200: {
            'description': 'Producto encontrado',
            'schema': {
                'type': 'object',
                'properties': {
                    'producto_id': {'type': 'integer', 'example': 1},
                    'nombre': {'type': 'string', 'example': 'Lámpara Inteligente'},
                    'descripcion': {'type': 'string', 'example': 'Lámpara con diseño moderno y conexión Wi-Fi'},
                    'alto': {'type': 'string', 'example': '12.00'},
                    'ancho': {'type': 'string', 'example': '6.00'},
                    'largo': {'type': 'string', 'example': '9.00'},
                    'gbl': {'type': 'string', 'example': 'path/to/file.gbl'},
                    'precio': {'type': 'string', 'example': '29.99'},
                    'categoria_producto': {
                        'type': 'object',
                        'properties': {
                            'categoria_producto_id': {'type': 'integer', 'example': 1},
                            'nombre': {'type': 'string', 'example': 'Lámparas'}
                        }
                    },
                    'detalles_catalogo': {
                        'type': 'object',
                        'properties': {
                            'producto_id': {'type': 'integer', 'example': 1},
                            'detalles': {'type': 'string', 'example': 'Lámpara incluida en catálogo'}
                        }
                    },
                    'detalles_lamparas_ranpu': {
                        'type': 'object',
                        'properties': {
                            'producto_id': {'type': 'integer', 'example': 1},
                            'detalles': {'type': 'string', 'example': 'Detalles específicos de Ranpu'}
                        }
                    },
                    'detalles_productos_ia': {
                        'type': 'object',
                        'properties': {
                            'producto_id': {'type': 'integer', 'example': 1},
                            'detalles': {'type': 'string', 'example': 'Detalles generados por IA'}
                        }
                    },
                    'imagenes': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'imagen_producto_id': {'type': 'integer', 'example': 1},
                                'descripcion': {'type': 'string', 'example': 'Vista frontal'},
                                'ubicacion': {'type': 'string', 'example': '/images/product1_front.jpg'},
                                'producto_id': {'type': 'integer', 'example': 1}
                            }
                        }
                    }
                }
            }
        },
        404: {'description': 'Producto no encontrado'}
    }
})
def get_producto_por_id(producto_id):
    """Obtener un producto por su ID, incluyendo detalles y categoría."""
    producto = Productos.query.get(producto_id)
    if not producto:
        return jsonify({"message": "Producto no encontrado"}), 404

    detalles_catalogo = DetallesCatalogo.query.filter_by(producto_id=producto_id).first()
    detalles_lamparas = DetallesLamparasRanpu.query.filter_by(producto_id=producto_id).first()
    detalles_ia = DetallesProductosIA.query.filter_by(producto_id=producto_id).first()

    response = producto.to_dict()
    response["categoria_producto"] = (
        producto.categoria_producto.to_dict()
        if producto.categoria_producto else {"categoria_producto_id": producto.categoria_producto_id, "nombre": None}
    )
    response["detalles_catalogo"] = (
        {"producto_id": producto_id, "detalles": detalles_catalogo.detalles}
        if detalles_catalogo else {"producto_id": producto_id, "detalles": None}
    )
    response["detalles_lamparas_ranpu"] = (
        {"producto_id": producto_id, "detalles": detalles_lamparas.detalles}
        if detalles_lamparas else {"producto_id": producto_id, "detalles": None}
    )
    response["detalles_productos_ia"] = (
        {"producto_id": producto_id, "detalles": detalles_ia.detalles}
        if detalles_ia else {"producto_id": producto_id, "detalles": None}
    )

    response["imagenes"] = [
        imagen.to_dict() for imagen in producto.imagenes
    ]

    return jsonify(response), 200

@productos_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Productos'],
    'summary': 'Crear un nuevo producto con detalles e imágenes relacionadas',
    'description': 'Crea un nuevo producto, incluyendo detalles en las tablas relacionadas (detalles_catalogo, detalles_lamparas_ranpu, detalles_productos_ia) y permite subir varias imágenes asociadas.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'example': 'Lámpara Inteligente'},
                    'descripcion': {'type': 'string', 'example': 'Lámpara con diseño moderno y conexión Wi-Fi'},
                    'alto': {'type': 'string', 'example': '12.00'},
                    'ancho': {'type': 'string', 'example': '6.00'},
                    'largo': {'type': 'string', 'example': '9.00'},
                    'gbl': {'type': 'string', 'example': 'path/to/file.gbl'},
                    'precio': {'type': 'string', 'example': '29.99'},
                    'categoria_producto_id': {'type': 'integer', 'example': 1},
                    'detalles_catalogo': {
                        'type': 'object',
                        'properties': {
                            'detalles': {'type': 'string', 'example': 'Lámpara incluida en catálogo'}
                        }
                    },
                    'detalles_lamparas_ranpu': {
                        'type': 'object',
                        'properties': {
                            'detalles': {'type': 'string', 'example': 'Detalles específicos de Ranpu'}
                        }
                    },
                    'detalles_productos_ia': {
                        'type': 'object',
                        'properties': {
                            'detalles': {'type': 'string', 'example': 'Detalles generados por IA'}
                        }
                    },
                    'imagenes': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'ubicacion': {'type': 'string', 'example': '/images/product1_front.jpg'},
                                'descripcion': {'type': 'string', 'example': 'Vista frontal'}
                            }
                        }
                    }
                },
                'required': ['nombre', 'descripcion', 'alto', 'ancho', 'largo', 'gbl', 'precio', 'categoria_producto_id']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Producto creado exitosamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'producto_id': {'type': 'integer', 'example': 1},
                    'nombre': {'type': 'string', 'example': 'Lámpara Inteligente'},
                    'imagenes': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'ubicacion': {'type': 'string', 'example': '/images/product1_front.jpg'},
                                'descripcion': {'type': 'string', 'example': 'Vista frontal'}
                            }
                        }
                    }
                }
            }
        },
        400: {'description': 'Datos inválidos en la solicitud'}
    }
})
def create_producto():
    """Crear un producto y, opcionalmente, agregar detalles e imágenes relacionadas."""
    data = request.get_json()

    # Validar campos obligatorios
    required_fields = ['nombre', 'descripcion', 'alto', 'ancho', 'largo', 'gbl', 'precio', 'categoria_producto_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"El campo '{field}' es obligatorio"}), 400

    try:
        # Crear producto
        nuevo_producto = Productos(
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            alto=data['alto'],
            ancho=data['ancho'],
            largo=data['largo'],
            gbl=data['gbl'],
            precio=data['precio'],
            categoria_producto_id=data['categoria_producto_id']
        )
        db.session.add(nuevo_producto)
        db.session.flush()  # Obtener producto_id antes de commit

        # Crear detalles opcionales
        if 'detalles_catalogo' in data and data['detalles_catalogo'].get('detalles'):
            detalles_catalogo = DetallesCatalogo(
                producto_id=nuevo_producto.producto_id,
                detalles=data['detalles_catalogo']['detalles']
            )
            db.session.add(detalles_catalogo)

        if 'detalles_lamparas_ranpu' in data and data['detalles_lamparas_ranpu'].get('detalles'):
            detalles_lamparas_ranpu = DetallesLamparasRanpu(
                producto_id=nuevo_producto.producto_id,
                detalles=data['detalles_lamparas_ranpu']['detalles']
            )
            db.session.add(detalles_lamparas_ranpu)

        if 'detalles_productos_ia' in data and data['detalles_productos_ia'].get('detalles'):
            detalles_productos_ia = DetallesProductosIA(
                producto_id=nuevo_producto.producto_id,
                detalles=data['detalles_productos_ia']['detalles']
            )
            db.session.add(detalles_productos_ia)

        # Crear imágenes
        if 'imagenes' in data:
            for imagen_data in data['imagenes']:
                nueva_imagen = ImagenesProductos(
                    producto_id=nuevo_producto.producto_id,
                    ubicacion=imagen_data['ubicacion'],
                    descripcion=imagen_data['descripcion']
                )
                db.session.add(nueva_imagen)

        db.session.commit()

        # Respuesta exitosa
        response = nuevo_producto.to_dict()
        response["categoria_producto"] = nuevo_producto.categoria_producto.to_dict() if nuevo_producto.categoria_producto else None
        response["detalles_catalogo"] = {
            "producto_id": nuevo_producto.producto_id,
            "detalles": data['detalles_catalogo']['detalles'] if 'detalles_catalogo' in data else None
        }
        response["detalles_lamparas_ranpu"] = {
            "producto_id": nuevo_producto.producto_id,
            "detalles": data['detalles_lamparas_ranpu']['detalles'] if 'detalles_lamparas_ranpu' in data else None
        }
        response["detalles_productos_ia"] = {
            "producto_id": nuevo_producto.producto_id,
            "detalles": data['detalles_productos_ia']['detalles'] if 'detalles_productos_ia' in data else None
        }
        response["imagenes"] = [
            {"ubicacion": img['ubicacion'], "descripcion": img['descripcion']}
            for img in data['imagenes']
        ] if 'imagenes' in data else []

        return jsonify(response), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al crear el producto", "error": str(e)}), 500

@productos_bp.route('/cart', methods=['POST'])
@swag_from({
    'tags': ['Productos'],
    'summary': 'Obtener múltiples productos por sus IDs',
    'description': 'Obtiene los detalles de múltiples productos en base a un arreglo de IDs proporcionado.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'productIds': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                        'example': [1, 2, 3]
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Lista de productos',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'producto_id': {'type': 'integer', 'example': 1},
                        'nombre': {'type': 'string', 'example': 'Lámpara Inteligente'},
                        'descripcion': {'type': 'string', 'example': 'Lámpara con diseño moderno y conexión Wi-Fi'},
                        'alto': {'type': 'string', 'example': '12.00'},
                        'ancho': {'type': 'string', 'example': '6.00'},
                        'largo': {'type': 'string', 'example': '9.00'},
                        'gbl': {'type': 'string', 'example': 'path/to/file.gbl'},
                        'precio': {'type': 'string', 'example': '29.99'},
                        'categoria_producto': {
                            'type': 'object',
                            'properties': {
                                'categoria_producto_id': {'type': 'integer', 'example': 1},
                                'nombre': {'type': 'string', 'example': 'Lámparas'}
                            }
                        },
                        'detalles_catalogo': {
                            'type': 'object',
                            'properties': {
                                'producto_id': {'type': 'integer', 'example': 1},
                                'detalles': {'type': 'string', 'example': 'Lámpara incluida en catálogo'}
                            }
                        },
                        'detalles_lamparas_ranpu': {
                            'type': 'object',
                            'properties': {
                                'producto_id': {'type': 'integer', 'example': 1},
                                'detalles': {'type': 'string', 'example': 'Detalles específicos de Ranpu'}
                            }
                        },
                        'detalles_productos_ia': {
                            'type': 'object',
                            'properties': {
                                'producto_id': {'type': 'integer', 'example': 1},
                                'detalles': {'type': 'string', 'example': 'Detalles generados por IA'}
                            }
                        },
                        'imagenes': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'imagen_producto_id': {'type': 'integer', 'example': 1},
                                    'descripcion': {'type': 'string', 'example': 'Vista frontal'},
                                    'ubicacion': {'type': 'string', 'example': '/images/product1_front.jpg'},
                                    'producto_id': {'type': 'integer', 'example': 1}
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {'description': 'Solicitud inválida'},
        404: {'description': 'Uno o más productos no encontrados'}
    }
})
def get_productos_por_ids():
    """Obtener múltiples productos por sus IDs."""
    data = request.get_json()
    product_ids = data.get('productIds', [])

    if not product_ids or not isinstance(product_ids, list):
        return jsonify({"message": "Debe proporcionar una lista de IDs de productos válida en 'productIds'"}), 400

    # Query all products at once
    productos = Productos.query.filter(Productos.producto_id.in_(product_ids)).all()

    if not productos:
        return jsonify({"message": "No se encontraron productos para los IDs proporcionados"}), 404

    # Map product IDs to allow duplicates in the result
    productos_dict = {producto.producto_id: producto for producto in productos}
    resultado = []

    for product_id in product_ids:
        producto = productos_dict.get(product_id)
        if not producto:
            continue

        detalles_catalogo = DetallesCatalogo.query.filter_by(producto_id=product_id).first()
        detalles_lamparas = DetallesLamparasRanpu.query.filter_by(producto_id=product_id).first()
        detalles_ia = DetallesProductosIA.query.filter_by(producto_id=product_id).first()

        producto_dict = producto.to_dict()
        producto_dict["categoria_producto"] = (
            producto.categoria_producto.to_dict()
            if producto.categoria_producto else {"categoria_producto_id": producto.categoria_producto_id, "nombre": None}
        )
        producto_dict["detalles_catalogo"] = (
            {"producto_id": product_id, "detalles": detalles_catalogo.detalles}
            if detalles_catalogo else {"producto_id": product_id, "detalles": None}
        )
        producto_dict["detalles_lamparas_ranpu"] = (
            {"producto_id": product_id, "detalles": detalles_lamparas.detalles}
            if detalles_lamparas else {"producto_id": product_id, "detalles": None}
        )
        producto_dict["detalles_productos_ia"] = (
            {"producto_id": product_id, "detalles": detalles_ia.detalles}
            if detalles_ia else {"producto_id": product_id, "detalles": None}
        )
        producto_dict["imagenes"] = [
            imagen.to_dict() for imagen in producto.imagenes
        ]

        resultado.append(producto_dict)

    return jsonify(resultado), 200

@productos_bp.route('/calculate_total', methods=['POST'])
@swag_from({
    'tags': ['Productos'],
    'summary': 'Calcular el total de una transacción',
    'description': 'Calcula el subtotal (productos multiplicados por su cantidad), aplica el impuesto actual activo y luego agrega una tarifa de entrega fija.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'items': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'producto_id': {'type': 'integer', 'example': 1},
                                'quantity': {'type': 'integer', 'example': 2}
                            },
                            'required': ['producto_id', 'quantity']
                        }
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Resumen de la transacción con impuesto aplicado',
            'schema': {
                'type': 'object',
                'properties': {
                    'Subtotal': {'type': 'number', 'example': 59.98},
                    'TaxValue': {'type': 'number', 'example': 15.00},
                    'CalculatedTax': {'type': 'number', 'example': 8.997},
                    'DeliveryFee': {'type': 'number', 'example': 2.00},
                    'Total': {'type': 'number', 'example': 70.97}
                }
            }
        },
        400: {'description': 'Solicitud inválida'},
        404: {'description': 'Uno o más productos no encontrados'}
    }
})
def calculate_total():
    """Calcular el total de una transacción, incluyendo impuestos y tarifa de envío."""
    data = request.get_json()
    items = data.get('items', [])

    if not items or not isinstance(items, list):
        return jsonify({"message": "Debe proporcionar una lista válida de productos con cantidades en 'items'"}), 400

    # Retrieve the active tax
    active_tax = Impuestos.query.filter_by(activo=True).first()
    if not active_tax:
        return jsonify({"message": "No hay ningún impuesto activo configurado"}), 400

    tax_percentage = float(active_tax.porcentaje) / 100  # Convert to percentage
    tax_value = active_tax.porcentaje

    subtotal = 0
    delivery_fee = 2.00

    for item in items:
        producto_id = item.get('producto_id')
        quantity = item.get('quantity', 0)

        if not producto_id or not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"message": f"ID de producto o cantidad inválida en el item: {item}"}), 400

        producto = Productos.query.get(producto_id)
        if not producto:
            return jsonify({"message": f"Producto con ID {producto_id} no encontrado"}), 404

        # Multiply price by quantity and accumulate in the subtotal
        subtotal += float(producto.precio) * quantity

    # Calculate tax
    calculated_tax = subtotal * tax_percentage

    # Calculate total
    total = subtotal + calculated_tax + delivery_fee

    return jsonify({
        "Subtotal": f"{subtotal:.2f}",
        "TaxValue": f"{tax_value:.2f}",
        "CalculatedTax": f"{calculated_tax:.2f}",
        "DeliveryFee": f"{delivery_fee:.2f}",
        "Total": f"{total:.2f}"
    }), 200

@productos_bp.route('/<int:producto_id>', methods=['PUT'])
@swag_from({
    'tags': ['Productos'],
    'summary': 'Actualizar un producto existente',
    'description': 'Actualiza un producto existente, incluyendo imágenes y detalles relacionados. Si no se envían imágenes o detalles en el cuerpo de la solicitud, se eliminan los existentes.',
    'parameters': [
        {
            'name': 'producto_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del producto a actualizar'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'example': 'Lámpara Inteligente'},
                    'descripcion': {'type': 'string', 'example': 'Lámpara con diseño moderno y conexión Wi-Fi'},
                    'alto': {'type': 'string', 'example': '12.00'},
                    'ancho': {'type': 'string', 'example': '6.00'},
                    'largo': {'type': 'string', 'example': '9.00'},
                    'gbl': {'type': 'string', 'example': 'path/to/file.gbl'},
                    'precio': {'type': 'string', 'example': '29.99'},
                    'categoria_producto_id': {'type': 'integer', 'example': 1},
                    'imagenes': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'descripcion': {'type': 'string', 'example': 'Vista frontal'},
                                'ubicacion': {'type': 'string', 'example': '/images/product1_front.jpg'}
                            }
                        }
                    },
                    'detalles_catalogo': {
                        'type': 'object',
                        'properties': {
                            'detalles': {'type': 'string', 'example': 'Lámpara incluida en catálogo'}
                        }
                    },
                    'detalles_lamparas_ranpu': {
                        'type': 'object',
                        'properties': {
                            'detalles': {'type': 'string', 'example': 'Detalles específicos de Ranpu'}
                        }
                    },
                    'detalles_productos_ia': {
                        'type': 'object',
                        'properties': {
                            'detalles': {'type': 'string', 'example': 'Detalles generados por IA'}
                        }
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Producto actualizado correctamente',
            'schema': {'type': 'object'}
        },
        404: {'description': 'Producto no encontrado'},
        400: {'description': 'Datos inválidos'}
    }
})
def update_producto(producto_id):
    """Actualizar un producto existente, eliminando imágenes y detalles si no se envían."""
    producto = Productos.query.get(producto_id)
    if not producto:
        return jsonify({"message": "Producto no encontrado"}), 404

    data = request.get_json()

    try:
        # Actualizar los campos básicos del producto
        for field in ['nombre', 'descripcion', 'alto', 'ancho', 'largo', 'gbl', 'precio', 'categoria_producto_id']:
            if field in data:
                setattr(producto, field, data[field])

        # Manejar imágenes
        if 'imagenes' in data:
            # Eliminar imágenes existentes
            ImagenesProductos.query.filter_by(producto_id=producto_id).delete()
            # Agregar nuevas imágenes
            for imagen in data['imagenes']:
                nueva_imagen = ImagenesProductos(
                    producto_id=producto_id,
                    descripcion=imagen['descripcion'],
                    ubicacion=imagen['ubicacion']
                )
                db.session.add(nueva_imagen)
        else:
            # Si no se envían imágenes, eliminarlas todas
            ImagenesProductos.query.filter_by(producto_id=producto_id).delete()

        # Manejar detalles (catálogo, lámparas Ranpu, IA)
        detalle_models = [
            (DetallesCatalogo, 'detalles_catalogo'),
            (DetallesLamparasRanpu, 'detalles_lamparas_ranpu'),
            (DetallesProductosIA, 'detalles_productos_ia')
        ]

        for model, key in detalle_models:
            detalle = model.query.filter_by(producto_id=producto_id).first()
            if key in data and data[key].get('detalles'):
                if detalle:
                    detalle.detalles = data[key]['detalles']
                else:
                    nuevo_detalle = model(
                        producto_id=producto_id,
                        detalles=data[key]['detalles']
                    )
                    db.session.add(nuevo_detalle)
            elif detalle:
                # Si no se envía el detalle, eliminarlo
                db.session.delete(detalle)

        db.session.commit()

        # Respuesta
        response = producto.to_dict()
        response["categoria_producto"] = producto.categoria_producto.to_dict() if producto.categoria_producto else None
        response["imagenes"] = [imagen.to_dict() for imagen in producto.imagenes]
        response["detalles_catalogo"] = {
            "producto_id": producto.producto_id,
            "detalles": DetallesCatalogo.query.filter_by(producto_id=producto_id).first().detalles
            if DetallesCatalogo.query.filter_by(producto_id=producto_id).first() else None
        }
        response["detalles_lamparas_ranpu"] = {
            "producto_id": producto.producto_id,
            "detalles": DetallesLamparasRanpu.query.filter_by(producto_id=producto_id).first().detalles
            if DetallesLamparasRanpu.query.filter_by(producto_id=producto_id).first() else None
        }
        response["detalles_productos_ia"] = {
            "producto_id": producto.producto_id,
            "detalles": DetallesProductosIA.query.filter_by(producto_id=producto_id).first().detalles
            if DetallesProductosIA.query.filter_by(producto_id=producto_id).first() else None
        }

        return jsonify(response), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al actualizar el producto", "error": str(e)}), 500

@productos_bp.route('/<int:producto_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Productos'],
    'summary': 'Eliminar un producto y sus relaciones',
    'description': 'Elimina un producto de la base de datos junto con todas las filas relacionadas en las tablas de imágenes y detalles.',
    'parameters': [
        {
            'name': 'producto_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del producto a eliminar'
        }
    ],
    'responses': {
        200: {'description': 'Producto eliminado exitosamente'},
        404: {'description': 'Producto no encontrado'},
        500: {'description': 'Error al eliminar el producto'}
    }
})
def delete_producto(producto_id):
    """Eliminar un producto y todas sus relaciones (imágenes y detalles)."""
    producto = Productos.query.get(producto_id)
    if not producto:
        return jsonify({"message": "Producto no encontrado"}), 404

    try:
        # Eliminar imágenes relacionadas
        ImagenesProductos.query.filter_by(producto_id=producto_id).delete()

        # Eliminar detalles relacionados
        DetallesCatalogo.query.filter_by(producto_id=producto_id).delete()
        DetallesLamparasRanpu.query.filter_by(producto_id=producto_id).delete()
        DetallesProductosIA.query.filter_by(producto_id=producto_id).delete()

        # Eliminar el producto
        db.session.delete(producto)
        db.session.commit()

        return jsonify({"message": "Producto eliminado exitosamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al eliminar el producto", "error": str(e)}), 500
