from ..database import db

class DetallesCatalogo(db.Model):
    __tablename__ = "detalles_catalogo"

    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), primary_key=True)
    detalles = db.Column(db.String(50), nullable=False)

    producto = db.relationship('Productos', backref=db.backref('detalles_catalogo', lazy=True))

    def to_dict(self):
        return {
            "producto_id": self.producto_id,
            "detalles": self.detalles
        }
