from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models.direcciones import Direcciones
from ..schemas.direcciones_schema import DireccionesSchema
from ..database import db

# Middleware protections
from api.middlewares.origin_middleware import validate_origin
from api.middlewares.firebase_auth_middleware import firebase_auth_required

# Crear el Blueprint para direcciones
direcciones_bp = Blueprint('direcciones', __name__, url_prefix='/direcciones')

# Instancias del schema
direccion_schema = DireccionesSchema()
multiple_direcciones_schema = DireccionesSchema(many=True)

# @direcciones_bp.route('/', methods=['GET'])
# @validate_origin()
# @firebase_auth_required
# @swag_from({
#     'tags': ['Direcciones'],
#     'summary': 'Listar direcciones',
#     'description': 'Obtiene todas las direcciones registradas en la base de datos.',
#     'responses': {
#         200: {
#             'description': 'Lista de direcciones',
#             'schema': {
#                 'type': 'array',
#                 'items': {
#                     'type': 'object',
#                     'properties': {
#                         'direccion_id': {'type': 'integer', 'example': 1},
#                         'cedula': {'type': 'string', 'example': '0102030405'},
#                         'nombre_completo': {'type': 'string', 'example': 'Juan Perez'},
#                         'telefono': {'type': 'string', 'example': '0987654321'},
#                         'calle_principal': {'type': 'string', 'example': 'Calle Principal'},
#                         'calle_secundaria': {'type': 'string', 'example': 'Calle Secundaria'},
#                         'ciudad': {'type': 'string', 'example': 'Quito'},
#                         'provincia': {'type': 'string', 'example': 'Pichincha'},
#                         'numeracion': {'type': 'string', 'example': '1234'},
#                         'referencia': {'type': 'string', 'example': 'Frente al parque'},
#                         'codigo_postal': {'type': 'string', 'example': '170123'}
#                     }
#                 }
#             }
#         }
#     }
# })
# def get_direcciones():
#     """Obtener todas las direcciones"""
#     direcciones = Direcciones.query.all()
#     return jsonify(multiple_direcciones_schema.dump(direcciones)), 200

# @direcciones_bp.route('/', methods=['POST'])
# @validate_origin()
# @firebase_auth_required
# @swag_from({
#     'tags': ['Direcciones'],
#     'summary': 'Crear dirección',
#     'description': 'Crea una nueva dirección en la base de datos.',
#     'parameters': [
#         {
#             'name': 'body',
#             'in': 'body',
#             'required': True,
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'cedula': {'type': 'string', 'example': '0102030405'},
#                     'nombre_completo': {'type': 'string', 'example': 'Juan Perez'},
#                     'telefono': {'type': 'string', 'example': '0987654321'},
#                     'calle_principal': {'type': 'string', 'example': 'Calle Principal'},
#                     'calle_secundaria': {'type': 'string', 'example': 'Calle Secundaria'},
#                     'ciudad': {'type': 'string', 'example': 'Quito'},
#                     'provincia': {'type': 'string', 'example': 'Pichincha'},
#                     'numeracion': {'type': 'string', 'example': '1234'},
#                     'referencia': {'type': 'string', 'example': 'Frente al parque'},
#                     'codigo_postal': {'type': 'string', 'example': '170123'}
#                 }
#             }
#         }
#     ],
#     'responses': {
#         201: {
#             'description': 'Dirección creada exitosamente',
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'direccion_id': {'type': 'integer', 'example': 1},
#                     'cedula': {'type': 'string', 'example': '0102030405'},
#                     'nombre_completo': {'type': 'string', 'example': 'Juan Perez'},
#                     'telefono': {'type': 'string', 'example': '0987654321'},
#                     'calle_principal': {'type': 'string', 'example': 'Calle Principal'},
#                     'calle_secundaria': {'type': 'string', 'example': 'Calle Secundaria'},
#                     'ciudad': {'type': 'string', 'example': 'Quito'},
#                     'provincia': {'type': 'string', 'example': 'Pichincha'},
#                     'numeracion': {'type': 'string', 'example': '1234'},
#                     'referencia': {'type': 'string', 'example': 'Frente al parque'},
#                     'codigo_postal': {'type': 'string', 'example': '170123'}
#                 }
#             }
#         },
#         400: {'description': 'Error al crear la dirección'}
#     }
# })
# def create_direccion():
#     """Crear una nueva dirección"""
#     data = request.get_json()
#     try:
#         direccion = direccion_schema.load(data, session=db.session)
#         db.session.add(direccion)
#         db.session.commit()
#         return jsonify(direccion_schema.dump(direccion)), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 400

