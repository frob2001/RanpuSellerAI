from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.categorias_productos import CategoriasProductos

class CategoriasProductosSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CategoriasProductos
        load_instance = True
