from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.modelo import Modelo

class ModeloSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Modelo
        load_instance = True
