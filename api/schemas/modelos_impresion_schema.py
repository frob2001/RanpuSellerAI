from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.modelos_impresion import ModelosImpresion

class ModelosImpresionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ModelosImpresion
        load_instance = True
