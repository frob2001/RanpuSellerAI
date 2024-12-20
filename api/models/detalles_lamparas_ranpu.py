from ..database import db

class DetallesLamparasRanpu(db.Model):
    __tablename__ = "detalles_lamparas_ranpu"

    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), primary_key=True)
    detalles = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "producto_id": self.producto_id,
            "detalles": self.detalles
        }
