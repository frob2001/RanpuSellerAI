from flask import Blueprint, jsonify, request
from .models import EstadosImpresoras
from .schemas import EstadosImpresorasSchema
from .database import db

api_bp = Blueprint("api", __name__)

estado_schema = EstadosImpresorasSchema()
estados_schema = EstadosImpresorasSchema(many=True)

@api_bp.route("/estados", methods=["GET"])
def get_estados():
    """
    Obtener todos los estados
    ---
    tags:
      - Estados Impresoras
    summary: Obtiene la lista completa de estados de impresoras.
    responses:
      200:
        description: Lista de estados obtenida correctamente.
        schema:
          type: array
          items:
            properties:
              estado_impresora_id:
                type: integer
                example: 1
              nombre:
                type: string
                example: "Disponible"
    """
    estados = EstadosImpresoras.query.all()
    serialized_data = estados_schema.dump(estados)
    return jsonify(serialized_data)

@api_bp.route("/estados/<int:id>", methods=["GET"])
def get_estado(id):
    """
    Obtener un estado específico
    ---
    tags:
      - Estados Impresoras
    summary: Obtiene un estado de impresora por su ID.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID del estado de la impresora.
    responses:
      200:
        description: Estado obtenido correctamente.
        schema:
          properties:
            estado_impresora_id:
              type: integer
              example: 1
            nombre:
              type: string
              example: "Disponible"
      404:
        description: Estado no encontrado.
    """
    estado = EstadosImpresoras.query.get_or_404(id)
    serialized_data = estado_schema.dump(estado)
    return jsonify(serialized_data)

@api_bp.route("/estados", methods=["POST"])
def create_estado():
    """
    Crear un nuevo estado
    ---
    tags:
      - Estados Impresoras
    summary: Crea un nuevo estado de impresora.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            nombre:
              type: string
              example: "En mantenimiento"
    responses:
      201:
        description: Estado creado correctamente.
        schema:
          properties:
            estado_impresora_id:
              type: integer
              example: 2
            nombre:
              type: string
              example: "En mantenimiento"
    """
    data = request.json
    new_estado = EstadosImpresoras(nombre=data["nombre"])
    db.session.add(new_estado)
    db.session.commit()
    serialized_data = estado_schema.dump(new_estado)
    return jsonify(serialized_data), 201

@api_bp.route("/estados/<int:id>", methods=["PUT"])
def update_estado(id):
    """
    Actualizar un estado existente
    ---
    tags:
      - Estados Impresoras
    summary: Actualiza el nombre de un estado existente.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID del estado a actualizar.
      - name: body
        in: body
        required: true
        schema:
          properties:
            nombre:
              type: string
              example: "Ocupado"
    responses:
      200:
        description: Estado actualizado correctamente.
        schema:
          properties:
            estado_impresora_id:
              type: integer
              example: 2
            nombre:
              type: string
              example: "Ocupado"
      404:
        description: Estado no encontrado.
    """
    estado = EstadosImpresoras.query.get_or_404(id)
    data = request.json
    estado.nombre = data["nombre"]
    db.session.commit()
    serialized_data = estado_schema.dump(estado)
    return jsonify(serialized_data)

@api_bp.route("/estados/<int:id>", methods=["DELETE"])
def delete_estado(id):
    """
    Eliminar un estado
    ---
    tags:
      - Estados Impresoras
    summary: Elimina un estado de impresora por su ID.
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID del estado a eliminar.
    responses:
      200:
        description: Estado eliminado correctamente.
        schema:
          properties:
            message:
              type: string
              example: "Estado deleted"
      404:
        description: Estado no encontrado.
    """
    estado = EstadosImpresoras.query.get_or_404(id)
    db.session.delete(estado)
    db.session.commit()
    return jsonify({"message": "Estado deleted"})
