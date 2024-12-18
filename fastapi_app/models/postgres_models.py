from sqlalchemy import Column, Integer, String
from fastapi_app.database import Base

class EstadoImpresora(Base):
    __tablename__ = 'estado_impresora'

    estado_impresora_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
