from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.productos_pedidos import ProductosPedidos

class ProductosPedidosSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProductosPedidos
        load_instance = True
