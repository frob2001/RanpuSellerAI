from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.categorias_filamentos import CategoriasFilamentos

class CategoriasFilamentosSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CategoriasFilamentos
        load_instance = True
