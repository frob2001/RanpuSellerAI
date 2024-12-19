from ..database import db

class Productos(db.Model):
    __tablename__ = "productos"

    producto_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(1000), nullable=False)
    alto = db.Column(db.Numeric(10, 2), nullable=False)
    ancho = db.Column(db.Numeric(10, 2), nullable=False)
    largo = db.Column(db.Numeric(10, 2), nullable=False)
    gbl = db.Column(db.String(1000), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    categoria_producto_id = db.Column(db.Integer, db.ForeignKey('categorias_productos.categoria_producto_id'), nullable=False)

    categoria_producto = db.relationship('CategoriasProductos', backref=db.backref('productos', lazy=True))
    imagenes_productos = db.relationship('ImagenesProductos', backref='producto', lazy=True)
    modelo = db.relationship('Modelo', backref='producto', lazy=True)
    productos_pedidos = db.relationship('ProductosPedidos', backref='producto', lazy=True)

    # Esta línea es redundante si ya está declarada en DetallesCatalogo
    # detalles_catalogo_list = db.relationship('DetallesCatalogo', backref='producto', lazy=True)

    def to_dict(self):
        return {
            "producto_id": self.producto_id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "alto": str(self.alto),
            "ancho": str(self.ancho),
            "largo": str(self.largo),
            "gbl": self.gbl,
            "precio": str(self.precio),
            "categoria_producto_id": self.categoria_producto_id
        }
