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
    'description': 'Obtiene una lista de todos los modelos registrados en el sistema.',
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
                        'producto_id': {'type': 'integer', 'example': 1}
                    }
                }
            }
        }
    }
})
def get_todos_modelos():
    """Obtener todos los modelos registrados."""
    modelos = Modelos.query.all()
    return jsonify(modelos_schema.dump(modelos)), 200


@modelos_bp.route('/<int:modelo_id>', methods=['GET'])
@swag_from({
    'tags': ['Modelos'],
    'summary': 'Obtener un modelo por ID',
    'description': 'Obtiene un modelo específico por su ID.',
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
    """Obtener un modelo específico por su ID."""
    modelo = Modelos.query.get(modelo_id)
    if not modelo:
        return jsonify({"message": "Modelo no encontrado"}), 404
    return jsonify(modelo_schema.dump(modelo)), 200


@modelos_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Modelos'],
    'summary': 'Crear un nuevo modelo',
    'description': 'Registra un nuevo modelo asociado a un producto.',
    'responses': {
        201: {'description': 'Modelo creado exitosamente'},
        400: {'description': 'Datos inválidos en la solicitud'}
    }
})
def create_modelo():
    """Crear un nuevo modelo asociado a un producto."""
    data = request.get_json()
    try:
        nuevo_modelo = modelo_schema.load(data, session=db.session)
        db.session.add(nuevo_modelo)
        db.session.commit()
        return jsonify(modelo_schema.dump(nuevo_modelo)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al crear el modelo", "error": str(e)}), 500


@modelos_bp.route('/<int:modelo_id>', methods=['PUT'])
@swag_from({
    'tags': ['Modelos'],
    'summary': 'Actualizar un modelo existente',
    'description': 'Actualiza los datos de un modelo existente.',
    'parameters': [
        {
            'name': 'modelo_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del modelo a actualizar'
        }
    ],
    'responses': {
        200: {'description': 'Modelo actualizado exitosamente'},
        404: {'description': 'Modelo no encontrado'},
        400: {'description': 'Datos inválidos en la solicitud'}
    }
})
def update_modelo(modelo_id):
    """Actualizar un modelo existente."""
    modelo = Modelos.query.get(modelo_id)
    if not modelo:
        return jsonify({"message": "Modelo no encontrado"}), 404
    data = request.get_json()
    try:
        for key, value in data.items():
            setattr(modelo, key, value)
        db.session.commit()
        return jsonify(modelo_schema.dump(modelo)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al actualizar el modelo", "error": str(e)}), 500


@modelos_bp.route('/<int:modelo_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Modelos'],
    'summary': 'Eliminar un modelo existente',
    'description': 'Elimina un modelo específico por su ID.',
    'parameters': [
        {
            'name': 'modelo_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del modelo a eliminar'
        }
    ],
    'responses': {
        200: {'description': 'Modelo eliminado exitosamente'},
        404: {'description': 'Modelo no encontrado'}
    }
})
def delete_modelo(modelo_id):
    """Eliminar un modelo existente."""
    modelo = Modelos.query.get(modelo_id)
    if not modelo:
        return jsonify({"message": "Modelo no encontrado"}), 404
    try:
        db.session.delete(modelo)
        db.session.commit()
        return jsonify({"modelo_id": modelo_id, "message": "Modelo eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al eliminar el modelo", "error": str(e)}), 500
