from ..database import db

class ModelosImpresion(db.Model):
    __tablename__ = "modelos_impresion"

    impresion_id = db.Column(db.Integer, db.ForeignKey('impresion.impresion_id'), primary_key=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo.modelo_id'), primary_key=True)

    impresion = db.relationship('Impresion', backref=db.backref('modelos_impresion', lazy=True))
    modelo = db.relationship('Modelo', backref=db.backref('modelos_impresion', lazy=True))

    def to_dict(self):
        return {
            "impresion_id": self.impresion_id,
            "modelo_id": self.modelo_id
        }
