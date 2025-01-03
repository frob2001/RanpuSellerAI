from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.usuarios import Usuarios
from ..schemas.usuarios_schema import UsuariosSchema
from ..database import db

usuarios_bp = Blueprint('usuarios', __name__)

# Instancia del esquema
usuario_schema = UsuariosSchema()
usuarios_schema = UsuariosSchema(many=True)

@usuarios_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Listar usuarios',
    'description': 'Obtiene todos los usuarios registrados en la base de datos.',
    'responses': {
        200: {
            'description': 'Lista de usuarios',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'usuario_id': {'type': 'integer', 'example': 1},
                        'firebase_uid': {'type': 'string', 'example': 'Alkasdhjaskdj123jk'}
                    }
                }
            }
        }
    }
})
def get_usuarios():
    """Obtener todos los usuarios"""
    usuarios = Usuarios.query.all()
    return jsonify(usuarios_schema.dump(usuarios)), 200

@usuarios_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Crear usuario',
    'description': 'Crea un nuevo usuario en la base de datos.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'usuario_id': {'type': 'integer', 'example': 1},
                    'firebase_uid': {'type': 'string', 'example': 'Alkasdhjaskdj123jk'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Usuario creado exitosamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'usuario_id': {'type': 'integer', 'example': 1},
                    'firebase_uid': {'type': 'string', 'example': 'Alkasdhjaskdj123jk'}
                }
            }
        },
        400: {'description': 'Error al crear usuario'}
    }
})
def create_usuario():
    """Crear un nuevo usuario"""
    data = request.get_json()
    try:
        usuario = usuario_schema.load(data, session=db.session)
        db.session.add(usuario)
        db.session.commit()
        return jsonify(usuario_schema.dump(usuario)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@usuarios_bp.route('/<int:usuario_id>', methods=['GET'])
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Obtener usuario',
    'description': 'Obtiene un usuario por su ID.',
    'parameters': [
        {
            'name': 'usuario_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del usuario'
        }
    ],
    'responses': {
        200: {
            'description': 'Usuario obtenido',
            'schema': {
                'type': 'object',
                'properties': {
                    'usuario_id': {'type': 'integer', 'example': 1},
                    'firebase_uid': {'type': 'string', 'example': 'Alkasdhjaskdj123jk'}
                }
            }
        },
        404: {'description': 'Usuario no encontrado'}
    }
})
def get_usuario(usuario_id):
    """Obtener un usuario por ID"""
    usuario = Usuarios.query.get_or_404(usuario_id)
    return jsonify(usuario_schema.dump(usuario)), 200

@usuarios_bp.route('/<int:usuario_id>', methods=['PUT'])
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Actualizar usuario',
    'description': 'Actualiza los datos de un usuario existente.',
    'parameters': [
        {
            'name': 'usuario_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del usuario'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'usuario_id': {'type': 'integer', 'example': 1}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Usuario actualizado',
            'schema': {
                'type': 'object',
                'properties': {
                    'usuario_id': {'type': 'integer', 'example': 1}
                }
            }
        },
        400: {'description': 'Error al actualizar usuario'}
    }
})
def update_usuario(usuario_id):
    """Actualizar un usuario existente"""
    usuario = Usuarios.query.get_or_404(usuario_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            setattr(usuario, key, value)
        db.session.commit()
        return jsonify(usuario_schema.dump(usuario)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@usuarios_bp.route('/<int:usuario_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Eliminar usuario',
    'description': 'Elimina un usuario por su ID.',
    'parameters': [
        {
            'name': 'usuario_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID del usuario'
        }
    ],
    'responses': {
        200: {'description': 'Usuario eliminado exitosamente'},
        400: {'description': 'Error al eliminar usuario'}
    }
})
def delete_usuario(usuario_id):
    """Eliminar un usuario"""
    usuario = Usuarios.query.get_or_404(usuario_id)
    try:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"message": "Usuario eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
