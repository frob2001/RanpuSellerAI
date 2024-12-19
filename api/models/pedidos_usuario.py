from ..database import db

class PedidosUsuario(db.Model):
    __tablename__ = "pedidos_usuario"

    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.pedido_id'), primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'), primary_key=True)

    pedido = db.relationship('Pedidos', backref=db.backref('pedidos_usuario', lazy=True))
    usuario = db.relationship('Usuarios', backref=db.backref('pedidos_usuario', lazy=True))

    def to_dict(self):
        return {
            "pedido_id": self.pedido_id,
            "usuario_id": self.usuario_id
        }
