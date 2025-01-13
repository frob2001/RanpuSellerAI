from ..database import db

class DetallesProductosIA(db.Model):
    __tablename__ = "detalles_productos_ia"

    producto_id = db.Column(db.Integer, db.ForeignKey('productos.producto_id'), primary_key=True)
    detalles = db.Column(db.String(500), nullable=False)
    time_to_die = db.Column(db.DateTime, nullable=True)
    is_in_cart = db.Column(db.Boolean, nullable=False, default=False)
    is_in_order = db.Column(db.Boolean, nullable=False, default=False)
    obj_downloadable_url = db.Column(db.String(5000), nullable=True)
    url_expiring_date = db.Column(db.DateTime, nullable=True)
    origin_task_id = db.Column(db.String(200), nullable=True)
    scale = db.Column(db.Numeric(5, 2), nullable=False)

    def to_dict(self):
        return {
            "producto_id": self.producto_id,
            "detalles": self.detalles,
            "time_to_die": self.time_to_die,
            "is_in_cart": self.is_in_cart,
            "is_in_order": self.is_in_order,
            "obj_downloadable_url": self.obj_downloadable_url,
            "url_expiring_date": self.url_expiring_date,
            "origin_task_id": self.origin_task_id,
            "scale": float(self.scale)
        }
