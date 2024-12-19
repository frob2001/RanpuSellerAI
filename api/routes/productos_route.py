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
    'description': 'Obtiene una lista de todos los productos, incluyendo la categoría y detalles de las tablas relacionadas.',
    'responses': {
        200: {
            'description': 'Lista de productos con detalles y categoría',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'producto_id': {'type': 'integer', 'example': 1},
                        'nombre': {'type': 'string', 'example': 'Lámpara Inteligente'},
                        'descripcion': {'type': 'string', 'example': 'Lámpara con diseño moderno y conexión Wi-Fi'},
                        'alto': {'type': 'string', 'example': '10.00'},
                        'ancho': {'type': 'string', 'example': '5.00'},
                        'largo': {'type': 'string', 'example': '8.00'},
                        'gbl': {'type': 'string', 'example': 'path/to/file.gbl'},
                        'precio': {'type': 'string', 'example': '25.99'},
                        'categoria_producto': {
                            'type': 'object',
                            'properties': {
                                'categoria_producto_id': {'type': 'integer', 'example': 1},
                                'nombre': {'type': 'string', 'example': 'Iluminación'}
                            }
                        },
                        'detalles_catalogo': {'type': 'string', 'example': 'Lámpara catalogada para el hogar'},
                        'detalles_lamparas_ranpu': {'type': 'string', 'example': 'Detalles exclusivos de Ranpu'},
                        'detalles_productos_ia': {'type': 'string', 'example': 'Detalles generados por IA'}
                    }
                }
            }
        }
    }
})
def get_productos():
    """Obtiene todos los productos, incluyendo sus detalles y categorías."""
    productos = Productos.query.all()
    resultado = []
    for producto in productos:
        data = producto.to_dict()
        data["categoria_producto"] = CategoriasProductos.query.get(producto.categoria_producto_id).to_dict()
        data["detalles_catalogo"] = DetallesCatalogo.query.filter_by(producto_id=producto.producto_id).first()
        data["detalles_lamparas_ranpu"] = DetallesLamparasRanpu.query.filter_by(producto_id=producto.producto_id).first()
        data["detalles_productos_ia"] = DetallesProductosIA.query.filter_by(producto_id=producto.producto_id).first()
        resultado.append(data)
    return jsonify(resultado), 20

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
                    'detalles_catalogo': {'type': 'string', 'example': 'Lámpara incluida en catálogo'},
                    'detalles_lamparas_ranpu': {'type': 'string', 'example': 'Detalles específicos de Ranpu'},
                    'detalles_productos_ia': {'type': 'string', 'example': 'Detalles generados por IA'}
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
    response["categoria_producto"] = producto.categoria_producto.to_dict() if producto.categoria_producto else None
    response["detalles_catalogo"] = detalles_catalogo.detalles if detalles_catalogo else None
    response["detalles_lamparas_ranpu"] = detalles_lamparas.detalles if detalles_lamparas else None
    response["detalles_productos_ia"] = detalles_ia.detalles if detalles_ia else None

    return jsonify(response), 200


@productos_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Productos'],
    'summary': 'Crear un nuevo producto',
    'description': 'Crea un nuevo producto con la posibilidad de agregar detalles en las tablas relacionadas.',
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
                    'alto': {'type': 'string', 'example': '10.00'},
                    'ancho': {'type': 'string', 'example': '5.00'},
                    'largo': {'type': 'string', 'example': '8.00'},
                    'gbl': {'type': 'string', 'example': 'path/to/file.gbl'},
                    'precio': {'type': 'string', 'example': '25.99'},
                    'categoria_producto_id': {'type': 'integer', 'example': 1},
                    'detalles_catalogo': {'type': 'string', 'example': 'Lámpara catalogada para el hogar'},
                    'detalles_lamparas_ranpu': {'type': 'string', 'example': 'Detalles exclusivos de Ranpu'},
                    'detalles_productos_ia': {'type': 'string', 'example': 'Detalles generados por IA'}
                }
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
                    'descripcion': {'type': 'string', 'example': 'Lámpara con diseño moderno y conexión Wi-Fi'},
                    'alto': {'type': 'string', 'example': '10.00'},
                    'ancho': {'type': 'string', 'example': '5.00'},
                    'largo': {'type': 'string', 'example': '8.00'},
                    'gbl': {'type': 'string', 'example': 'path/to/file.gbl'},
                    'precio': {'type': 'string', 'example': '25.99'},
                    'categoria_producto_id': {'type': 'integer', 'example': 1}
                }
            }
        }
    }
})
def create_producto():
    """Crea un nuevo producto con detalles opcionales."""
    data = request.json
    nuevo_producto = Productos(
        nombre=data["nombre"],
        descripcion=data["descripcion"],
        alto=data["alto"],
        ancho=data["ancho"],
        largo=data["largo"],
        gbl=data["gbl"],
        precio=data["precio"],
        categoria_producto_id=data["categoria_producto_id"]
    )
    db.session.add(nuevo_producto)
    db.session.flush()

    if "detalles_catalogo" in data and data["detalles_catalogo"]:
        detalle_catalogo = DetallesCatalogo(
            producto_id=nuevo_producto.producto_id,
            detalles=data["detalles_catalogo"]
        )
        db.session.add(detalle_catalogo)

    if "detalles_lamparas_ranpu" in data and data["detalles_lamparas_ranpu"]:
        detalle_lamparas = DetallesLamparasRanpu(
            producto_id=nuevo_producto.producto_id,
            detalles=data["detalles_lamparas_ranpu"]
        )
        db.session.add(detalle_lamparas)

    if "detalles_productos_ia" in data and data["detalles_productos_ia"]:
        detalle_ia = DetallesProductosIA(
            producto_id=nuevo_producto.producto_id,
            detalles=data["detalles_productos_ia"]
        )
        db.session.add(detalle_ia)

    db.session.commit()
    return jsonify(nuevo_producto.to_dict()), 201

