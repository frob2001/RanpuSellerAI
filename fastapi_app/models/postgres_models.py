from sqlalchemy import Column, Integer, String, Float
from fastapi_app.database import Base

class Impresora(Base):
    __tablename__ = "impresoras"

    impresora_id = Column(Integer, primary_key=True, index=True)
    marca = Column(String, nullable=False)
    estado_impresora_id = Column(Integer, nullable=False)
    alto_area = Column(Float, nullable=True)
    ancho_area = Column(Float, nullable=True)
    largo_area = Column(Float, nullable=True)
    max_temp_cama = Column(Float, nullable=True)
    max_temp_extrusor = Column(Float, nullable=True)
    diametro_extrusor = Column(Float, nullable=True)
    consumo_electrico = Column(Float, nullable=True)
    filamento_id = Column(Integer, nullable=True)
