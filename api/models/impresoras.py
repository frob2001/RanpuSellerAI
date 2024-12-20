from ..database import db

class Impresoras(db.Model):
    __tablename__ = "impresoras"

    impresora_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    marca = db.Column(db.String(50), nullable=False)
    estado_impresora_id = db.Column(db.Integer, db.ForeignKey('estados_impresoras.estado_impresora_id'), nullable=False)
    alto_area = db.Column(db.Numeric(10, 2), nullable=False)
    ancho_area = db.Column(db.Numeric(10, 2), nullable=False)
    largo_area = db.Column(db.String(1000), nullable=False)
    max_temp_cama = db.Column(db.Numeric(10, 2), nullable=False)
    max_temp_extrusor = db.Column(db.Numeric(10, 2), nullable=False)
    diametro_extrusor = db.Column(db.Integer, nullable=False)
    consumo_electrico = db.Column(db.Numeric(10, 2), nullable=False)
    filamento_id = db.Column(db.Integer, db.ForeignKey('filamentos.filamento_id'), nullable=False)

    # Relaciones
    estado_impresora = db.relationship('EstadosImpresoras', backref=db.backref('impresoras', lazy=True))
    filamento = db.relationship('Filamentos', backref=db.backref('impresoras', lazy=True))

    def to_dict(self):
        return {
            "impresora_id": self.impresora_id,
            "marca": self.marca,
            "estado_impresora_id": self.estado_impresora_id,
            "alto_area": str(self.alto_area),
            "ancho_area": str(self.ancho_area),
            "largo_area": self.largo_area,
            "max_temp_cama": str(self.max_temp_cama),
            "max_temp_extrusor": str(self.max_temp_extrusor),
            "diametro_extrusor": self.diametro_extrusor,
            "consumo_electrico": str(self.consumo_electrico),
            "filamento_id": self.filamento_id
        }