# Agrega las descripciones de Swagger a las rutas PUT y DELETE de manera similar.
@productos_bp.route('/<int:producto_id>', methods=['PUT'])
@swag_from({
    'tags': ['Productos'],
    'summary': 'Actualizar un producto',
    'description': 'Permite actualizar un producto existente. Además, puede modificar o eliminar detalles en las tablas relacionadas.',
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
                    'nombre': {'type': 'string', 'example': 'Lámpara Inteligente Actualizada'},
                    'descripcion': {'type': 'string', 'example': 'Lámpara con diseño moderno y conexión Wi-Fi mejorada'},
                    'alto': {'type': 'string', 'example': '12.00'},
                    'ancho': {'type': 'string', 'example': '6.00'},
                    'largo': {'type': 'string', 'example': '9.00'},
                    'gbl': {'type': 'string', 'example': 'path/to/new_file.gbl'},
                    'precio': {'type': 'string', 'example': '29.99'},
                    'categoria_producto_id': {'type': 'integer', 'example': 2},
                    'detalles_catalogo': {'type': 'string', 'example': 'Lámpara actualizada en catálogo'},
                    'detalles_lamparas_ranpu': {'type': 'string', 'example': 'Detalles actualizados de Ranpu'},
                    'detalles_productos_ia': {'type': 'string', 'example': 'Detalles generados por IA actualizados'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Producto actualizado exitosamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'producto_id': {'type': 'integer', 'example': 1},
                    'nombre': {'type': 'string', 'example': 'Lámpara Inteligente Actualizada'},
                    'descripcion': {'type': 'string', 'example': 'Lámpara con diseño moderno y conexión Wi-Fi mejorada'},
                    'alto': {'type': 'string', 'example': '12.00'},
                    'ancho': {'type': 'string', 'example': '6.00'},
                    'largo': {'type': 'string', 'example': '9.00'},
                    'gbl': {'type': 'string', 'example': 'path/to/new_file.gbl'},
                    'precio': {'type': 'string', 'example': '29.99'},
                    'categoria_producto_id': {'type': 'integer', 'example': 2}
                }
            }
        },
        404: {'description': 'Producto no encontrado'}
    }
})
def update_producto(producto_id):
    """Actualiza un producto existente, incluyendo detalles."""
    producto = Productos.query.get(producto_id)
    if not producto:
        return jsonify({"message": "Producto no encontrado"}), 404

    data = request.json
    producto.nombre = data.get("nombre", producto.nombre)
    producto.descripcion = data.get("descripcion", producto.descripcion)
    producto.alto = data.get("alto", producto.alto)
    producto.ancho = data.get("ancho", producto.ancho)
    producto.largo = data.get("largo", producto.largo)
    producto.gbl = data.get("gbl", producto.gbl)
    producto.precio = data.get("precio", producto.precio)
    producto.categoria_producto_id = data.get("categoria_producto_id", producto.categoria_producto_id)

    # Actualizar detalles
    if "detalles_catalogo" in data:
        detalle_catalogo = DetallesCatalogo.query.filter_by(producto_id=producto_id).first()
        if data["detalles_catalogo"]:
            if not detalle_catalogo:
                detalle_catalogo = DetallesCatalogo(producto_id=producto_id, detalles=data["detalles_catalogo"])
                db.session.add(detalle_catalogo)
            else:
                detalle_catalogo.detalles = data["detalles_catalogo"]
        elif detalle_catalogo:
            db.session.delete(detalle_catalogo)

    if "detalles_lamparas_ranpu" in data:
        detalle_lamparas = DetallesLamparasRanpu.query.filter_by(producto_id=producto_id).first()
        if data["detalles_lamparas_ranpu"]:
            if not detalle_lamparas:
                detalle_lamparas = DetallesLamparasRanpu(producto_id=producto_id, detalles=data["detalles_lamparas_ranpu"])
                db.session.add(detalle_lamparas)
            else:
                detalle_lamparas.detalles = data["detalles_lamparas_ranpu"]
        elif detalle_lamparas:
            db.session.delete(detalle_lamparas)

    if "detalles_productos_ia" in data:
        detalle_ia = DetallesProductosIA.query.filter_by(producto_id=producto_id).first()
        if data["detalles_productos_ia"]:
            if not detalle_ia:
                detalle_ia = DetallesProductosIA(producto_id=producto_id, detalles=data["detalles_productos_ia"])
                db.session.add(detalle_ia)
            else:
                detalle_ia.detalles = data["detalles_productos_ia"]
        elif detalle_ia:
            db.session.delete(detalle_ia)

    db.session.commit()
    return jsonify(producto.to_dict()), 200

@productos_bp.route('/<int:producto_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Productos'],
    'summary': 'Eliminar un producto',
    'description': 'Elimina un producto junto con todos sus detalles en las tablas relacionadas.',
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
        404: {'description': 'Producto no encontrado'}
    }
})
def delete_producto(producto_id):
    """Elimina un producto junto con sus detalles."""
    producto = Productos.query.get(producto_id)
    if not producto:
        return jsonify({"message": "Producto no encontrado"}), 404

    # Eliminar detalles
    DetallesCatalogo.query.filter_by(producto_id=producto_id).delete()
    DetallesLamparasRanpu.query.filter_by(producto_id=producto_id).delete()
    DetallesProductosIA.query.filter_by(producto_id=producto_id).delete()

    # Eliminar producto
    db.session.delete(producto)
    db.session.commit()
    return jsonify({"message": "Producto eliminado exitosamente"}), 200

