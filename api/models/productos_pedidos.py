from ..database import db

class ProductosPedidos(db.Model):
    __tablename__ = "productos_pedidos"

    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.pedido_id'), primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)

    pedido = db.relationship('Pedidos', backref=db.backref('productos_pedidos_list', lazy=True))  # Renombramos el backref
    producto = db.relationship('Productos', backref=db.backref('productos_pedidos_list', lazy=True))

    def to_dict(self):
        return {
            "pedido_id": self.pedido_id,
            "producto_id": self.producto_id,
            "cantidad": self.cantidad
        }
