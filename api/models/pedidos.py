from ..database import db

class Pedidos(db.Model):
    __tablename__ = "pedidos"

    pedido_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_envio = db.Column(db.DateTime, nullable=False)
    fecha_entrega = db.Column(db.DateTime, nullable=False)
    fecha_pago = db.Column(db.DateTime, nullable=False)
    estado_pedido_id = db.Column(db.Integer, db.ForeignKey('estados_pedidos.estado_pedido_id'), nullable=False)
    direccion_id = db.Column(db.Integer, db.ForeignKey('direcciones.direccion_id'), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    impuesto_id = db.Column(db.Integer, db.ForeignKey('impuestos.impuesto_id'), nullable=False)
    precio_final = db.Column(db.Numeric(10, 2), nullable=False)
    pago_id = db.Column(db.String(1000), nullable=False)
    temporal_cart_id = db.Column(db.String(100), nullable=False)
    detalles_pago = db.Column(db.JSON, nullable=True)              
    ingreso_neto = db.Column(db.Numeric(10, 2), nullable=True) 

    estado_pedido = db.relationship('EstadosPedidos', backref=db.backref('pedidos', lazy=True))
    direcciones = db.relationship('Direcciones', backref=db.backref('pedidos', lazy=True))
    impuesto = db.relationship('Impuestos', backref=db.backref('pedidos', lazy=True))

    def to_dict(self):
        return {
            "pedido_id": self.pedido_id,
            "fecha_envio": self.fecha_envio.isoformat() if self.fecha_envio else None,
            "fecha_entrega": self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            "fecha_pago": self.fecha_pago.isoformat() if self.fecha_pago else None,
            "estado_pedido_id": self.estado_pedido_id,
            "direccion_id": self.direccion_id,
            "precio": str(self.precio),
            "impuesto_id": self.impuesto_id,
            "precio_final": str(self.precio_final),
            "pago_id": self.pago_id,
            "temporal_cart_id": self.temporal_cart_id,
            "detalles_pago": self.detalles_pago if self.detalles_pago else None, 
            "ingreso_neto": str(self.ingreso_neto) if self.ingreso_neto else None
        }
