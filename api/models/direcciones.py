from ..database import db

class Direcciones(db.Model):
    __tablename__ = "direcciones"

    direccion_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cedula = db.Column(db.String(10), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    calle_principal = db.Column(db.String(100), nullable=False)
    calle_secundaria = db.Column(db.String(100), nullable=True)
    ciudad = db.Column(db.String(50), nullable=False)
    provincia = db.Column(db.String(50), nullable=False)
    numeracion = db.Column(db.String(10), nullable=True)
    referencia = db.Column(db.String(255), nullable=True)
    codigo_postal = db.Column(db.String(10), nullable=True)

    def to_dict(self):
        return {
            "direccion_id": self.direccion_id,
            "cedula": self.cedula,
            "nombre_completo": self.nombre_completo,
            "telefono": self.telefono,
            "calle_principal": self.calle_principal,
            "calle_secundaria": self.calle_secundaria,
            "ciudad": self.ciudad,
            "provincia": self.provincia,
            "numeracion": self.numeracion,
            "referencia": self.referencia,
            "codigo_postal": self.codigo_postal
        }
