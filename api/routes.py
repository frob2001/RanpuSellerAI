from flask import Blueprint, jsonify, request
from .models import EstadoImpresora
from .schemas import EstadoImpresoraSchema
from .database import db

api_bp = Blueprint("api", __name__)

estado_schema = EstadoImpresoraSchema()
estados_schema = EstadoImpresoraSchema(many=True)

@api_bp.route("/estados", methods=["GET"])
def get_estados():
    estados = EstadoImpresora.query.all()
    return estados_schema.jsonify(estados)

@api_bp.route("/estados/<int:id>", methods=["GET"])
def get_estado(id):
    estado = EstadoImpresora.query.get_or_404(id)
    return estado_schema.jsonify(estado)

@api_bp.route("/estados", methods=["POST"])
def create_estado():
    data = request.json
    new_estado = EstadoImpresora(nombre=data["nombre"])
    db.session.add(new_estado)
    db.session.commit()
    return estado_schema.jsonify(new_estado), 201

@api_bp.route("/estados/<int:id>", methods=["PUT"])
def update_estado(id):
    estado = EstadoImpresora.query.get_or_404(id)
    data = request.json
    estado.nombre = data["nombre"]
    db.session.commit()
    return estado_schema.jsonify(estado)

@api_bp.route("/estados/<int:id>", methods=["DELETE"])
def delete_estado(id):
    estado = EstadoImpresora.query.get_or_404(id)
    db.session.delete(estado)
    db.session.commit()
    return jsonify({"message": "Estado deleted"})