# @direcciones_bp.route('/<int:direccion_id>', methods=['GET'])
# @validate_origin()
# @firebase_auth_required
# @swag_from({
#     'tags': ['Direcciones'],
#     'summary': 'Obtener dirección',
#     'description': 'Obtiene una dirección por su ID.',
#     'parameters': [
#         {
#             'name': 'direccion_id',
#             'in': 'path',
#             'required': True,
#             'type': 'integer',
#             'description': 'ID de la dirección'
#         }
#     ],
#     'responses': {
#         200: {
#             'description': 'Dirección obtenida',
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'direccion_id': {'type': 'integer', 'example': 1},
#                     'cedula': {'type': 'string', 'example': '0102030405'},
#                     'nombre_completo': {'type': 'string', 'example': 'Juan Perez'},
#                     'telefono': {'type': 'string', 'example': '0987654321'},
#                     'calle_principal': {'type': 'string', 'example': 'Calle Principal'},
#                     'calle_secundaria': {'type': 'string', 'example': 'Calle Secundaria'},
#                     'ciudad': {'type': 'string', 'example': 'Quito'},
#                     'provincia': {'type': 'string', 'example': 'Pichincha'},
#                     'numeracion': {'type': 'string', 'example': '1234'},
#                     'referencia': {'type': 'string', 'example': 'Frente al parque'},
#                     'codigo_postal': {'type': 'string', 'example': '170123'}
#                 }
#             }
#         },
#         404: {'description': 'Dirección no encontrada'}
#     }
# })
# def get_direccion(direccion_id):
#     """Obtener una dirección por ID"""
#     direccion = Direcciones.query.get_or_404(direccion_id)
#     return jsonify(direccion_schema.dump(direccion)), 200

# @direcciones_bp.route('/<int:direccion_id>', methods=['PUT'])
# @validate_origin()
# @firebase_auth_required
# @swag_from({
#     'tags': ['Direcciones'],
#     'summary': 'Actualizar dirección',
#     'description': 'Actualiza los datos de una dirección existente.',
#     'parameters': [
#         {
#             'name': 'direccion_id',
#             'in': 'path',
#             'required': True,
#             'type': 'integer',
#             'description': 'ID de la dirección'
#         },
#         {
#             'name': 'body',
#             'in': 'body',
#             'required': True,
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'cedula': {'type': 'string', 'example': '0102030405'},
#                     'nombre_completo': {'type': 'string', 'example': 'Juan Perez'},
#                     'telefono': {'type': 'string', 'example': '0987654321'},
#                     'calle_principal': {'type': 'string', 'example': 'Calle Principal'},
#                     'calle_secundaria': {'type': 'string', 'example': 'Calle Secundaria'},
#                     'ciudad': {'type': 'string', 'example': 'Quito'},
#                     'provincia': {'type': 'string', 'example': 'Pichincha'},
#                     'numeracion': {'type': 'string', 'example': '1234'},
#                     'referencia': {'type': 'string', 'example': 'Frente al parque'},
#                     'codigo_postal': {'type': 'string', 'example': '170123'}
#                 }
#             }
#         }
#     ],
#     'responses': {
#         200: {
#             'description': 'Dirección actualizada',
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'direccion_id': {'type': 'integer', 'example': 1},
#                     'cedula': {'type': 'string', 'example': '0102030405'},
#                     'nombre_completo': {'type': 'string', 'example': 'Juan Perez'},
#                     'telefono': {'type': 'string', 'example': '0987654321'},
#                     'calle_principal': {'type': 'string', 'example': 'Calle Principal'},
#                     'calle_secundaria': {'type': 'string', 'example': 'Calle Secundaria'},
#                     'ciudad': {'type': 'string', 'example': 'Quito'},
#                     'provincia': {'type': 'string', 'example': 'Pichincha'},
#                     'numeracion': {'type': 'string', 'example': '1234'},
#                     'referencia': {'type': 'string', 'example': 'Frente al parque'},
#                     'codigo_postal': {'type': 'string', 'example': '170123'}
#                 }
#             }
#         },
#         400: {'description': 'Error al actualizar la dirección'}
#     }
# })
# def update_direccion(direccion_id):
#     """Actualizar una dirección existente"""
#     direccion = Direcciones.query.get_or_404(direccion_id)
#     data = request.get_json()
#     try:
#         direccion = direccion_schema.load(data, instance=direccion, session=db.session)
#         db.session.commit()
#         return jsonify(direccion_schema.dump(direccion)), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 400

# @direcciones_bp.route('/<int:direccion_id>', methods=['DELETE'])
# @validate_origin()
# @firebase_auth_required
# @swag_from({
#     'tags': ['Direcciones'],
#     'summary': 'Eliminar dirección',
#     'description': 'Elimina una dirección por su ID.',
#     'parameters': [
#         {
#             'name': 'direccion_id',
#             'in': 'path',
#             'required': True,
#             'type': 'integer',
#             'description': 'ID de la dirección'
#         }
#     ],
#     'responses': {
#         200: {'description': 'Dirección eliminada exitosamente'},
#         400: {'description': 'Error al eliminar la dirección'}
#     }
# })
# def delete_direccion(direccion_id):
#     """Eliminar una dirección"""
#     direccion = Direcciones.query.get_or_404(direccion_id)
#     try:
#         db.session.delete(direccion)
#         db.session.commit()
#         return jsonify({"message": "Dirección eliminada exitosamente"}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 400
