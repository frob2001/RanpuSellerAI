from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        "postgresql://ranpubackenddatabase_user:"
        "pKqQ12aSzKeFiqvsR5pUEUFipbWWcgox"
        "@dpg-ctgraj0gph6c73ck0ppg-a:5432/ranpubackenddatabase"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
