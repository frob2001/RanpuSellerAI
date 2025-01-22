from flask import Blueprint, request, jsonify
from flasgger import swag_from
from datetime import datetime, timezone
from ..models.usuarios import Usuarios
from ..schemas.usuarios_schema import UsuariosSchema
from ..database import db

# Middleware protections
from api.middlewares.origin_middleware import validate_origin
from api.middlewares.firebase_auth_middleware import firebase_auth_required

usuarios_bp = Blueprint('usuarios', __name__)

# Instancia del esquema
usuario_schema = UsuariosSchema()
usuarios_schema = UsuariosSchema(many=True)

@usuarios_bp.route('/', methods=['GET'])
@validate_origin()
@firebase_auth_required
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
@validate_origin()
@firebase_auth_required
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Crear usuario',
    'description': 'Crea un nuevo usuario en la base de datos o actualiza la fecha de último inicio de sesión si el usuario ya existe.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
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
                    'firebase_uid': {'type': 'string', 'example': 'Alkasdhjaskdj123jk'},
                    'ai_gen_tokens': {'type': 'integer', 'example': 2},
                    'last_login': {'type': 'string', 'example': '2025-01-09T12:00:00'}
                }
            }
        },
        200: {
            'description': 'Usuario ya existe, último inicio de sesión actualizado',
            'schema': {
                'type': 'object',
                'properties': {
                    'usuario_id': {'type': 'integer', 'example': 1},
                    'firebase_uid': {'type': 'string', 'example': 'Alkasdhjaskdj123jk'},
                    'last_login': {'type': 'string', 'example': '2025-01-09T12:00:00'}
                }
            }
        },
        400: {'description': 'Error al procesar la solicitud'}
    }
})
def create_usuario():
    """Crear un nuevo usuario o actualizar el último inicio de sesión"""
    data = request.get_json()
    firebase_uid = data.get('firebase_uid')

    if not firebase_uid:
        return jsonify({"error": "firebase_uid is required."}), 400

    existing_user = Usuarios.query.filter_by(firebase_uid=firebase_uid).first()

    if existing_user:
        try:
            existing_user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            return jsonify({'message': 'User updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

    try:
        new_user = Usuarios(
            firebase_uid=firebase_uid,
            ai_gen_tokens=2,
            last_login=datetime.now(timezone.utc)
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@usuarios_bp.route('/<int:usuario_id>', methods=['GET'])
@validate_origin()
@firebase_auth_required
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
@validate_origin()
@firebase_auth_required
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
@validate_origin()
@firebase_auth_required
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

@usuarios_bp.route('/tokens/<string:firebase_uid>', methods=['GET'])
@validate_origin()
@firebase_auth_required
@swag_from({
    'tags': ['Usuarios'],
    'summary': 'Obtener AI generation tokens de un usuario por su Firebase UID',
    'description': 'Devuelve la cantidad de `ai_gen_tokens` para un usuario específico identificado por su Firebase UID.',
    'parameters': [
        {
            'name': 'firebase_uid',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': 'Firebase UID del usuario'
        }
    ],
    'responses': {
        200: {
            'description': 'Cantidad de tokens devuelta exitosamente',
            'schema': {
                'type': 'object',
                'properties': {
                    'ai_gen_tokens': {'type': 'integer', 'example': 3}
                }
            }
        },
        404: {
            'description': 'Usuario no encontrado en la base de datos'
        }
    }
})
def get_ai_gen_tokens(firebase_uid):
    """
    Obtener la cantidad de AI generation tokens (ai_gen_tokens) de un usuario,
    buscando por su Firebase UID.
    """
    user = Usuarios.query.filter_by(firebase_uid=firebase_uid).first()
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    return jsonify({
        'ai_gen_tokens': user.ai_gen_tokens
    }), 200
