from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.direcciones import Direcciones

class DireccionesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Direcciones
        load_instance = True