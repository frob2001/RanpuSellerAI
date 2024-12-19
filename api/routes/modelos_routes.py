from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.modelos import Modelos
from ..schemas.modelos_schema import ModelosSchema
from ..database import db

# Crear el Blueprint para modelos
modelos_bp = Blueprint('modelos', __name__)

# Instancias del schema
modelo_schema = ModelosSchema()
modelos_schema = ModelosSchema(many=True)

@modelos_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Modelos'],
    'summary': 'Obtener todos los modelos',
    'description': 'Obtiene una lista de todos los modelos registrados en el sistema, incluyendo el producto asociado.',
    'responses': {
        200: {
            'description': 'Lista de modelos',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'modelo_id': {'type': 'integer', 'example': 1},
                        'tiempo_estimado': {'type': 'string', 'example': '01:30:00'},
                        'alto': {'type': 'string', 'example': '10.00'},
                        'ancho': {'type': 'string', 'example': '5.00'},
                        'largo': {'type': 'string', 'example': '7.00'},
                        'stl': {'type': 'string', 'example': 'path/to/file.stl'},
                        'stock': {'type': 'integer', 'example': 100},
                        'producto': {
                            'type': 'object',
                            'properties': {
                                'producto_id': {'type': 'integer', 'example': 1},
                                'nombre': {'type': 'string', 'example': 'Lámpara Redonda'}
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_todos_modelos():
    """Obtener todos los modelos registrados, incluyendo el producto asociado."""
    modelos = Modelos.query.all()
    response = [
        {
            **modelo_schema.dump(modelo),
            "producto": {
                **modelo.producto.to_dict(),
                "producto_id": modelo.producto_id  # Incluyendo producto_id dentro del objeto producto
            }
        } for modelo in modelos
    ]
    return jsonify(response), 200


@modelos_bp.route('/<int:modelo_id>', methods=['GET'])
@swag_from({
    'tags': ['Modelos'],
    'summary': 'Obtener un modelo por ID',
    'description': 'Obtiene un modelo específico por su ID, incluyendo el producto asociado.',
    'parameters': [
        {
            'name': 'modelo_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del modelo a obtener'
        }
    ],
    'responses': {
        200: {'description': 'Modelo encontrado'},
        404: {'description': 'Modelo no encontrado'}
    }
})
def get_modelo_por_id(modelo_id):
    """Obtener un modelo específico por su ID, incluyendo el producto asociado."""
    modelo = Modelos.query.get(modelo_id)
    if not modelo:
        return jsonify({"message": "Modelo no encontrado"}), 404
    response = {
        **modelo_schema.dump(modelo),
        "producto": {
            **modelo.producto.to_dict(),
            "producto_id": modelo.producto_id  # Incluyendo producto_id dentro del objeto producto
        }
    }
    return jsonify(response), 200


@modelos_bp.route('/producto/<int:producto_id>', methods=['GET'])
@swag_from({
    'tags': ['Modelos'],
    'summary': 'Obtener modelos por producto',
    'description': 'Obtiene todos los modelos asociados a un producto específico por su ID.',
    'parameters': [
        {
            'name': 'producto_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del producto para buscar los modelos asociados'
        }
    ],
    'responses': {
        200: {
            'description': 'Modelos encontrados',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'modelo_id': {'type': 'integer', 'example': 1},
                        'tiempo_estimado': {'type': 'string', 'example': '01:30:00'},
                        'alto': {'type': 'string', 'example': '10.00'},
                        'ancho': {'type': 'string', 'example': '5.00'},
                        'largo': {'type': 'string', 'example': '7.00'},
                        'stl': {'type': 'string', 'example': 'path/to/file.stl'},
                        'stock': {'type': 'integer', 'example': 100},
                        'producto': {
                            'type': 'object',
                            'properties': {
                                'producto_id': {'type': 'integer', 'example': 1},
                                'nombre': {'type': 'string', 'example': 'Lámpara Redonda'}
                            }
                        }
                    }
                }
            }
        },
        404: {'description': 'Producto no encontrado'}
    }
})
def get_modelos_por_producto(producto_id):
    """Obtener modelos asociados a un producto específico."""
    modelos = Modelos.query.filter_by(producto_id=producto_id).all()
    if not modelos:
        return jsonify({"message": "No se encontraron modelos para este producto"}), 404
    response = [
        {
            **modelo_schema.dump(modelo),
            "producto": {
                **modelo.producto.to_dict(),
                "producto_id": modelo.producto_id  # Incluyendo producto_id dentro del objeto producto
            }
        } for modelo in modelos
    ]
    return jsonify(response), 200


@modelos_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Modelos'],
    'summary': 'Crear un nuevo modelo',
    'description': 'Crea un nuevo modelo asociado a un producto específico.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'tiempo_estimado': {'type': 'string', 'example': '01:30:00'},
                    'alto': {'type': 'string', 'example': '10.00'},
                    'ancho': {'type': 'string', 'example': '5.00'},
                    'largo': {'type': 'string', 'example': '7.00'},
                    'stl': {'type': 'string', 'example': 'path/to/file.stl'},
                    'stock': {'type': 'integer', 'example': 100},
                    'producto_id': {'type': 'integer', 'example': 1}
                },
                'required': [
                    'tiempo_estimado', 'alto', 'ancho', 'largo', 'stl', 'stock', 'producto_id'
                ]
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Modelo creado exitosamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'modelo_id': {'type': 'integer', 'example': 1},
                    'message': {'type': 'string', 'example': 'Modelo creado exitosamente'}
                }
            }
        },
        400: {'description': 'Datos inválidos en la solicitud'},
        500: {'description': 'Error interno del servidor'}
    }
})
def create_modelo():
    """Crear un nuevo modelo asociado a un producto."""
    data = request.get_json()

    try:
        # Validar que el producto exista
        producto_id = data.get('producto_id')
        if not producto_id:
            return jsonify({"message": "El campo 'producto_id' es obligatorio"}), 400

        # Crear el modelo
        nuevo_modelo = modelo_schema.load(data, session=db.session)
        db.session.add(nuevo_modelo)
        db.session.commit()

        # Respuesta exitosa
        return jsonify({
            "modelo_id": nuevo_modelo.modelo_id,
            "message": "Modelo creado exitosamente"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al crear el modelo", "error": str(e)}), 500
