from ..database import db

class EstadosPedidos(db.Model):
    __tablename__ = "estados_pedidos"

    estado_pedido_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    nombre_ingles = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "estado_pedido_id": self.estado_pedido_id,
            "nombre": self.nombre,
            "nombre_ingles": self.nombre_ingles
        }
