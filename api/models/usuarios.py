from ..database import db

class Usuarios(db.Model):
    __tablename__ = "usuarios"

    usuario_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def to_dict(self):
        return {
            "usuario_id": self.usuario_id
        }
