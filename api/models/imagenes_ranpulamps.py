from ..database import db

class ImagenesRanpulamps(db.Model):
    __tablename__ = "imagenes_ranpulamps"

    imagenes_ranpulamps_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imagen_url = db.Column(db.String(1000), nullable=False)
    producto_pedido_id = db.Column(db.Integer, db.ForeignKey('productos_pedidos.producto_pedido_id'), nullable=False)

    # Relationship to access producto_pedido if needed
    producto_pedido = db.relationship('ProductosPedidos', backref='imagenes')

    def to_dict(self):
        return {
            "imagenes_ranpulamps_id": self.imagenes_ranpulamps_id,
            "imagen_url": self.imagen_url,
            "producto_pedido_id": self.producto_pedido_id
        }
