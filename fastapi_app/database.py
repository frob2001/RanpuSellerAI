from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Configuración de la base de datos
DATABASE_URL = "postgresql://ranpubackenddatabase_user:pKqQl2aSzKeFiqvsR5pUEUFipbWWcgox@dpg-ctgraj0gph6c73ck0ppg-a.oregon-postgres.render.com/ranpubackenddatabase"

# Crear la instancia del motor de SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declaración de la clase base
class Base(DeclarativeBase):
    pass
