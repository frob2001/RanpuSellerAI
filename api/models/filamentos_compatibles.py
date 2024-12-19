from ..database import db

class FilamentosCompatibles(db.Model):
    __tablename__ = "filamentos_compatibles"

    impresora_id = db.Column(db.Integer, db.ForeignKey('impresoras.impresora_id'), primary_key=True)
    categoria_filamento_id = db.Column(db.Integer, db.ForeignKey('categorias_filamentos.categoria_filamento_id'), primary_key=True)

    impresora = db.relationship('Impresoras', backref=db.backref('filamentos_compatibles', lazy=True))
    categoria_filamento = db.relationship('CategoriasFilamentos', backref=db.backref('filamentos_compatibles', lazy=True))

    def to_dict(self):
        return {
            "impresora_id": self.impresora_id,
            "categoria_filamento_id": self.categoria_filamento_id
        }
