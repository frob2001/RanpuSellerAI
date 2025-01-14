from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.colores import Colores

class ColoresSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Colores
        load_instance = True
