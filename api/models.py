from .database import db

class EstadoImpresora(db.Model):
    __tablename__ = "estado_impresora"

    estado_impresora_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "estado_impresora_id": self.estado_impresora_id,
            "nombre": self.nombre
        }