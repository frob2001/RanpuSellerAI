from ..database import db

class Colores(db.Model):
    __tablename__ = "colores"

    color_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    nombre_ingles = db.Column(db.String(50), nullable=False)
    hexadecimal = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            "color_id": self.color_id,
            "nombre": self.nombre,
            "nombre_ingles": self.nombre_ingles,
            "hexadecimal": self.hexadecimal
        }
