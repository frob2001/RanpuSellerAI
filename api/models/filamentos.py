from ..database import db

class Filamentos(db.Model):
    __tablename__ = "filamentos"

    filamento_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    color = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    peso_inicial = db.Column(db.Numeric(10, 2), nullable=False)
    peso_actual = db.Column(db.Numeric(10, 2), nullable=False)
    longitud_inicial = db.Column(db.Numeric(10, 2), nullable=False)
    longitud_actual = db.Column(db.Numeric(10, 2), nullable=False)
    precio_compra = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_compra = db.Column(db.DateTime, nullable=False)
    categoria_filamento_id = db.Column(db.Integer, db.ForeignKey('categorias_filamentos.categoria_filamento_id'), nullable=False)

    # Relaciones
    categoria_filamento = db.relationship('CategoriasFilamentos', backref=db.backref('filamentos', lazy=True))

    def to_dict(self):
        return {
            "filamento_id": self.filamento_id,
            "color": self.color,
            "marca": self.marca,
            "peso_inicial": str(self.peso_inicial),
            "peso_actual": str(self.peso_actual),
            "longitud_inicial": str(self.longitud_inicial),
            "longitud_actual": str(self.longitud_actual),
            "precio_compra": str(self.precio_compra),
            "fecha_compra": self.fecha_compra.isoformat() if self.fecha_compra else None,
            "categoria_filamento_id": self.categoria_filamento_id
        }
