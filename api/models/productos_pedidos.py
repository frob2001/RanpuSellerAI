from ..database import db

class ProductosPedidos(db.Model):
    __tablename__ = "productos_pedidos"

    producto_pedido_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.pedido_id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)

    pedido = db.relationship('Pedidos', backref=db.backref('productos_pedidos_list', lazy=True))
    producto = db.relationship('Productos', backref=db.backref('productos_pedidos_list', lazy=True))

    def to_dict(self):
        return {
            "producto_pedido_id": self.producto_pedido_id,
            "pedido_id": self.pedido_id,
            "producto_id": self.producto_id,
            "cantidad": self.cantidad
        }
