from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.modelos import Modelos

class ModelosSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Modelos
        load_instance = True
        include_fk = True  # Incluye claves foráneas explícitamente
