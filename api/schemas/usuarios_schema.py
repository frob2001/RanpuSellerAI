from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.usuarios import Usuarios

class UsuariosSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuarios
        load_instance = True
