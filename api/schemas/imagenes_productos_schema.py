from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.imagenes_productos import ImagenesProductos

class ImagenesProductosSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ImagenesProductos
        load_instance = True
