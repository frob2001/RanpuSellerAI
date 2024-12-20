from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.pedidos_usuario import PedidosUsuario

class PedidosUsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PedidosUsuario
        load_instance = True
