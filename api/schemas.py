from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .models import EstadoImpresora

class EstadoImpresoraSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EstadoImpresora
        load_instance = True
