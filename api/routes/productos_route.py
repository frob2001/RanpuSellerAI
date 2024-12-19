from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.productos import Productos
from ..models.categorias_productos import CategoriasProductos
from ..models.detalles_catalogo import DetallesCatalogo
from ..models.detalles_lamparas_ranpu import DetallesLamparasRanpu
from ..models.detalles_productos_ia import DetallesProductosIA
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
    'summary': 'Crear un nuevo producto',
    'description': 'Crea un nuevo producto y, opcionalmente, puede agregar detalles en las tablas relacionadas (detalles_catalogo, detalles_lamparas_ranpu y detalles_productos_ia).',
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
                    'detalles_catalogo': {'type': 'string', 'example': 'Lámpara incluida en catálogo'},
                    'detalles_lamparas_ranpu': {'type': 'string', 'example': 'Detalles específicos de Ranpu'},
                    'detalles_productos_ia': {'type': 'string', 'example': 'Detalles generados por IA'}
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
                    'message': {'type': 'string', 'example': 'Producto creado exitosamente'},
                    'producto': {'type': 'object'}
                }
            }
        },
        400: {'description': 'Datos inválidos en la solicitud'}
    }
})
def create_producto():
    """Crear un producto y, opcionalmente, agregar detalles en tablas relacionadas."""
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
        if 'detalles_catalogo' in data:
            detalles_catalogo = DetallesCatalogo(
                producto_id=nuevo_producto.producto_id,
                detalles=data['detalles_catalogo']
            )
            db.session.add(detalles_catalogo)

        if 'detalles_lamparas_ranpu' in data:
            detalles_lamparas_ranpu = DetallesLamparasRanpu(
                producto_id=nuevo_producto.producto_id,
                detalles=data['detalles_lamparas_ranpu']
            )
            db.session.add(detalles_lamparas_ranpu)

        if 'detalles_productos_ia' in data:
            detalles_productos_ia = DetallesProductosIA(
                producto_id=nuevo_producto.producto_id,
                detalles=data['detalles_productos_ia']
            )
            db.session.add(detalles_productos_ia)

        db.session.commit()

        # Respuesta exitosa
        response = nuevo_producto.to_dict()
        response["categoria_producto"] = nuevo_producto.categoria_producto.to_dict() if nuevo_producto.categoria_producto else None
        response["detalles_catalogo"] = data.get('detalles_catalogo')
        response["detalles_lamparas_ranpu"] = data.get('detalles_lamparas_ranpu')
        response["detalles_productos_ia"] = data.get('detalles_productos_ia')

        return jsonify({"message": "Producto creado exitosamente", "producto": response}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al crear el producto", "error": str(e)}), 500
