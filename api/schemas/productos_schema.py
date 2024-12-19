from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.productos import Productos

class ProductosSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Productos
        load_instance = True
