from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.filamentos import Filamentos

class FilamentosSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Filamentos
        load_instance = True
