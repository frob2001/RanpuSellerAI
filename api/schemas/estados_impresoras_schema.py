from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.estados_impresoras import EstadosImpresoras

class EstadosImpresorasSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EstadosImpresoras
        load_instance = True
