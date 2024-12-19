from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.detalles_productos_ia import DetallesProductosIA

class DetallesProductosIASchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DetallesProductosIA
        load_instance = True
