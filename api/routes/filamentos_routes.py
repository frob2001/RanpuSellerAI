from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.filamentos import Filamentos
from ..schemas.filamentos_schema import FilamentosSchema
from ..models.colores import Colores
from ..database import db

# Crear el Blueprint para filamentos
filamentos_bp = Blueprint('filamentos', __name__)

# Instancias del schema
filamento_schema = FilamentosSchema()
filamentos_schema = FilamentosSchema(many=True)

@filamentos_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Filamentos'],
    'summary': 'Obtener todos los filamentos',
    'description': 'Obtiene una lista de todos los filamentos.',
    'responses': {
        200: {
            'description': 'Lista de filamentos',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'filamento_id': {'type': 'integer', 'example': 1},
                        'color': {'type': 'string', 'example': 'Rojo'},
                        'marca': {'type': 'string', 'example': 'Esun'},
                        'peso_inicial': {'type': 'string', 'example': '1000.00'},
                        'peso_actual': {'type': 'string', 'example': '800.00'},
                        'longitud_inicial': {'type': 'string', 'example': '330.00'},
                        'longitud_actual': {'type': 'string', 'example': '250.00'},
                        'precio_compra': {'type': 'string', 'example': '25.00'},
                        'fecha_compra': {'type': 'string', 'example': '2023-01-01T00:00:00'},
                        'categoria_filamento_id': {'type': 'integer', 'example': 1}
                    }
                }
            }
        }
    }
})
def get_todos_filamentos():
    """Obtener todos los filamentos."""
    filamentos = Filamentos.query.all()
    return jsonify(filamentos_schema.dump(filamentos)), 200


@filamentos_bp.route('/<int:filamento_id>', methods=['GET'])
@swag_from({
    'tags': ['Filamentos'],
    'summary': 'Obtener un filamento por ID',
    'description': 'Obtiene un filamento específico por su ID.',
    'parameters': [
        {
            'name': 'filamento_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del filamento a obtener'
        }
    ],
    'responses': {
        200: {'description': 'Filamento encontrado'},
        404: {'description': 'Filamento no encontrado'}
    }
})
def get_filamento_por_id(filamento_id):
    """Obtener un filamento por ID."""
    filamento = Filamentos.query.get(filamento_id)
    if not filamento:
        return jsonify({"message": "Filamento no encontrado"}), 404
    return jsonify(filamento_schema.dump(filamento)), 200


@filamentos_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Filamentos'],
    'summary': 'Crear un nuevo filamento',
    'description': 'Registra un nuevo filamento con todos sus atributos.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'color': {'type': 'string', 'example': 'Rojo'},
                    'marca': {'type': 'string', 'example': 'Esun'},
                    'peso_inicial': {'type': 'number', 'example': 1000.00},
                    'peso_actual': {'type': 'number', 'example': 800.00},
                    'longitud_inicial': {'type': 'number', 'example': 330.00},
                    'longitud_actual': {'type': 'number', 'example': 250.00},
                    'precio_compra': {'type': 'number', 'example': 25.00},
                    'fecha_compra': {'type': 'string', 'example': '2023-01-01T00:00:00'},
                    'categoria_filamento_id': {'type': 'integer', 'example': 1}
                },
                'required': [
                    'color', 'marca', 'peso_inicial', 'peso_actual',
                    'longitud_inicial', 'longitud_actual', 'precio_compra',
                    'fecha_compra', 'categoria_filamento_id'
                ]
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Filamento creado exitosamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'filamento_id': {'type': 'integer', 'example': 1},
                    'color': {'type': 'string', 'example': 'Rojo'},
                    'marca': {'type': 'string', 'example': 'Esun'},
                    'peso_inicial': {'type': 'number', 'example': 1000.00},
                    'peso_actual': {'type': 'number', 'example': 800.00},
                    'longitud_inicial': {'type': 'number', 'example': 330.00},
                    'longitud_actual': {'type': 'number', 'example': 250.00},
                    'precio_compra': {'type': 'number', 'example': 25.00},
                    'fecha_compra': {'type': 'string', 'example': '2023-01-01T00:00:00'},
                    'categoria_filamento_id': {'type': 'integer', 'example': 1}
                }
            }
        },
        400: {'description': 'Datos inválidos en la solicitud'},
        500: {'description': 'Error interno del servidor'}
    }
})
def create_filamento():
    """Crear un nuevo filamento."""
    data = request.get_json()

    try:
        # Validar y cargar los datos con el esquema
        nuevo_filamento = filamento_schema.load(data, session=db.session)
        db.session.add(nuevo_filamento)
        db.session.commit()

        # Devolver el nuevo filamento creado
        return jsonify(filamento_schema.dump(nuevo_filamento)), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al crear el filamento", "error": str(e)}), 500


@filamentos_bp.route('/<int:filamento_id>', methods=['PUT'])
@swag_from({
    'tags': ['Filamentos'],
    'summary': 'Actualizar un filamento',
    'description': 'Actualiza los datos de un filamento existente.',
    'parameters': [
        {
            'name': 'filamento_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del filamento a actualizar'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'color': {'type': 'string', 'example': 'Rojo'},
                    'marca': {'type': 'string', 'example': 'Esun'},
                    'peso_inicial': {'type': 'number', 'example': 1000.00},
                    'peso_actual': {'type': 'number', 'example': 800.00},
                    'longitud_inicial': {'type': 'number', 'example': 330.00},
                    'longitud_actual': {'type': 'number', 'example': 250.00},
                    'precio_compra': {'type': 'number', 'example': 25.00},
                    'fecha_compra': {'type': 'string', 'example': '2023-01-01T00:00:00'},
                    'categoria_filamento_id': {'type': 'integer', 'example': 1}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Filamento actualizado exitosamente'},
        404: {'description': 'Filamento no encontrado'},
        400: {'description': 'Datos inválidos en la solicitud'},
        500: {'description': 'Error interno del servidor'}
    }
})
def update_filamento(filamento_id):
    """Actualizar un filamento."""
    data = request.get_json()
    filamento = Filamentos.query.get(filamento_id)

    if not filamento:
        return jsonify({"message": "Filamento no encontrado"}), 404

    try:
        # Actualizar los datos del filamento existente
        for key, value in data.items():
            if hasattr(filamento, key):
                setattr(filamento, key, value)

        db.session.commit()
        return jsonify(filamento_schema.dump(filamento)), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al actualizar el filamento", "error": str(e)}), 500


@filamentos_bp.route('/<int:filamento_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Filamentos'],
    'summary': 'Eliminar un filamento',
    'description': 'Elimina un filamento existente por su ID.',
    'parameters': [
        {
            'name': 'filamento_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del filamento a eliminar'
        }
    ],
    'responses': {
        200: {'description': 'Filamento eliminado exitosamente'},
        404: {'description': 'Filamento no encontrado'},
        500: {'description': 'Error interno del servidor'}
    }
})
def delete_filamento(filamento_id):
    """Eliminar un filamento."""
    filamento = Filamentos.query.get(filamento_id)

    if not filamento:
        return jsonify({"message": "Filamento no encontrado"}), 404

    try:
        db.session.delete(filamento)
        db.session.commit()
        return jsonify({"message": "Filamento eliminado exitosamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al eliminar el filamento", "error": str(e)}), 500
