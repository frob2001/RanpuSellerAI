from ..database import db

class Usuarios(db.Model):
    __tablename__ = "usuarios"

    usuario_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firebase_uid = db.Column(db.String(128), nullable=True)
    ai_gen_tokens = db.Column(db.Integer, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "usuario_id": self.usuario_id,
            "firebase_uid": self.firebase_uid,
            "ai_gen_tokens": self.ai_gen_tokens,
            "last_login": self.last_login
        }
