from ..database import db

class Modelos(db.Model):
    __tablename__ = "modelos"

    modelo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tiempo_estimado = db.Column(db.Time, nullable=False)
    alto = db.Column(db.Numeric(10, 2), nullable=False)
    ancho = db.Column(db.Numeric(10, 2), nullable=False)
    largo = db.Column(db.Numeric(10, 2), nullable=False)
    stl = db.Column(db.String(1000), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), nullable=False)

    # Cambiar el nombre del backref
    producto = db.relationship('Productos', backref=db.backref('modelos', lazy=True))

    def to_dict(self):
        return {
            "modelo_id": self.modelo_id,
            "tiempo_estimado": self.tiempo_estimado.isoformat(),
            "alto": str(self.alto),
            "ancho": str(self.ancho),
            "largo": str(self.largo),
            "stl": self.stl,
            "stock": self.stock,
            "producto_id": self.producto_id
        }
