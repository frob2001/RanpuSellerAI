from fastapi import FastAPI
from fastapi_app.routes.example_routes import router as estado_impresora_router
from fastapi_app.database import Base, engine

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(title="API de Estados de Impresoras", version="1.0.0")

# Registrar rutas con prefijo
app.include_router(estado_impresora_router, prefix="/fastapi")
