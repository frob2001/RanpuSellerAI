from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.pedidos import Pedidos

class PedidosSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Pedidos
        load_instance = True
