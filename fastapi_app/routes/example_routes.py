from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_app.database import SessionLocal
from fastapi_app.models.postgres_models import Impresora

router = APIRouter()

# Dependencia para obtener sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Obtener todas las impresoras
@router.get("/api/impresoras", response_model=list[dict])
def get_impresoras(db: Session = Depends(get_db)):
    impresoras = db.query(Impresora).all()
    return [{"impresora_id": i.impresora_id, "marca": i.marca, "alto_area": i.alto_area, "ancho_area": i.ancho_area} for i in impresoras]

# Crear una nueva impresora
@router.post("/api/impresoras", response_model=dict)
def create_impresora(impresora: dict, db: Session = Depends(get_db)):
    nueva_impresora = Impresora(**impresora)
    db.add(nueva_impresora)
    db.commit()
    db.refresh(nueva_impresora)
    return {"message": "Impresora creada", "impresora_id": nueva_impresora.impresora_id}

# Actualizar una impresora
@router.put("/api/impresoras/{id}", response_model=dict)
def update_impresora(id: int, updated_data: dict, db: Session = Depends(get_db)):
    impresora = db.query(Impresora).filter(Impresora.impresora_id == id).first()
    if not impresora:
        raise HTTPException(status_code=404, detail="Impresora no encontrada")
    for key, value in updated_data.items():
        setattr(impresora, key, value)
    db.commit()
    return {"message": "Impresora actualizada"}

# Eliminar una impresora
@router.delete("/api/impresoras/{id}", response_model=dict)
def delete_impresora(id: int, db: Session = Depends(get_db)):
    impresora = db.query(Impresora).filter(Impresora.impresora_id == id).first()
    if not impresora:
        raise HTTPException(status_code=404, detail="Impresora no encontrada")
    db.delete(impresora)
    db.commit()
    return {"message": "Impresora eliminada"}
