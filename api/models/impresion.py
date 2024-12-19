from ..database import db

class Impresion(db.Model):
    __tablename__ = "impresion"

    impresion_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    cantidad_filamento = db.Column(db.Numeric(10, 2), nullable=False)
    tiempo_impresion = db.Column(db.Time, nullable=False)
    peso = db.Column(db.Numeric(10, 2), nullable=False)
    impresora_id = db.Column(db.Integer, db.ForeignKey('impresoras.impresora_id'), nullable=False)
    filamento_id = db.Column(db.Integer, db.ForeignKey('filamentos.filamento_id'), nullable=False)

    impresora = db.relationship('Impresoras', backref=db.backref('impresion', lazy=True))
    filamento = db.relationship('Filamentos', backref=db.backref('impresion', lazy=True))
    modelos = db.relationship('ModelosImpresion', backref='impresion', lazy=True)

    def to_dict(self):
        return {
            "impresion_id": self.impresion_id,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
            "cantidad_filamento": str(self.cantidad_filamento),
            "tiempo_impresion": self.tiempo_impresion.isoformat() if self.tiempo_impresion else None,
            "peso": str(self.peso),
            "impresora_id": self.impresora_id,
            "filamento_id": self.filamento_id,
            "modelos": [modelo.to_dict() for modelo in self.modelos]
        }
