from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.impresoras import Impresoras

class ImpresorasSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Impresoras
        load_instance = True
