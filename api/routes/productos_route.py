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

