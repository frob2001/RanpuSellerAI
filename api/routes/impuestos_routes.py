from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.impuestos import Impuestos
from ..schemas.impuestos_schema import ImpuestosSchema
from ..database import db

impuestos_bp = Blueprint('impuestos', __name__)

# Instancias de los schemas
impuestos_schema = ImpuestosSchema()
multiple_impuestos_schema = ImpuestosSchema(many=True)

@impuestos_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Impuestos'],
    'summary': 'Listar impuestos',
    'description': 'Obtiene todos los impuestos registrados en la base de datos.',
    'responses': {
        200: {
            'description': 'Lista de impuestos',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'impuesto_id': {'type': 'integer', 'example': 1},
                        'nombre': {'type': 'string', 'example': 'IVA'},
                        'porcentaje': {'type': 'string', 'example': '12.00'},
                        'activo': {'type': 'boolean', 'example': True}
                    }
                }
            }
        }
    }
})
def get_impuestos():
    """Obtener todos los impuestos"""
    impuestos = Impuestos.query.all()
    return jsonify(multiple_impuestos_schema.dump(impuestos)), 200

@impuestos_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Impuestos'],
    'summary': 'Crear impuesto',
    'description': 'Crea un nuevo impuesto en la base de datos.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'example': 'IVA'},
                    'porcentaje': {'type': 'string', 'example': '12.00'},
                    'activo': {'type': 'boolean', 'example': False}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Impuesto creado exitosamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'impuesto_id': {'type': 'integer', 'example': 1},
                    'nombre': {'type': 'string', 'example': 'IVA'},
                    'porcentaje': {'type': 'string', 'example': '12.00'},
                    'activo': {'type': 'boolean', 'example': False}
                }
            }
        },
        400: {'description': 'Error al crear impuesto'}
    }
})
def create_impuesto():
    """Crear un nuevo impuesto"""
    data = request.get_json()
    try:
        impuesto = impuestos_schema.load(data, session=db.session)
        if data.get("activo"):
            # Desactivar todos los impuestos antes de activar uno nuevo
            Impuestos.query.update({"activo": False})
        db.session.add(impuesto)
        db.session.commit()
        return jsonify(impuestos_schema.dump(impuesto)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@impuestos_bp.route('/<int:impuesto_id>', methods=['GET'])
@swag_from({
    'tags': ['Impuestos'],
    'summary': 'Obtener impuesto',
    'description': 'Obtiene un impuesto por su ID.',
    'parameters': [
        {
            'name': 'impuesto_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del impuesto'
        }
    ],
    'responses': {
        200: {
            'description': 'Impuesto obtenido',
            'schema': {
                'type': 'object',
                'properties': {
                    'impuesto_id': {'type': 'integer', 'example': 1},
                    'nombre': {'type': 'string', 'example': 'IVA'},
                    'porcentaje': {'type': 'string', 'example': '12.00'}
                }
            }
        },
        404: {'description': 'Impuesto no encontrado'}
    }
})
def get_impuesto(impuesto_id):
    """Obtener un impuesto por ID"""
    impuesto = Impuestos.query.get_or_404(impuesto_id)
    return jsonify(impuestos_schema.dump(impuesto)), 200

@impuestos_bp.route('/<int:impuesto_id>', methods=['PUT'])
@swag_from({
    'tags': ['Impuestos'],
    'summary': 'Actualizar impuesto',
    'description': 'Actualiza los datos de un impuesto existente.',
    'parameters': [
        {
            'name': 'impuesto_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del impuesto'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nombre': {'type': 'string', 'example': 'IVA'},
                    'porcentaje': {'type': 'string', 'example': '14.00'},
                    'activo': {'type': 'boolean', 'example': True}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Impuesto actualizado',
            'schema': {
                'type': 'object',
                'properties': {
                    'impuesto_id': {'type': 'integer', 'example': 1},
                    'nombre': {'type': 'string', 'example': 'IVA'},
                    'porcentaje': {'type': 'string', 'example': '14.00'},
                    'activo': {'type': 'boolean', 'example': True}
                }
            }
        },
        400: {'description': 'Error al actualizar impuesto'}
    }
})
def update_impuesto(impuesto_id):
    """Actualizar un impuesto existente"""
    impuesto = Impuestos.query.get_or_404(impuesto_id)
    data = request.get_json()
    try:
        if data.get("activo"):
            # Desactivar todos los impuestos antes de activar el actualizado
            Impuestos.query.update({"activo": False})
        impuesto = impuestos_schema.load(data, instance=impuesto, session=db.session)
        db.session.commit()
        return jsonify(impuestos_schema.dump(impuesto)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@impuestos_bp.route('/<int:impuesto_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Impuestos'],
    'summary': 'Eliminar impuesto',
    'description': 'Elimina un impuesto por su ID.',
    'parameters': [
        {
            'name': 'impuesto_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del impuesto'
        }
    ],
    'responses': {
        200: {'description': 'Impuesto eliminado exitosamente'},
        400: {'description': 'Error al eliminar impuesto'}
    }
})
def delete_impuesto(impuesto_id):
    """Eliminar un impuesto"""
    impuesto = Impuestos.query.get_or_404(impuesto_id)
    try:
        db.session.delete(impuesto)
        db.session.commit()
        return jsonify({"message": "Impuesto eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
@impuestos_bp.route('/<int:impuesto_id>/activate', methods=['PATCH'])
@swag_from({
    'tags': ['Impuestos'],
    'summary': 'Activar impuesto',
    'description': 'Activa un impuesto y desactiva los demás, asegurando que solo un impuesto esté activo a la vez.',
    'parameters': [
        {
            'name': 'impuesto_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del impuesto a activar'
        }
    ],
    'responses': {
        200: {
            'description': 'Impuesto activado correctamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'impuesto_id': {'type': 'integer', 'example': 1},
                    'nombre': {'type': 'string', 'example': 'IVA'},
                    'porcentaje': {'type': 'string', 'example': '15.00'},
                    'activo': {'type': 'boolean', 'example': True}
                }
            }
        },
        400: {'description': 'Error al activar impuesto'}
    }
})
def activate_impuesto(impuesto_id):
    """Activar un impuesto y desactivar los demás"""
    impuesto = Impuestos.query.get_or_404(impuesto_id)
    try:
        # Desactivar todos los impuestos
        Impuestos.query.update({"activo": False})

        # Activar el impuesto seleccionado
        impuesto.activo = True
        db.session.commit()

        return jsonify(impuestos_schema.dump(impuesto)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400