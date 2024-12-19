from flask import Blueprint, request, jsonify
from ..models.usuarios import Usuarios
from ..schemas.usuarios_schema import UsuariosSchema
from ..database import db

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

# Instancia del esquema
usuario_schema = UsuariosSchema()
usuarios_schema = UsuariosSchema(many=True)

# Crear usuario
@usuarios_bp.route('/', methods=['POST'])
def create_usuario():
    data = request.get_json()
    try:
        usuario = usuario_schema.load(data, session=db.session)
        db.session.add(usuario)
        db.session.commit()
        return usuario_schema.jsonify(usuario), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Obtener todos los usuarios
@usuarios_bp.route('/', methods=['GET'])
def get_usuarios():
    usuarios = Usuarios.query.all()
    return usuarios_schema.jsonify(usuarios), 200

# Obtener un usuario por ID
@usuarios_bp.route('/<int:usuario_id>', methods=['GET'])
def get_usuario(usuario_id):
    usuario = Usuarios.query.get_or_404(usuario_id)
    return usuario_schema.jsonify(usuario), 200

# Actualizar un usuario
@usuarios_bp.route('/<int:usuario_id>', methods=['PUT'])
def update_usuario(usuario_id):
    usuario = Usuarios.query.get_or_404(usuario_id)
    data = request.get_json()
    try:
        for key, value in data.items():
            setattr(usuario, key, value)
        db.session.commit()
        return usuario_schema.jsonify(usuario), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Eliminar un usuario
@usuarios_bp.route('/<int:usuario_id>', methods=['DELETE'])
def delete_usuario(usuario_id):
    usuario = Usuarios.query.get_or_404(usuario_id)
    try:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"message": "Usuario eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Registrar el blueprint en tu app principal
# from .routes.usuarios import usuarios_bp
# app.register_blueprint(usuarios_bp)
