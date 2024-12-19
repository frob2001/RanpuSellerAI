from ..database import db

class ImagenesProductos(db.Model):
    __tablename__ = "imagenes_productos"

    imagen_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ruta = db.Column(db.String(1000), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), nullable=False)

    # Cambiamos el nombre del backref para evitar conflictos
    producto = db.relationship('Productos', backref=db.backref('imagenes_list', lazy=True))

    def to_dict(self):
        return {
            "imagen_id": self.imagen_id,
            "ruta": self.ruta,
            "producto_id": self.producto_id
        }
