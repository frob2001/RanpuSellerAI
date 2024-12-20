from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.impresion import Impresion

class ImpresionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Impresion
        load_instance = True
