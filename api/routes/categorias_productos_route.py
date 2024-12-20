from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.categorias_productos import CategoriasProductos
from ..database import db

categorias_productos_bp = Blueprint('categorias_productos', __name__)

@categorias_productos_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['CategoriasProductos'],
    'summary': 'Listar categorías de productos',
    'description': 'Obtiene todas las categorías de productos registradas en la base de datos.',
    'responses': {
        200: {
            'description': 'Lista de categorías de productos',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'categoria_producto_id': {'type': 'integer', 'example': 1},
                        'nombre': {'type': 'string', 'example': 'Electrónica'}
                    }
                }
            }
        }
    }
})
def get_categorias_productos():
    """Obtener todas las categorías de productos"""
    categorias = CategoriasProductos.query.all()
    return jsonify([categoria.to_dict() for categoria in categorias]), 200

@categorias_productos_bp.route('/<int:categoria_producto_id>', methods=['GET'])
@swag_from({
    'tags': ['CategoriasProductos'],
    'summary': 'Obtener categoría de producto',
    'description': 'Obtiene una categoría de producto por su ID.',
    'parameters': [
        {
            'name': 'categoria_producto_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID de la categoría de producto'
        }
    ],
    'responses': {
        200: {
            'description': 'Categoría de producto obtenida',
            'schema': {
                'type': 'object',
                'properties': {
                    'categoria_producto_id': {'type': 'integer', 'example': 1},
                    'nombre': {'type': 'string', 'example': 'Electrónica'}
                }
            }
        },
        404: {'description': 'Categoría de producto no encontrada'}
    }
})
def get_categoria_producto(categoria_producto_id):
    """Obtener una categoría de producto por ID"""
    categoria = CategoriasProductos.query.get_or_404(categoria_producto_id)
    return jsonify(categoria.to_dict()), 200

@categorias_productos_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['CategoriasProductos'],
    'summary': 'Crear categoría de producto',
    'description': 'Crea una nueva categoría de producto.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'example': 'Electrónica'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Categoría de producto creada exitosamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'categoria_producto_id': {'type': 'integer', 'example': 1},
                    'nombre': {'type': 'string', 'example': 'Electrónica'}
                }
            }
        },
        400: {'description': 'Error al crear categoría de producto'}
    }
})
def create_categoria_producto():
    """Crear una nueva categoría de producto"""
    data = request.get_json()
    try:
        categoria = CategoriasProductos(nombre=data['nombre'])
        db.session.add(categoria)
        db.session.commit()
        return jsonify(categoria.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@categorias_productos_bp.route('/<int:categoria_producto_id>', methods=['PUT'])
@swag_from({
    'tags': ['CategoriasProductos'],
    'summary': 'Actualizar categoría de producto',
    'description': 'Actualiza una categoría de producto existente.',
    'parameters': [
        {
            'name': 'categoria_producto_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID de la categoría de producto'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'example': 'Electrodomésticos'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Categoría de producto actualizada exitosamente'},
        400: {'description': 'Error al actualizar categoría de producto'}
    }
})
def update_categoria_producto(categoria_producto_id):
    """Actualizar una categoría de producto existente"""
    data = request.get_json()
    categoria = CategoriasProductos.query.get_or_404(categoria_producto_id)
    try:
        categoria.nombre = data['nombre']
        db.session.commit()
        return jsonify(categoria.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@categorias_productos_bp.route('/<int:categoria_producto_id>', methods=['DELETE'])
@swag_from({
    'tags': ['CategoriasProductos'],
    'summary': 'Eliminar categoría de producto',
    'description': 'Elimina una categoría de producto por su ID.',
    'parameters': [
        {
            'name': 'categoria_producto_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID de la categoría de producto'
        }
    ],
    'responses': {
        200: {'description': 'Categoría de producto eliminada exitosamente'},
        400: {'description': 'Error al eliminar categoría de producto'}
    }
})
def delete_categoria_producto(categoria_producto_id):
    """Eliminar una categoría de producto"""
    categoria = CategoriasProductos.query.get_or_404(categoria_producto_id)
    try:
        db.session.delete(categoria)
        db.session.commit()
        return jsonify({"message": "Categoría de producto eliminada exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
