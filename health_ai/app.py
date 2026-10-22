from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ IMPORTANT FIX (forces template refresh)
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    db.init_app(app)
    mail.init_app(app)

    from routes.auth import auth_bp
    from routes.prediction import pred_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(pred_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

        import os
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        os.makedirs("models_saved", exist_ok=True)

        _create_default_admin()

    return app


def _create_default_admin():
    from models import User
    try:
        admin = User.query.filter_by(email="admin@health.com").first()
        if not admin:
            admin = User(
                full_name="Administrator",
                email="admin@health.com",
                age=30,
                gender="Other",
                phone="0000000000",
                role="admin",
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("[App] Default admin created: admin@health.com / admin123")
    except Exception as e:
        print(f"[App] Admin creation skipped: {e}")