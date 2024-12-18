from .database import db

class EstadosImpresoras(db.Model):
    __tablename__ = "estados_impresoras"

    estado_impresora_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "estado_impresora_id": self.estado_impresora_id,
            "nombre": self.nombre
        }
