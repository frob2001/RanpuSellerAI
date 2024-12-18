from flask import Blueprint, jsonify, request
from .models import EstadosImpresoras
from .schemas import EstadosImpresorasSchema
from .database import db

api_bp = Blueprint("api", __name__)

estado_schema = EstadosImpresorasSchema()
estados_schema = EstadosImpresorasSchema(many=True)

@api_bp.route("/estados", methods=["GET"])
def get_estados():
    estados = EstadosImpresoras.query.all()
    serialized_data = estados_schema.dump(estados)  # Serializar datos
    return jsonify(serialized_data)  # Convertir a respuesta JSON

@api_bp.route("/estados/<int:id>", methods=["GET"])
def get_estado(id):
    estado = EstadosImpresoras.query.get_or_404(id)
    serialized_data = estado_schema.dump(estado)  # Serializar datos
    return jsonify(serialized_data)  # Convertir a respuesta JSON

@api_bp.route("/estados", methods=["POST"])
def create_estado():
    data = request.json
    new_estado = EstadosImpresoras(nombre=data["nombre"])
    db.session.add(new_estado)
    db.session.commit()
    serialized_data = estado_schema.dump(new_estado)  # Serializar datos
    return jsonify(serialized_data), 201  # Convertir a respuesta JSON

@api_bp.route("/estados/<int:id>", methods=["PUT"])
def update_estado(id):
    estado = EstadosImpresoras.query.get_or_404(id)
    data = request.json
    estado.nombre = data["nombre"]
    db.session.commit()
    serialized_data = estado_schema.dump(estado)  # Serializar datos
    return jsonify(serialized_data)  # Convertir a respuesta JSON

@api_bp.route("/estados/<int:id>", methods=["DELETE"])
def delete_estado(id):
    estado = EstadosImpresoras.query.get_or_404(id)
    db.session.delete(estado)
    db.session.commit()
    return jsonify({"message": "Estado deleted"})
