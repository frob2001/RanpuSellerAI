from ..database import db

class CategoriasFilamentos(db.Model):
    __tablename__ = "categorias_filamentos"

    categoria_filamento_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(1000), nullable=False)
    diametro = db.Column(db.Numeric(10, 2), nullable=False)
    temp_extrusion = db.Column(db.Numeric(10, 2), nullable=False)
    temp_cama = db.Column(db.Numeric(10, 2), nullable=False)
    resistencia = db.Column(db.Numeric(10, 2), nullable=False)
    flexibilidad = db.Column(db.Numeric(10, 2), nullable=False)
    material_base = db.Column(db.String(50), nullable=False)
    precio_kg = db.Column(db.Numeric(10, 2), nullable=False)

    filamentos = db.relationship('Filamentos', backref='categoria_filamento', lazy=True)

    def to_dict(self):
        return {
            "categoria_filamento_id": self.categoria_filamento_id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "diametro": str(self.diametro),
            "temp_extrusion": str(self.temp_extrusion),
            "temp_cama": str(self.temp_cama),
            "resistencia": str(self.resistencia),
            "flexibilidad": str(self.flexibilidad),
            "material_base": self.material_base,
            "precio_kg": str(self.precio_kg)
        }
