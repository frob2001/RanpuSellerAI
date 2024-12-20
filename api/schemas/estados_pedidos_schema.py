from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.estados_pedidos import EstadosPedidos

class EstadosPedidosSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EstadosPedidos
        load_instance = True
