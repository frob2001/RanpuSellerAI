from ..database import db

class ImagenesProductos(db.Model):
    __tablename__ = "imagenes_productos"

    imagen_producto_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(255), nullable=False)
    ubicacion = db.Column(db.String(1000), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), nullable=False)
    is_thumbnail = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {
            "imagen_producto_id": self.imagen_producto_id,
            "descripcion": self.descripcion,
            "ubicacion": self.ubicacion,
            "producto_id": self.producto_id,
            "is_thumbnail": self.is_thumbnail
        }
