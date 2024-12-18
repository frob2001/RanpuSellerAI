from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        "postgresql://ranpubackenddatabase_user:"
        "pKqQl2aSzKeFiqvsR5pUEUFipbWWcgox"
        "@dpg-ctgraj0gph6c73ck0ppg-a.oregon-postgres.render.com:5432/ranpubackenddatabase"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
