from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models.detalles_lamparas_ranpu import DetallesLamparasRanpu

class DetallesLamparasRanpuSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DetallesLamparasRanpu
        load_instance = True
