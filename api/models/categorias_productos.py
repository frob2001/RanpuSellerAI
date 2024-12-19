from ..database import db

class CategoriasProductos(db.Model):
    __tablename__ = "categorias_productos"

    categoria_producto_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "categoria_producto_id": self.categoria_producto_id,
            "nombre": self.nombre
        }
