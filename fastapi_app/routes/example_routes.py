from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_app.database import SessionLocal
from fastapi_app.models.postgres_models import EstadoImpresora
from fastapi_app.models.schemas import EstadoImpresoraSchema, EstadoImpresoraCreateUpdateSchema

router = APIRouter(prefix="/api/estado_impresoras", tags=["Estado Impresoras"])

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Obtener todos los estados
@router.get("/", response_model=list[EstadoImpresoraSchema])
def get_estados(db: Session = Depends(get_db)):
    return db.query(EstadoImpresora).all()

# Crear un nuevo estado
@router.post("/", response_model=EstadoImpresoraSchema)
def create_estado(estado: EstadoImpresoraCreateUpdateSchema, db: Session = Depends(get_db)):
    nuevo_estado = EstadoImpresora(nombre=estado.nombre)
    db.add(nuevo_estado)
    db.commit()
    db.refresh(nuevo_estado)
    return nuevo_estado

# Actualizar un estado existente
@router.put("/{id}", response_model=EstadoImpresoraSchema)
def update_estado(id: int, estado: EstadoImpresoraCreateUpdateSchema, db: Session = Depends(get_db)):
    estado_db = db.query(EstadoImpresora).filter(EstadoImpresora.estado_impresora_id == id).first()
    if not estado_db:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    estado_db.nombre = estado.nombre
    db.commit()
    db.refresh(estado_db)
    return estado_db

# Eliminar un estado
@router.delete("/{id}")
def delete_estado(id: int, db: Session = Depends(get_db)):
    estado_db = db.query(EstadoImpresora).filter(EstadoImpresora.estado_impresora_id == id).first()
    if not estado_db:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    db.delete(estado_db)
    db.commit()
    return {"message": "Estado eliminado correctamente"}
