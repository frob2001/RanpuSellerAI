from ..database import db

class Usuarios(db.Model):
    __tablename__ = "usuarios"

    usuario_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firebase_uid = db.Column(db.String(128), nullable=True)

    def to_dict(self):
        return {
            "usuario_id": self.usuario_id,
            "firebase_uid": self.firebase_uid
        }
