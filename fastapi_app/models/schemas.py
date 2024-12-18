from pydantic import BaseModel

# Esquema de respuesta (lectura)
class EstadoImpresoraSchema(BaseModel):
    estado_impresora_id: int
    nombre: str

    class Config:
        from_attributes = True

# Esquema para la creación y actualización
class EstadoImpresoraCreateUpdateSchema(BaseModel):
    nombre: str
