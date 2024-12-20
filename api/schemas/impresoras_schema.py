from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from ..models.impresoras import Impresoras

class ImpresorasSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Impresoras
        load_instance = True
        include_fk = True  # Incluye claves foráneas automáticamente

# Define explícitamente las claves foráneas si `include_fk` no funciona
estado_impresora_id = auto_field()
filamento_id = auto_field()
