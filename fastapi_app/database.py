from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://ranpubackenddatabase_user:pKqQl2aSzKeFiqvsR5pUEUFipbWWcgox@dpg-ctgraj0gph6c73ck0ppg-a:5432/ranpubackenddatabase"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
