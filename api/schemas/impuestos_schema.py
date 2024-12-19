from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.impuestos import Impuestos

class ImpuestosSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Impuestos
        load_instance = True
