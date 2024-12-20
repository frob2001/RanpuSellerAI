from ..database import db

class Impuestos(db.Model):
    __tablename__ = "impuestos"

    impuesto_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    porcentaje = db.Column(db.Numeric(5, 2), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {
            "impuesto_id": self.impuesto_id,
            "nombre": self.nombre,
            "porcentaje": str(self.porcentaje),
            "activo": self.activo
        }
