from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.detalles_catalogo import DetallesCatalogo

class DetallesCatalogoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DetallesCatalogo
        load_instance = True
