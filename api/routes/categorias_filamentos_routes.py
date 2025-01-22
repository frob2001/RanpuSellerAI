from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.categorias_filamentos import CategoriasFilamentos
from ..schemas.categorias_filamentos_schema import CategoriasFilamentosSchema
from ..database import db

# Middleware protections
from api.middlewares.origin_middleware import validate_origin

# Crear el Blueprint para categorias_filamentos
categorias_filamentos_bp = Blueprint('categorias_filamentos', __name__)

# Instancias del schema
categoria_filamento_schema = CategoriasFilamentosSchema()
categorias_filamentos_schema = CategoriasFilamentosSchema(many=True)

@categorias_filamentos_bp.route('/', methods=['GET'])
@validate_origin()
@swag_from({
    'tags': ['CategoriasFilamentos'],
    'summary': 'Obtener todas las categorías de filamentos',
    'description': 'Obtiene una lista de todas las categorías de filamentos.',
    'responses': {
        200: {
            'description': 'Lista de categorías de filamentos',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'categoria_filamento_id': {'type': 'integer', 'example': 1},
                        'nombre': {'type': 'string', 'example': 'PLA'},
                        'descripcion': {'type': 'string', 'example': 'Filamento biodegradable y fácil de imprimir'},
                        'diametro': {'type': 'string', 'example': '1.75'},
                        'temp_extrusion': {'type': 'string', 'example': '200.00'},
                        'temp_cama': {'type': 'string', 'example': '60.00'},
                        'resistencia': {'type': 'string', 'example': '7.00'},
                        'flexibilidad': {'type': 'string', 'example': '5.00'},
                        'material_base': {'type': 'string', 'example': 'Ácido Poliláctico'},
                        'precio_kg': {'type': 'string', 'example': '25.00'}
                    }
                }
            }
        }
    }
})
def get_todas_categorias_filamentos():
    """Obtener todas las categorías de filamentos."""
    categorias = CategoriasFilamentos.query.all()
    return jsonify(categorias_filamentos_schema.dump(categorias)), 200

@categorias_filamentos_bp.route('/<int:categoria_filamento_id>', methods=['GET'])
@validate_origin()
@swag_from({
    'tags': ['CategoriasFilamentos'],
    'summary': 'Obtener una categoría de filamento por ID',
    'description': 'Obtiene una categoría de filamento específica por su ID.',
    'parameters': [
        {
            'name': 'categoria_filamento_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID de la categoría de filamento a obtener'
        }
    ],
    'responses': {
        200: {'description': 'Categoría de filamento encontrada'},
        404: {'description': 'Categoría de filamento no encontrada'}
    }
})
def get_categoria_filamento_por_id(categoria_filamento_id):
    """Obtener una categoría de filamento por ID."""
    categoria = CategoriasFilamentos.query.get(categoria_filamento_id)
    if not categoria:
        return jsonify({"message": "Categoría de filamento no encontrada"}), 404
    return jsonify(categoria_filamento_schema.dump(categoria)), 200

@categorias_filamentos_bp.route('/', methods=['POST'])
@validate_origin()
@swag_from({
    'tags': ['CategoriasFilamentos'],
    'summary': 'Crear una nueva categoría de filamento',
    'description': 'Registra una nueva categoría de filamento con todos sus atributos.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'example': 'PLA'},
                    'descripcion': {'type': 'string', 'example': 'Filamento biodegradable'},
                    'diametro': {'type': 'number', 'example': 1.75},
                    'temp_extrusion': {'type': 'number', 'example': 200.0},
                    'temp_cama': {'type': 'number', 'example': 60.0},
                    'resistencia': {'type': 'number', 'example': 7.0},
                    'flexibilidad': {'type': 'number', 'example': 5.0},
                    'material_base': {'type': 'string', 'example': 'Ácido Poliláctico'},
                    'precio_kg': {'type': 'number', 'example': 25.0}
                },
                'required': [
                    'nombre', 'diametro', 'temp_extrusion', 'temp_cama',
                    'resistencia', 'flexibilidad', 'material_base', 'precio_kg'
                ]
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Categoría de filamento creada exitosamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'categoria_filamento_id': {'type': 'integer', 'example': 1},
                    'nombre': {'type': 'string', 'example': 'PLA'},
                    'descripcion': {'type': 'string', 'example': 'Filamento biodegradable'},
                    'diametro': {'type': 'number', 'example': 1.75},
                    'temp_extrusion': {'type': 'number', 'example': 200.0},
                    'temp_cama': {'type': 'number', 'example': 60.0},
                    'resistencia': {'type': 'number', 'example': 7.0},
                    'flexibilidad': {'type': 'number', 'example': 5.0},
                    'material_base': {'type': 'string', 'example': 'Ácido Poliláctico'},
                    'precio_kg': {'type': 'number', 'example': 25.0}
                }
            }
        },
        400: {'description': 'Datos inválidos en la solicitud'},
        500: {'description': 'Error interno del servidor'}
    }
})
def create_categoria_filamento():
    """Crear una nueva categoría de filamento."""
    data = request.get_json()

    try:
        # Validar y cargar los datos con el esquema
        nueva_categoria = categoria_filamento_schema.load(data, session=db.session)
        db.session.add(nueva_categoria)
        db.session.commit()

        # Devolver la nueva categoría creada
        return jsonify(categoria_filamento_schema.dump(nueva_categoria)), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al crear la categoría de filamento", "error": str(e)}), 500
    
