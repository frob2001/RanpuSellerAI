from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.filamentos import Filamentos
from ..models.colores import Colores

from marshmallow import fields

class FilamentosSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Filamentos
        load_instance = True

    categoria_filamento_id = fields.Integer(required=True)  # Asegúrate de que este campo exista
    color = fields.Nested("ColoresSchema", dump_only=True)
    
