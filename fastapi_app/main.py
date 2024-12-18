from fastapi import FastAPI
from fastapi_app.routes.example_routes import router
from fastapi_app.database import Base, engine

# Inicialización de la base de datos
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(title="Ranpu Backend API", version="1.0.0")

# Registrar rutas
app.include_router(router)

# Mensaje de prueba para la raíz
@app.get("/")
def read_root():
    return {"message": "Bienvenido a FastAPI - Ranpu Backend"}