@categorias_filamentos_bp.route('/<int:categoria_filamento_id>', methods=['PUT'])
@validate_origin()
@swag_from({
    'tags': ['CategoriasFilamentos'],
    'summary': 'Actualizar una categoría de filamento',
    'description': 'Actualiza los datos de una categoría de filamento existente.',
    'parameters': [
        {
            'name': 'categoria_filamento_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID de la categoría de filamento a actualizar'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'example': 'PLA'},
                    'descripcion': {'type': 'string', 'example': 'Filamento biodegradable'},
                    'diametro': {'type': 'number', 'example': 1.75},
                    'temp_extrusion': {'type': 'number', 'example': 200.0},
                    'temp_cama': {'type': 'number', 'example': 60.0},
                    'resistencia': {'type': 'number', 'example': 7.0},
                    'flexibilidad': {'type': 'number', 'example': 5.0},
                    'material_base': {'type': 'string', 'example': 'Ácido Poliláctico'},
                    'precio_kg': {'type': 'number', 'example': 25.0}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Categoría de filamento actualizada exitosamente'},
        404: {'description': 'Categoría de filamento no encontrada'},
        400: {'description': 'Datos inválidos en la solicitud'},
        500: {'description': 'Error interno del servidor'}
    }
})
def update_categoria_filamento(categoria_filamento_id):
    """Actualizar una categoría de filamento."""
    data = request.get_json()
    categoria = CategoriasFilamentos.query.get(categoria_filamento_id)

    if not categoria:
        return jsonify({"message": "Categoría de filamento no encontrada"}), 404

    try:
        # Actualizar los datos de la categoría existente
        for key, value in data.items():
            if hasattr(categoria, key):
                setattr(categoria, key, value)

        db.session.commit()
        return jsonify(categoria_filamento_schema.dump(categoria)), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al actualizar la categoría de filamento", "error": str(e)}), 500

@categorias_filamentos_bp.route('/<int:categoria_filamento_id>', methods=['DELETE'])
@validate_origin()
@swag_from({
    'tags': ['CategoriasFilamentos'],
    'summary': 'Eliminar una categoría de filamento',
    'description': 'Elimina una categoría de filamento existente por su ID.',
    'parameters': [
        {
            'name': 'categoria_filamento_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID de la categoría de filamento a eliminar'
        }
    ],
    'responses': {
        200: {'description': 'Categoría de filamento eliminada exitosamente'},
        404: {'description': 'Categoría de filamento no encontrada'},
        500: {'description': 'Error interno del servidor'}
    }
})
def delete_categoria_filamento(categoria_filamento_id):
    """Eliminar una categoría de filamento."""
    categoria = CategoriasFilamentos.query.get(categoria_filamento_id)

    if not categoria:
        return jsonify({"message": "Categoría de filamento no encontrada"}), 404

    try:
        db.session.delete(categoria)
        db.session.commit()
        return jsonify({"message": "Categoría de filamento eliminada exitosamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al eliminar la categoría de filamento", "error": str(e)}), 500
