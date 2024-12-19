from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.filamentos_compatibles import FilamentosCompatibles

class FilamentosCompatiblesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = FilamentosCompatibles
        load_instance = True
